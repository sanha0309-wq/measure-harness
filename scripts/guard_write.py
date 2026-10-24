"""PreToolUse 훅 — Claude(메인 세션 · 에이전트)의 파일 도구를 막는다.

- Write · Edit: runs/ · refs/ 아래는 스크립트만 쓴다 (CLAUDE.md §1-1)
- Read · Glob · Grep: refs/는 R8 채점용으로 스크립트(verify_refs.py)만 읽는다 (CLAUDE.md §1-7)
- Bash · PowerShell: 명령에 refs/ 경로(또는 cd · ls 등으로 refs 폴더)가 들어가면 막는다. git의 refs/heads · tags · remotes는 뺀다
  (경로를 글자 조각으로 이어 붙이는 식의 우회까지는 못 잡는다)
  막을 때마다 .claude/refs-access.log에 한 줄 → check.py C18이 센다
막으면 종료 코드 2 + stderr 이유.
"""
import datetime as dt
import json
import os
import re
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Glob", "Grep"}
SHELL_TOOLS = {"Bash", "PowerShell"}
# refs/ · refs\ 경로. 앞이 단어 글자면 다른 이름(verify_refs.py 등)이다
SHELL_PATH = re.compile(r"(?<![\w.-])refs[/\x5c](?!(heads|tags|remotes)/)")  # \x5c = 역슬래시
# 경로 구분자 없이 폴더만 넘기는 경우 (cd refs, ls refs …)
SHELL_DIR = re.compile(r"(?i)\b(cd|pushd|ls|dir|tree|find|sl|set-location|gci|get-childitem)\s+[\"']?(\./)?refs[\"']?(?=\s|$|[;&|)])")


def first_part(root: str, path: str) -> str:
    rel = os.path.relpath(os.path.abspath(os.path.join(root, path)), os.path.abspath(root))
    return rel.replace("\\", "/").split("/")[0], rel


def log_access(root: str, tool: str, what: str) -> None:
    log = os.path.join(root, ".claude", "refs-access.log")
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    with open(log, "a", encoding="utf-8") as f:
        f.write(f"{stamp}\t{tool}\t{' '.join(what.split())[:200]}\n")  # 한 줄 한 건 — 명령의 줄바꿈 · 탭은 공백으로


def main() -> int:
    for s in (sys.stdin, sys.stdout, sys.stderr):  # Windows 기본 cp949면 경로 · 이유 문구가 깨진다
        s.reconfigure(encoding="utf-8")
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool = event.get("tool_name", "")
    ti = event.get("tool_input") or {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()

    if tool in WRITE_TOOLS:
        path = ti.get("file_path") or ti.get("notebook_path")
        if path:
            first, rel = first_part(root, path)
            if first in ("runs", "refs"):
                print(f"막음: {rel} — {first}/ 아래는 스크립트만 쓴다 (CLAUDE.md §1-1). "
                      "에이전트 블록은 stdin으로 scripts/write_run.py에 넘긴다.", file=sys.stderr)
                return 2

    if tool in READ_TOOLS:
        cands = [ti.get(k) for k in ("file_path", "path", "pattern", "glob") if ti.get(k)]
        for c in cands:
            first, rel = first_part(root, c) if not c.startswith("*") else (c.split("/")[0], c)
            if first == "refs" or "refs/" in c.replace("\\", "/"):
                log_access(root, tool, c)
                print(f"막음: {c} — refs/는 R8 채점용으로 스크립트만 읽는다 (CLAUDE.md §1-7).", file=sys.stderr)
                return 2

    if tool in SHELL_TOOLS:
        cmd = ti.get("command") or ""
        if SHELL_PATH.search(cmd) or SHELL_DIR.search(cmd):
            log_access(root, tool, cmd)
            print("막음: 명령에 refs/가 들어 있다 — refs/는 R8 채점용으로 스크립트(verify_refs.py)만 읽는다 (CLAUDE.md §1-7).", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
