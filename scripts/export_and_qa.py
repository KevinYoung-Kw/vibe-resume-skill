#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_FORBIDDEN_TERMS = [
    "patch",
    "commit",
    "群聊",
    "ones",
    "ONES",
    "内部链接",
]

STRICT_FINAL_FORBIDDEN_TERMS = [
    "示例候选人",
    "某 AI 应用团队",
    "某内容增长团队",
    "138-0000-0000",
    "candidate@example.com",
    "example.com",
]


def run(command: list[str]) -> tuple[int, str, str]:
    process = subprocess.run(command, capture_output=True, text=True)
    return process.returncode, process.stdout, process.stderr


def find_chrome(explicit: str | None) -> str | None:
    if explicit:
        return explicit

    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def expected_font_for(html: Path, explicit: str | None) -> str:
    if explicit is not None:
        return explicit

    manifest_path = html.parent / "template-manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            value = manifest.get("expected_font")
            if isinstance(value, str) and value.strip():
                return value.strip()
        except (OSError, json.JSONDecodeError):
            pass
    return "PingFang"


def add_check(checks: list[dict], name: str, passed: bool, evidence: str, required: bool = True) -> None:
    checks.append(
        {
            "name": name,
            "passed": bool(passed),
            "required": bool(required),
            "evidence": evidence.strip(),
        }
    )


def export_pdf(html: Path, pdf: Path, chrome: str) -> tuple[bool, str]:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf}",
        html.resolve().as_uri(),
    ]
    code, stdout, stderr = run(command)
    if code != 0:
        return False, (stderr or stdout or "Chrome export failed")
    if not pdf.exists() or pdf.stat().st_size == 0:
        return False, "Chrome returned success but did not create a non-empty PDF."
    return True, f"Created {pdf} ({pdf.stat().st_size} bytes)"


def check_pdfinfo(pdf: Path, checks: list[dict]) -> None:
    tool = shutil.which("pdfinfo")
    if not tool:
        add_check(checks, "pdfinfo available", False, "pdfinfo not found; install poppler for this check.", required=False)
        return

    code, stdout, stderr = run([tool, str(pdf)])
    if code != 0:
        add_check(checks, "pdfinfo runs", False, stderr or stdout)
        return

    pages_match = re.search(r"^Pages:\s+(\d+)", stdout, re.M)
    pages_ok = bool(pages_match and pages_match.group(1) == "1")
    add_check(checks, "one page", pages_ok, pages_match.group(0) if pages_match else stdout)

    size_match = re.search(r"^Page size:\s+(.+)$", stdout, re.M)
    size_text = size_match.group(1) if size_match else ""
    size_ok = bool(re.search(r"59[0-9]\.?\d*\s+x\s+84[0-9]\.?\d*", size_text) or "A4" in size_text)
    add_check(checks, "A4 portrait", size_ok, size_text or "Page size not found.")


def check_fonts(pdf: Path, checks: list[dict], expected_font: str) -> None:
    tool = shutil.which("pdffonts")
    if not tool:
        add_check(checks, "pdffonts available", False, "pdffonts not found; install poppler for this check.", required=False)
        return

    code, stdout, stderr = run([tool, str(pdf)])
    if code != 0:
        add_check(checks, "pdffonts runs", False, stderr or stdout)
        return

    if expected_font:
        passed = expected_font in stdout
        add_check(checks, f"expected font contains {expected_font}", passed, stdout)
    else:
        add_check(checks, "fonts listed", bool(stdout.strip()), stdout)


def check_text(pdf: Path, html: Path, checks: list[dict], forbidden_terms: list[str]) -> None:
    tool = shutil.which("pdftotext")
    text = ""
    if not tool:
        add_check(checks, "pdftotext available", False, "pdftotext not found; install poppler for this check.", required=False)
    else:
        code, stdout, stderr = run([tool, "-layout", str(pdf), "-"])
        if code == 0:
            text = stdout
            add_check(checks, "pdftotext runs", True, f"Extracted {len(stdout)} characters.")
        else:
            add_check(checks, "pdftotext runs", False, stderr or stdout)

    html_text = html.read_text(encoding="utf-8", errors="ignore")
    haystack = f"{text}\n{html_text}"
    hits = [term for term in forbidden_terms if term and term in haystack]
    add_check(
        checks,
        "forbidden terms absent",
        not hits,
        "No forbidden terms found." if not hits else "Found: " + ", ".join(sorted(set(hits))),
    )


