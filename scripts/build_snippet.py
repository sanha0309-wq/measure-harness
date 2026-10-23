"""rules.yaml의 snippet 값으로 snippet/measure.js를 만든다 (규칙은 rules.yaml 한 곳).

configHash가 raw JSON에 실리고, ingest.py(I1)가 지금 rules.yaml과 같은지 대조한다.
"""
import json

from lib import ROOT, read_text, rules, utf8_io, write_text


def config() -> dict:
    s = rules()["snippet"]
    cfg = {"maxElements": s["max_elements"], "textPrefixChars": s["text_prefix_chars"], "props": s["props"]}
    import hashlib

    cfg["hash"] = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:12]
    return cfg


def main() -> None:
    utf8_io()
    src = read_text(ROOT / "snippet" / "measure.src.js")
    js = src.replace("/*CONFIG*/", json.dumps(config(), ensure_ascii=False))
    js = js.replace("// 이 파일을 직접 쓰지 않는다. `python scripts/build_snippet.py`가 rules.yaml 값을 넣어 snippet/measure.js를 만든다.",
                    "// 생성된 파일 — 고치지 않는다. 원본은 snippet/measure.src.js, 값은 rules.yaml.")
    write_text(ROOT / "snippet" / "measure.js", js)
    print(f"snippet/measure.js 생성 · configHash {config()['hash']}")


if __name__ == "__main__":
    main()
