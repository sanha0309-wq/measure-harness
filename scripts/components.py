"""measure.md §6 → tokens.html 컴포넌트 구역. measure.md 값 칸만 쓴다 (C19).

- 컴포넌트마다 크기 단계별 기본 견본 1개씩 + 올림 · 누름 · 비활성 견본 1개씩
- 못 잼 · 해당 없음 칸은 그리지 않고 빈 자리(data-empty)로 둔다
- 견본 묶음(figure.cs-wrap)마다 data-vals = 쓴 항목 ID → measure.md 값 칸(label 「」 뺌).
  인라인 style에는 그 값에서 나온 수 · 색만 들어간다. 꾸밈(배치 · 견본 글자 · 선 견본 크기)은 페이지 CSS에만 둔다
"""
import html
import json
import re

from lib import ID_RE, atoms, parts, read_text, rules, template

EMPTY_RE = re.compile(r"^(못 잼|해당 없음)")
LABEL_RE = re.compile(r"\s+—\s+「[^」]*」$")
PROPS = ["height", "width", "padding", "text", "radius", "color_default", "color_hover", "color_pressed", "color_disabled"]
STATES = [("color_hover", "올림"), ("color_pressed", "누름"), ("color_disabled", "비활성")]
SAMPLE = {"button": "버튼", "input": "입력 글자", "tab": "탭", "badge": "배지", "modal": "모달 제목", "empty": "비어 있음"}

CSS = """
.comp{border:1px solid var(--line);border-radius:8px;padding:16px;margin-bottom:12px;background:var(--card)}
.comp h3{font-size:14px;margin:0 0 12px}.row{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}
.cs-wrap{margin:0;display:flex;flex-direction:column;gap:6px;max-width:100%;overflow-x:auto}
.cs-wrap.est .cs{outline:2px dashed var(--est);outline-offset:2px}
.cs-wrap figcaption{color:var(--muted);font-size:12px}
.cs{display:inline-flex;align-items:center;box-sizing:border-box;white-space:nowrap}
.cs.block{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;white-space:normal}
.cs table{border-collapse:collapse}
.line{display:inline-block;width:24px;height:4px;vertical-align:middle;margin-left:6px;border-radius:2px}
.slots{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.slot{border:1px dashed var(--line);border-radius:6px;padding:6px 10px;color:var(--muted);font-size:12px}
"""


def clean(cell: str) -> str:
    return LABEL_RE.sub("", cell.strip())


def measure_values(d) -> dict:
    """measure.md → 항목 ID → (값 칸, 출처 칸). 값 칸은 label 「」을 뺀 글자."""
    out = {}
    for line in read_text(d / "measure.md").splitlines():
        m = ID_RE.search(line)
        if m and line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out[m.group(1)] = (clean(cells[1]) if len(cells) > 1 else "", cells[-1] if len(cells) > 2 else "")
    return out


def components() -> list[tuple[str, str, dict]]:
    """템플릿 §6 → [(키, 이름, {속성: (항목 ID, 칸 이름)})] 순서 그대로."""
    out = {}
    for it in template()["items"]:
        if not it["id"].startswith("comp."):
            continue
        _, key, prop = it["id"].split(".", 2)
        name = re.sub(r"^###\s*6-\d+\.\s*", "", it["section"] or "")
        out.setdefault(key, (name, {}))[1][prop] = (it["id"], it["label"])
    return [(k, n, p) for k, (n, p) in out.items()]


def pick(value: str, i: int, r: dict) -> str:
    ps = parts(value, r)
    return ps[min(i, len(ps) - 1)] if ps else ""


def px_pair(value: str, r: dict) -> str:
    return " ".join(f"{s.strip()}px" for s in value.split(r["formats"]["pair_sep"].strip()))


