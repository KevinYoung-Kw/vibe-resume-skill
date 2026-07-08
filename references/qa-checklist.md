# Resume QA Checklist

Use this checklist before considering an HTML/PDF resume complete.

## Required CLI Checks

Run the bundled script first:

```bash
python scripts/export_and_qa.py path/to/resume.html --pdf path/to/resume.pdf
```

If checking manually, run:

```bash
pdfinfo path/to/resume.pdf
pdffonts path/to/resume.pdf
pdftotext -layout path/to/resume.pdf -
pdftoppm -jpeg -r 180 path/to/resume.pdf /tmp/resume-check
```

Verify:

- `Pages: 1`.
- Page size is A4 portrait, roughly `595 x 842 pts`.
- Fonts include the intended family, usually `PingFangSC-Regular` and `PingFangSC-Semibold`.
- Text extraction order follows the resume reading order.
- No stale or sensitive terms remain:
  - unrelated old names, phone numbers, emails, or websites
  - `patch`, `commit`, `群聊`, `ones`, `内部链接`
  - old self-media terms if the user asked to remove them
  - template leftovers such as `example.com`, `138-0000-0000`, or `示例候选人` in final non-demo resumes

## Visual Review

Open or inspect the rendered screenshot.

- No text overlaps, clipping, cropped lines, or title/body collisions.
- Section hierarchy is clear: first-level title, second-level role/company, third-level item, body.
- Internal item spacing is consistent.
- Different companies/projects have slightly larger but still controlled gaps.
- Body line-height is readable and not cramped.
- Hard gate: the main content bottom whitespace must not exceed 15% of page height. The bundled QA script measures the main content area from the left edge through roughly 86% page width so a low QR code does not hide a hollow main column.
- The page does not feel hollow. If there is too much unused space, improve density with slightly larger type, line-height, and section rhythm before adding content.
- Parentheses and explanatory labels are lighter than main titles.
- Body text is not globally bold.
- Blue highlights are sparse and attached to real evidence.
- Website links are blue and underlined when meant to be clickable.
- QR code and caption align; QR is not too small and does not collide with core abilities.
- Avatar is color and correctly cropped.

## Common Fixes

- If the PDF becomes two pages: reduce body length first, then adjust line-height, then tune section gaps.
- If text looks dense: add a small amount of line-height before increasing page gaps.
- If content feels sparse: enlarge font, line-height, and vertical rhythm instead of inventing weak achievements; do not leave bottom whitespace above 15%.
- If typography feels loose horizontally: do not add arbitrary `letter-spacing`; preserve it only when the source template already uses that rule.
- If a highlight refuses to wrap: remove `nowrap` from the highlighted span unless it protects a short metric.
- If third-level projects feel disconnected: compress gaps inside the same company and keep company-to-company gaps only slightly larger.
