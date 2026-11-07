---
name: md-notes
description: Create or revise rigorous Obsidian Markdown course notes from textbooks, lecture slides, and existing note conventions. Use for chapter notes, lecture notes, formula-heavy derivations, and note-library migrations in technical subjects.
---

# Markdown Course Notes

Turn source material into durable Obsidian notes that preserve the reasoning, respect the course's local format, and keep formulas renderable across Obsidian and PDF.

## Resolve the project contract first

1. Read the nearest `AGENTS.md` and any project instructions above it.
2. Inspect completed notes in the destination library. Existing naming, metadata, section hierarchy, formula style, and figure conventions take precedence over generic memory.
3. Identify the editable source materials, the final Obsidian directory, and the chapter or lecture scope. Do not leave the final note only in the Codex project directory or an `outputs` folder.
4. If the destination is outside the writable workspace, ask the user to add it or grant access before writing.

## Select the note profile

| Project | Typical markers | Read |
| --- | --- | --- |
| Thermodynamics and statistical physics | `热统`, thermodynamics chapter notes | [thermodynamics-statistical-physics.md](references/thermodynamics-statistical-physics.md) |
| General relativity | `GR`, relativity lecture notes, Carroll | [general-relativity.md](references/general-relativity.md) |
| Solid-state physics | `固体物理`, lecture-numbered notes, slide-derived attachments | [solid-state-physics.md](references/solid-state-physics.md) |
| Another technical course | A course directory with its own AGENTS or completed notes | Use [workflow.md](references/workflow.md) and [textbook-chapter-template.md](assets/textbook-chapter-template.md), then adapt to local conventions |

When a project has no profile, infer a consistent format from its completed notes. Do not copy one project's chapter template into another when the existing structure clearly differs.

## Core workflow

1. **Inventory the evidence.** Locate the current textbook edition, latest lecture PDF/PPTX, solution manual, formula sheets, and previous notes. Confirm page ranges and which source is authoritative.
2. **Read the source by section.** Use both text and rendered pages for scans or image-heavy slides. Track derivations, examples, footnotes, starred sections, symbols, figures, and known source errors.
3. **Build an outline before drafting.** Map every in-scope section and decide what belongs in the chapter map, main text, supplementary material, figures, examples, and summary.
4. **Draft one complete note at a time.** Preserve every nontrivial derivation, condition, limit, and calculation step. Compress prose, not mathematics.
5. **Validate structure and Obsidian syntax.** Run the bundled validator. For formula- or layout-sensitive notes, render a preview with `$md-to-pdf` when that skill is available and inspect representative pages.
6. **Deliver into the designated note library.** Report the exact coverage, derived/flagged corrections, and validation performed.

Detailed source-reading, drafting, and review procedures are in [workflow.md](references/workflow.md). Read it for any new chapter, not only mechanical edits.

## Writing invariants

- Prefer short definitions, judgments, and conclusions; use tables for comparisons and lists for procedures.
- Keep source equation numbering. Never invent a number when the source is unreadable; describe the equation by section instead.
- Mark supplementary derivations and exercise solutions clearly.
- Preserve asterisked/optional sections, footnotes, and important historical attributions; state their status.
- Flag textbook errors, notation changes, unit systems, index conventions, and sign conventions where they affect use.
- Check dimensions, limiting cases, signs, and consistency between the main text and summary before delivery.
- Do not replace complete derivations with "it can be shown" or a list of final formulas.

## Obsidian and Markdown invariants

- Use only `$...$` for inline mathematics and `$$...$$` for display mathematics. Never use `\[...\]` or `\(...\)`.
- Keep each display-math delimiter pair on one line inside a blockquote, for example `> $$\varepsilon=...$$`. A lone `> $$` followed by lines without `>` breaks Obsidian parsing.
- Do not use literal table pipes inside a formula in a Markdown table. Use `\lvert ... \rvert` for absolute values.
- A `\tag{...}` belongs outside `\end{aligned}`. When each line of a multi-line display needs its own tag, use `align` with the tag on the corresponding line.
- Use relative image paths from the note directory. Verify every attachment exists.
- Use normal Markdown emphasis and links. Do not leave HTML entities such as `&#x20;` or escaped emphasis in prose.
- End textbook-note files at the required glossary unless the selected project profile explicitly includes exercises or self-tests.

Read [obsidian-markdown.md](references/obsidian-markdown.md) before fixing formula failures or creating a new template.

## Validation

Run the static validator before reporting completion:

```powershell
$skill = Join-Path $HOME ".agents\skills\md-notes"
python (Join-Path $skill "scripts\validate_notes.py") `
  "<path-to-note.md>" --profile auto
```

Use the active Python runtime. On Windows, if `python` launches the Microsoft Store stub, use the Python executable provided by the Codex runtime.

The validator checks frontmatter presence, required section structure, formula delimiters, multiline inline math, formula tags, table pipes, image targets, and common broken blockquote-math patterns. It does not replace visual or MathJax rendering.

For a render check, invoke `$md-to-pdf` to produce a temporary preview or PDF, then inspect at least the first page, a formula-dense page, a wide-table page, and an image-heavy page when applicable. Do not report a formula-heavy note as complete if actual MathJax parsing was never exercised.
