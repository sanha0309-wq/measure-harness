"""S1 — raw를 input.yaml · rules.yaml과 대조한다 (G-수집 I1~I6).

사용: python scripts/ingest.py <run>
차단 0 → 상태 「정리 중」. 차단 있으면 retries.ingest +1, 한도를 넘으면 종료 코드 4.
"""
import json
import sys

from build_snippet import config
from lib import GATE_FAIL, OK, STOP, dump_json, load_json, load_run, load_yaml, rules, run_dir, save_run, set_status, require_status, utf8_io

KEYS = {"snippet", "configHash", "screen", "url", "viewport", "dpr", "measuredAt", "truncated", "elements"}


def check(d) -> list[dict]:
    r = rules()
    inp = load_yaml(d / "input.yaml") or {}
    hits = []

    def hit(rule, where, detail):
        hits.append({"rule": rule, "item": where, "detail": detail})

    screens = {s["name"]: s for s in inp.get("screens") or []}
    dom_screens = {n for n, s in screens.items() if s.get("method", "dom") == "dom"}
    files = {p.stem[len("dom-"):]: p for p in (d / "raw").glob("dom-*.json")}

    for name, p in files.items():
        try:
            raw = load_json(p)
        except json.JSONDecodeError as e:
            hit("I1", p.name, f"JSON 아님: {e}")
            continue
        missing = KEYS - set(raw)
        if missing or raw.get("snippet") != "measure-harness":
            hit("I1", p.name, f"스니펫 형식 아님 (빠진 키 {sorted(missing)})")
            continue
        if raw["configHash"] != config()["hash"]:
            hit("I1", p.name, "지금 rules.yaml로 만든 스니펫이 아님 — build_snippet.py 후 다시 실행")
        for e in raw["elements"]:
            if not {"path", "text", "styles"} <= set(e):
                hit("I1", p.name, "요소 형식 아님")
                break
        if raw["viewport"].get("width") != r["run"]["viewport_width"]:
            hit("I2", p.name, f"화면 폭 {raw['viewport'].get('width')} ≠ {r['run']['viewport_width']}")
        if not isinstance(raw.get("dpr"), (int, float)):
            hit("I3", p.name, "devicePixelRatio 없음")
        if raw["screen"] != name:
            hit("I4", p.name, f"JSON 안 화면 이름 {raw['screen']} ≠ 파일 이름 {name}")
        if raw.get("truncated"):
            hit("I6", p.name, f"요소 {len(raw['elements'])}개에서 잘림")

    for name in dom_screens - set(files):
        hit("I4", name, "input.yaml에 있는데 raw/dom-*.json 없음")
    for name in set(files) - dom_screens:
        hit("I4", name, "raw는 있는데 input.yaml screens에 없음")

    for c in inp.get("captures") or []:
        if not isinstance(c.get("scale"), (int, float)):
            hit("I5", c.get("name"), "배율 없음")
        if not (d / "raw" / "captures" / str(c.get("file"))).exists():
            hit("I5", c.get("name"), f"파일 없음: raw/captures/{c.get('file')}")
    if not screens:
        hit("I4", "input.yaml", "screens 비어 있음")
    return hits


def main() -> int:
    utf8_io()
    d = run_dir(sys.argv[1])
    require_status(d, "수집 중")
    r = rules()
    levels = {g["id"]: g["level"] for g in r["gates"]["ingest"]}
    hits = check(d)
    blocks = [h for h in hits if levels[h["rule"]] == "block"]
    counts = {}
    for h in hits:
        counts[h["rule"]] = counts.get(h["rule"], 0) + 1
    dump_json(d / "raw" / "ingest-report.json", {"block": len(blocks), "warn": len(hits) - len(blocks), "counts": counts, "hits": hits})
    for h in hits:
        print(f"{h['rule']} [{levels[h['rule']]}] {h['item']}: {h['detail']}")
    print(f"차단 {len(blocks)} · 경고 {len(hits) - len(blocks)}")
    if not blocks:
        set_status(d, "정리 중")
        return OK
    data = load_run(d)
    data["retries"]["ingest"] += 1
    save_run(d, data)
    if data["retries"]["ingest"] > r["retry"]["ingest"]:
        print(f"수집 재시도 한도 초과 ({data['retries']['ingest']}/{r['retry']['ingest']}) — 화면을 input.yaml에서 빼거나 사람이 판단")
        return STOP
    return GATE_FAIL


if __name__ == "__main__":
    sys.exit(main())
