"""approval.md — 사람 승인 파일 하나. 양식 만들기와 확인 (G-승인)."""
import re

from lib import load_json, read_text, rules, sha256, write_text


def hashes(d) -> dict:
    return {n: sha256(d / n) for n in rules()["gates"]["approval"]["hashed"] if (d / n).exists()}


def render(d) -> str:
    g = rules()["gates"]["approval"]
    rep = load_json(d / "check-report.json")
    counts = " · ".join(f"{k} {v}" for k, v in sorted(rep["counts"].items())) or "없음"
    lines = [f"# 승인 — {d.name}", "",
             "> 사람이 쓰는 파일. 확인 항목을 하나씩 보고 `[x]`로 바꾸고, 승인자 · 날짜를 적는다.",
             "> 아래 해시는 스크립트가 쓴다. 승인한 뒤 산출물이 바뀌면 해시가 달라져 승인이 무효가 된다.", "",
             "## 확인 항목"]
    lines += [f"- [ ] {c}" for c in g["checklist"]]
    lines += ["", "## 점검 결과", f"차단 {rep['block']} · 경고 {rep['warn']} ({counts})", ""]
    w1 = [h for h in rep["hits"] if h["rule"] == "W1"]
    if w1:
        lines.append("W1 문구 원문 의심:")
        lines += [f"- `{h['item']}` {h['detail']}" for h in w1]
        lines.append("")
    lines += ["## 해시 (고치지 않는다)"] + [f"- {n}: {h}" for n, h in hashes(d).items()]
    lines += ["", "승인자: ", "날짜: ", ""]
    return "\n".join(lines)


def written_hashes(text: str) -> dict:
    return dict(re.findall(r"^- ([\w.\-]+): ([0-9a-f]{64})$", text, re.M))


def ensure(d) -> None:
    """양식이 없거나 산출물이 바뀌었으면 새로 만든다 (이전 체크는 무효)."""
    p = d / "approval.md"
    if not p.exists() or written_hashes(read_text(p)) != hashes(d):
        write_text(p, render(d))


def verify(d) -> list[str]:
    p = d / "approval.md"
    if not p.exists():
        return ["approval.md 없음"]
    t = read_text(p)
    errs = []
    g = rules()["gates"]["approval"]
    for c in g["checklist"]:
        if f"- [x] {c}" not in t and f"- [X] {c}" not in t:
            errs.append(f"확인 안 됨: {c}")
    if not re.search(r"^승인자:\s*\S", t, re.M):
        errs.append("승인자 없음")
    if not re.search(r"^날짜:\s*\S", t, re.M):
        errs.append("날짜 없음")
    if written_hashes(t) != hashes(d):
        errs.append("해시 다름 — 승인 뒤 산출물이 바뀜. check.py를 다시 돌리고 다시 승인")
    return errs
