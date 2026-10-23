"""tokens.json ↔ docs/our-tokens.example.json → compare.md. 허용 오차(rules.yaml tolerance) 밖의 차이만 행이 된다.

판단은 judge 블록. 없으면 rules.yaml judge.default (W4).
"""
from lib import DOCS, blocks, load_json, load_run, parse_color, report, rules, src_label
from tokens import leaves


def flat_ours() -> dict:
    tree = load_json(DOCS / "our-tokens.example.json")
    out = {}

    def walk(t, prefix):
        for k, v in t.items():
            if k.startswith("_"):
                continue
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict) and not key.startswith("type."):
                walk(v, key)
            else:
                out[key] = v

    walk(tree, "")
    return out


def tol_for(t: dict, r: dict):
    tl = r["tolerance"]
    if t["src"] == "dom":
        return tl["dom"]["length"], tl["dom"]["color"]
    if t["src"] == "pixel":
        return t.get("tol") or 0, tl["pixel"]["color_channel"]
    return None, None  # est — 항상 행


def same_scalar(ours, theirs, t, r) -> bool:
    ln, ch = tol_for(t, r)
    if ln is None:
        return False
    if isinstance(ours, str) and ours.startswith("#") or isinstance(theirs, str) and str(theirs)[:1] in "#r":
        a, b = parse_color(str(ours)), parse_color(str(theirs))
        if not a or not b:
            return str(ours).lower() == str(theirs).lower()
        return all(abs(x - y) <= ch for x, y in zip(a[:3], b[:3])) and abs(a[3] - b[3]) < 0.005
    if isinstance(ours, (int, float)) and isinstance(theirs, (int, float)):
        return abs(ours - theirs) <= ln
    if isinstance(ours, str) and isinstance(theirs, str):  # 글꼴: 첫 글꼴 이름끼리
        first = lambda s: s.split(",")[0].strip().strip("\"'").lower()
        return first(ours) == first(theirs)
    return False


def diff_text(ours, theirs) -> str:
    if isinstance(ours, (int, float)) and isinstance(theirs, (int, float)):
        d = theirs - ours
        return f"{d:+g}"
    return "다름"


def rows(d) -> list[dict]:
    r = rules()
    ours = flat_ours()
    theirs_tree = load_json(d / "tokens.json")
    judg = blocks(d)["judgments"]
    out = []

    def add(token, o, th, t, diff):
        j = judg.get(token)
        memo = []
        if j and j.get("why"):
            memo.append(j["why"])
        if j and j.get("propose") is not None:
            memo.append(f"제안 {j['propose']} 〔임의〕")
        out.append({"token": token, "ours": o, "theirs": th, "src": src_label(t), "src_kind": t["src"], "diff": diff,
                    "judge": j["judge"] if j else r["judge"]["default"], "default": j is None, "memo": " · ".join(memo)})

    for key, t in leaves(theirs_tree):
        if key not in ours:
            continue
        o, th = ours[key], t["value"]
        if isinstance(o, dict) and isinstance(th, dict):
            for f, ov in o.items():
                if f in th and not same_scalar(ov, th[f], t, r):
                    add(f"{key}.{f}", ov, th[f], t, diff_text(ov, th[f]))
        elif isinstance(o, list) and isinstance(th, list):
            ln, _ = tol_for(t, r)
            near = lambda x, pool: ln is not None and any(isinstance(y, (int, float)) and abs(x - y) <= ln for y in pool)
            extra = [x for x in th if not near(x, o)] if all(isinstance(x, (int, float)) for x in th) else th
            missing = [x for x in o if not near(x, th)]
            if extra or missing or ln is None:
                add(key, " / ".join(map(str, o)), " / ".join(map(str, th)), t,
                    f"더 있음 {extra or '—'} · 없음 {missing or '—'}")
        elif not same_scalar(o, th, t, r):
            add(key, o, th, t, diff_text(o, th))
    return out


def render(d) -> str:
    rs = rows(d)
    run = load_run(d)
    counts = {k: sum(1 for x in rs if x["judge"] == k) for k in rules()["judge"]["allowed"]}
    head = " · ".join(f"{k} {v}" for k, v in counts.items())
    table = report([(f"`{x['token']}`", x["ours"], x["theirs"], x["src"], x["diff"], x["judge"], x["memo"]) for x in rs],
                   ("토큰", "우리 값", "그 서비스 값", "출처", "차이", "판단", "메모"))
    return (f"# {run['run']} — 우리 값 대응표\n\n"
            f"> 우리 값: `docs/our-tokens.example.json` (공개용 예시). 허용 오차(`rules.yaml` tolerance) 밖의 차이만 행이 된다.\n\n"
            f"행 {len(rs)} · {head}\n\n{table}\n")
