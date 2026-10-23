# 산출물 형식 — 레퍼런스 실측 하네스

> 모든 산출물은 스크립트가 쓴다. 에이전트는 ① 블록만 돌려준다.
> 항목 ID는 `docs/measure-template.md`의 `<!-- id: … -->`가 기준이다 (측정 항목 86개 + 측정 정보 4개).

## run 폴더
```
runs/<서비스>-<날짜>[-n]/
  run.yaml            상태 · 재시도 횟수 · 이전 run (스크립트만 씀)
  input.yaml          잴 화면 · 캡처별 배율 (사람이 씀)
  raw/                dom-<화면>.json · captures/ (캡처는 커밋 안 됨)
  blocks/             에이전트 블록 · pixel.py 결과 (스크립트가 저장)
  measure.md  tokens.json  tokens.html  compare.md  gaps.md  corrections.md
  check-report.json  approval.md
```
- 공개하는 run은 `runs/demo-sample/` 하나. 대상은 저장소 안의 가상 견본 페이지 `fixtures/sample.html`
- 실서비스 홈 (손으로 잰 비교 기준) run은 비공개. R8에서 `refs/<service>-home.md`와 비교하는 데만 쓴다

## ① 에이전트 블록 (`blocks/*.yaml`)
값 블록 — 템플릿 항목 하나에 한 개
```yaml
- id: radius.button
  value: 8
  unit: px
  src: dom                 # dom | pixel | est | none | na
  el: main>section:nth-of-type(2)>button   # dom이면 필수 — 스니펫이 담은 요소 경로
  label: 시작하기          # 선택 — 요소를 알아보기 위한 짧은 화면 문구만. 긴 본문은 옮기지 않는다
- id: radius.modal
  value: 16
  src: pixel
  scale: 1.5               # pixel이면 필수
  tol: 1                   # pixel이면 필수
  capture: home-modal      # 캡처 파일 이름만
- id: color.status
  src: none                # 못 잼 — reason 필수
  reason: 홈 화면에 상태 색이 쓰인 요소가 없음
- id: comp.empty.color_hover
  src: na                  # 해당 없음 — reason 필수. 못 잼과 따로 센다
  reason: 빈 상태에는 올림 상태가 없음
- id: space.section_gap
  value: 40
  src: est                 # 추정 — basis 필수
  basis: 섹션 제목 위 여백 32 + 구분선 아래 8
```
- 〔임의〕(`src: arbitrary`)는 블록 형식에서 받지 않는다
- `value`에는 측정값만. 화면 문구는 `label`에만, `rules.yaml`의 `thresholds.label_max_chars` 이내
- `label`은 measure.md 값 칸에 `8 — 「시작하기」`처럼 값 뒤에 찍는다. tokens.json · compare.md에는 찍지 않는다
- `label`은 그 `el`의 실제 글자 앞부분으로 시작해야 한다 (C17). 스니펫이 요소마다 글자 앞부분을 담는다
- 캡처 값은 에이전트가 좌표(`box: [x1, y1, x2, y2]`)만 제안하고 `pixel.py`가 값을 확정한다

판단 블록 — compare.md 「판단」 제안
```yaml
- token: radius.md
  judge: 채택 후보         # 채택 후보 | 유지 | 보류
  why: 버튼 · 입력 반경이 모두 8로 우리 값과 같은 단계에 몰림
  propose: 12              # 선택. compare.md 메모에 「제안 12 〔임의〕」로만 들어간다
```
- 블록이 없으면 스크립트 기본값은 「보류」〔임의〕. 사람이 승인할 때 확인한다

규칙 블록 — measure.md §7
```yaml
- rule: 선택된 탭만 채움, 나머지는 구분선
  refs: [comp.tab.color_default, comp.tab.color_pressed]
```

## ② measure.md
- 목차와 행은 `write_run.py`가 템플릿에서 그대로 찍는다. 블록은 값 칸만 채운다
- 출처 표기: `〔DOM〕` · `〔픽셀 · 배율 1.5 · ±1〕` · `〔추정 · 근거〕`
- label이 있으면 값 칸에 `값 — 「label」`. W1(문구 원문 의심)은 「」 안을 세지 않는다 (label 길이는 C16이 센다)
- 블록이 없는 항목은 비워 두지 않고 `못 잼 (블록 없음)`으로 찍는다
- `src: none` → `못 잼 (이유)`, `src: na` → `해당 없음 (이유)`

## ③ tokens.json
`docs/our-tokens.example.json`과 같은 키 구조. 값마다 출처를 단다.
```json
{ "color":  { "text-primary": { "value": "#191F28", "src": "dom" } },
  "radius": { "md": { "value": 8, "src": "pixel", "scale": 1.5, "tol": 1 } } }
```
- 항목 ID → 토큰 키 대응은 `rules.yaml`의 `token_map`. 대응이 없는 항목은 measure.md에만 남는다

## ④ tokens.html
- 색 · 글자 · 간격 · 반경 · 그림자 · 크기 6구역. tokens.json의 값만 쓴다
- 견본마다 `data-token="<토큰 키>"`와 값 · 출처 표기. 견본 수 = 토큰 수
- 〔추정〕 견본은 점선 테두리 + 「추정」 라벨

## ⑤ compare.md
| 토큰 | 우리 값 | 그 서비스 값 | 출처 | 차이 | 판단 | 메모 |
|---|---|---|---|---|---|---|
- 차이가 `rules.yaml`의 허용 오차 안이면 행을 만들지 않는다 (AC-3)
- 판단은 채택 후보 / 유지 / 보류 중 하나

## ⑥ gaps.md
| 항목 | 상태 (못 잼 / 추정) | 이유 · 근거 | 다음에 재는 방법 |
|---|---|---|---|
- measure.md의 `못 잼` · `〔추정〕` 칸에서 뽑는다. `해당 없음`은 넣지 않는다

## ⑦ corrections.md
| 항목 | 이전 값 | 이전 출처 | 새 값 | 새 출처 | 이전 run |
|---|---|---|---|---|---|
- 같은 서비스의 이전 run이 있을 때만 생성. 달라진 항목만 (AC-5)
