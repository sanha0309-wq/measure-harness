# demo-sample 실측 — 2026-10-23

> 모든 값 뒤에 출처: 〔DOM〕 · 〔픽셀 · 배율 n · ±1〕 · 〔추정 · 근거〕
> 〔임의〕는 이 문서에 올 수 없다 (있으면 차단). 내가 정한 값은 compare.md의 채택 후보로만 둔다
> 못 잰 칸은 지우지 않는다 → `못 잼 (이유)` · 그 화면에 해당 요소가 없으면 → `해당 없음 (이유)`
> `<!-- id: … -->`는 항목 ID. 스크립트가 이 ID로 목차를 찍고 센다. 지우거나 바꾸지 않는다

## 0. 측정 정보
> 이 절은 run.yaml · input.yaml · raw에서 스크립트가 채운다

| 항목 | 값 |
|---|---|
| 측정 방법 <!-- id: meta.method --> | DOM |
| 화면 폭 <!-- id: meta.viewport --> | 1440 |
| 캡처 배율 <!-- id: meta.scale --> | 해당 없음 (캡처 없음) |
| 잰 화면 목록 <!-- id: meta.screens --> | home |

## 1. 배치
| 항목 | 값 | 출처 |
|---|---|---|
| 전체 폭 · 칼럼 구성 <!-- id: layout.columns --> | 1440 / 240 · 840 · 360 | 〔DOM〕 |
| 사이드바 폭 <!-- id: layout.sidebar --> | 240 | 〔DOM〕 |
| 본문 최대 폭 <!-- id: layout.content_max --> | 960 | 〔DOM〕 |
| 페이지 좌우 여백 <!-- id: layout.page_padding --> | 32 | 〔DOM〕 |
| 패널 폭 <!-- id: layout.panel --> | 360 | 〔DOM〕 |

## 2. 글자
| 쓰임 | 크기 / 행간 / 굵기 | 자간 | 출처 |
|---|---|---|---|
| 페이지 제목 <!-- id: type.title_page --> | 28 / 36 / 700 — 「가상 대시보드」 | -0.4 | 〔DOM〕 |
| 섹션 제목 <!-- id: type.title_section --> | 20 / 28 / 600 — 「요약」 | normal | 〔DOM〕 |
| 본문 <!-- id: type.body --> | 15 / 24 / 400 | normal | 〔DOM〕 |
| 보조 글자 <!-- id: type.caption --> | 13 / 18 / 400 — 「항목 A」 | normal | 〔DOM〕 |
| 버튼 라벨 <!-- id: type.button --> | 15 / 22 / 600 — 「저장」 | normal | 〔DOM〕 |
| 글꼴 <!-- id: type.family --> | Sample Sans | — | 〔DOM〕 |

## 3. 색
| 역할 | 값 | 출처 |
|---|---|---|
| 글자 기본 · 보조 · 비활성 <!-- id: color.text --> | #1A1C20 / #5B616E / #A3A9B3 | 〔DOM〕 |
| 배경 · 면 · 바닥 <!-- id: color.bg --> | #FFFFFF / #F7F8FA / #EEF0F3 | 〔DOM〕 |
| 선 <!-- id: color.border --> | #E1E4E8 | 〔DOM〕 |
| 주요 색 <!-- id: color.primary --> | #2B6CF6 — 「저장」 | 〔DOM〕 |
| 상태 (성공 · 경고 · 오류 · 정보) <!-- id: color.status --> | #1F9D55 / #E8A317 / #D93B3B / #3A7BD5 | 〔DOM〕 |

## 4. 간격
| 항목 | 값 | 출처 |
|---|---|---|
| 간격 단계 <!-- id: space.scale --> | 4 / 8 / 12 / 16 / 20 / 24 / 32 | 〔DOM〕 |
| 카드 안쪽 여백 <!-- id: space.card_padding --> | 20 — 「항목 A」 | 〔DOM〕 |
| 카드 사이 <!-- id: space.card_gap --> | 16 | 〔DOM〕 |
| 섹션 사이 <!-- id: space.section_gap --> | 32 | 〔DOM〕 |

