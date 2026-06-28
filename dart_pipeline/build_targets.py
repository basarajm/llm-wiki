# -*- coding: utf-8 -*-
"""
build_targets.py — KOSPI/KOSDAQ 상장기업의 '가장 최근 사업보고서' 목록 생성.

방법:
  - DART 공시검색(list.json, pblntf_detail_ty=A001, last_reprt_at=Y)을 월 단위로 순회
  - corp_cls 가 Y(KOSPI)/K(KOSDAQ)이고 종목코드가 있는 항목만 채택
  - 동일 기업(corp_code)은 접수일(rcept_dt)이 가장 늦은 1건만 유지 → '최신 사업보고서'
  - 결과를 _state/targets.json 으로 저장

사용:
  python build_targets.py [--months 24]
"""

import argparse
import datetime as dt
import json
import os
import sys

import config
from dart_client import DartClient, DartDailyLimitError


def month_windows(months_back, today=None):
    """오늘로부터 months_back 개월 전 ~ 오늘까지를 월 단위 (bgn,end) 문자열로 생성."""
    today = today or dt.date.today()
    # 시작 월의 1일
    y, m = today.year, today.month
    total = months_back
    sm_year = y
    sm_month = m - total
    while sm_month <= 0:
        sm_month += 12
        sm_year -= 1
    cur = dt.date(sm_year, sm_month, 1)
    windows = []
    while cur <= today:
        # 해당 월의 말일
        if cur.month == 12:
            nxt = dt.date(cur.year + 1, 1, 1)
        else:
            nxt = dt.date(cur.year, cur.month + 1, 1)
        end = min(nxt - dt.timedelta(days=1), today)
        windows.append((cur.strftime("%Y%m%d"), end.strftime("%Y%m%d")))
        cur = nxt
    return windows


def build(months_back, api_key=None):
    client = DartClient(config.require_api_key(api_key),
                        request_delay=config.REQUEST_DELAY)
    windows = month_windows(months_back)
    print(f"[targets] {len(windows)}개 월 구간 조회 "
          f"({windows[0][0]} ~ {windows[-1][1]})", flush=True)

    best = {}  # corp_code -> item (최신 rcept 유지)
    for bgn, end in windows:
        cnt = 0
        for item in client.list_disclosures(
            bgn, end, config.PBLNTF_DETAIL_TY, last_reprt_at="Y"
        ):
            if item.get("corp_cls") not in config.TARGET_MARKETS:
                continue
            if not (item.get("stock_code") or "").strip():
                continue
            cc = item["corp_code"]
            key = (item.get("rcept_dt", ""), item.get("rcept_no", ""))
            if cc not in best or key > (best[cc].get("rcept_dt", ""),
                                        best[cc].get("rcept_no", "")):
                best[cc] = item
            cnt += 1
        print(f"  {bgn}~{end}: {cnt}건 (누적 기업 {len(best)})", flush=True)

    targets = []
    for cc, item in best.items():
        targets.append({
            "corp_code": cc,
            "corp_name": item.get("corp_name", "").strip(),
            "stock_code": (item.get("stock_code") or "").strip(),
            "market": config.MARKET_NAME.get(item.get("corp_cls"), item.get("corp_cls")),
            "report_nm": item.get("report_nm", "").strip(),
            "rcept_no": item.get("rcept_no", "").strip(),
            "rcept_dt": item.get("rcept_dt", "").strip(),
        })
    targets.sort(key=lambda t: (t["market"], t["stock_code"]))

    os.makedirs(config.STATE_DIR, exist_ok=True)
    with open(config.TARGETS_PATH, "w", encoding="utf-8") as f:
        json.dump(targets, f, ensure_ascii=False, indent=1)

    by_mkt = {}
    for t in targets:
        by_mkt[t["market"]] = by_mkt.get(t["market"], 0) + 1
    print(f"\n[targets] 총 {len(targets)}개 기업 저장 → {config.TARGETS_PATH}")
    for k, v in sorted(by_mkt.items()):
        print(f"  {k}: {v}개")
    return targets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=config.LOOKBACK_MONTHS)
    ap.add_argument("--api-key", default=None, help="DART API 키(미지정 시 env DART_API_KEY 사용)")
    args = ap.parse_args()
    try:
        build(args.months, api_key=args.api_key)
    except DartDailyLimitError as e:
        print(f"[중단] 일일 한도 초과: {e}. 내일 다시 실행하세요.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
