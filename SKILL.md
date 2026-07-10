---
name: html-resume-builder
description: Build, rewrite, QA, and expand one-page HTML/PDF resume templates from existing resumes, Word/PDF materials, portfolios, websites, or user notes. Use this skill whenever the user asks to create, iterate, polish, migrate, template-match, export, or design new resume/CV templates as HTML/PDF, especially when they care about strict layout, typography, one-page density, STAR wording, optional component DIY, QR/avatar assets, screenshot QA, template-agent variants, and final acceptance gates.
---

# HTML Resume Builder

Use this skill to produce polished, one-page resume artifacts from raw materials. The default output is an editable HTML file and an exported PDF that follows a selected template exactly enough for recruiting use: stable A4 dimensions, consistent typography, predictable spacing, clear hierarchy, verified screenshot, and no accidental sensitive-material leaks.

This skill is intentionally workflow-heavy. Resume work fails when the model jumps straight into writing prose or nudges layout by eye without QA. Follow the staged process below.

When expanding the template library, work one direction at a time: produce a brief, implement in an isolated workspace, QA and compare against the baseline, then seek user approval before admission. Do not split the resume into module Agents; components are AI-decided slots inside the selected template. The admitted bundled templates are: `basic-a4` (baseline), `editorial` (dual-column editorial), `sidebar-compact` (dark sidebar), `timeline-grid` (growth timeline), `minimal-prose` (quiet prose), `mono-raw` (brutalist monospace), `code-poetry` (source-code metaphor), `swiss-neue` (Swiss grid), `bauhaus` (geometric editorial), `corporate-classic` (formal corporate), `gov-red` (Chinese institutional style), and `folio-ledger` (annual-report ledger).

## Core Principles

- Treat a resume as both a **content artifact** and a **layout artifact**. Improve the wording, but keep the visual hierarchy and template constraints under control.
- Prefer evidence-based statements. Write achievements as Situation/Task -> Action -> Result when space allows, and avoid fake metrics.
- Preserve recruiter readability. Put internship work under `实习经历`, portfolio/project work under `项目作品/个人经历`, and skills under `核心能力`; do not move work into a misleading section just because it fits visually.
- Preserve template fidelity before pursuing novelty. If a new template or variant is not at least as good as the baseline template in layout stability, visual rhythm, density, and recruiting readability, reject it instead of adding it to the template library.
- For new templates, visual quality must be verified at full-page screenshot scale before admission.
- Keep one-page resumes honest and visually full. If content is light, enlarge type, line-height, and section rhythm rather than padding with weak claims or leaving large blank areas. If content is dense, compress carefully without breaking hierarchy.
- Let AI decide optional resume components inside the selected template's slots. Components such as campus experience, certificates, language ability, portfolio links, or tool chains may be added, renamed, merged, or omitted when they improve the resume, but they must not break the template structure or misclassify facts.
- Never expose internal links, issue IDs, private group chats, patches, commits, document paths, raw prompts, or confidential tool names unless the user explicitly wants them shown.
- Use a final QA pass. A resume is not done until PDF page count, fonts, text extraction, screenshot, spacing, and sensitive-word checks pass.

## Layout Hard Constraints

These constraints override template defaults. They apply to every template in this family.

### Page Margins (页边距)

- **Maximum page padding: 10mm on any side.** No template should have left/right/top padding exceeding 10mm. The A4 page is 210mm wide; content should occupy at least 190mm of horizontal space.
- If a template uses absolute positioning, the leftmost content should start no later than 12mm from the page edge, and the rightmost content should end no earlier than 12mm from the right edge.
- When the generated resume shows obvious blank strips on either side, reduce padding first before considering any other adjustment.

### Density Adaptation (密度自适应)

- Template HTML provides a **structural skeleton**. The font sizes, line-heights, and section gaps defined in templates are **reference values, not fixed**.
- When filling a template with real content, AI must adapt spacing to fit the content volume:
  - **Content is light** (fewer experiences, shorter descriptions): increase font-size (+0.5–1pt), increase line-height (+0.05–0.1), increase section gaps slightly. The goal is a page that feels intentionally spacious and calm, not empty.
  - **Content is heavy** (many experiences, long descriptions): decrease section gaps, keep font-size stable or reduce by 0.5pt max. Never go below 9pt for body text.
  - **Bottom whitespace > 15%**: this is a hard QA failure. Adjust font-size/line-height/section-gap upward until the page is visually balanced.