## 5. 반경 · 그림자
| 항목 | 값 | 출처 |
|---|---|---|
| 반경 단계 <!-- id: radius.scale --> | 8 / 12 / 20 / 999 | 〔DOM〕 |
| 버튼 · 입력 · 카드 · 모달 반경 <!-- id: radius.components --> | 8 / 8 / 12 / 20 | 〔DOM〕 |
| 그림자 <!-- id: shadow.scale --> | rgba(0, 0, 0, 0.06) 0px 1px 2px 0px / rgba(0, 0, 0, 0.12) 0px 8px 24px 0px | 〔DOM〕 |

## 6. 컴포넌트
컴포넌트마다 같은 9행. 크기가 여러 단계면 값 칸에 `32 / 40 / 48`처럼 적는다

### 6-1. 버튼
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.button.height --> | 44 / 36 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.button.width --> | 못 잼 (raw에 min-width가 없고 폭이 글자 길이 따라 버튼마다 다름 (70 · 63.3333 · 85) — 최소 · 고정 폭 근거 없음) |  |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.button.padding --> | 0 · 20 / 0 · 16 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.button.text --> | 15 / 22 / 600 — 「저장」 | 〔DOM〕 |
| 반경 <!-- id: comp.button.radius --> | 8 — 「저장」 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.button.color_default --> | #FFFFFF / #2B6CF6 — 「저장」 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.button.color_hover --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 올림 상태 스타일 · 캡처 없음) |  |
| 색 · 누름 <!-- id: comp.button.color_pressed --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 누름 상태 스타일 · 캡처 없음) |  |
| 색 · 비활성 <!-- id: comp.button.color_disabled --> | #A3A9B3 / #EEF0F3 — 「보내기」 | 〔DOM〕 |

### 6-2. 입력
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.input.height --> | 44 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.input.width --> | 280 | 〔DOM〕 |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.input.padding --> | 0 · 14 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.input.text --> | 15 / 24 / 400 | 〔DOM〕 |
| 반경 <!-- id: comp.input.radius --> | 8 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.input.color_default --> | #1A1C20 / #FFFFFF / #E1E4E8 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.input.color_hover --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 올림 상태 스타일 · 캡처 없음) |  |
| 색 · 누름 <!-- id: comp.input.color_pressed --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 누름(포커스) 상태 스타일 · 캡처 없음) |  |
| 색 · 비활성 <!-- id: comp.input.color_disabled --> | 해당 없음 (홈 화면에 비활성 입력이 없음) |  |

### 6-3. 탭
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.tab.height --> | 40 — 「전체」 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.tab.width --> | 못 잼 (raw에 min-width가 없고 탭 폭 38은 글자 폭 + 좌우 여백으로 보임 — 최소 · 고정 폭 근거 없음) |  |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.tab.padding --> | 8 · 4 — 「전체」 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.tab.text --> | 15 / 24 / 600 — 「전체」 | 〔DOM〕 |
| 반경 <!-- id: comp.tab.radius --> | 0 — 「전체」 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.tab.color_default --> | #5B616E / rgba(0, 0, 0, 0) — 「진행」 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.tab.color_hover --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 올림 상태 스타일 · 캡처 없음) |  |
| 색 · 누름 <!-- id: comp.tab.color_pressed --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 누름 상태 스타일 · 캡처 없음 (선택 탭은 §7 규칙에 적음)) |  |
| 색 · 비활성 <!-- id: comp.tab.color_disabled --> | 해당 없음 (홈 화면에 비활성 탭이 없음) |  |

### 6-4. 배지
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.badge.height --> | 22 — 「정상」 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.badge.width --> | 못 잼 (raw에 min-width가 없고 배지 폭 40은 글자 폭 + 좌우 여백으로 보임 — 최소 · 고정 폭 근거 없음) |  |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.badge.padding --> | 3 · 8 — 「정상」 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.badge.text --> | 12 / 16 / 600 — 「정상」 | 〔DOM〕 |
| 반경 <!-- id: comp.badge.radius --> | 999 — 「정상」 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.badge.color_default --> | #1F9D55 / #E6F4EC — 「정상」 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.badge.color_hover --> | 해당 없음 (배지는 누를 수 없는 표시 요소라 올림 상태가 성립하지 않음) |  |
| 색 · 누름 <!-- id: comp.badge.color_pressed --> | 해당 없음 (배지는 누를 수 없는 표시 요소라 누름 상태가 성립하지 않음) |  |
| 색 · 비활성 <!-- id: comp.badge.color_disabled --> | 해당 없음 (배지는 표시 요소라 비활성 상태가 성립하지 않음) |  |

