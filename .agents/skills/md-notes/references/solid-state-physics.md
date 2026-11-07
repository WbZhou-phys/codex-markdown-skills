# Solid-State Physics Profile

Use this profile for lecture-based solid-state notes in a solid-state course folder.

## Destination and naming

- Obsidian library: `<your Obsidian vault>/固体物理/`.
- Filename: `固体物理-XX-主题.md`, where `XX` is the two-digit lecture/chapter number.
- Store figures under the project's existing `attachments/` directory.

## Source hierarchy

- Treat the latest lecture PDF/PPTX as the primary scope authority.
- Use the specified textbook edition to resolve definitions, standard derivations, and missing context.
- When a new slide deck supersedes an older deck, use the new one for the note but do not delete old course files unless explicitly requested.
- Confirm the exact slide-page range and textbook range in the frontmatter.

## Frontmatter and title

Use the existing Chinese metadata keys:

```yaml
---
课程: 固体物理
讲次: 02
主题: 第二章 晶体的结合（Crystal binding）
覆盖范围: 课件《...》第 1–43 页；教材 §2.1–§2.3（p.50–66）
教材: 胡安、章维益《固体物理学》（第三版）
日期: YYYY-MM-DD
tags:
  - 固体物理
  - 主题标签
---
```

Use `更新:` instead of `日期:` when revising an existing lecture note.

## Structure

Use the numbering already established in the note library:

1. `# 固体物理 XX · 第X章 章节名`.
2. Blockquote `本章主线`.
3. `## 0. 一页速览` with the highest-value concepts, formulas, or comparisons.
4. Numbered main sections, usually `## N. §x.y ...` and `### N.M ...`.
5. `## N. 易错点`.
6. `## N. 课堂提问与例题回顾`.

Do **not** add `## N. 作业与自测` or `## 附：图示索引`. End the note with `## N. 课堂提问与例题回顾`. Images stay inline with short italic captions; do not build a separate figure index.

Use [solid-lecture-template.md](../assets/solid-lecture-template.md) as a starting point.

## Figures

- Crop complete diagrams, plots, crystal structures, and experimental spectra from current slides when they materially aid understanding.
- Remove page chrome and avoid cutting axes, legends, labels, or captions.
- Store images under `attachments/` with stable descriptive names such as `ch2-05-Madelung.png`.
- Include a short italic caption below the image.
- Verify every image link from the note directory.

## Writing requirements

- Keep the lecture's logical sequence but merge repetitive slides.
- Explain experimental figures and tables quantitatively, not only by name.
- Preserve formulas even when slides do not provide textbook numbering.
- Flag slide errors, ambiguous labels, or differences from the textbook.
- Add exam-oriented checks, common errors, and classroom questions when supported by the source.
