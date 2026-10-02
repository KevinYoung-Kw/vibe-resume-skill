---
name: html-resume-builder
description: >-
  Build one-page HTML/PDF resumes from copy-paste YAML using one of 12 official templates.
  HARD GATES: deliver exactly one A4 page; never invent a layout — copy assets/templates/<id> into output/<id>/ and edit that copy only.
  Keep a full inventory in raw.data.yaml.
  For each job, COPY selected entries into resume.data.yaml (polish there), then apply that file to a template.
  Apply pasted YAML by replacing visible text in the official resume.html, then run QA.
  Default template is basic-a4.
  Use when creating, iterating, polishing copy, migrating, exporting, or designing resume/CV HTML/PDF.
  For polishing resume copy, prefer writing-oriented models (Claude Fable 5 / Claude Opus 4.6-4.7 or Opus 5 / Kimi K3 / GLM-5.1-5.3-max / Qwen 3.8 Max); do not use GPT-5.6 Terra/Luna or GPT-5.5 Instant.
---

# HTML Resume Builder

Use this skill to produce polished, **one-page** resume artifacts from structured facts. The default loop is **data first**: keep a `raw.data.yaml` inventory, copy selected entries into one `resume.data.yaml` per job, then apply that file to an official template. The default output is an editable HTML file and an exported PDF that follows a selected template exactly enough for recruiting use: stable A4 dimensions, consistent typography, predictable spacing, clear hierarchy, verified screenshot, and no accidental sensitive-material leaks.

This skill is intentionally workflow-heavy. Resume work fails when the model jumps straight into writing prose, invents a new HTML document, or nudges layout by eye without QA. Follow the **Mandatory Workflow** below before any other step.

When expanding the template library, work one direction at a time: produce a brief, implement in an isolated workspace, QA and compare against the baseline, then seek user approval before admission. Do not split the resume into module Agents; components are AI-decided slots inside the selected template.

## Mandatory Workflow (do this every time)

These steps are hard gates. Skipping them is a failed run, even if the page looks fine.

There are two data files. Do not mix them.

| File | What it is |
|------|------------|
| `raw.data.yaml` | 履历库. Every job, project, campus thing the user wants remembered. Can be long. **Never printed.** |
| `resume.data.yaml` | One application. Copied from raw, then polished for this JD. This is what you apply to a template. |

Job A and job B share the same raw. Each gets its own `resume.data.yaml` (e.g. `output/ai-intern/resume.data.yaml` vs `output/growth/resume.data.yaml`).

### 1. Collect facts into `raw.data.yaml`

Extract education, internships, projects, skills, contacts, and assets into the inventory. Use `examples/raw.data.yaml` as the shape. Keep extra experiences even if they will not fit one page. Add `id` / `tags` on entries so later jobs can select them (`ai-product`, `growth`, `frontend`, …).

**Show the raw file** so the user can copy it and keep adding facts. Do not hide the inventory in chat-only notes.

Do **not** write `resume.data.yaml` yet unless the user already named a target job and asked to export.

### 2. For a job: copy from raw → `resume.data.yaml`

When the user names a role or pastes a JD:

1. **Copy** (do not move) the matching entries from `raw.data.yaml` into a new `resume.data.yaml`. Set `layer: resume` and `source_raw`.
2. Leave unused entries in raw (frontend intern stays in raw when exporting an AI-product resume).
3. Polish **only** the copied `resume.data.yaml`: tighter summary/bullets, skill order, `target_role` / `jd`. Follow `references/copy-optimize.md`.
4. Show the selected id list + the resume YAML. Wait for accept.
5. Apply **that** `resume.data.yaml` to a template (step 3). Export is this copy logic, not a third published file.

If they later say 投 B 岗位, start a new `resume.data.yaml` from the same raw. Do not overwrite job A's file.

Never delete from raw to make one page. Cuts happen only on the resume copy.

### 2.5 Do not invent a polished sibling

