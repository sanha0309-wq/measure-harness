"""git pre-commit — 이미지 · refs/ · 시연 run 밖의 run이 스테이징되면 커밋을 거부한다 (rules.yaml commit_block).

.gitignore는 `git add -f`로 뚫리므로 여기서 한 번 더 막는다. 설치: python scripts/install_hooks.py
"""
import subprocess
import sys

from lib import rules, utf8_io


def blocked(paths: list[str]) -> list[tuple[str, str]]:
    cb = rules()["commit_block"]
    out = []
    for p in paths:
        low = p.lower()
        if any(low.endswith(e) for e in cb["image_ext"]):
            out.append((p, "이미지"))
        elif any(p.startswith(x) for x in cb["paths"]):
            out.append((p, "refs/ (비공개)"))
        elif p.startswith("runs/") and not p.startswith(cb["runs_allowed_prefix"]):
            out.append((p, "시연 run 밖의 run (비공개)"))
    return out


def main() -> int:
    utf8_io()
    names = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                           capture_output=True, text=True, encoding="utf-8", check=True).stdout.split("\n")
    bad = blocked([n.strip() for n in names if n.strip()])
    for p, why in bad:
        print(f"커밋 거부: {p} — {why}", file=sys.stderr)
    if bad:
        print(f"{len(bad)}개. `git restore --staged <파일>`로 빼고 다시 커밋", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
