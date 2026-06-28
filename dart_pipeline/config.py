# -*- coding: utf-8 -*-
"""
config.py — DART 다운로드 파이프라인 설정.

⚠️ API 키는 이 파일에 저장하지 않습니다. 아래 중 하나로 외부에서 주입하세요.
   1) 환경변수:   set DART_API_KEY=발급받은키        (Windows)
                  export DART_API_KEY=발급받은키      (bash)
   2) 실행 인자:  python run.py --api-key 발급받은키
                  python build_targets.py --api-key 발급받은키

DART OpenAPI 키 발급: https://opendart.fss.or.kr/  (무료, 일 20,000회)
"""

import os
import sys

# 환경변수에서만 읽음(하드코딩 금지). 비어 있으면 CLI 인자 또는 require_api_key()로 보완.
DART_API_KEY = os.environ.get("DART_API_KEY", "").strip()


def require_api_key(cli_value=None):
    """env 또는 CLI 인자에서 API 키를 확보. 없으면 안내 후 종료."""
    key = (cli_value or DART_API_KEY or "").strip()
    if not key:
        sys.exit(
            "[설정 오류] DART API 키가 없습니다.\n"
            "  환경변수 DART_API_KEY 를 설정하거나 --api-key 인자를 전달하세요.\n"
            "  키 발급: https://opendart.fss.or.kr/"
        )
    return key


# 대상 시장 (corp_cls): Y=유가증권(KOSPI), K=코스닥(KOSDAQ), N=코넥스, E=기타
TARGET_MARKETS = {"Y", "K"}

MARKET_NAME = {"Y": "KOSPI", "K": "KOSDAQ", "N": "KONEX", "E": "기타"}

# 최신 사업보고서 탐색 기간(개월). 비-12월 결산법인까지 안전하게 포함하도록 넉넉히 설정.
LOOKBACK_MONTHS = 24

# 사업보고서 공시유형 상세코드
PBLNTF_DETAIL_TY = "A001"  # 사업보고서

# 요청 간 지연(초) — DART 분당 요청제한(코드 020) 회피용
REQUEST_DELAY = 0.15

# 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "_state")
OUTPUT_DIR = os.path.join(BASE_DIR, "dart_md")
TARGETS_PATH = os.path.join(STATE_DIR, "targets.json")
PROGRESS_PATH = os.path.join(STATE_DIR, "progress.json")
FAILURES_PATH = os.path.join(STATE_DIR, "failures.json")
