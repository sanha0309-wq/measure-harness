"""S3 — rules.yaml gates.check를 센다 → check-report.json.

사용: python scripts/check.py <run>
차단 0 → 「승인 대기」 + approval.md 양식. 차단 있으면 retries.check_to_organize +1 → 「정리 중」 (종료 코드 1),
한도를 넘으면 「점검 중」에 멈춤 (종료 코드 4).
"""
import datetime as dt
import html
import json
import re
import sys

import approval
import compare
import components
import pixel
from lib import (GATE_FAIL, ID_RE, OK, REFS_LOG, STOP, atoms, locked_at, blocks, sha256, dump_json, gap_rows, kind_of, load_json, load_run,
                 load_yaml, measured_ids, parse_color, parts, read_text, rules, run_dir, save_run, service_names,
                 set_status, require_status, template, utf8_io)
from tokens import swatch_keys

def raw_index(d) -> dict:
    """요소 경로 → [(화면, 요소)]."""
    idx = {}
    for p in (d / "raw").glob("dom-*.json"):
        raw = load_json(p)
        for e in raw["elements"]:
            idx.setdefault(e["path"], []).append((raw["screen"], e))
    return idx


def el_atoms(elems) -> dict:
    colors, nums, strings = set(), set(), []
    for _, e in elems:
        for v in e["styles"].values():
            a = atoms(v)
            colors |= {c for c in a["colors"]}
            nums |= set(a["nums"])
            strings.append(str(v).lower())
        if "rect" in e:
            nums |= {round(x, 2) for x in e["rect"][2:]}
    return {"colors": colors, "nums": nums, "strings": strings}


def dom_mismatch(b, idx, r) -> list[str]:
    """C7 — 값의 색 · 수 · 낱말이 모두 그 el의 raw 스타일 값에 있어야 한다."""
    els = b["el"] if isinstance(b["el"], list) else [b["el"]]
    ps = parts(b["value"], r)
    pairs = list(zip(ps, els)) if len(els) > 1 and len(els) == len(ps) else [(str(b["value"]), None)]
    bad = []
    for part, el in pairs:
        pool = el_atoms([x for e in ([el] if el else els) for x in idx.get(e, [])])
        if b["id"] == "type.family":
            if not any(str(b["value"]).strip().lower() in s for s in pool["strings"]):
                bad.append(f"글꼴 {b['value']!r}가 raw font-family에 없음")
            continue
        a = atoms(part)
        bad += [f"색 {c} 없음" for c in a["colors"] if c not in pool["colors"]]
        bad += [f"수 {n} 없음" for n in a["nums"] if n not in pool["nums"]]
        bad += [f"낱말 {w!r} 없음" for w in a["words"] if not any(w.lower() in s for s in pool["strings"])]
    return bad


def parse_measure(d):
    rows, headings = {}, []
    for line in read_text(d / "measure.md").splitlines():
        if line.startswith("## ") or line.startswith("### "):
            headings.append(line.strip())
        m = ID_RE.search(line)
        if m and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.setdefault(m.group(1), []).append(cells)
    return headings, rows