def collect_html_layout_metrics(html: Path, chrome: str) -> tuple[dict | None, str]:
    probe = r"""
<script id="__resume_qa_probe">
(() => {
  const selectors = '[data-resume-section],[data-resume-entry],[data-resume-body]';
  const numericWeight = value => {
    if (value === 'normal') return 400;
    if (value === 'bold') return 700;
    const parsed = Number.parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 400;
  };
  const visible = element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' &&
      Number.parseFloat(style.opacity || '1') > 0 && rect.width > 0 && rect.height > 0 &&
      element.textContent.trim().length > 0;
  };
  const describe = element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const fontSize = Number.parseFloat(style.fontSize) || 0;
    let lineHeight = Number.parseFloat(style.lineHeight);
    if (!Number.isFinite(lineHeight)) lineHeight = fontSize * 1.45;
    return {
      text: element.textContent.replace(/\s+/g, ' ').trim().slice(0, 80),
      top: rect.top,
      right: rect.right,
      bottom: rect.bottom,
      left: rect.left,
      width: rect.width,
      height: rect.height,
      fontSize,
      fontWeight: numericWeight(style.fontWeight),
      lineHeight,
      lineRatio: fontSize > 0 ? lineHeight / fontSize : 0,
      kind: element.hasAttribute('data-resume-section') ? 'section' :
        element.hasAttribute('data-resume-entry') ? 'entry' : 'body'
    };
  };
  const overlapX = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 4;
  const nodes = Array.from(document.querySelectorAll(selectors)).filter(visible);
  const records = nodes.map(describe);
  const bodies = records.filter(record => record.kind === 'body');
  const lineValues = bodies.map(record => record.lineHeight).filter(value => value > 0).sort((a, b) => a - b);
  const medianLineHeight = lineValues.length ? lineValues[Math.floor(lineValues.length / 2)] : 16;
  const sectionLeadGaps = [];
  const entryGaps = [];

  records.forEach((record, index) => {
    if (record.kind !== 'section') return;
    for (let nextIndex = index + 1; nextIndex < records.length; nextIndex += 1) {
      const candidate = records[nextIndex];
      if (candidate.kind === 'section') break;
      if (!overlapX(record, candidate) || candidate.top < record.bottom - 1) continue;
      const gap = Math.max(0, candidate.top - record.bottom);
      sectionLeadGaps.push({
        from: record.text,
        to: candidate.text,
        pixels: gap,
        lines: gap / medianLineHeight
      });
      break;
    }
  });

  records.forEach((record, index) => {
    if (record.kind !== 'entry') return;
    let nextEntryIndex = -1;
    for (let nextIndex = index + 1; nextIndex < records.length; nextIndex += 1) {
      if (records[nextIndex].kind === 'section') break;
      if (records[nextIndex].kind === 'entry' && overlapX(record, records[nextIndex])) {
        nextEntryIndex = nextIndex;
        break;
      }
    }
    if (nextEntryIndex < 0) return;
    const nextEntry = records[nextEntryIndex];
    if (nextEntry.top <= record.top) return;
    let occupiedBottom = record.bottom;
    for (let bodyIndex = index + 1; bodyIndex < nextEntryIndex; bodyIndex += 1) {
      const between = records[bodyIndex];
      if (between.kind === 'body' && overlapX(record, between) && between.top < nextEntry.top + 1) {
        occupiedBottom = Math.max(occupiedBottom, between.bottom);
      }
    }
    const gap = Math.max(0, nextEntry.top - occupiedBottom);
    entryGaps.push({
      from: record.text,
      to: nextEntry.text,
      pixels: gap,
      lines: gap / medianLineHeight
    });
  });

  const output = {
    bodyCount: bodies.length,
    bodyFontMin: bodies.length ? Math.min(...bodies.map(record => record.fontSize)) : null,
    bodyWeightMin: bodies.length ? Math.min(...bodies.map(record => record.fontWeight)) : null,
    bodyLineRatioMin: bodies.length ? Math.min(...bodies.map(record => record.lineRatio)) : null,
    smallestBody: bodies.slice().sort((a, b) => a.fontSize - b.fontSize)[0] || null,
    lightestBody: bodies.slice().sort((a, b) => a.fontWeight - b.fontWeight)[0] || null,
    tightestBody: bodies.slice().sort((a, b) => a.lineRatio - b.lineRatio)[0] || null,
    sectionLeadGaps,
    entryGaps,
    largestGap: sectionLeadGaps.concat(entryGaps).sort((a, b) => b.lines - a.lines)[0] || null
  };
  const metrics = document.createElement('pre');
  metrics.id = '__resume_qa_metrics';
  metrics.style.display = 'none';
  metrics.textContent = JSON.stringify(output);
  document.body.appendChild(metrics);
})();
</script>
"""

    source = html.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"</body\s*>", source, flags=re.I):
        instrumented = re.sub(
            r"</body\s*>",
            lambda _: probe + "\n</body>",
            source,
            count=1,
            flags=re.I,
        )
    else:
        instrumented = source + probe

    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".html",
            prefix=".resume-qa-",
            dir=html.parent,
            delete=False,
        ) as temp_file:
            temp_file.write(instrumented)
            temp_path = Path(temp_file.name)

        command = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--allow-file-access-from-files",
            "--virtual-time-budget=1500",
            "--dump-dom",
            temp_path.resolve().as_uri(),
        ]
        code, stdout, stderr = run(command)
        if code != 0:
            return None, stderr or stdout or "Chrome layout probe failed."
        match = re.search(r'<pre id="__resume_qa_metrics"[^>]*>(.*?)</pre>', stdout, flags=re.S)
        if not match:
            return None, "Layout probe output was not found in Chrome DOM dump."
        return json.loads(html_lib.unescape(match.group(1))), "Layout metrics collected."
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def check_html_layout(
    html: Path,
    chrome: str,
    checks: list[dict],
    *,
    min_body_font_px: float,
    min_body_font_weight: float,
    min_body_line_ratio: float,
    max_semantic_gap_lines: float,
    required: bool,
) -> None:
    metrics, evidence = collect_html_layout_metrics(html, chrome)
    add_check(checks, "semantic layout metrics available", metrics is not None, evidence, required=required)
    if metrics is None:
        return

    body_count = int(metrics.get("bodyCount") or 0)
    add_check(
        checks,
        "semantic body markers present",
        body_count > 0,
        f"Found {body_count} elements with data-resume-body.",
        required=required,
    )
    if body_count == 0:
        return

    font_min = float(metrics.get("bodyFontMin") or 0)
    weight_min = float(metrics.get("bodyWeightMin") or 0)
    line_ratio_min = float(metrics.get("bodyLineRatioMin") or 0)
    largest_gap = metrics.get("largestGap")
    gap_lines = float(largest_gap.get("lines") or 0) if isinstance(largest_gap, dict) else 0.0

    add_check(
        checks,
        "body font size >= readability floor",
        font_min >= min_body_font_px - 0.05,
        f"minimum={font_min:.2f}px, limit={min_body_font_px:.2f}px, sample={metrics.get('smallestBody')}",
        required=required,
    )
    add_check(
        checks,
        "body font weight >= regular",
        weight_min >= min_body_font_weight,
        f"minimum={weight_min:.0f}, limit={min_body_font_weight:.0f}, sample={metrics.get('lightestBody')}",
        required=required,
    )
    add_check(
        checks,
        "body line height >= readability floor",
        line_ratio_min >= min_body_line_ratio - 0.01,
        f"minimum={line_ratio_min:.2f}, limit={min_body_line_ratio:.2f}, sample={metrics.get('tightestBody')}",
        required=required,
    )
    add_check(
        checks,
        "semantic vertical gaps <= limit",
        gap_lines <= max_semantic_gap_lines,
        f"largest={gap_lines:.2f} lines, limit={max_semantic_gap_lines:.2f}, gap={largest_gap}",
        required=required,
    )


