"""tokens.json · measure.md → tokens.html.

- 토큰 구역: tokens.json에 있는 값만 쓴다. 견본 하나 = data-token 하나 (C10)
- 컴포넌트 구역: measure.md §6 값 칸만으로 그린다 (scripts/components.py, C19)

사용: python scripts/build_html.py <run>   (보통은 write_run.py --render가 부른다)
"""
import html
import sys

import components
from lib import load_json, load_run, run_dir, src_label, utf8_io, write_text
from tokens import leaves

GROUPS = [("색", ["color"]), ("글자", ["font", "type"]), ("간격", ["space"]), ("반경", ["radius"]),
          ("그림자", ["shadow"]), ("크기", ["layout", "component"])]

CSS = """
:root{--fg:#1d1f23;--muted:#666b73;--line:#d9dce1;--bg:#fff;--card:#f6f7f9;--est:#c2410c}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--fg:#e8eaed;--muted:#a0a5ad;--line:#3a3d42;--bg:#16181b;--card:#1f2226;--est:#fb923c}}
:root[data-theme="dark"]{--fg:#e8eaed;--muted:#a0a5ad;--line:#3a3d42;--bg:#16181b;--card:#1f2226;--est:#fb923c}
*{box-sizing:border-box}body{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto}h1{font-size:20px;margin:0 0 4px}h2{font-size:16px;margin:32px 0 12px}
.meta{color:var(--muted);margin:0}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.sw{border:1px solid var(--line);border-radius:8px;padding:12px;background:var(--card);overflow-wrap:anywhere}
.sw.est{border:2px dashed var(--est)}.tag{display:inline-block;font-size:11px;font-weight:700;color:var(--est);margin-left:6px}
.key{font-weight:600}.val{font-family:ui-monospace,monospace;font-size:12px}.src{color:var(--muted);font-size:12px}
.chip{height:48px;border-radius:6px;border:1px solid var(--line);margin-bottom:8px}
.bar{height:12px;background:var(--fg);border-radius:2px;margin-bottom:8px;max-width:100%}
.box{width:56px;height:56px;background:var(--bg);border:1px solid var(--line);margin-bottom:8px}
"""


def preview(group: str, key: str, v) -> str:
    e = html.escape(str(v), quote=True)
    if group == "색":
        return f'<div class="chip" style="background:{e}"></div>'
    if group == "글자" and isinstance(v, dict):
        size, lh, w = v.get("size"), v.get("lineHeight"), v.get("weight")
        return f'<div style="font-size:{size}px;line-height:{lh}px;font-weight:{w}">가나다 Aa 123</div>'
    if group == "글자":
        return f'<div style="font-family:{e}">가나다 Aa 123</div>'
    if group in ("간격", "크기") and isinstance(v, (int, float)):
        return f'<div class="bar" style="width:{v}px"></div>'
    if group == "반경" and isinstance(v, (int, float)):
        return f'<div class="box" style="border-radius:{min(v, 28)}px"></div>'
    if group == "그림자":
        return f'<div class="box" style="box-shadow:{e};border:0"></div>'
    return ""


def swatch(group: str, key: str, t: dict, v) -> str:
    est = t["src"] == "est"
    shown = ", ".join(f"{k} {x}" for k, x in v.items()) if isinstance(v, dict) else v
    return (f'<div class="sw{" est" if est else ""}" data-token="{html.escape(key)}">'
            f"{preview(group, key, v)}"
            f'<div class="key">{html.escape(key)}{"<span class=tag>추정</span>" if est else ""}</div>'
            f'<div class="val">{html.escape(str(shown))}</div>'
            f'<div class="src">{html.escape(src_label(t))}</div></div>')


def render(d) -> str:
    run = load_run(d)
    tree = load_json(d / "tokens.json")
    body = []
    total = 0
    for title, tops in GROUPS:
        cards = []
        for top in tops:
            for key, t in leaves({top: tree.get(top, {})}):
                if isinstance(t["value"], list):
                    cards += [swatch(title, f"{key}[{i}]", t, x) for i, x in enumerate(t["value"])]
                else:
                    cards.append(swatch(title, key, t, t["value"]))
        total += len(cards)
        body.append(f"<h2>{title} · {len(cards)}</h2><div class=grid>{''.join(cards) or '<p class=meta>토큰 없음</p>'}</div>")
    comp_html, n_fig, n_empty = components.render(d)
    body.append(f"<h2>컴포넌트 · 견본 {n_fig} · 빈 자리 {n_empty}</h2>{comp_html}")
    return ("<!doctype html><html lang=ko><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(run['service'])} 디자인 시스템</title><style>{CSS}{components.CSS}</style></head><body><main>"
            f"<h1>{html.escape(run['run'])} 디자인 시스템</h1>"
            f"<p class=meta>스크립트로 생성 — 토큰은 tokens.json, 컴포넌트는 measure.md §6 · 토큰 견본 {total}개 · 점선 = 〔추정〕 · 빈 자리 = 못 잼 · 해당 없음</p>"
            + "".join(body) + "</main></body></html>\n")


def main() -> None:
    utf8_io()
    d = run_dir(sys.argv[1])
    write_text(d / "tokens.html", render(d))


if __name__ == "__main__":
    main()
