// 레퍼런스 실측 하네스 — DOM 스니펫 원본.
// 생성된 파일 — 고치지 않는다. 원본은 snippet/measure.src.js, 값은 rules.yaml.
(function () {
  const CONFIG = {"maxElements": 2000, "textPrefixChars": 20, "props": ["font-family", "font-size", "line-height", "font-weight", "letter-spacing", "color", "background-color", "border-color", "border-width", "border-radius", "box-shadow", "padding", "margin", "gap", "width", "height", "max-width", "grid-template-columns", "opacity"], "hash": "0c280d889ef2"};

  function pathOf(el) {
    const parts = [];
    while (el && el.nodeType === 1 && el !== document.documentElement) {
      let i = 1;
      let s = el;
      while ((s = s.previousElementSibling)) if (s.tagName === el.tagName) i++;
      parts.unshift(el.tagName.toLowerCase() + ":nth-of-type(" + i + ")");
      el = el.parentElement;
    }
    return parts.join(">");
  }

  function visible(el, cs, rect) {
    if (cs.display === "none" || cs.visibility === "hidden") return false;
    if (rect.width <= 0 || rect.height <= 0) return false;
    return rect.bottom > 0 && rect.right > 0 && rect.top < innerHeight && rect.left < innerWidth;
  }

  // opts.returnJson — copy() 대신 JSON 문자열을 돌려준다 (scripts/collect.py). 재는 로직은 같다
  window.measure = function (screen, opts) {
    if (!screen) throw new Error("measure('<화면 이름>')처럼 화면 이름을 넣어 주세요");
    const elements = [];
    let seen = 0;
    for (const el of document.body.querySelectorAll("*")) {
      const cs = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      if (!visible(el, cs, rect)) continue;
      seen++;
      if (elements.length >= CONFIG.maxElements) continue;
      const styles = {};
      for (const p of CONFIG.props) styles[p] = cs.getPropertyValue(p);
      const text = (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, CONFIG.textPrefixChars);
      elements.push({
        path: pathOf(el),
        tag: el.tagName.toLowerCase(),
        text: text,
        rect: [rect.x, rect.y, rect.width, rect.height].map((v) => Math.round(v * 100) / 100),
        styles: styles,
      });
    }
    const out = {
      snippet: "measure-harness",
      configHash: CONFIG.hash,
      screen: screen,
      url: location.href,
      viewport: { width: innerWidth, height: innerHeight },
      dpr: devicePixelRatio,
      measuredAt: new Date().toISOString(),
      visibleCount: seen,
      truncated: seen > elements.length,
      elements: elements,
    };
    const json = JSON.stringify(out);
    if (opts && opts.returnJson) return json;
    if (typeof copy === "function") {
      copy(json);
      console.log("복사됨 → raw/dom-" + screen + ".json에 붙여 넣기 (요소 " + elements.length + "/" + seen + ")");
    } else {
      console.log(json);
    }
    return out.elements.length;
  };
  console.log("준비됨 — measure('<화면 이름>')");
})();
