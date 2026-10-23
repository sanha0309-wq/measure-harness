// 레퍼런스 실측 하네스 — DOM 스니펫 원본.
// 이 파일을 직접 쓰지 않는다. `python scripts/build_snippet.py`가 rules.yaml 값을 넣어 snippet/measure.js를 만든다.
(function () {
  const CONFIG = /*CONFIG*/;

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

  window.measure = function (screen) {
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
