"""하네스 스크립트 공통 — 경로 · rules.yaml · 템플릿 · run 상태 · 값 파싱.

수치와 규칙은 rules.yaml에서만 읽는다. 이 파일에 새 수치를 두지 않는다.
"""
from __future__ import annotations

import datetime as dt
import fnmatch
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
RUNS = Path(os.environ.get("HARNESS_RUNS") or ROOT / "runs")  # 시험은 임시 폴더로 바꾼다
REFS_LOG = Path(os.environ.get("HARNESS_REFS_LOG") or ROOT / ".claude" / "refs-access.log")  # guard 훅이 쓰는 곳
TEMPLATE = DOCS / "measure-template.md"

# 종료 코드 — 메인 세션은 이 숫자로 다음 할 일을 정한다 (CLAUDE.md §2)
OK, GATE_FAIL, USAGE, BLOCK_PARSE, STOP = 0, 1, 2, 3, 4


def utf8_io() -> None:
    # Windows 기본 cp949면 stdin 블록 · 출력의 한글이 깨진다 — PYTHONUTF8 없이도 UTF-8로 고정
    for s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except AttributeError:
            pass


def read_text(p: Path) -> str:
    return io.open(p, encoding="utf-8").read()


def write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def load_yaml(p: Path):
    return yaml.safe_load(read_text(p)) if p.exists() else None


def dump_yaml(p: Path, data) -> None:
    write_text(p, yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200))


def load_json(p: Path):
    # utf-8-sig — Windows 메모장 · PowerShell로 저장한 raw는 BOM이 붙는다. BOM 없는 파일은 utf-8과 같게 읽힌다
    return json.loads(io.open(p, encoding="utf-8-sig").read())


def dump_json(p: Path, data) -> None:
    write_text(p, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rules() -> dict:
    return load_yaml(ROOT / "rules.yaml")


# ---------- 템플릿 ----------

ID_RE = re.compile(r"<!--\s*id:\s*([\w.\-]+)\s*-->")


def template() -> dict:
    """measure-template.md → 제목 목록 · 항목 목록 (순서 그대로)."""
    headings, items = [], []
    section = None
    for line in read_text(TEMPLATE).splitlines():
        if line.startswith("## ") or line.startswith("### "):
            headings.append(line.strip())
            section = line.strip()
            continue
        m = ID_RE.search(line)
        if m and line.startswith("|"):
            label = ID_RE.sub("", line.split("|")[1]).strip()
            ncols = line.count("|") - 1
            items.append({"id": m.group(1), "label": label, "section": section, "ncols": ncols})
    return {"headings": headings, "items": items}


def measured_ids() -> list[str]:
    return [i["id"] for i in template()["items"] if not i["id"].startswith("meta.")]


def kind_of(item_id: str, r: dict) -> str:
    for k in r["kinds"]:
        if fnmatch.fnmatchcase(item_id, k["match"]):
            return k["kind"]
    return "free"


# ---------- run ----------

def run_dir(run: str) -> Path:
    d = RUNS / run
    if not (d / "run.yaml").exists():
        raise SystemExit(f"run 없음: {d}")
    return d


def load_run(d: Path) -> dict:
    return load_yaml(d / "run.yaml")


def locked_at(d: Path) -> str | None:
    """값이 처음 해시로 잠긴 시각 = 처음 「승인 대기」에 들어가 approval.md에 해시를 기록한 때. check.py가 run.yaml locked_at에 남긴다.
    그 칸이 생기기 전 run은 첫 approval 파일(reopen이 옆에 옮겨 둔 것, 없으면 approval.md)의 생성 시각,
    approval 파일이 없으면 check-report.json 수정 시각으로 대신한다."""
    data = load_run(d)

    def iso(ts):
        return dt.datetime.fromtimestamp(ts).isoformat(timespec="seconds")

    # approval 파일은 처음 잠길 때 만들어진다 → 생성 시각이 잠금의 증거. 적힌 값과 둘 중 이른 쪽
    kept = [d / r["approval_kept"] for r in data.get("reopened") or [] if r.get("approval_kept")]
    seen = [data["locked_at"]] if data.get("locked_at") else []
    for p in kept + [d / "approval.md"]:
        if p.exists():
            st = p.stat()
            seen.append(iso(getattr(st, "st_birthtime", None) or st.st_ctime))  # Windows의 st_ctime = 생성 시각
            break
    if seen:
        return min(seen)
    rep = d / "check-report.json"  # 다시 연 옛 run만 — 새 run의 점검 실패 보고서는 잠금이 아니다
    return iso(rep.stat().st_mtime) if data.get("reopened") and rep.exists() else None


def save_run(d: Path, data: dict) -> None:
    dump_yaml(d / "run.yaml", data)


def set_status(d: Path, status: str) -> None:
    r = rules()
    assert status in r["status_flow"], status
    data = load_run(d)
    data["status"] = status
    save_run(d, data)


def require_status(d: Path, *allowed: str) -> dict:
    data = load_run(d)
    if data["status"] not in allowed:
        raise SystemExit(f"상태가 {data['status']} — 이 단계는 {' · '.join(allowed)}에서만 돈다")
    return data


def service_names(d: Path) -> list[str]:
    data = load_run(d)
    inp = load_yaml(d / "input.yaml") or {}
    names = [data["service"]] + list(inp.get("service_aliases") or [])
    return [n for n in names if n]


# ---------- 블록 ----------

def blocks(d: Path) -> dict:
    """저장된 블록 전부. values는 id → 블록 (measurer + pixel.py 합침)."""
    b = d / "blocks"
    meas = load_yaml(b / "measurer.yaml") or {}
    pix = load_yaml(b / "pixel.yaml") or {}
    judge = load_yaml(b / "judge.yaml") or {}
    values = {v["id"]: dict(v) for v in meas.get("values") or []}
    proposed = {p["id"] for p in meas.get("pixels") or []}
    for v in pix.get("values") or []:
        if v["id"] in proposed:  # 지금 좌표 제안이 있는 항목만 — 값 블록으로 바뀐 항목의 옛 픽셀 값은 버린다
            values[v["id"]] = dict(v)
    return {
        "values": values,
        "measurer_values": {v["id"]: v for v in meas.get("values") or []},
        "pixels": meas.get("pixels") or [],
        "pixel_values": {v["id"]: v for v in pix.get("values") or []},
        "rules": meas.get("rules") or [],
        "judgments": {j["token"]: j for j in judge.get("judgments") or []},
    }


# ---------- 값 파싱 ----------

COLOR_RE = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b|rgba?\([^)]*\)")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def parse_color(s: str):
    s = s.strip()
    if s.startswith("#"):
        h = s[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0)
    nums = [float(x) for x in NUM_RE.findall(s)]
    if len(nums) < 3:
        return None
    a = nums[3] if len(nums) > 3 else 1.0
    return (round(nums[0]), round(nums[1]), round(nums[2]), round(a, 3))


