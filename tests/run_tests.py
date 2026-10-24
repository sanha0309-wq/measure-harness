"""하네스 시험 — fixture로 정상 run을 만든 뒤, 한 군데씩 망가뜨려 「그 규칙 ID만」 걸리는지 센다.

사용: python tests/run_tests.py
- 실제 runs/ · .claude/refs-access.log는 건드리지 않는다 (HARNESS_RUNS · HARNESS_REFS_LOG를 임시 폴더로)
- raw는 헤드리스 Chrome으로 fixtures/sample.html에 스니펫을 돌려 만든다 (tests/headless_raw.py)
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
GOLD = ROOT / "tests" / "golden_measurer.yaml"
RUN = "demo-sample-2026-10-23"
sys.stdout.reconfigure(encoding="utf-8")


def sh(args, env, stdin=None):
    p = subprocess.run([PY, *args], cwd=ROOT, env=env, input=stdin, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


def make_env(tmp: Path) -> dict:
    env = dict(os.environ, HARNESS_RUNS=str(tmp / "runs"), HARNESS_REFS_LOG=str(tmp / "refs.log"), PYTHONIOENCODING="utf-8")
    (tmp / "runs").mkdir(parents=True, exist_ok=True)
    return env


def base_run(tmp: Path, raw: Path) -> dict:
    env = make_env(tmp)
    sh(["scripts/new_run.py", "demo-sample", "--date", "2026-10-23"], env)
    d = tmp / "runs" / RUN
    shutil.copy(raw, d / "raw" / "dom-home.json")
    assert sh(["scripts/ingest.py", RUN], env)[0] == 0
    assert sh(["scripts/write_run.py", RUN, "--from", "measurer"], env, GOLD.read_text(encoding="utf-8"))[0] == 0
    sh(["scripts/pixel.py", RUN], env)
    assert sh(["scripts/write_run.py", RUN, "--render"], env)[0] == 0
    return env


def check(env, d):
    code, out = sh(["scripts/check.py", RUN], env)
    rep = json.loads((d / "check-report.json").read_text(encoding="utf-8"))
    levels = {g["id"]: g["level"] for g in yaml.safe_load((ROOT / "rules.yaml").read_text(encoding="utf-8"))["gates"]["check"]}
    blocks = {k: v for k, v in rep["counts"].items() if levels[k] == "block"}
    return code, blocks, rep


def block(values=None, pixels=None):
    out = {}
    if values is not None:
        out["values"] = values
    if pixels is not None:
        out["pixels"] = pixels
    return "```yaml\n" + yaml.safe_dump(out, allow_unicode=True) + "```\n"


GOLDV = {v["id"]: v for v in yaml.safe_load(GOLD.read_text(encoding="utf-8"))["values"]}
TH = GOLDV["comp.table.height"]["el"][0]


def edit(path: Path, a: str, b: str):
    s = path.read_text(encoding="utf-8")
    assert a in s, (path, a)
    path.write_text(s.replace(a, b, 1), encoding="utf-8", newline="\n")


def drop_line(path: Path, start: str):
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    path.write_text("".join(x for x in lines if not x.startswith(start)), encoding="utf-8", newline="\n")


def drop_last(path: Path, start: str):
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    i = max(i for i, x in enumerate(lines) if x.startswith(start))
    path.write_text("".join(lines[:i] + lines[i + 1:]), encoding="utf-8", newline="\n")


def sign(d: Path):
    s = (d / "approval.md").read_text(encoding="utf-8").replace("- [ ]", "- [x]").replace("승인자: ", "승인자: 시험").replace("날짜: ", "날짜: 2026-10-23")
    (d / "approval.md").write_text(s, encoding="utf-8")


def log_line(t: Path, rest: str):
    """시험용 refs-access.log에 지금 시각으로 한 줄 (도구 · 대상 · 누가)."""
    import datetime as dt
    with (t / "refs.log").open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now().isoformat(timespec='seconds')}\t{rest}\n")


# (이름, 블록 또는 파일 고치기, 기대 차단 {규칙: 개수})
CASES = [
    ("정상", None, {}),
    ("출처 없는 칸 (measure.md 손으로 고침)", lambda d: edit(d / "measure.md", "| 240 | 〔DOM〕 |", "| 240 |  |"), {"C3": 1}),
    ("〔임의〕 (measure.md 손으로 고침)", lambda d: edit(d / "measure.md", "| 960 | 〔DOM〕 |", "| 960 〔임의〕 | 〔DOM〕 |"), {"C4": 1}),
    ("제목 지움", lambda d: edit(d / "measure.md", "## 4. 간격\n", ""), {"C1": 1}),
    ("추정에 근거 없음", block([{"id": "space.section_gap", "value": 32, "src": "est"}]), {"C5": 1}),
    ("색 형식 오류 (#FFF)", block([dict(GOLDV["comp.button.color_default"], value="#FFF / #2B6CF6")]), {"C6": 1}),
    ("반올림 (268.45 → 268)", block([{"id": "comp.table.width", "value": 268, "src": "dom", "el": TH}]), {"C7": 1}),
    ("raw와 다른 색", block([dict(GOLDV["color.primary"], value="#2B6CF7")]), {"C7": 1}),
    ("measurer가 픽셀 값을 직접 씀", block([{"id": "comp.modal.radius", "value": 20, "src": "pixel", "scale": 1, "tol": 1}]), {"C8": 1}),
    ("gaps.md 행 지움", lambda d: drop_line(d / "gaps.md", "| `comp.button.color_hover`"), {"C9": 1}),
    ("tokens.html 견본 하나 지움", lambda d: edit(d / "tokens.html", 'data-token="color.primary"', 'data-gone="color.primary"'), {"C10": 1}),
    ("compare.md 행 지움", lambda d: edit(d / "compare.md", "| `color.primary`", "| `color.x`"), {"C11": 1}),
    ("run 폴더에 이미지", lambda d: (d / "shot.png").write_bytes(b"\x89PNG"), {"C12": 1}),
    ("raw에 없는 el", block([dict(GOLDV["comp.input.height"], el="body>nope:nth-of-type(1)")]), {"C13": 1}),
    ("basis에 서비스 이름", block([{"id": "space.section_gap", "value": 32, "src": "est", "basis": "demo-sample 섹션 여백에서 계산"}]), {"C14": 1}),
    ("label 20자 넘음", block([dict(GOLDV["comp.modal.width"], label="가상 안내 이 글은 하네스가 실측 문서로 옮기면")]), {"C16": 1}),
    ("label이 el 글자와 다름", block([dict(GOLDV["comp.input.height"], label="저장")]), {"C17": 1}),
    ("컴포넌트 견본 값 손으로 고침", lambda d: edit(d / "tokens.html", "height:44px", "height:45px"), {"C19": 1}),
    ("못 잼 칸의 빈 자리 지움", lambda d: edit(d / "tokens.html", 'data-empty="', 'data-gone="'), {"C19": 1}),
    ("screen.html 값 하나 고침", lambda d: edit(d / "screen.html", "px;top:", "px;top:1"), {"C21": 1}),
    ("screen.html 마지막 요소 지움", lambda d: drop_last(d / "screen.html", '<div class="el"'), {"C21": 1}),
    ("refs 접근 기록", lambda d: (d.parent.parent / "refs.log").write_text("2999-01-01T00:00:00\tRead\trefs/x.md\n", encoding="utf-8"), {"C18": 1}),
]


def judge_case(env, d):
    """추정 행을 채택 후보로 → C15."""
    sh(["scripts/write_run.py", RUN, "--from", "measurer"], env,
       block([{"id": "space.card_padding", "value": 20, "src": "est", "basis": "카드 안 글자 위치에서 계산"}]))
    sh(["scripts/write_run.py", RUN, "--render"], env)
    sh(["scripts/write_run.py", RUN, "--from", "judge"], env,
       "```yaml\n" + yaml.safe_dump({"judgments": [{"token": "layout.cardPadding", "judge": "채택 후보", "why": "시험"}]}, allow_unicode=True) + "```")


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="harness-test-"))
    raw = tmp / "raw-home.json"
    code, out = sh(["tests/headless_raw.py", "fixtures/sample.html", "home", str(raw)], dict(os.environ))
    assert code == 0, out
    results = []

    def record(name, want, got, extra=""):
        ok = want == got
        results.append(ok)
        print(f"{'통과' if ok else '실패'} | {name} | 기대 {want or '차단 0'} | 결과 {got or '차단 0'} {extra}")

    for i, (name, mut, want) in enumerate(CASES):
        t = tmp / f"case{i}"
        env = base_run(t, raw)
        d = t / "runs" / RUN
        if isinstance(mut, str):
            sh(["scripts/write_run.py", RUN, "--from", "measurer"], env, mut)
            sh(["scripts/write_run.py", RUN, "--render"], env)
        elif mut:
            mut(d)
        _, got, _ = check(env, d)
        record(name, want, got)

    t = tmp / "judge"
    env = base_run(t, raw)
    judge_case(env, t / "runs" / RUN)
    record("추정 행이 채택 후보", {"C15": 1}, check(env, t / "runs" / RUN)[1])

    # BOM 붙은 raw (Windows 메모장 · PowerShell 저장) → 수집 통과, 점검 차단 0
    t = tmp / "bom"
    bom_raw = tmp / "raw-home-bom.json"
    bom_raw.write_bytes(b"\xef\xbb\xbf" + raw.read_bytes())
    env = base_run(t, bom_raw)
    record("BOM 붙은 raw", {}, check(env, t / "runs" / RUN)[1])

    # collect.py (Playwright · 설치된 Chrome)로 수집 → ingest 통과 → 모범 블록 86개 · C7 0 · 차단 0
    t = tmp / "collect"
    env = make_env(t)
    sh(["scripts/new_run.py", "demo-sample", "--date", "2026-10-23"], env)
    d = t / "runs" / RUN
    c1, out1 = sh(["scripts/collect.py", RUN, "home", "fixtures/sample.html"], env)
    c2 = sh(["scripts/write_run.py", RUN, "--from", "measurer"], env, GOLD.read_text(encoding="utf-8"))[0]
    sh(["scripts/pixel.py", RUN], env)
    sh(["scripts/write_run.py", RUN, "--render"], env)
    _, got, rep = check(env, d)
    record("collect.py로 수집 (모범 블록 · C7 · 차단)", (0, 0, 86, 0, {}),
           (c1, c2, len(GOLDV), rep["counts"].get("C7", 0), got), "" if c1 == 0 else out1[-300:])

    # guard 훅 — Bash 명령에 refs/ 경로 → 2 + refs-access.log 한 줄, verify_refs.py 실행 → 0 · 기록 없음
    t = tmp / "guard"
    (t / ".claude").mkdir(parents=True)
    genv = dict(os.environ, CLAUDE_PROJECT_DIR=str(t))
    def guard(cmd):
        ev = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
        return subprocess.run([PY, "scripts/guard_write.py"], cwd=ROOT, env=genv, input=ev, capture_output=True, text=True, encoding="utf-8").returncode
    g1, g2 = guard("cat refs/x-home.md"), guard(f"python scripts/verify_refs.py {RUN}")
    glog = t / ".claude" / "refs-access.log"
    lines = glog.read_text(encoding="utf-8").splitlines() if glog.exists() else []
    record("Bash로 refs 읽기 막음 · 기록", (2, 0, 1), (g1, g2, sum("\tBash\t" in x for x in lines)))

    # 블록 자체를 못 읽음 → 3, 한 번 더 → 4 (retry.block_parse 1)
    t = tmp / "parse"
    env = base_run(t, raw)
    bad = block([{"id": "color.primary", "value": "#2B6CF6", "src": "arbitrary"}])
    c1 = sh(["scripts/write_run.py", RUN, "--from", "measurer"], env, bad)[0]
    c2 = sh(["scripts/write_run.py", RUN, "--from", "measurer"], env, bad)[0]
    record("〔임의〕 블록 거부 · 재요청 한도", (3, 4), (c1, c2))

    # 점검 → 정리 재시도 한도 (retry.check_to_organize 2) → 세 번째 차단에서 4
    t = tmp / "retry"
    env = base_run(t, raw)
    d = t / "runs" / RUN
    codes = []
    for _ in range(3):
        edit(d / "measure.md", "| 240 | 〔DOM〕 |", "| 240 |  |")
        codes.append(check(env, d)[0])
        sh(["scripts/write_run.py", RUN, "--render"], env) if codes[-1] == 1 else None
    record("점검→정리 재시도 한도", [1, 1, 4], codes)

    # 승인 — 체크 없음 → 1, 체크 · 서명 → 0, 승인 뒤 산출물 바뀜 → 해시 다름
    t = tmp / "approve"
    env = base_run(t, raw)
    d = t / "runs" / RUN
    check(env, d)
    a1 = sh(["scripts/finalize.py", RUN], env)[0]
    sign(d)
    edit(d / "gaps.md", "못 잼 8", "못 잼 8 ")
    a2 = sh(["scripts/finalize.py", RUN], env)
    edit(d / "gaps.md", "못 잼 8 ", "못 잼 8")
    a3 = sh(["scripts/finalize.py", RUN], env)[0]
    record("승인 (체크 없음 / 승인 뒤 바뀜 / 정상)", (1, 1, 0), (a1, a2[0], a3), "· 해시 다름 잡힘" if "해시" in a2[1] else "")

    # 다시 열기 — 완료 → 정리 중, 다시 찍고 점검 → 승인 대기 (이전 서명은 새 양식으로 지워짐)
    # 첫 승인 뒤 메인 세션의 refs 접근은 C18로 세지 않는다
    log_line(t, "Read\trefs/x-home.md\tmain")
    r1 = sh(["scripts/reopen.py", RUN, "시험"], env)[0]
    r2 = sh(["scripts/write_run.py", RUN, "--render"], env)[0]
    r3, b3, _ = check(env, d)
    st = yaml.safe_load((d / "run.yaml").read_text(encoding="utf-8"))
    signed = "승인자: 시험" in (d / "approval.md").read_text(encoding="utf-8")
    record("다시 열기 (reopen · render · check · 서명 남음)", (0, 0, 0, "승인 대기", 1, False),
           (r1, r2, r3, st["status"], len(st.get("reopened") or []), signed))
    record("첫 승인 뒤 메인 세션 refs 접근은 안 걸림", {}, b3)

    def approved_then_reopened(name):
        t = tmp / name
        env = base_run(t, raw)
        d = t / "runs" / RUN
        check(env, d)
        sign(d)
        sh(["scripts/finalize.py", RUN], env)
        return t, env, d

    # 잠긴 뒤(승인 대기) · 승인 전 메인 세션 접근은 세지 않는다
    t = tmp / "locked-main"
    env = base_run(t, raw)
    d = t / "runs" / RUN
    check(env, d)
    locked = bool(yaml.safe_load((d / "run.yaml").read_text(encoding="utf-8")).get("locked_at"))
    log_line(t, "Read\trefs/x-home.md\tmain")
    sign(d)
    sh(["scripts/finalize.py", RUN], env)
    sh(["scripts/reopen.py", RUN, "시험"], env)
    sh(["scripts/write_run.py", RUN, "--render"], env)
    record("잠긴 뒤 · 승인 전 메인 세션 refs 접근은 안 걸림 (locked_at 기록)", ({}, True), (check(env, d)[1], locked))

    # 첫 승인 뒤라도 measurer · judge의 접근은 센다
    t, env, d = approved_then_reopened("reopen-agent")
    log_line(t, "Read\trefs/x-home.md\tmeasurer")
    sh(["scripts/reopen.py", RUN, "시험"], env)
    sh(["scripts/write_run.py", RUN, "--render"], env)
    record("첫 승인 뒤 measurer refs 접근은 걸림", {"C18": 1}, check(env, d)[1])

    # 다시 연 run에서 measure.md가 바뀌면 C20
    t, env, d = approved_then_reopened("reopen-c20")
    sh(["scripts/reopen.py", RUN, "시험"], env)
    sh(["scripts/write_run.py", RUN, "--render"], env)
    (d / "measure.md").write_text((d / "measure.md").read_text(encoding="utf-8") + "\n", encoding="utf-8", newline="\n")
    record("reopen 뒤 measure.md 바뀜", {"C20": 1}, check(env, d)[1])

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n시험 {len(results)} · 통과 {sum(results)} · 실패 {len(results) - sum(results)}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
