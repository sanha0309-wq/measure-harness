"""raw만으로 화면을 재현한다 → screen.html (요소마다 absolute 상자 하나).

사용: python scripts/replay.py <run>   (상태와 상관없이 돈다 — 승인 해시 대상 파일은 건드리지 않는다)
- 요소마다 raw의 rect · rules.yaml replay.props 값 · 글자 앞부분을 그대로 옮긴다. 값을 새로 만들거나 고치지 않는다
- raw에 없는 속성은 쓰지 않는다. 글자는 자식 요소가 없는 요소에만 (부모 글자는 자식 글자와 겹친다)
- 이미지 · 아이콘(replay.placeholder_tags와 그 안쪽 요소)은 placeholder_color 자리 상자
- 쓴 뒤 C21(요소 수 · 값이 raw와 같음)을 바로 센다. 어긋나면 종료 코드 1
"""
import html
import re
import sys

from lib import GATE_FAIL, OK, load_json, rules, run_dir, utf8_io, write_text

ATTR_RE = re.compile(r'(data-[\w-]+)="([^"]*)"')
EL_RE = re.compile(r'^<div class="el"([^>]*) style="([^"]*)">(.*)</div>$')


def screens(d) -> list[dict]:
    return [load_json(p) for p in sorted((d / "raw").glob("dom-*.json"))]


def is_placeholder(e, r) -> bool:
    """그 요소나 조상이 이미지 · 아이콘 태그 — 경로 조각의 태그로 본다."""
    tags = set(r["replay"]["placeholder_tags"])
    return e["tag"].lower() in tags or any(seg.split(":")[0].lower() in tags for seg in e["path"].split(">"))


def leaves(elems) -> set[str]:
    paths = [e["path"] for e in elems]
    parents = {p for p in paths for q in paths if q.startswith(p + ">")}
    return set(paths) - parents


def expected(e, r, leaf: set[str]) -> dict:
    """요소 하나가 screen.html에 가져야 할 것 — 그리기와 C21이 같이 쓴다."""
    x, y, w, h = e["rect"]
    style = {"left": f"{x}px", "top": f"{y}px", "width": f"{w}px", "height": f"{h}px"}
    ph = is_placeholder(e, r)
    if ph:
        style["background-color"] = r["replay"]["placeholder_color"]
    else:
        style |= {k: e["styles"][k] for k in r["replay"]["props"] if k in e["styles"]}
    text = "" if ph or e["path"] not in leaf else (e.get("text") or "")
    return {"path": e["path"], "tag": e["tag"], "placeholder": ph, "style": style, "text": text}


def render(d) -> str:
    r = rules()
    out = ["<!doctype html>", '<html lang="ko"><head><meta charset="utf-8">', f"<title>{html.escape(d.name)} · 화면 재현</title>",
           "<style>body{margin:0}.screen{position:relative;overflow:hidden}"
           ".el{position:absolute;box-sizing:border-box;margin:0;white-space:nowrap;overflow:hidden}</style>",
           "</head><body>"]
    for raw in screens(d):
        vp = raw["viewport"]
        leaf = leaves(raw["elements"])
        out.append(f'<section class="screen" data-screen="{html.escape(raw["screen"])}" '
                   f'style="width:{vp["width"]}px;height:{vp["height"]}px">')
        for e in raw["elements"]:
            x = expected(e, r, leaf)
            style = ";".join(f"{k}:{v}" for k, v in x["style"].items())
            ph = ' data-placeholder="1"' if x["placeholder"] else ""
            out.append(f'<div class="el" data-path="{html.escape(x["path"])}" data-tag="{html.escape(x["tag"])}"{ph} '
                       f'style="{html.escape(style)}">{html.escape(x["text"])}</div>')
        out.append("</section>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


def parse(text: str) -> list[dict]:
    got = []
    for line in text.splitlines():
        m = EL_RE.match(line)
        if not m:
            continue
        attrs = {k: html.unescape(v) for k, v in ATTR_RE.findall(m.group(1))}
        style = {}
        for part in html.unescape(m.group(2)).split(";"):
            if ":" in part:
                k, v = part.split(":", 1)
                style[k.strip()] = v.strip()
        got.append({"path": attrs.get("data-path"), "tag": attrs.get("data-tag"), "placeholder": "data-placeholder" in attrs,
                    "style": style, "text": html.unescape(m.group(3))})
    return got


def verify(d) -> list[tuple[str, str]]:
    """C21 — screen.html 요소 수 · 순서 · 위치 · 값 · 글자가 raw와 같다."""
    p = d / "screen.html"
    if not p.exists():
        return [("screen.html", "없음 — replay.py를 다시")]
    r = rules()
    want = []
    for raw in screens(d):
        leaf = leaves(raw["elements"])
        want += [expected(e, r, leaf) for e in raw["elements"]]
    got = parse(p.read_text(encoding="utf-8"))
    bad = []
    if len(got) != len(want):
        bad.append(("screen.html", f"요소 {len(got)}개 ≠ raw {len(want)}개"))
    for i, (g, w) in enumerate(zip(got, want)):
        if g != w:
            keys = [k for k in w if g.get(k) != w[k]]
            if "style" in keys:
                keys += [f"{k}" for k in sorted(set(g["style"]) | set(w["style"])) if g["style"].get(k) != w["style"].get(k)]
            bad.append((w["path"], f"{i}번째 요소 다름: {', '.join(keys)}"))
    return bad


def main() -> int:
    utf8_io()
    d = run_dir(sys.argv[1])
    write_text(d / "screen.html", render(d))
    bad = verify(d)
    n = sum(len(s["elements"]) for s in screens(d))
    for item, detail in bad:
        print(f"C21 [block] {item}: {detail}")
    print(f"찍음: screen.html · 요소 {n} · C21 차단 {len(bad)}")
    return GATE_FAIL if bad else OK


if __name__ == "__main__":
    sys.exit(main())
