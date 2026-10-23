"""S4 — approval.md를 확인하고 「완료」로 (G-승인).

사용: python scripts/finalize.py <run>
"""
import sys

import approval
from lib import GATE_FAIL, OK, require_status, run_dir, set_status, utf8_io


def main() -> int:
    utf8_io()
    d = run_dir(sys.argv[1])
    require_status(d, "승인 대기")
    errs = approval.verify(d)
    for e in errs:
        print(f"승인 확인 실패: {e}")
    if errs:
        print("「승인 대기」에 머문다")
        return GATE_FAIL
    set_status(d, "완료")
    print(f"완료: {d.name}")
    return OK


if __name__ == "__main__":
    sys.exit(main())
