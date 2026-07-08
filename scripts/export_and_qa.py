#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
    "陈若岚",
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
    while index < len(data) and data[index:index + 1].isspace():
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
    parser.add_argument("--expected-font", default="PingFang", help="Font substring expected in pdffonts output.")
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

    if pdf.exists() and pdf.stat().st_size > 0:
        check_pdfinfo(pdf, checks)
        check_fonts(pdf, checks, args.expected_font)
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