- Do not leave large hollow areas. Do not pad with weak content to fill space — adjust typography instead.

### Avatar & QR (头像与二维码)

- **Avatar must have zero border and zero border-radius.** No frames, no rounded corners, no shadows. A clean rectangular image, period.
- Avatar must remain in its original color. Never apply grayscale, sepia, or any filter to a personal headshot.
- QR codes may be grayscale if the template is monochrome, but must not be obscured or clipped by any other element.
- If a QR code is present, it must be fully visible — no overlap with text, pills, or other components.

### Section Spacing (模块间距)

- Section-to-section vertical gap should be proportional to the content density. Reference range: 4–7mm between major sections.
- Within a section, entry-to-entry gap: 2–3.5mm.
- These values flex based on content volume — they are not fixed. The goal is consistent visual rhythm across the full page, not mathematical equality.

## When Starting

1. Identify the target role and audience.
   - Examples: `AI 技术产品`, `AIGC 智能评测`, `AI 视觉内容编导`, `游戏视频设计`, `产品运营`.
   - If the user gives no role, infer from the strongest recent materials, then state the assumption.
2. Gather source materials.
   - Existing resumes: PDF, PPTX, DOCX, HTML.
   - Supporting materials: work summaries, project docs, portfolio websites, spreadsheets, screenshots.
   - Assets: avatar/headshot, QR code, portfolio URL, website URL.
3. Choose the template.
   - Start with `assets/templates/basic-a4/` unless the user names another template.
   - Future templates should live under `assets/templates/<template-name>/`.
   - If expanding the template library, follow `references/template-expansion.md` before implementing or accepting any new template.
4. Decide whether this is:
   - **Template migration**: style must match an existing resume.
   - **New resume from materials**: style comes from a bundled template.
   - **Iteration**: edit an existing HTML/PDF resume while preserving style.
   - **Template expansion**: propose one new style direction, implement in an isolated workspace, compare against the baseline, and seek user approval before admission.

## Recommended Workflow

### Step 1: Template Selection

**先让用户选模板，再开始写内容。**

1. 向用户展示可用模板列表（名称 + 一句话风格描述），让用户指定：

   | 模板 | 风格 |
   |------|------|
   | basic-a4（默认） | 经典单栏，ATS 友好，适合所有场景 |
   | editorial | 双栏 Grid，字重层级分明 |
   | sidebar-compact | 深色侧栏，辨识度高 |
   | timeline-grid | 时间轴叙事，适合经历丰富 |
   | minimal-prose | Stripe 极简，留白即设计 |
   | corporate-classic | 外企极简，纯黑白，内容为王 |
   | gov-red | 党政风，庄重规范，适合国企/事业单位 |
   | folio-ledger | 年报档案索引，编号清晰，适合中高信息密度 |
   | mono-raw | Brutalist 风，工具即美学 |
   | code-poetry | 源代码隐喻，极客风 |
   | swiss-neue | 瑞士主义，隐形网格，克制优雅 |
   | bauhaus | 包豪斯几何，三原色点缀 |

2. 如果用户没有明确偏好，默认使用 **basic-a4**。
3. 用户确认后，锁定模板，不再中途切换（除非用户主动要求）。

### Step 1.5: Style Lock

模板确定后，检查并锁定视觉参数：

- 页面尺寸：A4 竖版（除非用户另行要求）
- 字体：通常为 PingFang SC
- 色彩层级：主色、标题深灰、正文灰、辅助浅灰
- 结构模块：姓名/信息、头像、个人介绍、教育经历、实习/工作经历、项目经历、核心能力、二维码
- 组件位置：标题、分割线、日期对齐、正文缩进、头像和二维码位置

对于已有 HTML 模板，直接编辑源文件。除非模板已经无法修复，否则不要从零重建布局。

### Step 2: Fact Extraction and Filtering

Extract facts from source files and websites. Keep a short fact inventory before writing:

- Education: school, major, dates, GPA/rank, awards/certificates.
- Internships: company, role, dates, responsibilities, shipped outputs, measurable results.
- Projects: name, context, actions, result, public evidence.
- Skills: tools, workflows, domain knowledge, evaluation methods.
- Links/assets: website, portfolio, QR, avatar/headshot.

Filter facts by role relevance. De-emphasize or remove unrelated side projects unless they support the target role.

### Step 3: Resume Copywriting