def box_style(key: str, v: dict, i: int, color: str | None, r: dict) -> list[str]:
    """견본 상자의 인라인 style 조각. v = 속성 → 값 칸 (잰 칸만)."""
    st = []
    if "height" in v and key != "table":
        st.append(f"height:{pick(v['height'], i, r)}px")
    if "width" in v:
        st.append(f"width:{pick(v['width'], 0, r)}px")
    if "padding" in v and key != "table":
        st.append(f"padding:{px_pair(pick(v['padding'], i, r), r)}")
    if "text" in v:
        n = atoms(v["text"])["nums"]
        st += [f"{p}:{x:g}{u}" for p, x, u in zip(("font-size", "line-height", "font-weight"), n, ("px", "px", ""))]
    if "radius" in v:
        st.append(f"border-radius:{pick(v['radius'], 0, r)}px")
    if color:
        cs = parts(color, r)
        if len(cs) > 0:
            st.append(f"color:{cs[0]}")
        if len(cs) > 1:
            st.append(f"background:{cs[1]}")
    return st


def body(key: str, v: dict, color: str | None, r: dict) -> str:
    """견본 안쪽. 표는 머리글 1줄 + 행 2줄 (높이 = 높이 칸 첫 조각 · 둘째 조각)."""
    if key != "table":
        return html.escape(SAMPLE.get(key, key))
    cell = f' style="padding:{px_pair(pick(v["padding"], 0, r), r)}"' if "padding" in v else ""
    rows = []
    for n, tag in ((0, "th"), (1, "td"), (1, "td")):
        h = f' style="height:{pick(v["height"], n, r)}px"' if "height" in v else ""
        rows.append(f"<tr{h}>" + "".join(f"<{tag}{cell}>가나다</{tag}>" for _ in range(3)) + "</tr>")
    return "<table>" + "".join(rows) + "</table>"


def line_chip(color: str | None, r: dict) -> str:
    cs = parts(color, r) if color else []
    return f'<span class="line" title="선" style="background:{html.escape(cs[2])}"></span>' if len(cs) > 2 else ""


def figure(key: str, used: dict, v: dict, i: int, color: str | None, caption: str, est: bool, r: dict) -> str:
    st = ";".join(box_style(key, v, i, color, r))
    cls = "cs block" if key in ("modal", "empty", "table") else "cs"
    vals = html.escape(json.dumps(used, ensure_ascii=False), quote=True)
    return (f'<figure class="cs-wrap{" est" if est else ""}" data-vals="{vals}">'
            f'<div class="{cls}" style="{html.escape(st, quote=True)}">{body(key, v, color, r)}</div>'
            f'<figcaption>{html.escape(caption)}{line_chip(color, r)}</figcaption></figure>')


def render(d) -> tuple[str, int, int]:
    """→ (HTML, 견본 수, 빈 자리 수)."""
    r = rules()
    mv = measure_values(d)
    out, n_fig, n_empty = [], 0, 0
    for key, name, props in components():
        got, empty, est = {}, [], False
        for prop, (iid, label) in props.items():
            val, src = mv.get(iid, ("", ""))
            if not val or EMPTY_RE.match(val):
                empty.append((iid, label, (EMPTY_RE.match(val).group(1) if val else "못 잼")))
            else:
                got[prop] = (iid, val)
                est = est or "〔추정" in src
        base = {p: got[p][1] for p in PROPS[:5] if p in got}
        figs = []
        if "color_default" in got or base:
            sizes = max([len(parts(base[p], r)) for p in ("height", "padding") if p in base] or [1])
            color = got.get("color_default", (None, None))[1]
            used = {got[p][0]: got[p][1] for p in PROPS[:5] + ["color_default"] if p in got}
            for i in range(sizes):
                figs.append(figure(key, used, base, i, color, f"기본{f' · 단계 {i + 1}' if sizes > 1 else ''}", est, r))
            for prop, cap in STATES:
                if prop in got:
                    used_s = {**{got[p][0]: got[p][1] for p in PROPS[:5] if p in got}, got[prop][0]: got[prop][1]}
                    figs.append(figure(key, used_s, base, 0, got[prop][1], cap, est, r))
        slots = "".join(f'<div class="slot" data-empty="{html.escape(iid)}">{html.escape(label)} · {why}</div>'
                        for iid, label, why in empty)
        n_fig += len(figs)
        n_empty += len(empty)
        out.append(f'<section class="comp" data-comp="{key}"><h3>{html.escape(name)}</h3>'
                   f'<div class="row">{"".join(figs) or "<p class=meta>그릴 값 없음</p>"}</div>'
                   f'{f"<div class=slots>{slots}</div>" if slots else ""}</section>')
    return "".join(out), n_fig, n_empty
