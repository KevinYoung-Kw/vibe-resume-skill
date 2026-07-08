# Basic A4 Template Contract

Use this reference when editing `assets/templates/basic-a4/resume.html` or a resume derived from it.

## Page

- Size: A4 portrait, `210mm x 297mm`.
- Print margin: `0`.
- Main canvas: `.page`, `position: relative`, white background, overflow hidden.
- Primary font: `PingFang SC`, with `PingFangSC-Regular`, `-apple-system`, and `BlinkMacSystemFont` fallback.
- Color logic:
  - Primary blue: `#2563eb` for name, lead highlights, metric highlights, and active website links.
  - Dark title: `#1f2937` for section and role titles.
  - Body gray: `#707785` for regular body text.
  - Muted gray: `#8a93a1` for parentheses, explanations, and low-emphasis tags.
  - Separator gray: `#c4c9d2` for vertical dividers.
  - Rule gray: `#f0f0f0` for section horizontal lines.

## Components

- `.name`: candidate name, blue, large, light weight.
- `.meta`: basic info and links, single or double line, no forced wrapping unless content exceeds the safe width.
- `.avatar`: color headshot. Do not grayscale personal photos.
- `.section-title`: first-level module title, regular weight, dark gray.
- `.section-line`: subtle horizontal divider before most modules.
- `.role-title`: company/education line, semibold, single line.
- `.item-title`: project or sub-experience line, semibold, single line.
- `.date`: right-aligned date, regular weight, muted body gray.
- `.body`: regular body copy, justified when useful, no artificial bolding.
- `.subhead`: third-level project title inside a body block. It should sit close to its body text, but not touch it.
- `.highlight`: one blue emphasis per paragraph where possible. Use for verified results, not vague claims.
- `.muted`: parentheses, supporting labels, or low-emphasis explanations.
- `.sep`: vertical separators. Keep light so they do not compete with text.
- `.site-link`: blue and underlined when the URL should appear clickable.
- `.footer-img` and `.footer-note`: QR or portfolio marker. Align image and caption as a single unit.

## Spacing Rules

Adjust top coordinates only after content is stable.

- First-level title to first content line: keep a clear gap similar to other first-level modules.
- Company/role line to first third-level item: slightly wider than subhead-to-body spacing.
- Third-level item to its body: tight but readable.
- Third-level item to next third-level item in the same company: compact and consistent.
- Different companies/projects: slightly larger than internal item gaps, but not so large that the page loses density.
- Core abilities: title and body must not overlap; QR can sit to the right or lower-right, but body text must keep a safe margin.
- Hard density rule: in final QA, the main content bottom whitespace must be no more than 15% of page height. A QR code or footer placed low on the page must not be used to hide an empty main content area.
- If a finished screenshot has large empty areas, tune body font size, line-height, and vertical spacing before adding weak content. The page should feel full, credible, and calm.
- Do not introduce arbitrary character tracking. Preserve `letter-spacing` only when it is an explicit part of the template being matched.

## Content Placement

- Put actual work under the correct experience block. Do not place internship features under projects if they were internship work.
- Keep public projects under `项目经历`, `个人经历`, or a similar section.
- Keep skills as capability statements, not disguised project history.
- Do not reveal internal links, issue IDs, patch/commit details, raw group chat names, or private document paths.

## Asset Rules

- Use real candidate headshot in color.
- Use QR codes with sufficient white quiet zone and enough size to scan.
- Decorative non-headshot images may be grayscale if the template visual style is subdued.
- If the resume is a demo/template, use fake names, fake contact details, and non-scannable placeholder assets.