Write in recruiter-friendly Chinese. Prefer compact STAR-style statements:

- Situation/Task: the problem, scene, or requirement.
- Action: what the candidate personally did.
- Result: shipped output, measurable change, evaluation result, adoption, recognition, or public portfolio evidence.

Good line pattern:

`面对 [具体场景/问题]，负责 [个人动作]，通过 [方法/工具/流程] 完成 [交付物]，最终 [结果/影响]。`

Avoid weak filler:

- “具备较强能力”
- “参与相关工作”
- “负责部分事项”
- “学习能力强”

If a metric is not public or not known, do not invent one. Use verifiable alternatives: release status, review passed, coverage scope, samples/cases, team adoption, portfolio link.

### Step 4: HTML Implementation

Use the selected template directory:

- Copy `assets/templates/basic-a4/` into the output workspace, or edit the user-provided HTML if iterating.
- Replace only content and necessary asset references first.
- Adjust positions after content is stable.
- Keep class names and style tokens consistent.

For a one-page A4 resume, use absolute-positioned blocks only when preserving a strict template. For new templates, stable CSS grids are acceptable, but always export and screenshot-test.

### Step 4.1: Component Slot DIY

The selected template owns the structure; AI owns the component choice inside allowed slots.

- Keep the default backbone unless the template contract says otherwise: header, intro, education, internship, project or personal experience, core abilities, footer/QR.
- AI may add, remove, rename, or merge optional sections when that improves the candidate's story.
- AI should decide whether optional content deserves its own section or should be merged into education/core abilities/project experience.

**Available section titles** (pick what fits the candidate; do not use all):

| Category | Section titles |
|----------|---------------|
| Core (almost always present) | 个人介绍 · 教育经历 · 核心能力 |
| Experience | 实习经历 · 工作经历 · 项目经历 · 个人项目 |
| Campus / Student | 校园经历 · 社团经历 · 学生工作 · 志愿服务 |
| Achievements | 竞赛经历 · 获奖情况 · 荣誉奖项 |
| Skills & Certs | 专业技能 · 工具链 · 语言能力 · 证书/资格 |
| Portfolio | 作品集 · 开源贡献 · 个人博客 |
| Other | 兴趣爱好 · 自我评价 · 培训经历 · 科研经历 · 发表论文 |

Naming rule: use the title that most honestly describes the content. 已正式入职的用「工作经历」，在校生用「实习经历」；有社团管理经验的单独列「社团经历」，没有就不硬凑。
- Component DIY is not a reason to invent facts, add weak filler, or move internship work into project experience.
- Do not spawn separate agents for individual resume components. Use subagents for template style research/implementation, then let the main resume-building pass fill components.

### Step 4.5: Density and White Space Tuning

After the first PDF export, inspect the screenshot as a whole page, not only line by line. Apply the **Layout Hard Constraints** from above. Specific process:

1. **Check page margins first.** If left/right padding > 10mm, reduce it. This is the single most common cause of "looks too empty" feedback.
2. **Measure bottom whitespace.** If the last content element ends more than 15% above the page bottom, the page is too loose. Adjust in this order:
   - Increase body font-size by 0.5–1pt
   - Increase line-height by 0.05–0.1
   - Increase section gaps by 1–2mm
   - Only after all three are maxed out, consider adding an optional section (awards, tools, self-summary)
3. **If content is dense** and overflows or feels cramped:
   - Reduce section gaps first (down to 4mm minimum between sections)
   - Reduce entry gaps (down to 2mm minimum)
   - Shorten copy before shrinking font below 9pt
4. **Never use `letter-spacing` for density control.** It is a design accent, not a spacing tool.
5. **Re-export and screenshot after each adjustment.** A page that passes CLI checks can still fail visually.

### Step 5: Asset Handling

- **Avatar/headshot**: keep original color. No grayscale, no filters, no border, no border-radius, no shadow. Pure rectangular image with `object-fit: cover`.
- **QR codes**: may be grayscale if the template is monochrome. Must not be clipped or overlapped by any element. Keep a quiet white margin around the scannable area.
- **QR visibility**: if a QR code appears in the template, it must be 100% unobstructed. If layout pushes content over the QR, the QR must move or the content must shrink — never allow partial occlusion.
- Website links: use blue underlined text when it should read as clickable.
- If using demo assets, keep them fake and clearly non-personal.

### Step 6: Export and QA