No `resume.polished.data.yaml`. The pair is raw (bank) vs resume (this job). 润色 writes into `resume.data.yaml`.

### 3. Copy the official template, then edit that copy only

```bash
mkdir -p output
cp -R assets/templates/<template-id> output/<template-id>/
```

`python scripts/create_workspace.py --template <template-id> --output output/<template-id>` is equivalent.

Edit **only** `output/<template-id>/resume.html` (and its local assets). Never edit files under `assets/templates/` for a candidate resume.

### 4. Forbidden

- Writing a new HTML document from scratch, even if it "looks like" a template
- Using a template that is not in the 12-id allowlist
- Skipping QA
- Switching templates mid-run unless the user asks
- Introducing a mustache / Handlebars / template-engine rewrite of the 12 official files. There is no render engine. Apply YAML by replacing **visible text** in the official `resume.html` while keeping CSS, class names, semantic `data-*` markers (including `data-template="<id>"`), and structure

### 5. Template allowlist (12 ids)

`basic-a4` (baseline) · `editorial` · `sidebar-compact` · `timeline-grid` · `minimal-prose` · `mono-raw` · `code-poetry` · `swiss-neue` · `bauhaus` · `corporate-classic` · `gov-red` · `folio-ledger`

If the user does not pick a template, **default to `basic-a4` and say so**.

### 6. One page is a hard stop

A resume is not deliverable unless it is exactly one A4 page.

1. Run existing QA scripts when they are present:
   - `python scripts/export_and_qa.py output/<id>/resume.html --pdf output/<id>/resume.pdf --template <id>`
   - `node scripts/check-template-id.mjs --html output/<id>/resume.html --template <id>`
2. If `pdfinfo` page count ≠ 1, **do not deliver**. Compress layout within the existing density / typography-floor rules, or ask the user (named cuts vs. keep-all vs. an explicit two-page exception).
3. If the user said `全部保留` / `不要删减`, do not delete facts to force one page — stop and ask.
4. A screenshot or HTML that looks "almost one page" is not enough. The PDF page count must be 1.

`examples/demo/` is the out-of-the-box render: official `basic-a4` filled from `examples/demo.data.yaml`. Users can open `examples/demo/resume.html` immediately.

## When the AI may change the look（什么时候可以改模板）

There are four different jobs. Do not mix them. “改模板” almost never means inventing HTML.

### A. 换数据（默认，随时可以，这不是改模板）

User pastes YAML or says apply. Copy the official template, replace visible text, then tune density. Keep CSS, class names, `data-template`, and structure. This is the normal loop.

### B. 换官方模板（用户要「全变样」时，这是最好的改法）

Same YAML, different allowlisted id. Always `cp -R` a fresh official folder. Never mix two templates' CSS.

Do this when:

- The user names a template (`swiss-neue`, `gov-red`, …)
- The user says 换风格 / 全变样 / 太普通 / 换一套
- The current template is a bad fit (e.g. `gov-red` for a geek role, `sidebar-compact` overflowing, `code-poetry` for a 国企投递)
- The first deliverable used the default `basic-a4` and the user wants a restyle

If unsure which official template fits, show the 12-id table and ask. Do not invent a 13th look.

### C. 在当前模板里微调版式（内容稳定之后才做）

OK: font-size ±0.5–1pt, line-height, section/entry gaps, absolute coordinates, duplicating or deleting an existing official block of the same kind.

Not OK: new sidebar, new grid, new color system, new font family, rewriting `resume.html` from scratch, stamping `data-template` onto invented markup.

### D. 发明新模板（正常写简历时禁止）

Only follow `references/template-expansion.md`: one direction, brief first, isolated workspace, compare against `basic-a4`, user admits it. A color swap is not a new template. Do not edit `assets/templates/` during a candidate resume run.

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

## Content Preservation & Deletion Gate