def check(d) -> list[dict]:
    r = rules()
    hits = []

    def hit(rule, item, detail):
        hits.append({"rule": rule, "item": item, "detail": detail})

    tpl = template()
    b = blocks(d)
    vals = b["values"]
    idx = raw_index(d)
    inp = load_yaml(d / "input.yaml") or {}

    # C1 · C2 · C3 · C4 — measure.md
    headings, rows = parse_measure(d)
    if headings != tpl["headings"]:
        miss = [h for h in tpl["headings"] if h not in headings]
        hit("C1", "measure.md", f"제목 목록이 템플릿과 다름 (빠짐 {miss[:3]}, 순서 · 추가 포함)")
    for i in tpl["items"]:
        n = len(rows.get(i["id"], []))
        if n != 1:
            hit("C2", i["id"], f"measure.md에 {n}번")
    for iid, rs in rows.items():
        if iid.startswith("meta."):
            continue
        cells = rs[0]
        if len(cells) >= 3 and not re.match(r"^(못 잼|해당 없음)", cells[1]) and not cells[-1]:
            hit("C3", iid, "값은 있는데 출처 없음")
    body = [ln for ln in read_text(d / "measure.md").splitlines() if not ln.startswith(">")]  # 머리말 안내문은 빼고
    n_arb = sum(ln.count("〔임의〕") for ln in body)
    if n_arb:
        hit("C4", "measure.md", f"〔임의〕 {n_arb}개")

    # C5 · C6 · C7 · C13 · C14 · C16 · C17 — 블록
    req = r["sources"]["required"]
    names = [n.lower() for n in service_names(d)]
    color_re, length_re = re.compile(r["formats"]["color"]), re.compile(r["formats"]["length"])
    for iid, v in vals.items():
        src = v.get("src")
        for f in req.get(src, []):
            if v.get(f) in (None, ""):
                hit("C5", iid, f"src {src}에 {f} 없음")
        if src in ("dom", "pixel", "est") and v.get("value") not in (None, ""):
            kind = kind_of(iid, r)
            subs = [s.strip() for p in parts(v["value"], r) for s in p.split(r["formats"]["pair_sep"].strip())]
            if kind == "color":
                bad = [s for s in subs if not color_re.match(s)]
            elif kind == "length":
                bad = [s for s in subs if not length_re.match(s)]
            else:
                bad = []
            if bad:
                hit("C6", iid, f"{kind} 형식 아님: {bad[:3]}")
        if src == "dom" and v.get("el"):
            els = v["el"] if isinstance(v["el"], list) else [v["el"]]
            gone = [e for e in els if e not in idx]
            if gone:
                hit("C13", iid, f"raw에 없는 el {gone[:2]}")
            elif v.get("value") not in (None, ""):
                bad = dom_mismatch(v, idx, r)
                if bad:
                    hit("C7", iid, "; ".join(bad[:4]))
        for f in ("value", "basis"):
            if v.get(f) and any(n in str(v[f]).lower() for n in names):
                hit("C14", iid, f"{f}에 서비스 이름")
        lab = v.get("label")
        if lab:
            if len(str(lab)) > r["thresholds"]["label_max_chars"]:
                hit("C16", iid, f"label {len(str(lab))}자")
            els = v.get("el") if isinstance(v.get("el"), list) else [v.get("el")]
            texts = [e["text"] for el in els if el for _, e in idx.get(el, [])]
            norm = lambda s: re.sub(r"\s+", " ", str(s)).strip()
            cut = r["snippet"]["text_prefix_chars"]  # 스니펫은 글자를 이만큼만 담는다 → 담긴 길이까지만 비교
            if not texts or not any(norm(t).startswith(norm(lab)[:max(len(norm(t)), 1)] if len(norm(t)) >= cut else norm(lab))
                                    for t in texts):
                hit("C17", iid, f"label {lab!r}이 el 글자로 시작하지 않음")

    # C8 — 픽셀 값은 pixel.py만
    for iid, v in b["measurer_values"].items():
        if v.get("src") == "pixel":
            hit("C8", iid, "measurer가 픽셀 값을 직접 씀 — 좌표(pixels)만 제안해야 한다")
    if b["pixels"]:
        fresh = {x["id"]: x for x in pixel.measure_all(d)}
        for p in b["pixels"]:
            got = b["pixel_values"].get(p["id"])
            if got is None:
                hit("C8", p["id"], "좌표 제안은 있는데 pixel.py 결과 없음 — pixel.py를 돌려야 한다")
            elif got.get("value") != fresh[p["id"]].get("value"):
                hit("C8", p["id"], f"pixel.yaml {got.get('value')} ≠ 다시 잰 값 {fresh[p['id']].get('value')}")

    # C9 — gaps.md
    want = {g[0] for g in gap_rows(vals)}
    have = set(re.findall(r"^\| `([\w.\-]+)`", read_text(d / "gaps.md"), re.M))
    for x in sorted(want ^ have):
        hit("C9", x, "gaps.md에 " + ("없음" if x in want else "더 있음"))

    # C10 — tokens.html
    keys = swatch_keys(load_json(d / "tokens.json"))
    shown = re.findall(r'data-token="([^"]+)"', read_text(d / "tokens.html"))
    if len(shown) != len(keys) or set(shown) != set(keys):
        hit("C10", "tokens.html", f"견본 {len(shown)} · 토큰 {len(keys)} · 없는 키 {sorted(set(shown) - set(keys))[:3]}")

    # C19 — tokens.html 컴포넌트 견본 = measure.md §6 값
    page = html.unescape  # data-vals · style은 escape되어 있다
    mv = components.measure_values(d)
    figs = re.findall(r'<figure class="cs-wrap[^"]*" data-vals="([^"]*)">(.*?)</figure>', read_text(d / "tokens.html"), re.S)
    drawn = set()
    for vals_s, inner in figs:
        used = json.loads(page(vals_s))
        pool = {"colors": [], "nums": []}
        for iid, val in used.items():
            drawn.add(iid)
            want = mv.get(iid, ("", ""))[0]
            if val != want:
                hit("C19", iid, f"견본 값 {val!r} ≠ measure.md {want!r}")
            a = atoms(val)
            pool["colors"] += a["colors"]
            pool["nums"] += a["nums"]
        for st in re.findall(r'style="([^"]*)"', inner):
            a = atoms(page(st))
            extra = [c for c in a["colors"] if c not in pool["colors"]] + [n for n in a["nums"] if n not in pool["nums"]]
            if extra:
                hit("C19", ",".join(used) or "tokens.html", f"견본 style에 measure.md에 없는 값 {extra[:3]}")
    empties = set(re.findall(r'data-empty="([^"]+)"', read_text(d / "tokens.html")))
    for key, _, props in components.components():
        for iid, _ in props.values():
            val = mv.get(iid, ("", ""))[0]
            unmeasured = not val or components.EMPTY_RE.match(val)
            if unmeasured and iid in drawn:
                hit("C19", iid, "못 잼 · 해당 없음인데 견본에 그려짐")
            elif unmeasured and iid not in empties:
                hit("C19", iid, "못 잼 · 해당 없음인데 빈 자리 없음")
            elif not unmeasured and iid not in drawn:
                hit("C19", iid, "값이 있는데 견본에 없음")

    # C11 · C15 · W4 — compare.md
    rs = compare.rows(d)
    written = re.findall(r"^\| `([^`]+)` \|.*\| ([^|]+) \|[^|]*\|$", read_text(d / "compare.md"), re.M)
    if [t for t, _ in written] != [x["token"] for x in rs]:
        hit("C11", "compare.md", "행이 지금 값과 다름 — write_run.py --render를 다시")
    for x in rs:
        if x["judge"] not in r["judge"]["allowed"]:
            hit("C11", x["token"], f"판단 {x['judge']}")
        if x["src_kind"] == "est" and x["judge"] == "채택 후보":
            hit("C15", x["token"], "〔추정〕 행이 채택 후보")
        if x["default"]:
            hit("W4", x["token"], f"판단 블록 없음 → {r['judge']['default']}")
    for j in b["judgments"].values():
        if j.get("why") and any(n in str(j["why"]).lower() for n in names):
            hit("C14", j["token"], "why에 서비스 이름")

    # C12 — 이미지는 raw/captures/ 안에만
    exts = set(r["commit_block"]["image_ext"])
    for p in d.rglob("*"):
        if p.suffix.lower() in exts and (d / "raw" / "captures") not in p.parents:
            hit("C12", str(p.relative_to(d)), "raw/captures/ 밖 이미지")

    # C18 — refs/ 접근 (guard 훅 기록)
    # 생성 ≤ 시각 < 처음 잠긴 때(첫 「승인 대기」)면 센다. always_count 에이전트의 줄은 생성 뒤면 언제든 센다
    ra = r["refs_access"]
    log = REFS_LOG
    since, until = load_run(d).get("created_at", ""), locked_at(d)
    if log.exists():
        for line in read_text(log).splitlines():
            f = line.split("\t")
            stamp, actor = f[0], (f[3] if len(f) > 3 else ra["legacy_actor"])
            if stamp >= since and (actor in ra["always_count"] or until is None or stamp < until):
                hit("C18", "refs/", f"{actor} · " + "\t".join(f[1:3])[:80])

    # C20 — 다시 연 run: 값 파일은 reopen 전 승인 해시 그대로
    reopened = load_run(d).get("reopened") or []
    if reopened:
        before = reopened[-1].get("approved_hashes") or {}
        for n in r["reopen"]["locked"]:
            if not (d / n).exists() or sha256(d / n) != before.get(n):
                hit("C20", n, "reopen 전 승인 해시와 다름" if before.get(n) else "reopen 전 승인 해시 없음")

    # W1 — 값 칸 문구 원문 의심
    run_re = re.compile(r"[가-힣A-Za-z][가-힣A-Za-z ]{%d,}[가-힣A-Za-z]" % (r["thresholds"]["quote_run_chars"] - 1))
    for iid, rws in rows.items():
        if iid.startswith("meta.") or iid in r["formats"]["w1_exclude"]:
            continue
        for c in rws[0][1:-1] if len(rws[0]) > 2 else rws[0][1:]:
            if re.match(r"^(못 잼|해당 없음)", c):
                continue
            m = run_re.search(re.sub(r"「[^」]*」", "", c))
            if m:
                hit("W1", iid, f"「{m.group()[:24]}」")

    # W2 · W3 — 비율
    ids = measured_ids()
    na = sum(1 for i in ids if (vals.get(i) or {}).get("src") == "na")
    none = sum(1 for i in ids if i not in vals or vals[i].get("src") == "none")
    est = sum(1 for i in ids if (vals.get(i) or {}).get("src") == "est")
    base = max(len(ids) - na, 1)
    if none / base > r["thresholds"]["unmeasured_ratio"]:
        hit("W2", "measure.md", f"못 잼 {none}/{base} = {none / base:.0%}")
    if est / base > r["thresholds"]["estimated_ratio"]:
        hit("W3", "measure.md", f"추정 {est}/{base} = {est / base:.0%}")

    # W5 — 배율
    for c in inp.get("captures") or []:
        if c.get("scale") not in r["sources"]["scale_expected"]:
            hit("W5", c.get("name"), f"배율 {c.get('scale')}")
    return hits