### 6-5. 표
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.table.height --> | 40 / 48 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.table.width --> | 못 잼 (표 폭 776은 본문 폭을 그대로 채움 — raw에 최소 · 고정 폭 지정 근거 없음) |  |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.table.padding --> | 0 · 12 — 「가」 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.table.text --> | 15 / 24 / 400 — 「가」 | 〔DOM〕 |
| 반경 <!-- id: comp.table.radius --> | 0 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.table.color_default --> | #1A1C20 / rgba(0, 0, 0, 0) / #E1E4E8 — 「가」 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.table.color_hover --> | 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 행 올림 상태 스타일 · 캡처 없음) |  |
| 색 · 누름 <!-- id: comp.table.color_pressed --> | 해당 없음 (표 행에 누름 동작이 보이지 않아 누름 상태가 성립하지 않음) |  |
| 색 · 비활성 <!-- id: comp.table.color_disabled --> | 해당 없음 (홈 화면 표에 비활성 행이 없음) |  |

### 6-6. 모달 · 드로어
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.modal.height --> | 216 — 「가상 안내」 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.modal.width --> | 못 잼 (카드 폭 312는 패널 폭 안을 채운 값으로 보임 — raw에 최소 · 고정 폭 지정 근거 없음) |  |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.modal.padding --> | 24 — 「가상 안내」 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.modal.text --> | 15 / 24 / 400 | 〔DOM〕 |
| 반경 <!-- id: comp.modal.radius --> | 20 — 「가상 안내」 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.modal.color_default --> | #1A1C20 / #FFFFFF — 「가상 안내」 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.modal.color_hover --> | 해당 없음 (모달 몸체는 누르는 요소가 아니라 올림 상태가 성립하지 않음) |  |
| 색 · 누름 <!-- id: comp.modal.color_pressed --> | 해당 없음 (모달 몸체는 누르는 요소가 아니라 누름 상태가 성립하지 않음) |  |
| 색 · 비활성 <!-- id: comp.modal.color_disabled --> | 해당 없음 (모달 몸체에는 비활성 상태가 성립하지 않음) |  |

### 6-7. 빈 상태
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.empty.height --> | 83.3333 — 「아직 항목이 없어요」 | 〔DOM〕 |
| 폭 (최소 / 고정) <!-- id: comp.empty.width --> | 못 잼 (빈 상태 폭 776은 본문 폭을 그대로 채움 — raw에 최소 · 고정 폭 지정 근거 없음) |  |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.empty.padding --> | 32 — 「아직 항목이 없어요」 | 〔DOM〕 |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.empty.text --> | 13 / 18 / 400 — 「아직 항목이 없어요」 | 〔DOM〕 |
| 반경 <!-- id: comp.empty.radius --> | 12 — 「아직 항목이 없어요」 | 〔DOM〕 |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.empty.color_default --> | #5B616E / rgba(0, 0, 0, 0) / #E1E4E8 | 〔DOM〕 |
| 색 · 올림 <!-- id: comp.empty.color_hover --> | 해당 없음 (빈 상태는 누르는 요소가 아니라 올림 상태가 성립하지 않음) |  |
| 색 · 누름 <!-- id: comp.empty.color_pressed --> | 해당 없음 (빈 상태는 누르는 요소가 아니라 누름 상태가 성립하지 않음) |  |
| 색 · 비활성 <!-- id: comp.empty.color_disabled --> | 해당 없음 (빈 상태에는 비활성 상태가 성립하지 않음) |  |

## 7. 읽히는 규칙

