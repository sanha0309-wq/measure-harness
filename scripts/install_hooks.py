"""git pre-commit 훅 설치 — .git/hooks/pre-commit이 scripts/precommit.py를 부르게 한다."""
from lib import ROOT, utf8_io, write_text

HOOK = """#!/bin/sh
# measure-harness: 이미지 · refs/ · 비공개 run 커밋 금지 (scripts/precommit.py)
exec python "$(git rev-parse --show-toplevel)/scripts/precommit.py"
"""


def main() -> None:
    utf8_io()
    git = ROOT / ".git"
    if not git.is_dir():
        raise SystemExit("git 저장소가 아니다 — 먼저 git init")
    p = git / "hooks" / "pre-commit"
    write_text(p, HOOK)
    p.chmod(0o755)
    print(f"설치: {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
