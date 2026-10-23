"""같은 서비스의 바로 이전 run과 블록을 비교해 달라진 항목만 → corrections.md (AC-5). 이전 run이 없으면 None."""
from lib import RUNS, blocks, load_run, report, src_label


def value_of(b):
    if b is None:
        return "못 잼 (블록 없음)"
    if b.get("src") == "none":
        return f"못 잼 ({b.get('reason', '')})"
    if b.get("src") == "na":
        return f"해당 없음 ({b.get('reason', '')})"
    return str(b.get("value"))


def previous(d):
    run = load_run(d)
    prev = []
    for p in RUNS.iterdir():
        if p == d or not (p / "run.yaml").exists():
            continue
        o = load_run(p)
        if o["service"] == run["service"] and (o["date"], o["run"]) < (run["date"], run["run"]) and (p / "blocks" / "measurer.yaml").exists():
            prev.append(((o["date"], o["run"]), p))
    return max(prev)[1] if prev else None


def render(d):
    p = previous(d)
    if p is None:
        return None
    new, old = blocks(d)["values"], blocks(p)["values"]
    rows = []
    for iid in sorted(set(new) | set(old)):
        a, b = old.get(iid), new.get(iid)
        if value_of(a) != value_of(b) or (a or {}).get("src") != (b or {}).get("src"):
            rows.append((f"`{iid}`", value_of(a), src_label(a) if a else "", value_of(b), src_label(b) if b else "", p.name))
    return (f"# {d.name} — 정정 목록\n\n> 이전 run `{p.name}`과 달라진 항목만.\n\n정정 {len(rows)}\n\n"
            + report(rows, ("항목", "이전 값", "이전 출처", "새 값", "새 출처", "이전 run")) + "\n")
