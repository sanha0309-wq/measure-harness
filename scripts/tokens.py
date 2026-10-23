"""블록 → tokens.json. 항목 ID → 토큰 키 대응은 rules.yaml의 token_map.

토큰 하나 = {"value": …, "src": …(, scale, tol | basis)}. compare: set이면 value가 목록.
"""
import re

from lib import COLOR_RE, NUM_RE, atoms, blocks, color_hex, num, parse_color, parts, rules

TYPE_FIELDS = ["size", "lineHeight", "weight", "letterSpacing"]


def scalar(s: str):
    s = s.strip()
    if COLOR_RE.fullmatch(s):
        return color_hex(parse_color(s))
    if re.fullmatch(r"-?\d+(\.\d+)?(px)?", s):
        return num(NUM_RE.search(s).group())
    return s


def leaf(b: dict, value) -> dict:
    t = {"value": value, "src": b["src"]}
    if b["src"] == "pixel":
        t.update(scale=b.get("scale"), tol=b.get("tol"))
    if b["src"] == "est":
        t["basis"] = b.get("basis")
    return t


def put(tree: dict, key: str, val) -> None:
    *path, last = key.split(".")
    for k in path:
        tree = tree.setdefault(k, {})
    tree[last] = val


def build(d) -> dict:
    r = rules()
    vals = blocks(d)["values"]
    out, mismatch = {}, []
    for iid, m in r["token_map"].items():
        b = vals.get(iid)
        if not b or b.get("src") not in ("dom", "pixel", "est"):
            continue
        keys = m["keys"]
        if m.get("compare") == "set":
            if iid == "shadow.scale":
                v = parts(b["value"], r)
            else:
                v = sorted(set(atoms(b["value"])["nums"]))
            put(out, keys[0], leaf(b, v))
        elif iid.startswith("type.") and iid != "type.family":
            ps = [scalar(p) for p in parts(b["value"], r)]
            put(out, keys[0], leaf(b, dict(zip(TYPE_FIELDS, ps))))
        elif iid == "type.family":
            put(out, keys[0], leaf(b, str(b["value"]).strip()))
        else:
            ps = parts(b["value"], r)
            if len(ps) != len(keys):
                mismatch.append(f"{iid}: 값 {len(ps)}개 · 키 {len(keys)}개")
            for k, p in zip(keys, ps):
                put(out, k, leaf(b, scalar(p)))
    if mismatch:
        out["_mismatch"] = mismatch
    return out


def leaves(tree: dict, prefix=""):
    """(토큰 키, 토큰) 목록. _로 시작하는 키는 뺀다."""
    for k, v in tree.items():
        if k.startswith("_"):
            continue
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and "src" in v:
            yield key, v
        elif isinstance(v, dict):
            yield from leaves(v, key)


def swatch_keys(tree: dict) -> list[str]:
    """견본 하나 = 이 목록의 키 하나. 목록 값은 원소마다 key[i]."""
    out = []
    for k, t in leaves(tree):
        if isinstance(t["value"], list):
            out += [f"{k}[{i}]" for i in range(len(t["value"]))]
        else:
            out.append(k)
    return out