Treat an existing resume and user-prepared resume copy as source material the user has already selected. **Do not silently delete or materially weaken it to make the page fit.**

- Default to preservation mode when iterating an existing PDF, Word, PPTX, or HTML resume. Text the user pastes and explicitly asks to include also counts as selected resume content. Keep every company, role, project, date, metric, credential, named deliverable, link, and user-authored bullet unless the user approves its removal.
- A major edit includes deleting an entire entry or bullet, merging entries so a distinct fact disappears, removing a metric/result, changing section ownership, or replacing a specific accomplishment with a generic summary. Ask before making any of these changes.
- Compression is allowed without a separate approval only when it removes repetition or shortens syntax while preserving the same facts, ownership, result, and level of specificity.
- If the requested content does not fit one page, first repair layout and wording within the readability limits below. If it still does not fit, **do not deliver**. Ask the user to choose: a denser but still readable one-page layout; a named list of lower-priority cuts; or an explicit two-page exception (never the default).
- If the user says `全部保留`, `不要删减`, or equivalent, do not remove content. A one-page preference never overrides an explicit preservation request.
- Maintain a short change ledger during iteration: `retained`, `compressed without fact loss`, and `proposed removal`. Show proposed removals to the user before applying them.

## Layout Hard Constraints

These constraints override template defaults. They apply to every template in this family.

### Page Margins (页边距)

- **Maximum page padding: 10mm on any side.** No template should have left/right/top padding exceeding 10mm. The A4 page is 210mm wide; content should occupy at least 190mm of horizontal space.
- If a template uses absolute positioning, the leftmost content should start no later than 12mm from the page edge, and the rightmost content should end no earlier than 12mm from the right edge.
- When the generated resume shows obvious blank strips on either side, reduce padding first before considering any other adjustment.
- **Margins are also a floor, not just a ceiling.** Do not crush page padding below roughly 6mm to gain density. A resume whose content touches the paper edge reads as desperate, not efficient. Edges need quiet space to breathe.

### White Space Principle (留白原则)

- The density rules above exist to prevent hollow, half-empty pages — they are **not** a mandate to stuff the page. Deliberate white space is part of good typography: page margins, breathing room between sections, and a calm bottom edge within the 15% budget are features, not defects.
- Never manufacture density. Do not solve "the page has white space" by inventing extra components, splitting content into additional columns, breaking paragraphs into pill grids, or adding decorative filler blocks. A page filled with layout gimmicks is worse than a page with honest white space.
- When content genuinely runs light, the correct tools are typography (slightly larger type, taller line-height, calmer section rhythm) and — only if the user has real material — one meaningful optional section. When in doubt, prefer a calm, slightly airy page over a crowded one.

### Density Adaptation (密度自适应)

- Template HTML provides a **structural skeleton**. The font sizes, line-heights, and section gaps defined in templates are **reference values, not fixed**.
- When filling a template with real content, AI must adapt spacing to fit the content volume:
  - **Content is light** (fewer experiences, shorter descriptions): increase font-size (+0.5–1pt), increase line-height (+0.05–0.1), increase section gaps slightly. The goal is a page that feels intentionally spacious and calm, not empty.
  - **Content is heavy** (many experiences, long descriptions): remove excessive section/entry gaps first, compress repeated wording without dropping facts, then keep font-size stable or reduce by 0.5pt max. Never go below 9pt for body text.
  - **Bottom whitespace > 15%**: this is a hard QA failure. Adjust font-size/line-height/section-gap upward until the page is visually balanced.
- Do not leave large hollow areas. Do not pad with weak content to fill space — adjust typography instead.
- Never shrink body text while large section or entry gaps remain. Small, thin text plus visible hollow bands is a layout failure even when the PDF is one page.

### Typography Readability Floor (正文字体下限)

