# Template Expansion Protocol

Use this reference when expanding `html-resume-builder` with additional resume templates.

The default template is not a loose inspiration board. Treat `assets/templates/basic-a4/` as the baseline quality bar. New templates may vary in style, but they must match or exceed the baseline in layout stability, visual rhythm, information density, recruiting readability, and PDF export reliability.

Current admitted template library: `basic-a4`, `editorial`, `sidebar-compact`, `timeline-grid`, `minimal-prose`, `mono-raw`, `code-poetry`, `swiss-neue`, `bauhaus`, `corporate-classic`, `gov-red`, `folio-ledger`.

---

## Core Expansion Rules

1. **One at a time.** Never explore multiple new templates in parallel. Each expansion attempt focuses on exactly one new direction.
2. **No color-swap templates.** Changing colors, fonts, or decorative flourishes without restructuring information architecture does not constitute a new template.
3. **Structure ≠ quality.** A different layout does not automatically mean a better resume. The new template must look like a mature one-page Chinese resume, not a dashboard, UI mockup, poster, infographic, or portfolio landing page.
4. **QA pass ≠ quality pass.** Technical export checks prove "not broken." They do not prove "good enough to send to a recruiter."
5. **New templates live in isolated workspaces until admitted.** Never write a candidate template directly into `assets/templates/`.
6. **Failure records stay outside the Skill.** Post-mortems, rejection notes, and failed candidates should be stored in the task workspace, not in the Skill directory.

---

## Component Slot System

Templates expose component slots. AI decides which slots to use during resume generation.

AI may:

- Add, remove, rename, or merge optional components: `社团经历`, `校园经历`, `证书`, `语言能力`, `工具链`, `作品集`, `竞赛经历`.
- Decide whether optional content becomes its own section or merges into education/project/core abilities.
- Rename section titles for role fit (e.g. `项目经历` → `项目作品`).
- Choose how many items per section.

AI must not:

- Move internship work into project experience for visual convenience.
- Invent facts, metrics, awards, tools, or organizations.
- Add decorative components that do not improve recruiting readability.
- Break the template's page grid, section rhythm, typography, or QA gates.

---

## Expansion Workflow (Sequential, One Direction at a Time)

### Step 1: Template Direction Brief

Before any implementation, write a brief:

```markdown
# <Template Name>

## Design Basis
What reference quality or document tradition this draws from. Must cite a real precedent (e.g., a known resume format, publication style, design system) — not "I thought this would look cool."

## Target Users
Roles, candidate seniority, and content density this template fits.

## Inherited Baseline Layout
Which structures remain from basic-a4 (component slots, semantic categories, reading order).

## Allowed Variations
Typography, color, spacing, component arrangement, asset placement.

## Forbidden Choices
What would make this style cheap, misleading, dashboard-like, or below the baseline.

## Likely Failure Modes
Three to five ways this direction might fail, based on prior experience.

## Acceptance Criteria
How the main Agent should prove the template is at least as good as basic-a4.
```

**Gate:** The brief must be reviewed before implementation. If the direction is weak, off-target, or likely to produce a dashboard/UI mockup, reject it here and choose a different direction.

### Step 2: Implement in Isolated Workspace

After the brief passes:

- Create a workspace directory outside the Skill (e.g., in the task output directory).
- Implement `resume.html` and `template-manifest.json`.
- Use the same demo content as `basic-a4` for fair comparison.
- Use fake/placeholder assets; never real personal data.

### Step 3: Export and QA

Run the export and QA pipeline with the shared demo content:

```bash
python scripts/export_and_qa.py workspace/resume.html --pdf workspace/resume.pdf
```

Required evidence:

1. Exported one-page A4 PDF.
2. Full-page screenshot (180 DPI JPEG via `pdftoppm`).
3. `pdfinfo`: one page, A4 portrait.
4. `pdffonts`: expected Chinese font handling.
5. `pdftotext -layout`: logical reading order preserved.
6. Main content bottom whitespace ≤ 15%.
7. No real personal or company-sensitive information.
8. No overlap, clipping, collision, or broken asset crops.

### Step 4: Side-by-Side Comparison with basic-a4

Using the same demo content, produce:

- A review page (via `scripts/build_template_candidate_review.py`) or manual side-by-side screenshots.
- Explicit comparison on: structure clarity, typography hierarchy, section rhythm, body readability, density, and overall professional impression.

### Step 5: Main Agent Quality Gate

The main Agent evaluates the candidate against the baseline. Reject if:

- It is merely a re-skin (color/font change only).
- Structure is different but aesthetics are worse (cramped, chaotic, fragmented).
- It resembles a dashboard, UI mockup, poster, infographic, or landing page more than a resume.
- Density is not controlled (too hollow or too packed).
- It is not something you would confidently send to a real recruiter.
- It is not at least as good as basic-a4 in overall quality.

If rejected, record the reason in the task workspace (not in the Skill) and stop. Do not iterate the same failed direction endlessly.

### Step 6: User Confirmation

**Before admitting a template into the formal library, the user must see and approve it.**

Present to the user:

- The rendered screenshot.
- The HTML file (openable in browser).
- The exported PDF.
- A brief explanation of the design direction and how it compares to basic-a4.

Only after explicit user approval, move files to `assets/templates/<template-name>/`.

Run `--strict-final` only after replacing demo content with a real candidate's verified content. It is not part of the template style comparison.

---

## What Makes a Good New Template

A new template should:

- Reorganize the same component semantics (education, internship, project, skills, etc.) in a way that improves HR scanning efficiency for a specific candidate type.
- Feel like a mature, production-ready resume format — something a real person would submit.
- Have a clear reason to exist beyond "it looks different."
- Maintain typographic hierarchy and visual calm.
- Be maintainable: content changes should not break the layout.

A new template should NOT:

- Look like a tech dashboard or SaaS product page.
- Pack information so densely it feels like a data table.
- Use novelty at the expense of readability.
- Require the reader to decode the layout before reading the content.

---

## After Admission

Once a template is admitted:

- Place files in `assets/templates/<template-name>/`.
- Include `resume.html`, `template-manifest.json`, and any required assets.
- Update `scripts/create_workspace.py` if needed (it auto-discovers templates by directory name).
- The template becomes available for future resume builds.
