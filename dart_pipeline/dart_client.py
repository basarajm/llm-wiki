# -*- coding: utf-8 -*-
"""
dart_client.py — DART OpenAPI 클라이언트 (표준 라이브러리 urllib 만 사용).

기능:
  - list_disclosures(): 공시검색(list.json) 페이지네이션
  - download_document(): 공시서류 원문(document.xml) ZIP 바이트 다운로드
  - DART 상태코드 처리(분당 제한·일일 제한·데이터 없음 등) 및 네트워크 재시도
"""

import json
import time
import urllib.parse
import urllib.request
import urllib.error

BASE = "https://opendart.fss.or.kr/api"

# DART 상태코드 의미
STATUS_MSG = {
    "000": "정상",
    "010": "등록되지 않은 키",
    "011": "사용할 수 없는 키",
    "012": "접근할 수 없는 IP",
    "013": "조회된 데이터 없음",
    "014": "파일이 존재하지 않음",
    "020": "분당 요청 한도 초과",
    "021": "일일 조회 한도 초과",
    "100": "부적절한 값",
    "101": "부적절한 접근",
    "800": "시스템 점검 중",
    "900": "정의되지 않은 오류",
    "901": "사용자 계정 변경",
}


class DartDailyLimitError(Exception):
    """일일 조회 한도(코드 021) 초과 — 다음 날 재시도 필요."""


class DartError(Exception):
    pass


class DartClient:
    def __init__(self, api_key, request_delay=0.15, max_retries=4):
        self.api_key = api_key
        self.request_delay = request_delay
        self.max_retries = max_retries

    # ---- 저수준 HTTP ----
    def _open(self, path, params, timeout=60):
        q = dict(params)
        q["crtfc_key"] = self.api_key
        url = f"{BASE}/{path}?{urllib.parse.urlencode(q)}"
        last_err = None
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": "Mozilla/5.0 (dart-pipeline)"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return r.read()
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
        raise DartError(f"HTTP 실패: {url} ({last_err})")

    # ---- 공시검색 ----
    def list_disclosures(self, bgn_de, end_de, pblntf_detail_ty,
                         last_reprt_at="Y", page_count=100, corp_code=None):
        """기간 내 해당 유형 공시를 페이지네이션하며 항목을 yield.

        corp_code 지정 시 특정 기업만 조회(단, DART 규정상 검색기간 3개월 이내).
        """
        page_no = 1
        while True:
            params = {
                "bgn_de": bgn_de,
                "end_de": end_de,
                "pblntf_detail_ty": pblntf_detail_ty,
                "last_reprt_at": last_reprt_at,
                "page_no": page_no,
                "page_count": page_count,
            }
            if corp_code:
                params["corp_code"] = corp_code
            raw = self._open("list.json", params)
            time.sleep(self.request_delay)
            data = json.loads(raw.decode("utf-8"))
            status = data.get("status")
            if status == "013":  # 데이터 없음
                return
            if status == "020":  # 분당 제한 → 대기 후 같은 페이지 재시도
                time.sleep(61)
                continue
            if status == "021":
                raise DartDailyLimitError(STATUS_MSG["021"])
            if status != "000":
                raise DartError(f"list.json status={status} "
                                f"({STATUS_MSG.get(status, '?')}) {data.get('message')}")
            for item in data.get("list", []):
                yield item
            total_page = int(data.get("total_page", 1) or 1)
            if page_no >= total_page:
                return
            page_no += 1

    # ---- 원문 다운로드 ----
    def download_document(self, rcept_no, timeout=120):
        """document.xml ZIP 바이트를 반환. 오류 시 DartError/DartDailyLimitError."""
        for attempt in range(self.max_retries):
            raw = self._open("document.xml", {"rcept_no": rcept_no}, timeout=timeout)
            time.sleep(self.request_delay)
            if raw[:2] == b"PK":  # ZIP 시그니처
                return raw
            # ZIP이 아니면 보통 XML/JSON 오류 응답
            head = raw[:400].decode("utf-8", "replace")
            if "<status>020" in head or '"020"' in head:
                time.sleep(61)
                continue
            if "<status>021" in head or '"021"' in head:
                raise DartDailyLimitError(STATUS_MSG["021"])
            # 014(파일없음) 등은 재시도 무의미
            raise DartError(f"비-ZIP 응답 (rcept_no={rcept_no}): {head[:200]}")
        raise DartError(f"원문 다운로드 반복 실패 (rcept_no={rcept_no})")