- Recruiter-facing body text must be at least `9pt` (`12px` in CSS) and normally use `font-weight: 400` or stronger. Weight `300` is reserved for dates, parentheses, captions, and other supporting labels, not paragraphs.
- Body line-height should normally stay between `1.35` and `1.7`. Do not reduce line-height below the point where adjacent lines visually touch.
- If the page is sparse, increase body size and line-height before increasing large inter-section gaps. If the page is dense, reduce gaps before reducing type.

### Avatar & QR (头像与二维码)

- **Avatar must have zero border and zero border-radius.** No frames, no rounded corners, no shadows. A clean rectangular image, period.
- Avatar must remain in its original color. Never apply grayscale, sepia, or any filter to a personal headshot.
- QR codes may be grayscale if the template is monochrome, but must not be obscured or clipped by any other element.
- If a QR code is present, it must be fully visible — no overlap with text, pills, or other components.

### Section Spacing (模块间距)

- Section-to-section vertical gap should be proportional to the content density. Reference range: 4–7mm between major sections.
- Within the same company or section, entry-to-entry gap: 2–3.5mm. Different companies may use 3–5mm, but should not look detached.
- A blank vertical band larger than roughly two body line-heights between consecutive semantic blocks is a QA failure unless the selected template explicitly defines that area as an intentional visual zone.
- These values flex based on content volume — they are not fixed. The goal is consistent visual rhythm across the full page, not mathematical equality.

## When Starting

Run the Mandatory Workflow first. The steps below are intake details, not a license to skip YAML, the template copy, or QA.

1. Identify the target role and audience.
   - Examples: `AI 技术产品`, `AIGC 智能评测`, `AI 视觉内容编导`, `游戏视频设计`, `产品运营`.
   - If the user gives no role, infer from the strongest recent materials, then state the assumption.
2. Gather source materials.
   - Existing resumes: PDF, PPTX, DOCX, HTML.
   - Supporting materials: work summaries, project docs, portfolio websites, spreadsheets, screenshots.
   - Assets: avatar/headshot, QR code, portfolio URL, website URL.
   - Decide preservation mode: existing resume content and text explicitly requested for inclusion are `preserve by default`; background materials not marked for full inclusion may be selectively summarized only after the user understands that not every source detail will appear.
3. Choose the template from the 12-id allowlist only.
   - If the user does not name one, default to `basic-a4` and tell them you did.
   - Copy `assets/templates/<template-id>/` into `output/<template-id>/`. Do not write a new HTML file.
   - Future templates should live under `assets/templates/<template-name>/` only after admission.
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

2. 如果用户没有明确偏好，默认使用 **basic-a4**，并明确告诉用户。
3. 只允许上面这 12 个 id。用户点名 allowlist 之外的模板时，拒绝并列出允许的 id。
4. 用户确认后，锁定模板，不再中途切换（除非用户主动要求）。

### Step 1.5: Style Lock

模板确定后，检查并锁定视觉参数：

- 页面尺寸：A4 竖版（除非用户另行要求）
- 字体：通常为 PingFang SC
- 色彩层级：主色、标题深灰、正文灰、辅助浅灰
- 结构模块：姓名/信息、头像、个人介绍、教育经历、实习/工作经历、项目经历、核心能力、二维码
- 组件位置：标题、分割线、日期对齐、正文缩进、头像和二维码位置

对于已有 HTML 模板，只编辑 `output/<template-id>/` 里的副本。除非模板已经无法修复，否则不要从零重建布局。

### Step 2: Fact Extraction into `raw.data.yaml`

Extract facts from source files and websites into `raw.data.yaml` (schema: `schema/resume.schema.json`). **Show this inventory so the user can copy it and keep adding.** Only after a target job exists, copy selected entries into `resume.data.yaml`. Keep a short fact inventory before writing:

- Education: school, major, dates, GPA/rank, awards/certificates.
- Internships: company, role, dates, responsibilities, shipped outputs, measurable results.
- Projects: name, context, actions, result, public evidence.
- Skills: tools, workflows, domain knowledge, evaluation methods.
- Links/assets: website, portfolio, QR, avatar/headshot.

