"""S1 자동 수집 — 설치된 Chrome(Playwright)으로 페이지를 열고 snippet/measure.js를 돌려 raw를 저장한 뒤 ingest.py까지 돌린다.

사용: python scripts/collect.py <run> <화면 이름> <URL 또는 파일 경로> [--headed]
- 창 크기는 rules.yaml의 run.viewport_width × 900. 브라우저는 새로 내려받지 않는다 (channel="chrome")
- 저장: runs/<run>/raw/dom-<화면>.json. 화면은 input.yaml screens에 있어야 한다 (없으면 ingest가 I4로 막는다)
- 로그인이 필요한 화면은 콘솔에 붙여 넣는 방식으로 잰다 (README)
- 종료 코드는 ingest.py와 같다
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from lib import ROOT, USAGE, read_text, require_status, rules, run_dir, utf8_io, write_text

HEIGHT = 900


def page_url(target: str) -> str:
    if re.match(r"^[a-z][a-z0-9+.\-]*://", target, re.I):
        return target
    p = Path(target)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.exists():
        raise SystemExit(f"URL도 파일도 아님: {target}")
    return p.resolve().as_uri()


def collect(url: str, screen: str, headed: bool = False) -> str:
    from playwright.sync_api import sync_playwright

    snippet = read_text(ROOT / "snippet" / "measure.js")
    w = rules()["run"]["viewport_width"]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=not headed)
        try:
            page = browser.new_page(viewport={"width": w, "height": HEIGHT})
            page.goto(url, wait_until="load")
            page.evaluate(snippet)
            return page.evaluate("s => measure(s, { returnJson: true })", screen)
        finally:
            browser.close()


def main() -> int:
    utf8_io()
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("screen")
    ap.add_argument("url")
    ap.add_argument("--headed", action="store_true", help="창을 띄워서 연다")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9\-]*", a.screen):
        print("화면 이름은 영문 소문자 · 숫자 · - 만 (파일 이름)")
        return USAGE
    d = run_dir(a.run)
    require_status(d, "수집 중")
    dest = d / "raw" / f"dom-{a.screen}.json"
    write_text(dest, collect(page_url(a.url), a.screen, a.headed))
    print(f"저장: runs/{a.run}/raw/dom-{a.screen}.json")
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "ingest.py"), a.run]).returncode


if __name__ == "__main__":
    sys.exit(main())
