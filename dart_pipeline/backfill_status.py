"""products/financial_products/ratings 소급 백필 추적 헬퍼.

옵션 B: 이미 Full 인제스트된 기업에 product/financial_product/ratings를 소급 생성.
- 대상: wiki/companies/*.md 중 is_stub != true (실제 인제스트 완료 기업)
- 진행: wiki/outputs/backfill-done.json (백필 처리 완료한 기업 wiki 노드명 집합)
- 정렬: ticker(종목코드) 오름차순, 없으면 이름순 뒤로

사용:
  python backfill_status.py            # 현황 + 대기 상위 10개
  python backfill_status.py --next 3   # 대기 상위 3개(JSON, 이름만)
  python backfill_status.py --done "삼성전자,SK하이닉스"  # 백필 완료 표시
"""
import os, sys, json, glob, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.join(HERE, "..", "wiki")
STATE = os.path.join(WIKI, "outputs", "backfill-done.json")


def read_fm(path):
    fm = {}
    try:
        with open(path, encoding="utf-8") as f:
            txt = f.read()
    except OSError:
        return fm
    if not txt.startswith("---"):
        return fm
    end = txt.find("\n---", 3)
    if end == -1:
        return fm
    for line in txt[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def full_companies():
    out = []
    for f in glob.glob(os.path.join(WIKI, "companies", "*.md")):
        name = os.path.splitext(os.path.basename(f))[0]
        fm = read_fm(f)
        if fm.get("is_stub", "").strip().lower() == "true":
            continue
        if fm.get("type", "").strip() != "Company":
            continue
        ticker = fm.get("ticker", "").strip().strip('"')
        out.append((ticker if ticker else "zzz999", name))
    out.sort(key=lambda x: (x[0], x[1]))
    return [n for _, n in out]


def load_done():
    if os.path.exists(STATE):
        try:
            return set(json.load(open(STATE, encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    return set()


def save_done(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(sorted(s), open(STATE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", type=int, default=0)
    ap.add_argument("--done", default="")
    args = ap.parse_args()

    done = load_done()
    if args.done:
        for n in [x.strip() for x in args.done.split(",") if x.strip()]:
            done.add(n)
        save_done(done)

    full = full_companies()
    pending = [n for n in full if n not in done]

    if args.next:
        print(json.dumps(pending[:args.next], ensure_ascii=False))
        return

    print(f"[backfill] Full 기업 {len(full)} / 백필완료 {len(done)} / 대기 {len(pending)}")
    print("대기 상위 10:", json.dumps(pending[:10], ensure_ascii=False))


if __name__ == "__main__":
    main()