Rank facts by role relevance, but do not silently remove content from an existing resume. Mark lower-priority material as a proposed cut and ask the user before applying it. For a new resume built from raw supporting files, tell the user when the source volume requires representative selection rather than exhaustive inclusion.

### Step 3: Resume Copywriting

If the user asked to 打磨内容 or match a JD, Mandatory Workflow **2.5** and `references/copy-optimize.md` come first. This step is the same writing bar used inside that YAML pass — it is not a substitute for showing a polished YAML file.

排版、改模板可用日常编程模型。**润色简历正文**用写作向模型。

推荐：

- 海外：Claude Fable 5；Claude Opus 4.6 / 4.7（有 Opus 5 也行）
- 国内：Kimi K3（K2.6 也偏写作）；智谱 GLM-5.1 / 5.2 / 5.3-max；通义千问 Qwen 3.8 Max（结构化备选）

不要用：

- GPT-5.6 Terra / Luna：同代里写作掉档最狠
- GPT-5.5 默认 / Instant：日常默认档，文风空、套话多

其余模型不限定。

Write in recruiter-friendly Chinese (or the user's language). Prefer compact STAR-style statements:

- Situation/Task: the problem, scene, or requirement.
- Action: what the candidate personally did.
- Result: shipped output, measurable change, evaluation result, adoption, recognition, or public portfolio evidence.

Good line pattern:

`面对 [具体场景/问题]，通过 [个人动作 + 方法/工具] 交付 [产物]，结果 [已有事实]。`

Avoid weak filler:

- “具备较强能力”
- “参与相关工作”
- “负责部分事项”
- “学习能力强”
- “负责 / Helped with / Worked on” as the only verb

If a metric is not public or not known, do not invent one and do not guess “约 30%”. Ask, then use verifiable alternatives: release status, review passed, coverage scope, samples/cases, team adoption, portfolio link.

When a JD is present, weave only keywords the YAML already supports. Unproven JD skills stay in `optimize.notes` as ask / do-not-claim — never in `skills` or bullets.

### Step 4: Apply YAML into the official HTML (do not invent a layout)

Use the selected template directory:

- **Required:** `cp -R assets/templates/<template-id> output/<template-id>/` (or `scripts/create_workspace.py`). If iterating a user-provided HTML that already came from this skill, edit that copy.
- Start from the official `resume.html`. Replace visible text so it matches the confirmed YAML. Keep CSS, class names, DOM structure, and `data-template="<id>"` / `data-resume-*` markers.
- Add or remove entry blocks only by duplicating or deleting an existing official block of the same kind. Do not introduce a new grid, sidebar, or font system.
- Replace only content and necessary asset references first. Adjust positions after content is stable.
- Keep class names and style tokens consistent.
- Forbidden: a blank `resume.html` written from scratch; any template id outside the allowlist.

For a one-page A4 resume, use absolute-positioned blocks only when preserving a strict template. For new templates, stable CSS grids are acceptable, but always export and screenshot-test.

### Step 4.1: Component Slot DIY

The selected template owns the structure; AI owns the component choice inside allowed slots.

- Keep the default backbone unless the template contract says otherwise: header, intro, education, internship, project or personal experience, core abilities, footer/QR.
- For a new resume assembled from raw materials, AI may add, rename, or merge optional sections when that improves the candidate's story. When iterating an existing resume, removing or merging a section requires the Content Preservation & Deletion Gate above.
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
   - Only after all three are maxed out, consider adding an optional section (awards, tools, self-summary) — and only from real material the user provided. Never add extra columns, split rows, or decorative components purely to consume space; within the 15% bottom budget, remaining white space is intentional and acceptable
3. **If content is dense** and overflows or feels cramped:
   - Remove abnormal hollow bands and reduce section gaps first (down to 4mm minimum between sections)
   - Reduce entry gaps (down to 2mm minimum)
   - Compress repetition while preserving every fact
   - Reduce body font by at most 0.5pt, never below 9pt or regular weight
   - If it still does not fit, ask the user before deleting content or moving to two pages
4. **Never use `letter-spacing` for density control.** It is a design accent, not a spacing tool.
5. **Re-export and screenshot after each adjustment.** A page that passes CLI checks can still fail visually.

### Step 5: Asset Handling

- **Avatar/headshot**: keep original color. No grayscale, no filters, no border, no border-radius, no shadow. Pure rectangular image with `object-fit: cover`.
- **QR codes**: may be grayscale if the template is monochrome. Must not be clipped or overlapped by any element. Keep a quiet white margin around the scannable area.
- **QR visibility**: if a QR code appears in the template, it must be 100% unobstructed. If layout pushes content over the QR, the QR must move or the content must shrink — never allow partial occlusion.
- Website links: use blue underlined text when it should read as clickable.
- If using demo assets, keep them fake and clearly non-personal.

### Step 6: Export and QA

Run export and QA every time content or layout changes materially. **Skipping QA is forbidden.** If page count ≠ 1, the resume is not done — do not deliver it.

```bash
python scripts/export_and_qa.py output/<id>/resume.html --pdf output/<id>/resume.pdf --template <id>
node scripts/check-template-id.mjs --html output/<id>/resume.html --template <id>
```

Minimum checks:

1. `pdfinfo` confirms `Pages: 1` and A4 portrait. This is a hard stop.
2. `pdffonts` confirms the intended font family, usually `PingFangSC-Regular` and `PingFangSC-Semibold`.
3. `pdftotext -layout` confirms module order and no old-person or old-template text remains.
4. Render a JPEG/PNG screenshot using `pdftoppm` and inspect visually.
5. Search for sensitive or stale terms:
   - old names, old emails, old phone numbers
   - `patch`, `commit`, `群聊`, `ones`, `内部链接` (ASCII terms match on word boundaries, so `dispatch`/`milestones`/`committed` do not false-positive)
   - unrelated self-media terms when the user asked to remove them
6. Check visual layout:
   - no overlap, clipping, text touching QR/avatar, or title/body collision
   - title-to-body spacing matches the section hierarchy
   - body line-height is not cramped
   - body text is at least 9pt/12px and recruiter-facing paragraphs are not rendered with light (`300`) weight
   - no unexplained vertical gap exceeds roughly two body line-heights between consecutive sections or entries
   - main content bottom whitespace is no more than 15% of page height; this is a hard QA gate, not a suggestion
   - no large hollow areas; light resumes should use slightly larger type and calmer spacing
   - section rhythm is consistent
   - QR and footer captions align
7. Check content preservation against the source inventory:
   - every original company, project, date, metric, credential, and user-authored bullet is retained or explicitly approved for removal
   - compressed wording preserves the original fact, ownership, specificity, and result
   - any pending deletion proposal is surfaced to the user instead of being applied silently

When visual QA matters, show or inspect the rendered screenshot before declaring completion.

## Bundled Resources

- `schema/resume.schema.json`: copy-paste resume data schema (name, title, target_role, contacts, summary, experience, projects, education, skills, plus optional `jd` / `optimize` that never print).
- `examples/raw.data.yaml`: demo inventory (extra frontend / 社团 / 视觉 stay here).
- `examples/demo.data.yaml`: one job export copied from that raw (AI 产品 intern).
- `examples/demo/`: official `basic-a4` filled from `demo.data.yaml`.
- `assets/templates/basic-a4/`: baseline one-page resume template. Single column, absolute positioning, blue-gray color scheme.
- `assets/templates/editorial/`: dual-column grid. Left sidebar for education/skills/QR, right main for narrative. Monochrome (no color highlights), hierarchy through weight/size.
- `assets/templates/sidebar-compact/`: dark sidebar (deep navy) + white main body. Avatar/contact/education/skills in sidebar, experience/projects in main. Tags for skills.
- `assets/templates/timeline-grid/`: vertical timeline with dot nodes. Education in header meta, experiences along the spine, skill pills in footer.
- `assets/templates/minimal-prose/`: ultra-clean single-column, Stripe/Notion docs aesthetic. No rules, no color — hierarchy purely through weight, size, and generous whitespace.
- `assets/templates/mono-raw/`: Brutalist monospace (Menlo/SF Mono). Pure black-on-white, dashed dividers, `>` prefixed sub-headings, data in bold. Raw, honest, technical.
- `assets/templates/code-poetry/`: source code metaphor. `/* name */` comment block, `// SECTION` headers, `fn title()` entries, orange-highlighted metrics, `import {}` skills. Left gutter with line numbers.
- `assets/templates/swiss-neue/`: Swiss International Typographic Style. Invisible grid (16mm label column right-aligned), mathematical spacing (8/4.5/2.5mm), light-weight (300) muted-red name as sole accent. Zero decorative elements.
- `assets/templates/bauhaus/`: geometric single-column layout with red, blue, and yellow accents for creative roles.
- `assets/templates/corporate-classic/`: restrained black-gray corporate layout for formal delivery.
- `assets/templates/gov-red/`: Song-type institutional layout with restrained red section rules.
- `assets/templates/folio-ledger/`: European annual-report ledger with a full-height folio rail, numbered sections, and a single recruiter reading column.
- `references/template-contract.md`: layout contract for the basic A4 template.
- `references/template-expansion.md`: protocol for adding new template styles with template Agents and main-Agent acceptance gates.
- `references/copy-optimize.md`: YAML-first content polish — STAR/tight verbs, JD keywords, no invented metrics, before/after pair.
- `references/qa-checklist.md`: final QA checklist and common failure modes.
- `scripts/create_workspace.py`: copy a template into a working directory (`output/<template-id>/`).
- `scripts/export_and_qa.py`: export an HTML resume to PDF and run basic checks, including the `data-template` fingerprint and one-page gate.
- `scripts/check-template-id.mjs`: fail if output HTML is missing `data-template="<id>"` from the allowlist.

## Quick Start Commands

Prerequisites: Chrome or Chromium for PDF export, and poppler (`pdfinfo`/`pdffonts`/`pdftotext`/`pdftoppm`) for the QA checks. On macOS: `brew install poppler`. Missing poppler downgrades those checks to warnings instead of failing the run.

Create a working copy from the bundled template:

```bash
python scripts/create_workspace.py --template basic-a4 --output output/basic-a4
```

Export and QA the resume (one-page + official-template fingerprint):

```bash
python scripts/export_and_qa.py output/basic-a4/resume.html --pdf output/basic-a4/resume.pdf --template basic-a4 --strict-final
node scripts/check-template-id.mjs --html output/basic-a4/resume.html --template basic-a4
```

Use `--strict-final` for real candidate resumes so demo placeholders such as fake names, fake contact details, and `example.com` are rejected. The QA script also fails the resume when the main content bottom whitespace exceeds 15% of page height; use `--max-bottom-whitespace` only if a different template has an intentional footer system.

## Output Convention

Default deliverables live under `output/<template-id>/`:

- `output/<template-id>/resume.html` (official template copy, text replaced from YAML)
- `output/<template-id>/resume.pdf` (exactly one A4 page)
- `raw.data.yaml` at repo root or `output/raw.data.yaml` (inventory)
- `output/<role-or-template>/resume.data.yaml` (this job, copied from raw)
- Optional named exports: `<candidate-name>-<target-role>-模板版.html` / `.pdf`

Final response should include:

- Where the PDF and HTML are.
- What sources were used.
- What QA passed.
- Any assumptions or missing assets.

Keep the final response concise. If the user is still reviewing, summarize only the current change and the verification result.