- 선택된 탭만 기본 글자색 + 아래 2px 주요 색 선, 나머지 탭은 보조 글자색 · 선 없음 (굵기는 모두 600) (근거: comp.tab.color_default, comp.tab.text, color.text, color.primary)
- 배지는 상태 색 글자 + 같은 색조의 옅은 배경, 반경 999로 알약 모양 (근거: comp.badge.color_default, comp.badge.radius, color.status)
- 반경은 요소가 클수록 커짐 — 버튼 · 입력 8, 카드 · 빈 상태 12, 떠 있는 카드 20 (근거: radius.scale, radius.components, comp.empty.radius, comp.modal.radius)
- 주 버튼 높이 44는 입력 높이 44와 같고, 보조 버튼만 36 (근거: comp.button.height, comp.input.height)
- 선 색은 한 가지(#E1E4E8)이고 두께도 0.666667px 한 가지 — 입력 · 표 구분선 · 빈 상태 테두리 · 탭 바닥선 (근거: color.border, comp.input.color_default, comp.table.color_default, comp.empty.color_default)
- 표 머리는 13 / 18 / 600 보조 글자색 + 면 배경(#F7F8FA), 몸 칸은 15 / 24 / 400 기본 글자 + 아래 구분선 (근거: comp.table.text, comp.table.color_default, type.caption, color.bg)
- 섹션 사이 32는 페이지 좌우 여백 32 · 빈 상태 안쪽 여백 32와 같은 단계 (근거: space.section_gap, layout.page_padding, comp.empty.padding, space.scale)
- 그림자는 두 단계 — 카드는 옅고 짧게(0 1 2), 떠 있는 카드는 진하고 넓게(0 8 24) (근거: shadow.scale)
값 사이에서 보이는 규칙을 문장으로 (예: 「선택된 탭만 채움, 나머지는 구분선」). 문장마다 근거 항목 ID를 단다

## 8. 못 잰 것

- `comp.button.width` 폭 (최소 / 고정) — 못 잼 (raw에 min-width가 없고 폭이 글자 길이 따라 버튼마다 다름 (70 · 63.3333 · 85) — 최소 · 고정 폭 근거 없음)
- `comp.button.color_hover` 색 · 올림 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 올림 상태 스타일 · 캡처 없음)
- `comp.button.color_pressed` 색 · 누름 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 누름 상태 스타일 · 캡처 없음)
- `comp.input.color_hover` 색 · 올림 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 올림 상태 스타일 · 캡처 없음)
- `comp.input.color_pressed` 색 · 누름 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 누름(포커스) 상태 스타일 · 캡처 없음)
- `comp.tab.width` 폭 (최소 / 고정) — 못 잼 (raw에 min-width가 없고 탭 폭 38은 글자 폭 + 좌우 여백으로 보임 — 최소 · 고정 폭 근거 없음)
- `comp.tab.color_hover` 색 · 올림 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 올림 상태 스타일 · 캡처 없음)
- `comp.tab.color_pressed` 색 · 누름 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 누름 상태 스타일 · 캡처 없음 (선택 탭은 §7 규칙에 적음))
- `comp.badge.width` 폭 (최소 / 고정) — 못 잼 (raw에 min-width가 없고 배지 폭 40은 글자 폭 + 좌우 여백으로 보임 — 최소 · 고정 폭 근거 없음)
- `comp.table.width` 폭 (최소 / 고정) — 못 잼 (표 폭 776은 본문 폭을 그대로 채움 — raw에 최소 · 고정 폭 지정 근거 없음)
- `comp.table.color_hover` 색 · 올림 — 못 잼 (raw는 정지 상태 계산 스타일만 담음 — 행 올림 상태 스타일 · 캡처 없음)
- `comp.modal.width` 폭 (최소 / 고정) — 못 잼 (카드 폭 312는 패널 폭 안을 채운 값으로 보임 — raw에 최소 · 고정 폭 지정 근거 없음)
- `comp.empty.width` 폭 (최소 / 고정) — 못 잼 (빈 상태 폭 776은 본문 폭을 그대로 채움 — raw에 최소 · 고정 폭 지정 근거 없음)
→ gaps.md와 같은 목록 (스크립트가 `못 잼` · `〔추정〕` 칸에서 뽑는다)
