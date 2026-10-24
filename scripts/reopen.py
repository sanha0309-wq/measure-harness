"""「완료」 run을 다시 찍기 위해 「정리 중」으로 되돌린다 (하네스가 산출물 형식을 바꿨을 때).

사용: python scripts/reopen.py <run> "<이유>"
- raw · blocks는 그대로 둔다. 값 · 판단은 바뀌지 않고 산출물만 다시 찍는다
- 이전 approval.md는 approval.<시각>.md로 옮겨 두고, run.yaml reopened에 시각 · 이유 · 그때 승인 해시를 남긴다
- 그다음: write_run.py --render → check.py (새 approval.md 양식) → 사람이 다시 서명 → finalize.py
"""
import datetime as dt
import sys

import approval
from lib import OK, load_run, read_text, require_status, run_dir, save_run, set_status, utf8_io


def main() -> int:
    utf8_io()
    if len(sys.argv) < 3 or not sys.argv[2].strip():
        print('사용: python scripts/reopen.py <run> "<이유>"')
        return 1
    d = run_dir(sys.argv[1])
    require_status(d, "완료")
    p = d / "approval.md"
    now = dt.datetime.now().isoformat(timespec="seconds")
    data = load_run(d)
    kept = None
    if p.exists():  # 이전 승인은 지우지 않고 옆에 둔다 — 다시 찍은 뒤에는 사람이 새 양식에 다시 서명
        kept = p.with_name(f"approval.{now.replace(':', '')}.md")
        p.rename(kept)
    data.setdefault("reopened", []).append({
        "at": now,
        "reason": sys.argv[2].strip(),
        "approved_hashes": approval.written_hashes(read_text(kept)) if kept else {},
        "approval_kept": kept.name if kept else None,
    })
    save_run(d, data)
    set_status(d, "정리 중")
    print(f"되돌림: {d.name} 완료 → 정리 중. 다음: python scripts/write_run.py {d.name} --render")
    return OK


if __name__ == "__main__":
    sys.exit(main())
