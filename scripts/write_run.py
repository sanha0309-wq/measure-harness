"""S2 — 에이전트 블록을 받아 저장하고, 산출물을 찍는다. 파일을 쓰는 것은 이 스크립트다.

사용:
  python scripts/write_run.py <run> --from measurer   < 블록   (값 · 좌표 · 규칙. 실패 항목만 와도 ID로 덮어 합침)
  python scripts/write_run.py <run> --render                  (measure.md · tokens.json · gaps.md · tokens.html · compare.md · screen.html · corrections.md)
  python scripts/write_run.py <run> --from judge      < 블록   (판단 → compare.md 다시 찍기)
블록을 읽지 못하면 종료 코드 3 (retry.block_parse), 한도를 넘으면 4.
"""
import argparse
import datetime as dt
import sys

import yaml

from lib import (BLOCK_PARSE, ID_RE, OK, STOP, TEMPLATE, blocks, dump_json, dump_yaml, extract_yaml_block, gap_rows, load_json,
                 load_run, load_yaml, parts, read_text, report, rules, run_dir, save_run, src_label, template,
                 require_status, utf8_io, write_text)
import build_html
import compare
import diff_prev
import replay
import tokens as tokens_mod


# ---------- 블록 받기 ----------

def validate_measurer(data, r) -> list[str]:
    errs = []
    if not isinstance(data, dict):
        return ["최상위는 values · pixels · rules 키를 가진 사전이어야 한다"]
    extra = set(data) - {"values", "pixels", "rules"}
    if extra:
        errs.append(f"모르는 키 {sorted(extra)}")
    ids = {i["id"] for i in template()["items"]}
    allowed = set(r["sources"]["allowed"])
    for v in data.get("values") or []:
        if not isinstance(v, dict) or "id" not in v:
            errs.append(f"값 블록에 id 없음: {v}")
            continue
        if v["id"] not in ids or v["id"].startswith("meta."):
            errs.append(f"{v['id']}: 템플릿에 없는 항목 ID")
        if v.get("src") not in allowed:
            errs.append(f"{v['id']}: 허용 안 된 src {v.get('src')!r} (허용 {sorted(allowed)})")
    for p in data.get("pixels") or []:
        if not isinstance(p, dict) or not {"id", "capture", "box", "measure"} <= set(p):
            errs.append(f"좌표 블록에 id · capture · box · measure 필요: {p}")
        elif p["measure"] not in ("color", "width", "height") or len(p["box"]) != 4:
            errs.append(f"{p['id']}: measure는 color · width · height, box는 [x1, y1, x2, y2]")
    for rl in data.get("rules") or []:
        if not isinstance(rl, dict) or "rule" not in rl or not isinstance(rl.get("refs"), list):
            errs.append(f"규칙 블록에 rule · refs 필요: {rl}")
    return errs


def validate_judge(data, r) -> list[str]:
    if not isinstance(data, dict) or set(data) != {"judgments"}:
        return ["최상위는 judgments 키 하나"]
    errs = []
    for j in data["judgments"] or []:
        if not isinstance(j, dict) or "token" not in j:
            errs.append(f"판단 블록에 token 없음: {j}")
        elif j.get("judge") not in r["judge"]["allowed"]:
            errs.append(f"{j['token']}: judge는 {r['judge']['allowed']} 중 하나")
    return errs


def receive(d, who: str) -> int:
    r = rules()
    text = sys.stdin.read()
    run = load_run(d)
    try:
        data = yaml.safe_load(extract_yaml_block(text))
        errs = (validate_measurer if who == "measurer" else validate_judge)(data, r)
    except (yaml.YAMLError, ValueError) as e:
        errs = [f"YAML을 읽을 수 없음: {e}"]
    hist = d / "blocks" / "history"
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    write_text(hist / f"{who}-{stamp}.txt", text)
    if errs:
        run["retries"]["block_parse"] += 1
        save_run(d, run)
        for e in errs:
            print(f"블록 오류: {e}")
        if run["retries"]["block_parse"] > r["retry"]["block_parse"]:
            print(f"블록 재요청 한도 초과 ({run['retries']['block_parse']}/{r['retry']['block_parse']})")
            return STOP
        print("같은 에이전트에게 위 오류와 함께 다시 요청")
        return BLOCK_PARSE
    run["retries"]["block_parse"] = 0
    save_run(d, run)

    path = d / "blocks" / f"{who}.yaml"
    old = load_yaml(path) or {}
    if who == "measurer":
        merged = {
            "values": {v["id"]: v for v in old.get("values") or []},
            "pixels": {p["id"]: p for p in old.get("pixels") or []},
        }
        for v in data.get("values") or []:
            merged["values"][v["id"]] = v
            merged["pixels"].pop(v["id"], None)  # 값으로 다시 왔으면 좌표 제안은 버린다
        for p in data.get("pixels") or []:
            merged["pixels"][p["id"]] = p
            merged["values"].pop(p["id"], None)
        out = {"values": list(merged["values"].values()), "pixels": list(merged["pixels"].values()),
               "rules": data["rules"] if "rules" in data else old.get("rules") or []}
        print(f"저장: 값 {len(data.get('values') or [])} · 좌표 {len(data.get('pixels') or [])} · 규칙 {len(data.get('rules') or [])}")
    else:
        merged = {j["token"]: j for j in old.get("judgments") or []}
        for j in data["judgments"] or []:
            merged[j["token"]] = j
        out = {"judgments": list(merged.values())}
        print(f"저장: 판단 {len(data['judgments'] or [])}")
    dump_yaml(path, out)
    if who == "judge":
        render_compare(d)
    return OK