def color_hex(c) -> str:
    r, g, b, a = c
    if a >= 1:
        return f"#{r:02X}{g:02X}{b:02X}"
    return f"rgba({r},{g},{b},{a:g})"


def num(x: str):
    f = float(x)
    return int(f) if f.is_integer() else f


def atoms(value) -> dict:
    """값 문자열 → {colors: [...], nums: [...], words: [...]} (raw 대조용)."""
    s = str(value)
    colors = [parse_color(c) for c in COLOR_RE.findall(s)]
    rest = COLOR_RE.sub(" ", s)
    nums = [num(n) for n in NUM_RE.findall(rest)]
    words = [w for w in re.split(r"[\s/·,()]+", NUM_RE.sub(" ", rest)) if w and w != "px"]
    return {"colors": [c for c in colors if c], "nums": nums, "words": words}


def parts(value, r: dict) -> list[str]:
    return [p.strip() for p in str(value).split(r["formats"]["part_sep"].strip()) if p.strip()]


# ---------- 출처 표기 ----------

def src_label(b: dict) -> str:
    s = b.get("src")
    if s == "dom":
        return "〔DOM〕"
    if s == "pixel":
        return f"〔픽셀 · 배율 {b.get('scale')} · ±{b.get('tol')}〕"
    if s == "est":
        return f"〔추정 · {b.get('basis')}〕"
    return ""


def gap_rows(values: dict) -> list[tuple]:
    """gaps.md · §8 — 못 잼 + 추정 (해당 없음은 넣지 않는다). 블록 없는 항목은 못 잼."""
    rows = []
    for item in template()["items"]:
        iid = item["id"]
        if iid.startswith("meta."):
            continue
        b = values.get(iid)
        if b is None:
            rows.append((iid, item["label"], "못 잼", "블록 없음", ""))
        elif b.get("src") == "none":
            rows.append((iid, item["label"], "못 잼", b.get("reason", ""), b.get("next", "")))
        elif b.get("src") == "est":
            rows.append((iid, item["label"], "추정", b.get("basis", ""), b.get("next", "")))
    return rows


def extract_yaml_block(text: str) -> str:
    """에이전트 답에서 ```yaml 블록 하나만. 블록 밖 글은 버린다."""
    m = re.findall(r"```ya?ml\s*\n(.*?)```", text, re.S)
    if len(m) > 1:
        raise ValueError(f"yaml 블록이 {len(m)}개 — 하나만 돌려줘야 한다")
    return m[0] if m else text


def report(rows: list[tuple], head: tuple) -> str:
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return "\n".join(out)
