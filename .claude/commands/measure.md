---
description: 서비스 하나를 실측한다. 새 run을 만들거나, 같은 서비스의 진행 중인 run을 이어서 한다. URL을 주면 S1 수집을 collect.py로 한다.
argument-hint: <서비스> [<화면 이름> <URL>]
---

인자: $ARGUMENTS (첫 낱말 = 서비스, 이어서 화면 이름 · URL이 있을 수 있다)

CLAUDE.md의 진행 순서를 따른다.

1. `runs/`에서 `<서비스>-`로 시작하는 run 중 `run.yaml`의 `status`가 「완료」가 아닌 것을 찾는다
   - 있으면 그 run의 `status` 단계부터 이어서 한다
   - 없으면 `python scripts/new_run.py <서비스>`로 S0부터 시작한다
2. S1 수집
   - **URL을 줬으면** (화면 이름이 없으면 `home`): 사람에게 `runs/<run>/input.yaml`의 `screens`에 그 화면이 있는지 확인받은 뒤
     `python scripts/collect.py <run> <화면 이름> <URL>`을 돌린다. raw 저장과 `ingest.py`까지 스크립트가 한다. 종료 코드는 `ingest.py`와 같다
   - URL이 없거나, 로그인이 필요하거나, 캡처가 필요한 화면이면 사람 차례 — 멈추고 콘솔 붙여 넣기 방식(README)을 `docs/pipeline.md` 표대로 한 줄씩 보여 준다
3. 사람 차례(S1 수집 · S4 승인)에서는 멈춘다
4. 단계가 끝날 때마다 CLAUDE.md §4 보고 형식으로만 보고한다
