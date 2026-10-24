"""R8 하네스 검증 (1회) — 「완료」 run을 손으로 잰 refs 문서와 나란히 놓고 센다 (PRD §9-2).

사용: python scripts/verify_refs.py <run>
- refs를 읽는 스크립트는 이것 하나뿐이다. 평소 run 스크립트는 refs 없이 돈다
- 대응표는 rules.yaml refs_compare.map (refs 값 하나 → 템플릿 항목 ID 하나). quote가 refs 원문에 없으면 멈춘다
- 「원래 기준」과, refs_compare.exclude를 분모에서 뺀 「뺀 기준」 두 가지로 센다
- 결과는 runs/<run>/verify-refs.json. 판정 수치는 refs_compare.pass
"""
import re
import sys

from lib import ROOT, atoms, blocks, dump_json, load_json, load_run, load_yaml, parts, read_text, rules, run_dir, template, utf8_io

MEASURED = {"dom", "pixel", "est"}


def close(a: list, b: list, tol: float) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


def same(ref: str, ours: str, tol: float) -> bool:
    ra, oa = atoms(ref), atoms(ours)
    return (ra["colors"] == oa["colors"] and close(ra["nums"], oa["nums"], tol)
            and [w.lower() for w in ra["words"]] == [w.lower() for w in oa["words"]])


def excluded(item: dict, ex: dict) -> bool:
    iid = item.get("id") or ""
    return any(iid.endswith("." + s) for s in ex.get("id_suffix") or []) or item.get("tag") in (ex.get("tags") or [])


def count(rows: list[dict]) -> dict:
    measured = [x for x in rows if x["measured"]]
    return {
        "mapped": len(rows),
        "measured": len(measured),
        "match": sum(x["match"] for x in measured),
        "differ": sum(not x["match"] for x in measured),
        "coverage": round(len(measured) / len(rows), 3) if rows else None,
    }


def main() -> int:
    utf8_io()
    d = run_dir(sys.argv[1])
    if load_run(d)["status"] != "완료":
        print("R8은 「완료」 run에만 한다")
        return 1
    r = rules()
    rc = r["refs_compare"]
    mp = load_yaml(ROOT / rc["map"])
    if not mp:
        print(f"대응표 없음: {rc['map']}")
        return 1
    doc = read_text(ROOT / mp["refs"])
    values = blocks(d)["values"]
    ids = {i["id"] for i in template()["items"]}

    rows, bad = [], []
    for it in mp["items"]:
        quotes = it["quote"] if isinstance(it["quote"], list) else [it["quote"]]
        missing = [q for q in quotes if q not in doc]
        if missing or (it.get("id") is not None and it["id"] not in ids):
            bad.append({"item": it, "missing_quote": missing})
            continue
        iid = it.get("id")
        b = values.get(iid) if iid else None
        # 843 폭 값 — run은 폭 하나(run.viewport_width)만 재므로, 같은 ID에 값이 있어도 그 폭에서 잰 값이 아니다
        measured = bool(b) and b.get("src") in MEASURED and b.get("value") is not None and it.get("tag") != "w843"
        ours = None
        if measured:
            ours = str(b["value"])
            if it.get("part"):
                ps = parts(ours, r)
                ours = ps[it["part"] - 1] if it["part"] <= len(ps) else None
                measured = ours is not None
        tol = rc["tolerance"]["layout_length"] if (iid or "").startswith("layout.") else rc["tolerance"]["other"]
        rows.append({"id": iid, "part": it.get("part"), "tag": it.get("tag"), "refs": str(it["value"]),
                     "ours": ours, "measured": measured, "match": measured and same(str(it["value"]), ours, tol),
                     "excluded": excluded(it, rc.get("exclude") or {})})
    if bad:
        for x in bad:
            print(f"대응표 오류: {x['item'].get('id')} — refs 원문에 없음 {x['missing_quote']}" if x["missing_quote"]
                  else f"대응표 오류: 템플릿에 없는 ID {x['item'].get('id')}")
        return 1

    tpl = template()["headings"]
    got = [ln.strip() for ln in read_text(d / "measure.md").splitlines() if re.match(r"^#{2,3} ", ln)]
    toc = sum(a == b for a, b in zip(tpl, got)) / len(tpl) if len(tpl) == len(got) else 0.0
    rep = load_json(d / "check-report.json")
    missing_source = rep["counts"].get("C3", 0)

    bases = {"원래 기준": count(rows), "뺀 기준": count([x for x in rows if not x["excluded"]])}
    p = rc["pass"]
    out = {"run": d.name, "toc_match": round(toc, 3), "missing_source": missing_source, "bases": bases,
           "pass": {"toc_match": toc >= p["toc_match"], "missing_source": missing_source <= p["missing_source"],
                    **{f"coverage ({k})": (v["coverage"] or 0) >= p["coverage"] for k, v in bases.items()}},
           "differ": [x for x in rows if x["measured"] and not x["match"]], "rows": rows}
    dump_json(d / "verify-refs.json", out)

    print(f"목차 일치 {out['toc_match']} (기준 ≥ {p['toc_match']}) · 출처 없는 칸 {missing_source} (기준 ≤ {p['missing_source']})")
    print("| 기준 | 대응 항목 | 하네스가 잰 | 값 일치 | 다름 | 측정 범위 |")
    print("|---|---|---|---|---|---|")
    for k, v in bases.items():
        print(f"| {k} | {v['mapped']} | {v['measured']} | {v['match']} | {v['differ']} | {v['coverage']} (기준 ≥ {p['coverage']}) |")
    print("\n다름 (제외 여부 · ID · 조각 · refs · 하네스)")
    for x in out["differ"]:
        print(f"- {'뺌' if x['excluded'] else '셈'} · {x['id']} · {x['part'] or '전체'} · {x['refs']} · {x['ours']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
