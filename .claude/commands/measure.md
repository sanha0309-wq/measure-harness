---
description: 서비스 하나를 실측한다. 새 run을 만들거나, 같은 서비스의 진행 중인 run을 이어서 한다.
argument-hint: <서비스>
---

서비스: $ARGUMENTS

CLAUDE.md의 진행 순서를 따른다.

1. `runs/`에서 `$ARGUMENTS-`로 시작하는 run 중 `run.yaml`의 `status`가 「완료」가 아닌 것을 찾는다
   - 있으면 그 run의 `status` 단계부터 이어서 한다
   - 없으면 `python scripts/new_run.py $ARGUMENTS`로 S0부터 시작한다
2. 사람 차례(S1 수집 · S4 승인)에서는 멈추고, 사람이 할 일을 `docs/pipeline.md` 표대로 한 줄씩 보여 준다
3. 단계가 끝날 때마다 CLAUDE.md §4 보고 형식으로만 보고한다