# ---------- 찍기 ----------

def value_cell(b, item, r):
    if b is None:
        return "못 잼 (블록 없음)"
    if b.get("src") == "none":
        return f"못 잼 ({b.get('reason', '')})"
    if b.get("src") == "na":
        return f"해당 없음 ({b.get('reason', '')})"
    v = str(b.get("value", ""))
    return v + (f" — 「{b['label']}」" if b.get("label") else "")


def row_cells(b, item, r) -> list[str]:
    cell = value_cell(b, item, r)
    src = src_label(b) if b else ""
    if item["ncols"] == 2:
        return [cell]
    if item["ncols"] == 4:  # 글자: 크기/행간/굵기 | 자간 | 출처
        if b and b.get("src") in ("dom", "pixel", "est") and not item["id"].endswith("family"):
            ps = parts(b["value"], r)
            label = f" — 「{b['label']}」" if b.get("label") else ""
            main = " / ".join(ps[:3]) + label
            return [main, ps[3] if len(ps) > 3 else "못 잼 (자간 없음)", src]
        return [cell, "—", src]
    return [cell, src]


def meta_cells(d) -> dict:
    inp = load_yaml(d / "input.yaml") or {}
    screens = inp.get("screens") or []
    caps = inp.get("captures") or []
    methods = {s.get("method", "dom") for s in screens} | ({"capture"} if caps else set())
    method = "둘 다" if methods >= {"dom", "capture"} else ("캡처" if methods == {"capture"} else "DOM")
    widths = set()
    for p in (d / "raw").glob("dom-*.json"):
        widths.add(load_json(p)["viewport"]["width"])
    scales = ", ".join(f"{c['name']} {c['scale']}" for c in caps) or "해당 없음 (캡처 없음)"
    names = [s["name"] for s in screens] + [c["name"] for c in caps]
    return {"meta.method": method, "meta.viewport": ", ".join(map(str, sorted(widths))) or rules()["run"]["viewport_width"],
            "meta.scale": scales, "meta.screens": ", ".join(names)}


def render_measure(d) -> None:
    r = rules()
    run = load_run(d)
    b = blocks(d)
    vals = b["values"]
    meta = meta_cells(d)
    tpl = template()
    by_id = {i["id"]: i for i in tpl["items"]}
    out = []
    for line in read_text(TEMPLATE).splitlines():
        if line.startswith("# "):
            out.append(f"# {run['service']} 실측 — {run['date']}")
            continue
        m = ID_RE.search(line)
        if m and line.startswith("|"):
            iid = m.group(1)
            item = by_id[iid]
            head = line.split("|")[1].strip()
            cells = [str(meta[iid])] if iid.startswith("meta.") else row_cells(vals.get(iid), item, r)
            out.append("| " + " | ".join([head] + cells) + " |")
            continue
        out.append(line)
        if line.startswith("## 7."):
            out.append("")
            for rl in b["rules"]:
                out.append(f"- {rl['rule']} (근거: {', '.join(rl['refs'])})")
            if not b["rules"]:
                out.append("- 못 잼 (규칙 블록 없음)")
        if line.startswith("## 8."):
            out.append("")
            rows = gap_rows(vals)
            out += [f"- `{g[0]}` {g[1]} — {g[2]} ({g[3]})" for g in rows] or ["- 없음"]
    write_text(d / "measure.md", "\n".join(out) + "\n")


def render_gaps(d) -> None:
    rows = gap_rows(blocks(d)["values"])
    md = [f"# {load_run(d)['run']} — 아직 못 잰 것 · 추정값", "",
          f"못 잼 {sum(1 for x in rows if x[2] == '못 잼')} · 추정 {sum(1 for x in rows if x[2] == '추정')}", "",
          report([(f"`{g[0]}` {g[1]}", g[2], g[3], g[4]) for g in rows], ("항목", "상태 (못 잼 / 추정)", "이유 · 근거", "다음에 재는 방법"))]
    write_text(d / "gaps.md", "\n".join(md) + "\n")


def render_compare(d) -> None:
    write_text(d / "compare.md", compare.render(d))


def render_all(d) -> int:
    require_status(d, "정리 중", "점검 중")
    render_measure(d)
    dump_json(d / "tokens.json", tokens_mod.build(d))
    render_gaps(d)
    write_text(d / "tokens.html", build_html.render(d))
    render_compare(d)
    write_text(d / "screen.html", replay.render(d))
    cor = diff_prev.render(d)
    if cor:
        write_text(d / "corrections.md", cor)
    elif (d / "corrections.md").exists():
        (d / "corrections.md").unlink()
    print("찍음: measure.md · tokens.json · gaps.md · tokens.html · compare.md · screen.html" + (" · corrections.md" if cor else ""))
    return OK


def main() -> int:
    utf8_io()
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--from", dest="who", choices=["measurer", "judge"])
    g.add_argument("--render", action="store_true")
    a = ap.parse_args()
    d = run_dir(a.run)
    if a.render:
        return render_all(d)
    require_status(d, "정리 중", "점검 중")
    return receive(d, a.who)


if __name__ == "__main__":
    sys.exit(main())