def render_screenshot(pdf: Path, screenshot_prefix: Path, checks: list[dict]) -> None:
    tool = shutil.which("pdftoppm")
    if not tool:
        add_check(checks, "screenshot rendered", False, "pdftoppm not found; install poppler for screenshot rendering.", required=False)
        return

    screenshot_prefix.parent.mkdir(parents=True, exist_ok=True)
    code, stdout, stderr = run([tool, "-jpeg", "-r", "180", str(pdf), str(screenshot_prefix)])
    rendered = screenshot_prefix.parent / f"{screenshot_prefix.name}-1.jpg"
    passed = code == 0 and rendered.exists() and rendered.stat().st_size > 0
    add_check(
        checks,
        "screenshot rendered",
        passed,
        f"{rendered} ({rendered.stat().st_size} bytes)" if passed else (stderr or stdout),
    )


def read_ppm(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    index = 0

    def token() -> bytes:
        nonlocal index
        while index < len(data) and data[index:index + 1].isspace():
            index += 1
        if index < len(data) and data[index:index + 1] == b"#":
            while index < len(data) and data[index:index + 1] not in (b"\n", b"\r"):
                index += 1
            return token()
        start = index
        while index < len(data) and not data[index:index + 1].isspace():
            index += 1
        return data[start:index]

    magic = token()
    if magic != b"P6":
        raise ValueError(f"Unsupported PPM format: {magic!r}")
    width = int(token())
    height = int(token())
    max_value = int(token())
    if max_value != 255:
        raise ValueError(f"Unsupported PPM max value: {max_value}")
    if index >= len(data) or not data[index:index + 1].isspace():
        raise ValueError("PPM header is missing its pixel-data separator")
    if data[index:index + 2] == b"\r\n":
        index += 2
    else:
        index += 1
    pixels = data[index:]
    expected = width * height * 3
    if len(pixels) < expected:
        raise ValueError(f"PPM pixel data is incomplete: expected {expected}, got {len(pixels)}")
    return width, height, pixels[:expected]


def bottom_whitespace_ratio(
    width: int,
    height: int,
    pixels: bytes,
    *,
    left_ratio: float,
    right_ratio: float,
    white_threshold: int = 245,
) -> tuple[float, int | None]:
    x0 = max(0, min(width - 1, int(width * left_ratio)))
    x1 = max(x0 + 1, min(width, int(width * right_ratio)))
    row_width = x1 - x0
    min_ink_pixels = max(10, int(row_width * 0.0025))

    for y in range(height - 1, -1, -1):
        row_start = (y * width + x0) * 3
        ink_pixels = 0
        for x in range(row_width):
            offset = row_start + x * 3
            r, g, b = pixels[offset], pixels[offset + 1], pixels[offset + 2]
            if r < white_threshold or g < white_threshold or b < white_threshold:
                ink_pixels += 1
                if ink_pixels >= min_ink_pixels:
                    return (height - 1 - y) / height, y
    return 1.0, None


def check_bottom_whitespace(
    pdf: Path,
    checks: list[dict],
    *,
    max_ratio: float,
    main_content_right_ratio: float,
) -> None:
    tool = shutil.which("pdftoppm")
    if not tool:
        add_check(
            checks,
            "bottom whitespace <= limit",
            False,
            "pdftoppm not found; install poppler to measure bottom whitespace.",
            required=False,
        )
        return

    with tempfile.TemporaryDirectory(prefix="resume-bottom-whitespace-") as temp_dir:
        prefix = Path(temp_dir) / "page"
        code, stdout, stderr = run([tool, "-r", "120", "-singlefile", str(pdf), str(prefix)])
        ppm = prefix.with_suffix(".ppm")
        if code != 0 or not ppm.exists():
            add_check(checks, "bottom whitespace <= limit", False, stderr or stdout)
            return

        try:
            width, height, pixels = read_ppm(ppm)
            full_ratio, full_row = bottom_whitespace_ratio(
                width,
                height,
                pixels,
                left_ratio=0.02,
                right_ratio=0.98,
            )
            main_ratio, main_row = bottom_whitespace_ratio(
                width,
                height,
                pixels,
                left_ratio=0.03,
                right_ratio=main_content_right_ratio,
            )
        except Exception as exc:
            add_check(checks, "bottom whitespace <= limit", False, str(exc))
            return

    passed = main_ratio <= max_ratio
    add_check(
        checks,
        "main content bottom whitespace <= limit",
        passed,
        (
            f"main={main_ratio:.1%}, full={full_ratio:.1%}, limit={max_ratio:.1%}, "
            f"main_last_row={main_row}, full_last_row={full_row}"
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Export an HTML resume to PDF and run basic QA checks.")
    parser.add_argument("html", help="Path to resume.html.")
    parser.add_argument("--pdf", help="Output PDF path. Defaults to HTML stem with .pdf.")
    parser.add_argument("--screenshot", help="Screenshot prefix for pdftoppm. Defaults beside the PDF.")
    parser.add_argument("--chrome", help="Path to Chrome/Chromium.")
    parser.add_argument("--expected-font", help="Font substring expected in pdffonts output. Defaults to the template manifest, then PingFang.")
    parser.add_argument("--forbid-term", action="append", default=[], help="Additional forbidden term to scan.")
    parser.add_argument("--strict-final", action="store_true", help="Also reject bundled demo/template leftovers.")
    parser.add_argument(
        "--max-bottom-whitespace",
        type=float,
        default=0.15,
        help="Maximum allowed bottom whitespace ratio in the main content area.",
    )
    parser.add_argument(
        "--main-content-right-ratio",
        type=float,
        default=0.86,
        help="Right boundary ratio for main content whitespace measurement; excludes far-right QR/footer by default.",
    )
    parser.add_argument("--min-body-font-px", type=float, default=12.0, help="Minimum computed font size for data-resume-body elements.")
    parser.add_argument("--min-body-font-weight", type=float, default=400, help="Minimum computed font weight for recruiter-facing body text.")
    parser.add_argument("--min-body-line-ratio", type=float, default=1.30, help="Minimum computed line-height/font-size ratio for body text.")
    parser.add_argument("--max-semantic-gap-lines", type=float, default=2.25, help="Maximum vertical gap between consecutive semantic blocks, measured in body line-heights.")
    args = parser.parse_args()

    html = Path(args.html).expanduser().resolve()
    if not html.exists():
        raise SystemExit(f"HTML not found: {html}")

    pdf = Path(args.pdf).expanduser().resolve() if args.pdf else html.with_suffix(".pdf")
    screenshot_prefix = (
        Path(args.screenshot).expanduser().resolve()
        if args.screenshot
        else pdf.with_suffix("")
    )

    checks: list[dict] = []
    chrome = find_chrome(args.chrome)
    if not chrome:
        add_check(checks, "Chrome available", False, "Chrome/Chromium was not found.")
    else:
        add_check(checks, "Chrome available", True, chrome)
        ok, evidence = export_pdf(html, pdf, chrome)
        add_check(checks, "PDF exported", ok, evidence)
        check_html_layout(
            html,
            chrome,
            checks,
            min_body_font_px=args.min_body_font_px,
            min_body_font_weight=args.min_body_font_weight,
            min_body_line_ratio=args.min_body_line_ratio,
            max_semantic_gap_lines=args.max_semantic_gap_lines,
            required=args.strict_final,
        )

    if pdf.exists() and pdf.stat().st_size > 0:
        check_pdfinfo(pdf, checks)
        check_fonts(pdf, checks, expected_font_for(html, args.expected_font))
        forbidden_terms = DEFAULT_FORBIDDEN_TERMS + list(args.forbid_term)
        if args.strict_final:
            forbidden_terms += STRICT_FINAL_FORBIDDEN_TERMS
        check_text(pdf, html, checks, forbidden_terms)
        render_screenshot(pdf, screenshot_prefix, checks)
        check_bottom_whitespace(
            pdf,
            checks,
            max_ratio=args.max_bottom_whitespace,
            main_content_right_ratio=args.main_content_right_ratio,
        )

    failed_required = [check for check in checks if check["required"] and not check["passed"]]
    summary = {
        "html": str(html),
        "pdf": str(pdf),
        "screenshot_prefix": str(screenshot_prefix),
        "ok": not failed_required,
        "checks": checks,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if failed_required else 0


if __name__ == "__main__":
    raise SystemExit(main())
