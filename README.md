# 레퍼런스 실측 하네스

잘 만든 서비스의 화면 규격(배치 · 글자 · 색 · 간격 · 반경 · 컴포넌트)을 **매번 같은 목차, 같은 출처 표기로** 재서
실측 문서 · 토큰 · 견본 페이지 · 우리 값 대응표 · 빈 칸 목록으로 남기는 [Claude Code](https://claude.com/claude-code) 하네스입니다.
디자인을 만드는 하네스가 아니라 **리서치 하네스**입니다.

- 판정은 스크립트가 합니다. 규칙과 수치는 `rules.yaml` 한 곳에 있습니다
- 에이전트(measurer · judge)는 파일을 쓰지 않고 YAML 블록만 돌려줍니다. 파일은 `scripts/`가 씁니다
- 모든 값에 출처가 붙습니다: `〔DOM〕` · `〔픽셀 · 배율 1.5 · ±1〕` · `〔추정 · 근거〕`. 못 잰 칸은 `못 잼 (이유)`로 남습니다
- 사람은 입력(콘솔 스니펫 실행 · 캡처)과 승인(`approval.md`)만 합니다

## 설치

필요한 것: Python 3.10 이상, Claude Code, 크롬 계열 브라우저

```bash
pip install -r requirements.txt        # PyYAML, Pillow
python scripts/build_snippet.py        # rules.yaml 값으로 snippet/measure.js 생성
git init && python scripts/install_hooks.py   # 저장소를 받은 뒤 한 번 — 커밋 금지 훅 설치
```

`install_hooks.py`는 이미지 · `refs/` · 시연 run 밖의 run이 커밋되지 않게 막습니다 (.gitignore는 `git add -f`로 뚫리기 때문).

### Windows · 한글
모든 스크립트는 시작할 때 stdin · stdout · stderr를 UTF-8로 고정합니다 (`scripts/lib.py`의 `utf8_io`, 훅은 `guard_write.py` 안에서 직접).
`PYTHONUTF8` · `PYTHONIOENCODING`을 따로 설정하지 않아도 됩니다.
- 확인한 환경: Windows 11, 시스템 인코딩 cp949, Git Bash
- 확인한 것: 두 환경 변수를 모두 지운 상태에서 한글 블록을 stdin으로 `write_run.py`에 넘기는 S0→S3 한 바퀴(차단 0), `python tests/run_tests.py`(시험 22 · 통과 22)

## 먼저 demo-sample로 시험해 보기

`fixtures/sample.html`은 저장소 안의 **가상 견본 페이지**입니다. 실제 서비스가 아니고, 값의 정답이
`fixtures/sample.expected.yaml`에 있습니다. **평소 정확도 확인은 이 fixture로 합니다.**

### 자동 시험 (사람 손 없음)
```bash
python tests/run_tests.py
```
헤드리스 크롬으로 fixture에 스니펫을 돌려 진짜 raw를 만든 뒤, 정상 run이 차단 0인지 확인합니다.
그다음 한 군데씩 망가뜨려 그 규칙 ID만 걸리는지 셉니다. 바뀐 산출물 · 재시도 한도 · 승인 해시도 함께 봅니다.
임시 폴더에서 돌아서 `runs/`를 건드리지 않습니다.

### 직접 한 바퀴 (사람 경로)
1. Claude Code에서 `/measure demo-sample`
2. 아래 「콘솔 스니펫 붙여 넣기」대로 `fixtures/sample.html`을 열어 `measure('home')`을 실행하고, 결과를 `runs/demo-sample-<날짜>/raw/dom-home.json`에 붙여 넣습니다
3. Claude에게 「수집 끝」이라고 말하면 나머지(정리 → 점검)를 진행하고 숫자 표로 보고합니다
4. `approval.md`를 확인 · 서명하고 「승인했다」고 말하면 완료됩니다

공개되는 run은 `runs/demo-sample-*` 뿐입니다. 다른 run은 `.gitignore` 대상입니다.

## 실제 서비스 재기

```
/measure <서비스>        예: /measure some-service
```
- 서비스 이름은 폴더 이름이 됩니다 (영문 소문자 · 숫자 · `-`). 같은 날 다시 재면 `-2`, `-3`이 붙고 덮어쓰지 않습니다
- 진행 중인 run이 있으면 그 상태부터 이어서 합니다

### 사람이 할 일 (S1 수집)
`runs/<run>/input.yaml`을 채웁니다:
```yaml
service_aliases: [서비스 한글 이름, Service]   # 값 칸에 서비스 이름이 들어가면 차단 (C14)
screens:
  - { name: home, method: dom }
  - { name: home-2, method: dom }               # 스크롤 아래쪽
captures:                                        # 앱 · 로그인 화면 등 DOM으로 못 재는 화면
  - { name: home-modal, file: home-modal.png, scale: 1.5, screen: home }
```
캡처 파일은 `raw/captures/`에 둡니다. 캡처는 **어떤 경우에도 커밋되지 않습니다.** 배율은 사람이 적습니다.

### 콘솔 스니펫 붙여 넣기
1. 크롬에서 잴 페이지를 엽니다. 로그인이 필요하면 사람이 먼저 로그인해 둡니다 (하네스는 로그인하지 않습니다)
2. 개발자 도구(F12) → 기기 툴바(Ctrl+Shift+M) → 「반응형」에서 폭을 **1440**으로 맞춥니다. 화면 폭이 1440이 아니면 수집 단계에서 차단됩니다 (I2)
3. Console 탭에 `snippet/measure.js` 전체를 붙여 넣고 Enter. 처음이면 크롬이 붙여 넣기를 막는데, 안내대로 `allow pasting`을 입력한 뒤 다시 붙여 넣습니다
4. `measure('home')` 실행 → 결과 JSON이 클립보드에 복사됩니다
5. `runs/<run>/raw/dom-home.json` 파일을 만들어 붙여 넣습니다. Windows에서는 저장소 폴더의 PowerShell에서 클립보드를 그대로 BOM 없는 UTF-8로 저장할 수 있습니다:
   ```powershell
   [IO.File]::WriteAllText("$PWD\runs\<run>\raw\dom-home.json", (Get-Clipboard -Raw), (New-Object Text.UTF8Encoding $false))
   ```
   Windows PowerShell 5.1의 `Set-Content -Encoding utf8` · `Out-File`과 메모장은 BOM을 붙입니다. 수집 단계는 BOM이 있어도 읽지만, 위 명령을 쓰면 BOM이 붙지 않습니다. 위 명령은 터미널에 붙여 넣어 실행하는 것이고, JSON 파일 안에 붙여 넣는 것이 아닙니다
6. 아래쪽을 재려면 스크롤한 뒤 `measure('home-2')`처럼 다른 화면 이름으로 다시 실행합니다 (스니펫은 화면에 보이는 요소만 담습니다)

`snippet/measure.js`는 생성된 파일입니다. 고치려면 `snippet/measure.src.js` 또는 `rules.yaml`을 고치고 `build_snippet.py`를 다시 돌립니다.
(rules.yaml과 다른 설정으로 만든 스니펫의 결과는 수집 단계에서 차단됩니다 — I1)

## 산출물 (`runs/<서비스>-<날짜>/`)
| 파일 | 내용 |
|---|---|
| `measure.md` | 실측 문서. 목차는 `docs/measure-template.md` 그대로 (스크립트가 찍음). 값마다 출처 |
| `tokens.json` | 색 · 글자 · 간격 · 반경 · 그림자 · 크기 토큰. 키 구조는 `docs/our-tokens.example.json`과 같음 |
| `tokens.html` | 토큰 견본 페이지. tokens.json에서 스크립트로 생성 — 견본 수 = 토큰 수, 〔추정〕은 점선 |
| `compare.md` | 우리 값과 다른 항목만 + 판단(채택 후보 · 유지 · 보류) |
| `gaps.md` | 못 잼 · 추정 목록 (measure.md와 같은 항목) |
| `corrections.md` | 같은 서비스의 이전 run과 달라진 값만 (이전 run이 있을 때) |
| `check-report.json` | 점검 결과 — 차단 · 경고 개수, 규칙 ID별 개수 |
| `approval.md` | 사람 승인 파일. 산출물 해시가 묶여 있어 승인 뒤 바뀌면 무효 |

상태: 수집 중 → 정리 중 → 점검 중 → 승인 대기 → 완료. **완료 조건은 점검 차단 0 + 승인**입니다.

「우리 값」은 `docs/our-tokens.example.json`의 **공개용 예시 값**입니다. 자기 디자인 시스템과 비교하려면 이 파일을
로컬에서 바꾸되, 실제 사내 값은 공개 저장소에 커밋하지 마세요.

## refs 없이 돌아갑니다
`refs/`(손으로 잰 비교 기준 문서)는 **없어도 됩니다.** 평소 run의 어떤 스크립트도 refs를 읽지 않습니다.
- refs는 하네스를 만든 뒤 한 번 하는 **하네스 검증(R8)** 에서만 `scripts/verify_refs.py`가 읽습니다 (`docs/prd.md` §9-2)
- Claude(메인 세션 · 에이전트)는 refs를 읽지 않습니다. 훅이 막고, 시도는 점검에서 차단(C18)으로 셉니다
- `refs/`는 `.gitignore` · pre-commit 훅으로 공개되지 않습니다

## 저장소 구조
```
CLAUDE.md                  메인 세션 지침 (진행 역할)
rules.yaml                 규칙 · 수치 · 횟수 · 토큰 대응 — 전부 여기
docs/                      기준 문서 (PRD · 스토리 · 파이프라인 · 산출물 형식 · 실측 템플릿 · 우리 예시 값)
.claude/agents/            measurer · judge (Read · Glob · Grep만)
.claude/commands/measure.md  /measure
.claude/settings.json      훅 — runs/ · refs/ 쓰기 금지, refs/ 읽기 금지
scripts/                   new_run · ingest · write_run · pixel · check · finalize · build_snippet · precommit …
snippet/                   콘솔 스니펫 (measure.src.js → measure.js)
fixtures/                  가상 견본 페이지 + 정답
tests/                     자동 시험
```

## 범위 밖
클론 화면 만들기, 컴포넌트 HTML 재현, 대신 로그인, 다크 모드, 공식 디자인 시스템 문서 긁어오기, 사람이 지정하는 정정,
반응형 여러 폭, 움직임(motion), 서비스 여러 개 통합 비교, 접근성 점검 — `docs/prd.md` §7
