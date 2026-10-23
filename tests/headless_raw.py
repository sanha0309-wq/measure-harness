"""시험 전용 — 헤드리스 Chrome에서 페이지에 snippet/measure.js를 돌려 raw JSON을 받는다.

운영 경로는 사람이 콘솔에 붙여 넣는 방식이다 (docs/pipeline.md). 이 도구는 tests/에서만 쓴다.
사용: python tests/headless_raw.py <html 파일> <화면 이름> <저장 경로>
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from lib import read_text, rules, utf8_io, write_text  # noqa: E402

CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]


def capture(page: Path, screen: str) -> str:
    snippet = read_text(ROOT / "snippet" / "measure.js")
    hook = ("<script>window.copy=function(s){var p=document.createElement('pre');p.id='__raw';"
            "p.style.display='none';p.textContent=s;document.documentElement.appendChild(p);};</script>")
    run = f"<script>{snippet}\nwindow.addEventListener('load',function(){{measure({screen!r});}});</script>"
    src = read_text(page).replace("</body>", hook + run + "</body>")
    w = rules()["run"]["viewport_width"]
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / page.name  # 같은 이름 — url만 다르다
        write_text(f, src)
        chrome = next(c for c in CHROMES if os.path.exists(c))
        ww, wh = w, 900
        for _ in range(3):  # 헤드리스 창 크기와 innerWidth가 다르다 → 차이만큼 보정
            out = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                                  f"--window-size={ww},{wh}", "--virtual-time-budget=3000", "--dump-dom", f.as_uri()],
                                 capture_output=True, text=True, encoding="utf-8", timeout=60).stdout
            m = re.search(r'<pre id="__raw"[^>]*>(.*?)</pre>', out, re.S)
            if not m:
                raise SystemExit("raw를 받지 못함:\n" + out[-500:])
            raw = html.unescape(m.group(1))
            vp = json.loads(raw)["viewport"]
            if vp["width"] == w:
                return raw
            ww, wh = ww + w - vp["width"], wh + 900 - vp["height"]
    raise SystemExit(f"innerWidth를 {w}으로 맞추지 못함 (마지막 {vp})")


if __name__ == "__main__":
    utf8_io()
    page, screen, dest = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    write_text(dest, capture(page, screen))
    print(f"저장: {dest}")