def main() -> int:
    utf8_io()
    d = run_dir(sys.argv[1])
    require_status(d, "정리 중", "점검 중")
    set_status(d, "점검 중")
    r = rules()
    levels = {g["id"]: g["level"] for g in r["gates"]["check"]}
    hits = check(d)
    blk = [h for h in hits if levels[h["rule"]] == "block"]
    counts = {}
    for h in hits:
        counts[h["rule"]] = counts.get(h["rule"], 0) + 1
    failed_items = sorted({h["item"] for h in blk})
    dump_json(d / "check-report.json", {"run": d.name, "block": len(blk), "warn": len(hits) - len(blk),
                                        "counts": dict(sorted(counts.items())), "failed_items": failed_items, "hits": hits})
    for h in hits:
        print(f"{h['rule']} [{levels[h['rule']]}] {h['item']}: {h['detail']}")
    print(f"차단 {len(blk)} · 경고 {len(hits) - len(blk)}")
    data = load_run(d)
    if not blk:
        set_status(d, "승인 대기")
        approval.ensure(d)
        data = load_run(d)
        if not data.get("locked_at"):  # 처음 해시가 기록된 때만 — C18 구간의 끝. reopen 뒤에도 바꾸지 않는다
            data["locked_at"] = locked_at(d) or dt.datetime.now().isoformat(timespec="seconds")  # 옛 run은 첫 approval 생성 시각
            save_run(d, data)
        print(f"다음: 사람이 runs/{d.name}/approval.md 확인 · 서명 → finalize.py")
        return OK
    data["retries"]["check_to_organize"] += 1
    save_run(d, data)
    if data["retries"]["check_to_organize"] > r["retry"]["check_to_organize"]:
        print(f"점검→정리 재시도 한도 초과 ({data['retries']['check_to_organize']}/{r['retry']['check_to_organize']}) — 사람에게")
        return STOP
    set_status(d, "정리 중")
    print("다음: 실패 항목만 measurer에게 → " + ", ".join(failed_items[:20]))
    return GATE_FAIL


if __name__ == "__main__":
    sys.exit(main())
