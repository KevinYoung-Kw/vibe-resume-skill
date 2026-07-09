(function () {
  const params = new URLSearchParams(window.location.search);
  const capture = params.get("capture") === "1";
  const requestedProgress = Number(params.get("p"));
  const duration = Number(document.body.dataset.duration || 8);
  const demo = document.body.dataset.demo;

  function clamp(value, min = 0, max = 1) {
    return Math.max(min, Math.min(max, value));
  }

  function smooth(start, end, value) {
    const t = clamp((value - start) / (end - start));
    return t * t * (3 - 2 * t);
  }

  function easeOut(value) {
    return 1 - Math.pow(1 - clamp(value), 3);
  }

  function setStyle(selector, styles) {
    const node = document.querySelector(selector);
    if (!node) return;
    Object.assign(node.style, styles);
  }

  function setStyleAll(selector, callback) {
    document.querySelectorAll(selector).forEach((node, index) => {
      Object.assign(node.style, callback(node, index));
    });
  }

  function reveal(selector, p, start, end, y = 12) {
    const t = smooth(start, end, p);
    setStyle(selector, {
      opacity: String(t),
      transform: `translateY(${(1 - t) * y}px)`,
    });
  }

  function revealAll(selector, p, start, gap = 0.055, endOffset = 0.1, y = 10) {
    setStyleAll(selector, (_node, index) => {
      const t = smooth(start + index * gap, start + index * gap + endOffset, p);
      return {
        opacity: String(t),
        transform: `translateY(${(1 - t) * y}px)`,
      };
    });
  }

  function revealSequence(selector, p, starts, endOffset = 0.06, y = 8) {
    setStyleAll(selector, (_node, index) => {
      const start = starts[index] ?? starts[starts.length - 1];
      const t = smooth(start, start + endOffset, p);
      return {
        opacity: String(t),
        transform: `translateY(${(1 - t) * y}px)`,
      };
    });
  }

  function revealShot(selector, p, start, end, options = {}) {
    const raw = smooth(start, end, p);
    const t = easeOut(raw);
    const y = options.y ?? 16;
    const scale = options.scale ?? 0.96;
    const revealMask = options.mask ?? false;
    const styles = {
      opacity: String(t),
      transform: `translateY(${(1 - t) * y}px) scale(${scale + t * (1 - scale)})`,
    };
    if (revealMask) {
      styles.clipPath = `inset(0 0 ${(1 - t) * 100}% 0)`;
    }
    setStyle(selector, styles);
  }

  function scan(selector, p, start, end, distance = 520) {
    const t = smooth(start, end, p);
    const opacity = Math.sin(t * Math.PI);
    setStyle(selector, {
      opacity: String(opacity * 0.92),
      transform: `translateY(${(-110 + t * distance).toFixed(1)}%)`,
    });
  }

  function lineWidths(p) {
    setStyleAll(".resume-meta .line", (_node, index) => {
      const t = smooth(0.24 + index * 0.035, 0.38 + index * 0.035, p);
      const widths = [1, 0.72, 0.46];
      return { transform: `scaleX(${t * widths[index]})` };
    });
    setStyleAll(".resume-section .line", (_node, index) => {
      const t = smooth(0.38 + index * 0.018, 0.58 + index * 0.018, p);
      const width = [1, 0.84, 0.92, 0.56, 0.76, 0.48, 0.88, 0.68, 0.52][index % 9];
      return { transform: `scaleX(${t * width})` };
    });
  }

  function hero(p) {
    const messageStarts = [0.03, 0.14, 0.51, 0.64];
    revealSequence(".message", p, messageStarts, 0.09, 12);

    reveal(".intent-chip", p, 0.12, 0.22, 8);
    const flow = smooth(0.12, 0.48, p);
    setStyle(".flow-path", { opacity: String(flow * 0.8) });
    setStyle(".flow-dot", {
      transform: `translate(${flow * 390}px, ${smooth(0.34, 0.48, p) * 204}px)`,
      opacity: String(1 - smooth(0.52, 0.62, p)),
    });

    const card = smooth(0.20, 0.34, p);
    setStyle(".snippet-card", {
      opacity: String(card),
      transform: `translateY(${(1 - card) * 14}px) scale(${0.98 + card * 0.02})`,
    });

    const lineStarts = [0.22, 0.30, 0.38, 0.46, 0.52];
    revealSequence(".code-line", p, lineStarts, 0.055, 8);
    reveal(".code-cursor", p, 0.14, 0.20, 0);
    const cursorY = 17 + smooth(0.22, 0.54, p) * 84 + smooth(0.60, 0.82, p) * 37;
    setStyle(".code-cursor", {
      top: `${cursorY.toFixed(1)}px`,
      opacity: String((1 - smooth(0.88, 0.96, p)) * smooth(0.14, 0.20, p)),
    });

    revealShot(".hero-shot", p, 0.16, 0.49, { y: 16, scale: 0.96, mask: true });
    scan(".hero-shot .scan-line", p, 0.28, 0.54, 390);

    const swap = smooth(0.62, 0.78, p);
    setStyleAll(".old-code", () => ({
      opacity: String(1 - swap),
      transform: `translateX(${-10 * swap}px)`,
    }));
    setStyleAll(".new-code", () => ({
      opacity: String(swap),
      transform: `translateX(${(1 - swap) * 12}px)`,
    }));
    const replacePulse = smooth(0.58, 0.66, p) * (1 - smooth(0.84, 0.94, p));
    document.documentElement.style.setProperty("--replace-bg", String(replacePulse * 0.22));
    document.documentElement.style.setProperty("--replace-border", String(replacePulse));
    const update = smooth(0.68, 0.84, p);
    setStyle(".resume-update-region", {
      opacity: String(update),
      transform: `translateY(${(1 - update) * 5}px)`,
    });

    revealAll(".status-row", p, 0.72, 0.045, 0.085, 8);
    const glow = smooth(0.70, 0.84, p) * (1 - smooth(0.92, 0.98, p));
    setStyle(".template-glow", { opacity: String(glow * 0.95) });
    const badge = smooth(0.84, 0.94, p);
    setStyle(".pdf-badge", {
      opacity: String(badge),
      transform: `translateY(${(1 - badge) * 18}px) scale(${0.96 + badge * 0.04})`,
    });
  }

  function templates(p) {
    const cards = document.querySelectorAll(".preview-card");
    cards.forEach((node, index) => {
      const center = 0.18 + index * 0.18;
      const focus = Math.max(0, 1 - Math.abs(p - center) / 0.24);
      const active = smooth(0, 1, focus);
      const intro = smooth(0.06 + index * 0.04, 0.2 + index * 0.04, p);
      const x = (index - 1.5) * 92 + active * 24;
      const y = Math.abs(index - 1.5) * 14 - active * 12;
      const rotate = (index - 1.5) * -4 + active * 4;
      const scale = 0.78 + intro * 0.08 + active * 0.17;
      node.style.opacity = String(Math.max(intro * 0.76, active * 0.98));
      node.style.transform = `translate(${x}px, ${y}px) rotate(${rotate}deg) scale(${scale})`;
      node.style.zIndex = String(10 + Math.round(active * 20));
      node.style.borderColor = active > 0.56 ? "#2563eb" : "#dfe7f1";
    });
    revealAll(".semantic-row", p, 0.18, 0.08, 0.13, 0);
  }

  function qa(p) {
    revealShot(".qa-shot", p, 0.05, 0.24, { y: 12, scale: 0.96 });
    scan(".qa-shot .scan-line", p, 0.20, 0.62, 430);
    reveal(".guide-a4", p, 0.36, 0.50, 0);
    reveal(".guide-bottom", p, 0.46, 0.60, 0);
    revealAll(".qa-item", p, 0.42, 0.065, 0.13, 10);
    const seal = smooth(0.84, 0.96, p);
    setStyle(".final-seal", {
      opacity: String(seal),
      transform: `translateY(${(1 - seal) * 12}px)`,
    });
  }

  const renderers = { hero, templates, qa };

  function render(progress) {
    const p = clamp(progress);
    document.documentElement.style.setProperty("--p", String(p));
    const loopFade = 1 - smooth(0.94, 1, p);
    setStyle(".layout", { opacity: String(loopFade) });
    setStyle(".footer-note", { opacity: String(loopFade) });
    renderers[demo]?.(p);
  }

  if (capture && Number.isFinite(requestedProgress)) {
    render(requestedProgress);
  } else {
    const start = performance.now();
    function tick(now) {
      const elapsed = ((now - start) / 1000) % duration;
      render(elapsed / duration);
      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }
})();
