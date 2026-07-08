#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


DEFAULT_ORDER = [
    "baseline-basic-a4",
]


def first_line(text: str) -> str:
    return (text or "").splitlines()[0] if text else ""


def read_candidate(candidate_dir: Path) -> dict:
    qa_path = candidate_dir / "qa.json"
    manifest_path = candidate_dir / "template-manifest.json"
    qa = json.loads(qa_path.read_text(encoding="utf-8")) if qa_path.exists() else {"ok": False, "checks": []}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    checks = {check["name"]: check for check in qa.get("checks", [])}
    shot = next(candidate_dir.glob("*-check-1.jpg"), None)
    return {
        "id": candidate_dir.name,
        "display_name": manifest.get("display_name", candidate_dir.name),
        "summary": manifest.get("summary", ""),
        "qa_ok": qa.get("ok", False),
        "bottom": first_line(checks.get("main content bottom whitespace <= limit", {}).get("evidence", "")),
        "font": checks.get("expected font contains PingFang", {}).get("passed", False),
        "one_page": checks.get("one page", {}).get("passed", False),
        "a4": checks.get("A4 portrait", {}).get("passed", False),
        "screenshot": shot.name if shot else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a visual review page for resume template candidates.")
    parser.add_argument("root", help="Template candidate workspace root.")
    parser.add_argument("--output", help="Output review HTML path. Defaults to <root>/review.html.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    output = Path(args.output).expanduser().resolve() if args.output else root / "review.html"

    dirs = [root / item for item in DEFAULT_ORDER if (root / item).is_dir()]
    dirs += sorted([item for item in root.iterdir() if item.is_dir() and item.name not in DEFAULT_ORDER])
    candidates = [read_candidate(item) for item in dirs]

    cards = []
    rows = []
    for item in candidates:
        label = "Baseline" if item["id"] == "baseline-basic-a4" else "Candidate"
        decision = "baseline" if item["id"] == "baseline-basic-a4" else "pending-main-agent-review"
        screenshot = html.escape(item["screenshot"])
        card = f"""
        <section class="card">
          <div class="card-head">
            <div>
              <span class="eyebrow">{label}</span>
              <h2>{html.escape(item["display_name"])}</h2>
            </div>
            <span class="status {'ok' if item['qa_ok'] else 'fail'}">{'QA PASS' if item['qa_ok'] else 'QA FAIL'}</span>
          </div>
          <p>{html.escape(item["summary"])}</p>
          <img src="{html.escape(item['id'])}/{screenshot}" alt="{html.escape(item['display_name'])} screenshot">
          <div class="links">
            <a href="{html.escape(item['id'])}/resume.html">HTML</a>
            <a href="{html.escape(item['id'])}/{html.escape(item['id'])}.pdf">PDF</a>
            <a href="{html.escape(item['id'])}/qa.json">QA JSON</a>
          </div>
          <dl>
            <dt>Decision</dt><dd>{decision}</dd>
            <dt>Bottom whitespace</dt><dd>{html.escape(item["bottom"])}</dd>
            <dt>One page / A4 / Font</dt><dd>{item['one_page']} / {item['a4']} / {item['font']}</dd>
          </dl>
        </section>
        """
        cards.append(card)
        rows.append(
            f"<tr><td>{html.escape(item['display_name'])}</td><td>{item['qa_ok']}</td>"
            f"<td>{html.escape(item['bottom'])}</td><td>{decision}</td></tr>"
        )

    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>Resume Template Candidate Review</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 32px;
      background: #eef1f5;
      color: #172033;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
    }}
    header {{ max-width: 1440px; margin: 0 auto 24px; }}
    h1 {{ margin: 0 0 8px; font-size: 28px; font-weight: 650; }}
    .note {{ margin: 0; color: #667085; line-height: 1.6; max-width: 980px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(260px, 1fr));
      gap: 18px;
      max-width: 1440px;
      margin: 0 auto;
    }}
    .card {{
      background: #fff;
      border: 1px solid #dde3ec;
      border-radius: 8px;
      padding: 14px;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
    }}
    .card-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: start; margin-bottom: 8px; }}
    .eyebrow {{ display: block; color: #8a94a6; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; }}
    h2 {{ margin: 3px 0 0; font-size: 17px; }}
    .status {{ flex: 0 0 auto; font-size: 11px; font-weight: 700; border-radius: 999px; padding: 4px 8px; }}
    .status.ok {{ color: #047857; background: #d1fae5; }}
    .status.fail {{ color: #b91c1c; background: #fee2e2; }}
    .card p {{ min-height: 42px; margin: 0 0 10px; color: #687386; font-size: 12px; line-height: 1.45; }}
    .card img {{ width: 100%; display: block; border: 1px solid #e6ebf2; background: white; }}
    .links {{ display: flex; gap: 10px; margin: 10px 0; font-size: 12px; }}
    .links a {{ color: #2563eb; text-decoration: underline; }}
    dl {{ display: grid; grid-template-columns: 92px 1fr; gap: 4px 8px; margin: 0; font-size: 11px; line-height: 1.35; }}
    dt {{ color: #8a94a6; }}
    dd {{ margin: 0; color: #424b5a; }}
    table {{ width: 100%; max-width: 1440px; margin: 24px auto 0; border-collapse: collapse; background: #fff; border: 1px solid #dde3ec; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e6ebf2; text-align: left; font-size: 13px; }}
    th {{ background: #f8fafc; }}
  </style>
</head>
<body>
  <header>
    <h1>Resume Template Candidate Review</h1>
    <p class="note">候选模板尚未自动准入。主 Agent 必须基于同一份内容的 HTML/PDF/截图，与 baseline-basic-a4 对比；只有质量大于或等于原版，才允许收纳进正式模板库。</p>
  </header>
  <main class="grid">
    {''.join(cards)}
  </main>
  <table>
    <thead><tr><th>Template</th><th>QA</th><th>Bottom whitespace</th><th>Decision</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</body>
</html>
"""
    output.write_text(page, encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
