"""S0 — run 폴더를 만든다. 같은 서비스 · 같은 날이면 -2, -3 (덮어쓰지 않는다).

사용: python scripts/new_run.py <서비스> [--date YYYY-MM-DD]
"""
import argparse
import datetime as dt
import re

from lib import RUNS, dump_yaml, rules, utf8_io, write_text

INPUT_TEMPLATE = """# 사람이 채운다 (S1 수집). 형식은 docs/pipeline.md · docs/outputs.md
service: {service}
service_aliases: []        # 서비스의 다른 이름 (C14 — value · basis에 들어가면 차단). 예: [한글 이름, 영문 이름]

screens:                   # 잴 화면. DOM이면 raw/dom-<name>.json이 있어야 한다
  - {{ name: home, method: dom }}

captures: []               # 캡처 — raw/captures/<file>. 배율은 사람이 적는다
#  - {{ name: home-modal, file: home-modal.png, scale: 1.5, screen: home }}
"""


def main() -> None:
    utf8_io()
    ap = argparse.ArgumentParser()
    ap.add_argument("service")
    ap.add_argument("--date")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9\-]*", a.service):
        raise SystemExit("서비스 이름은 영문 소문자 · 숫자 · - 만 (폴더 이름)")
    r = rules()
    date = a.date or dt.date.today().strftime(r["run"]["date_format"])
    base = f"{a.service}-{date}"
    name, n = base, 1
    while (RUNS / name).exists():
        n += 1
        name = base + r["run"]["same_day_suffix"].format(n=n)
    d = RUNS / name
    (d / "raw" / "captures").mkdir(parents=True)
    (d / "blocks").mkdir()
    dump_yaml(d / "run.yaml", {
        "run": name, "service": a.service, "date": date, "status": r["status_flow"][0],
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "retries": {"ingest": 0, "check_to_organize": 0, "block_parse": 0},
    })
    write_text(d / "input.yaml", INPUT_TEMPLATE.format(service=a.service))
    print(f"run: {name}")
    print(f"다음: 사람이 runs/{name}/input.yaml을 채우고, snippet/measure.js 결과를 raw/dom-<화면>.json으로 저장")


if __name__ == "__main__":
    main()
