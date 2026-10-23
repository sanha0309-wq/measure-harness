# 〈서비스〉 실측 — 〈날짜〉

> 모든 값 뒤에 출처: 〔DOM〕 · 〔픽셀 · 배율 n · ±1〕 · 〔추정 · 근거〕
> 〔임의〕는 이 문서에 올 수 없다 (있으면 차단). 내가 정한 값은 compare.md의 채택 후보로만 둔다
> 못 잰 칸은 지우지 않는다 → `못 잼 (이유)` · 그 화면에 해당 요소가 없으면 → `해당 없음 (이유)`
> `<!-- id: … -->`는 항목 ID. 스크립트가 이 ID로 목차를 찍고 센다. 지우거나 바꾸지 않는다

## 0. 측정 정보
> 이 절은 run.yaml · input.yaml · raw에서 스크립트가 채운다

| 항목 | 값 |
|---|---|
| 측정 방법 <!-- id: meta.method --> | |
| 화면 폭 <!-- id: meta.viewport --> | |
| 캡처 배율 <!-- id: meta.scale --> | |
| 잰 화면 목록 <!-- id: meta.screens --> | |

## 1. 배치
| 항목 | 값 | 출처 |
|---|---|---|
| 전체 폭 · 칼럼 구성 <!-- id: layout.columns --> | | |
| 사이드바 폭 <!-- id: layout.sidebar --> | | |
| 본문 최대 폭 <!-- id: layout.content_max --> | | |
| 페이지 좌우 여백 <!-- id: layout.page_padding --> | | |
| 패널 폭 <!-- id: layout.panel --> | | |

## 2. 글자
| 쓰임 | 크기 / 행간 / 굵기 | 자간 | 출처 |
|---|---|---|---|
| 페이지 제목 <!-- id: type.title_page --> | | | |
| 섹션 제목 <!-- id: type.title_section --> | | | |
| 본문 <!-- id: type.body --> | | | |
| 보조 글자 <!-- id: type.caption --> | | | |
| 버튼 라벨 <!-- id: type.button --> | | | |
| 글꼴 <!-- id: type.family --> | | | |

## 3. 색
| 역할 | 값 | 출처 |
|---|---|---|
| 글자 기본 · 보조 · 비활성 <!-- id: color.text --> | | |
| 배경 · 면 · 바닥 <!-- id: color.bg --> | | |
| 선 <!-- id: color.border --> | | |
| 주요 색 <!-- id: color.primary --> | | |
| 상태 (성공 · 경고 · 오류 · 정보) <!-- id: color.status --> | | |

## 4. 간격
| 항목 | 값 | 출처 |
|---|---|---|
| 간격 단계 <!-- id: space.scale --> | | |
| 카드 안쪽 여백 <!-- id: space.card_padding --> | | |
| 카드 사이 <!-- id: space.card_gap --> | | |
| 섹션 사이 <!-- id: space.section_gap --> | | |

## 5. 반경 · 그림자
| 항목 | 값 | 출처 |
|---|---|---|
| 반경 단계 <!-- id: radius.scale --> | | |
| 버튼 · 입력 · 카드 · 모달 반경 <!-- id: radius.components --> | | |
| 그림자 <!-- id: shadow.scale --> | | |

## 6. 컴포넌트
컴포넌트마다 같은 9행. 크기가 여러 단계면 값 칸에 `32 / 40 / 48`처럼 적는다

### 6-1. 버튼
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.button.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.button.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.button.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.button.text --> | | |
| 반경 <!-- id: comp.button.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.button.color_default --> | | |
| 색 · 올림 <!-- id: comp.button.color_hover --> | | |
| 색 · 누름 <!-- id: comp.button.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.button.color_disabled --> | | |

### 6-2. 입력
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.input.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.input.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.input.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.input.text --> | | |
| 반경 <!-- id: comp.input.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.input.color_default --> | | |
| 색 · 올림 <!-- id: comp.input.color_hover --> | | |
| 색 · 누름 <!-- id: comp.input.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.input.color_disabled --> | | |

### 6-3. 탭
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.tab.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.tab.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.tab.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.tab.text --> | | |
| 반경 <!-- id: comp.tab.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.tab.color_default --> | | |
| 색 · 올림 <!-- id: comp.tab.color_hover --> | | |
| 색 · 누름 <!-- id: comp.tab.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.tab.color_disabled --> | | |

### 6-4. 배지
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.badge.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.badge.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.badge.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.badge.text --> | | |
| 반경 <!-- id: comp.badge.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.badge.color_default --> | | |
| 색 · 올림 <!-- id: comp.badge.color_hover --> | | |
| 색 · 누름 <!-- id: comp.badge.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.badge.color_disabled --> | | |

### 6-5. 표
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.table.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.table.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.table.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.table.text --> | | |
| 반경 <!-- id: comp.table.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.table.color_default --> | | |
| 색 · 올림 <!-- id: comp.table.color_hover --> | | |
| 색 · 누름 <!-- id: comp.table.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.table.color_disabled --> | | |

### 6-6. 모달 · 드로어
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.modal.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.modal.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.modal.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.modal.text --> | | |
| 반경 <!-- id: comp.modal.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.modal.color_default --> | | |
| 색 · 올림 <!-- id: comp.modal.color_hover --> | | |
| 색 · 누름 <!-- id: comp.modal.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.modal.color_disabled --> | | |

### 6-7. 빈 상태
| 항목 | 값 | 출처 |
|---|---|---|
| 높이 <!-- id: comp.empty.height --> | | |
| 폭 (최소 / 고정) <!-- id: comp.empty.width --> | | |
| 안쪽 여백 (상하 · 좌우) <!-- id: comp.empty.padding --> | | |
| 글자 (크기 / 행간 / 굵기) <!-- id: comp.empty.text --> | | |
| 반경 <!-- id: comp.empty.radius --> | | |
| 색 · 기본 (글자 / 배경 / 선) <!-- id: comp.empty.color_default --> | | |
| 색 · 올림 <!-- id: comp.empty.color_hover --> | | |
| 색 · 누름 <!-- id: comp.empty.color_pressed --> | | |
| 색 · 비활성 <!-- id: comp.empty.color_disabled --> | | |

## 7. 읽히는 규칙
값 사이에서 보이는 규칙을 문장으로 (예: 「선택된 탭만 채움, 나머지는 구분선」). 문장마다 근거 항목 ID를 단다

## 8. 못 잰 것
→ gaps.md와 같은 목록 (스크립트가 `못 잼` · `〔추정〕` 칸에서 뽑는다)
