"""S2 — measurer가 제안한 좌표에서 실제 픽셀을 읽어 값을 확정한다 (Pillow).

사용: python scripts/pixel.py <run>   → blocks/pixel.yaml
- color: 박스 안에서 가장 많은 색
- width / height: 박스 가운데 색에서 출발해, 같은 색(채널 ± tolerance.pixel.color_channel)이 이어지는 끝까지
  가로 · 세로로 훑는다 (박스 밖으로 sources.pixel_search_margin까지). 길이 ÷ 배율 = 값
배율은 input.yaml(사람이 적은 값), ±는 rules.yaml sources.pixel_tol.
"""
import sys
from collections import Counter

from PIL import Image

from lib import blocks, color_hex, dump_yaml, load_yaml, rules, run_dir, utf8_io


def close(a, b, ch) -> bool:
    return all(abs(x - y) <= ch for x, y in zip(a[:3], b[:3]))


def run_extent(img, start, step, limit, fill, ch) -> int:
    """start에서 step 방향으로 fill 색이 이어지는 픽셀 수 (start 제외)."""
    n, (x, y) = 0, start
    while True:
        x, y = x + step[0], y + step[1]
        if not (0 <= x < img.width and 0 <= y < img.height) or n >= limit or not close(img.getpixel((x, y)), fill, ch):
            return n
        n += 1


def measure_one(img, p: dict, scale: float, r: dict):
    x1, y1, x2, y2 = p["box"]
    ch = r["tolerance"]["pixel"]["color_channel"]
    if p["measure"] == "color":
        crop = img.crop((x1, y1, x2, y2))
        c = Counter(crop.getdata()).most_common(1)[0][0]
        return color_hex((c[0], c[1], c[2], 1.0)), None
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    fill = img.getpixel((cx, cy))
    m = r["sources"]["pixel_search_margin"]
    if p["measure"] == "width":
        left = run_extent(img, (cx, cy), (-1, 0), cx - x1 + m, fill, ch)
        right = run_extent(img, (cx, cy), (1, 0), x2 - cx + m, fill, ch)
        length = left + right + 1
    else:
        up = run_extent(img, (cx, cy), (0, -1), cy - y1 + m, fill, ch)
        down = run_extent(img, (cx, cy), (0, 1), y2 - cy + m, fill, ch)
        length = up + down + 1
    v = round(length / scale, 2)
    return (int(v) if float(v).is_integer() else v), length


def measure_all(d) -> list[dict]:
    r = rules()
    inp = load_yaml(d / "input.yaml") or {}
    caps = {c["name"]: c for c in inp.get("captures") or []}
    out = []
    for p in blocks(d)["pixels"]:
        c = caps.get(p["capture"])
        if c is None:
            out.append({"id": p["id"], "src": "none", "reason": f"input.yaml에 캡처 {p['capture']} 없음"})
            continue
        img = Image.open(d / "raw" / "captures" / c["file"]).convert("RGB")
        value, length = measure_one(img, p, float(c["scale"]), r)
        b = {"id": p["id"], "value": value, "src": "pixel", "scale": c["scale"], "tol": r["sources"]["pixel_tol"],
             "capture": p["capture"], "box": p["box"], "measure": p["measure"]}
        if length is not None:
            b["image_px"] = length
        out.append(b)
    return out


def main() -> None:
    utf8_io()
    d = run_dir(sys.argv[1])
    vals = measure_all(d)
    dump_yaml(d / "blocks" / "pixel.yaml", {"values": vals})
    print(f"픽셀 확정 {len(vals)}")


if __name__ == "__main__":
    main()
