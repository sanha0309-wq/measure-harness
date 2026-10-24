# 파이프라인 — 레퍼런스 실측 하네스

> 파일을 쓰는 것은 스크립트뿐이다. 에이전트는 YAML 블록을 돌려주고, 사람은 입력과 승인만 한다.
> 규칙 · 횟수 · 허용 오차는 `rules.yaml` 한 곳에 둔다.

## 상태 (run.yaml의 `status`, 스크립트만 바꾼다)
수집 중 → 정리 중 → 점검 중 → 승인 대기 → 완료

## 단계
| 단계 | 누가 | 하는 일 | 남는 파일 | 다음 상태로 가는 조건 |
|---|---|---|---|---|
| S0 시작 | 스크립트 `new_run.py <서비스>` | run 폴더 만들기. 같은 날 같은 서비스가 있으면 `-2`, `-3` | `run.yaml`, `input.yaml`(빈 양식) | — (수집 중) |
| S1 수집 | 사람 | `input.yaml`에 잴 화면 · 캡처별 배율 기입. 스니펫 실행 · JSON 저장 · 캡처 저장 | `input.yaml`, `raw/dom-<화면>.json`, `raw/captures/*` (커밋 안 됨) | — |
| | 스크립트 `ingest.py` | raw JSON 형식 · 화면 폭 1440 · dpr · 화면 이름이 input.yaml과 맞는지 대조 | `raw/ingest-report.json` | 차단 0 → **정리 중** |
| S2 정리 | 에이전트 | raw를 읽고 템플릿 항목마다 `{항목, 값, 출처}` YAML 블록을 돌려준다. 캡처 값은 **좌표만** 제안 | (파일 안 씀) | — |
| | 스크립트 `pixel.py` | 제안 좌표에서 Pillow로 실제 픽셀을 읽어 색 · 크기를 확정 | `blocks/pixel-*.yaml` | — |
| | 스크립트 `write_run.py` | 블록을 저장하고, **목차는 템플릿대로 찍어** measure.md · tokens.json · gaps.md 생성 | `blocks/*.yaml`, `measure.md`, `tokens.json`, `gaps.md` | — |
| | 스크립트 `build_html.py` | tokens.json → 토큰 견본, measure.md §6 → 컴포넌트 견본 | `tokens.html` | — |
| | 스크립트 `compare.py` | `docs/our-tokens.example.json`과 비교 | `compare.md` | — |
| | 스크립트 `diff_prev.py` | 같은 서비스의 이전 run이 있으면 달라진 값만 | `corrections.md` | 생성 끝 → **점검 중** |
| S3 점검 | 스크립트 `check.py` + `rules.yaml` | 차단 · 경고를 센다 | `check-report.json` | 차단 0 → **승인 대기** + `approval.md` 양식 생성 |
| S4 승인 | 사람 | `approval.md` 확인 항목 체크 · 서명 | `approval.md` | — |
| | 스크립트 `finalize.py` | 승인 파일 확인 | `run.yaml` | 확인 통과 → **완료** |

## 돌아갈 길
- S1 `ingest.py` 차단 → 사람이 raw를 다시 수집
- 수집 재시도 최대 횟수는 `rules.yaml`의 `retry.ingest`
- S3 차단 → S2로 돌아간다. 최대 횟수는 `rules.yaml`의 `retry.check_to_organize`
  - 넘으면 상태를 「점검 중」에 멈추고, 남은 차단 목록을 사람에게 보여 준다
- S4 승인 파일 확인 실패 → 「승인 대기」에 머문다
- 「완료」 run을 하네스 변경 뒤 다시 찍을 때 → `scripts/reopen.py <run> "<이유>"`로 「정리 중」 (raw · blocks 그대로, 이전 approval.md는 옆에 보관) → `--render` → S3 → S4 다시 서명

## DOM 스니펫 (`snippet/measure.js`)
- 사람이 개발자 도구 콘솔에 붙여 넣고 `measure('<화면 이름>')`으로 실행한다
- JSON 안에 화면 이름 · 화면 폭 · `devicePixelRatio` · URL · 측정 시각을 함께 담는다
- 화면에 보이는 요소만 담는다 (뷰포트 밖 · `display:none` · `visibility:hidden` 제외). 요소마다 요소 경로 + `rules.yaml`의 `snippet.props` + 글자 앞부분(`snippet.text_prefix_chars`자, label 대조용)
- 요소 수 상한은 `rules.yaml`의 `snippet.max_elements`. 넘으면 잘라서 경고 (I6)
- 뷰포트 아래쪽을 재려면 스크롤한 뒤 다른 화면 이름으로 다시 실행한다 (예: `home`, `home-2`)
- 게이트 규칙 전체는 `rules.yaml`의 `gates`
- 결과는 `copy()`로 클립보드에 넣는다. 사람은 `raw/dom-<화면>.json`에 붙여 넣기만 한다 (예비 경로)
- 자동 수집: `python scripts/collect.py <run> <화면 이름> <URL>` — 설치된 Chrome(Playwright, `channel="chrome"`)을 `run.viewport_width` × 900으로 열어 같은 스니펫을 `measure(<화면>, { returnJson: true })`로 돌리고, `raw/dom-<화면>.json` 저장 뒤 `ingest.py`까지 돌린다. 로그인 · 캡처가 필요한 화면은 콘솔 붙여 넣기로 한다
