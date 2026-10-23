# 레퍼런스 실측 하네스

## 0. 이 저장소가 하는 일
잘 만든 서비스의 화면 규격을 매번 같은 목차 · 같은 출처 표기로 재서, 실측 문서 · 토큰 · 견본 페이지 · 우리 값 대응표 · 빈 칸 목록으로 남긴다.
디자인 하네스가 아니라 **리서치 하네스**다. 너(메인 세션)는 **진행 역할**만 맡는다.

기준 문서 — 판단이 필요하면 여기서 찾는다. 이 파일에 내용을 다시 적지 않는다.
| 무엇 | 어디 |
|---|---|
| 목적 · 범위 · 조건 | `docs/prd.md` |
| 사용자 이야기 · 판정 | `docs/story-service.md`, `docs/story-work.md` |
| 단계 · 상태 · 돌아갈 길 | `docs/pipeline.md` |
| 산출물 · 블록 형식 | `docs/outputs.md` |
| 실측 문서 목차 · 항목 ID | `docs/measure-template.md` |
| 우리 값 (공개용 예시) | `docs/our-tokens.example.json` |
| 규칙 · 수치 · 횟수 · 대응표 | `rules.yaml` |

## 1. 절대 규칙
1. **`runs/**` · `refs/**`는 스크립트만 쓴다.** 너는 Write · Edit로 쓰지 않는다 (훅이 막는다). Bash 리다이렉션(`>`, `tee` 등)으로도 쓰지 않는다
2. **에이전트 블록은 받은 그대로 stdin으로 스크립트에 넘긴다.** 고치거나 줄이거나 요약하지 않는다. 블록이 틀렸으면 스크립트가 거부하게 둔다
3. **수치 · 규칙은 `rules.yaml`에서만 읽는다.** 지침이나 보고에 숫자를 새로 정하지 않는다
4. 판정은 스크립트가 한다. 차단 · 경고 · 통과를 네가 판단해서 바꾸지 않는다
5. 회사 이름 · 사내 값 · 캡처 이미지 · 남의 서비스 문구 원문을 커밋하지 않는다 (pre-commit 훅이 막는다)
6. 값은 measurer만, 판단은 judge만 만든다. 네가 값이나 판단을 채우지 않는다
7. **`refs/`는 읽지 않는다** (너도 에이전트도). R8 하네스 검증(1회)에서 `scripts/verify_refs.py`만 읽는다. 훅이 막고 시도는 C18로 세어진다. 평소 run에는 refs가 없다고 본다

## 2. 진행 순서
시작은 `/measure <서비스>`. 단계 정의는 `docs/pipeline.md`, 명령은 아래 한 줄씩.

| 단계 | 명령 · 할 일 |
|---|---|
| S0 | `python scripts/new_run.py <서비스>` |
| S1 | 사람 차례 → 멈춤. 사람이 끝났다고 하면 `python scripts/ingest.py <run>` |
| S2 | measurer 에이전트 호출 → 블록을 `python scripts/write_run.py <run> --from measurer`에 stdin으로 → `python scripts/pixel.py <run>` → `python scripts/write_run.py <run> --render` → judge 에이전트 호출 → 블록을 `python scripts/write_run.py <run> --from judge`에 stdin으로 |
| S3 | `python scripts/check.py <run>` |
| S4 | 사람 차례 → 멈춤. 사람이 승인했다고 하면 `python scripts/finalize.py <run>` |

- 이어서 할 때는 `runs/<run>/run.yaml`의 `status`를 보고 그 단계부터 한다
- S3 차단 → 실패한 규칙 ID · 항목 ID만 measurer에게 넘겨 그 항목 블록만 다시 받는다
- 블록을 스크립트가 읽지 못하면 오류 메시지와 함께 같은 에이전트에게 다시 요청한다
- 재시도 횟수는 스크립트가 `run.yaml`에 세고, 한도는 `rules.yaml`의 `retry`

## 3. 멈추는 곳
- **사람 차례:** S1 수집(input.yaml · 스니펫 실행 · 캡처), S4 승인(approval.md)
- **한도 초과:** 스크립트가 재시도 한도를 넘었다고 하면 멈추고, 남은 차단 목록을 보여 준다
- 스크립트가 0이 아닌 코드로 끝났는데 이유를 알 수 없으면 멈추고 출력을 그대로 보여 준다

## 4. 보고 형식
사람에게는 **스크립트가 낸 숫자만** 보여 준다. 평가하는 말(「대체로 잘 됐다」, 「거의 다 됐다」 등)은 쓰지 않는다.

```
| run | 상태 | 차단 | 경고 | 재시도 (점검→정리) |
|---|---|---|---|---|
| <run> | <status> | n | n | n / 한도 |

| 규칙 ID | 개수 |
|---|---|
| C3 | n |

다음: <다음에 할 일 한 줄>
```

## 5. 하지 않는 것
`docs/prd.md` §7 범위 밖. 거기 없는 일을 요청받으면 범위 밖인지 먼저 묻는다.