Run export and QA every time content or layout changes materially.

Minimum checks:

1. `pdfinfo` confirms `Pages: 1` and A4 portrait.
2. `pdffonts` confirms the intended font family, usually `PingFangSC-Regular` and `PingFangSC-Semibold`.
3. `pdftotext -layout` confirms module order and no old-person or old-template text remains.
4. Render a JPEG/PNG screenshot using `pdftoppm` and inspect visually.
5. Search for sensitive or stale terms:
   - old names, old emails, old phone numbers
   - `patch`, `commit`, `群聊`, `ones`, `内部链接`
   - unrelated self-media terms when the user asked to remove them
6. Check visual layout:
   - no overlap, clipping, text touching QR/avatar, or title/body collision
   - title-to-body spacing matches the section hierarchy
   - body line-height is not cramped
   - main content bottom whitespace is no more than 15% of page height; this is a hard QA gate, not a suggestion
   - no large hollow areas; light resumes should use slightly larger type and calmer spacing
   - section rhythm is consistent
   - QR and footer captions align

When visual QA matters, show or inspect the rendered screenshot before declaring completion.

## Bundled Resources

- `assets/templates/basic-a4/`: baseline one-page resume template. Single column, absolute positioning, blue-gray color scheme.
- `assets/templates/editorial/`: dual-column grid. Left sidebar for education/skills/QR, right main for narrative. Monochrome (no color highlights), hierarchy through weight/size.
- `assets/templates/sidebar-compact/`: dark sidebar (deep navy) + white main body. Avatar/contact/education/skills in sidebar, experience/projects in main. Tags for skills.
- `assets/templates/timeline-grid/`: vertical timeline with dot nodes. Education in header meta, experiences along the spine, skill pills in footer.
- `assets/templates/minimal-prose/`: ultra-clean single-column, Stripe/Notion docs aesthetic. No rules, no color — hierarchy purely through weight, size, and generous whitespace.
- `assets/templates/mono-raw/`: Brutalist monospace (Menlo/SF Mono). Pure black-on-white, dashed dividers, `>` prefixed sub-headings, data in bold. Raw, honest, technical.
- `assets/templates/code-poetry/`: source code metaphor. `/* name */` comment block, `// SECTION` headers, `fn title()` entries, orange-highlighted metrics, `import {}` skills. Left gutter with line numbers.
- `assets/templates/swiss-neue/`: Swiss International Typographic Style. Invisible grid (26mm label column right-aligned), mathematical spacing (8/4.5/2.5mm), light-weight (300) muted-red name as sole accent. Zero decorative elements.
- `assets/templates/bauhaus/`: geometric single-column layout with red, blue, and yellow accents for creative roles.
- `assets/templates/corporate-classic/`: restrained black-gray corporate layout for formal delivery.
- `assets/templates/gov-red/`: Song-type institutional layout with restrained red section rules.
- `assets/templates/folio-ledger/`: European annual-report ledger with a full-height folio rail, numbered sections, and a single recruiter reading column.
- `references/template-contract.md`: layout contract for the basic A4 template.
- `references/template-expansion.md`: protocol for adding new template styles with template Agents and main-Agent acceptance gates.
- `references/qa-checklist.md`: final QA checklist and common failure modes.
- `scripts/create_workspace.py`: copy a template into a working directory.
- `scripts/export_and_qa.py`: export an HTML resume to PDF and run basic checks.

## Quick Start Commands

Create a working copy from the bundled template:

```bash
python scripts/create_workspace.py --template basic-a4 --output /path/to/resume-workspace
```

Export and QA the resume:

```bash
python scripts/export_and_qa.py /path/to/resume-workspace/resume.html --pdf /path/to/resume-workspace/resume.pdf --strict-final
```

Use `--strict-final` for real candidate resumes so demo placeholders such as fake names, fake contact details, and `example.com` are rejected. The QA script also fails the resume when the main content bottom whitespace exceeds 15% of page height; use `--max-bottom-whitespace` only if a different template has an intentional footer system.

## Output Convention

Default deliverables:

- `<candidate-name>-<target-role>-模板版.html`
- `<candidate-name>-<target-role>-模板版.pdf`
- Optional working directory containing assets and scripts.

Final response should include:

- Where the PDF and HTML are.
- What sources were used.
- What QA passed.
- Any assumptions or missing assets.

Keep the final response concise. If the user is still reviewing, summarize only the current change and the verification result.
