# Thermodynamics and Statistical Physics Profile

Use this profile for the `热统` project or another course using the same textbook-chapter style.

## Destination and naming

- Obsidian library: `<your Obsidian vault>/热统/`
- Filename: `第X章 章节名（汪志诚 第六版）.md` or the exact edition specified by the user.
- Keep the final note only in the Obsidian library.

## Source hierarchy

- Use the specified textbook edition as the chapter authority.
- Read the actual textbook pages for derivations; the table of contents is only a navigation aid.
- When a solution manual or additional proof is supplied, label it as supplementary and integrate the full proof.

## Structure

1. YAML frontmatter with `tags` and `created`.
2. H1: `# 第X章　章节名`.
3. Blockquote with textbook, edition, section range, and page range.
4. `## 本章地图` table.
5. Main sections `## §x.y　标题` and subsections `### x.y.z 标题`.
6. `## 本章小结` with exactly:
   - `### 一、公式速查`
   - `### 二、概念脉络`
   - `### 三、易错点`
   - `### 四、名词中英对照`
7. End at the glossary. Do not add a self-test or exercise index.

Use [textbook-chapter-template.md](../assets/textbook-chapter-template.md) as a starting point.

## Content requirements

- Preserve every derivation, example calculation, and proof step.
- Keep textbook equation numbers with `\tag{...}`.
- Preserve footnotes, starred sections, and supplementary material; identify their status.
- Explicitly flag symbol differences such as work sign conventions or state-function choices.
- Make grouped comparisons into tables; keep prose compact.
- Check the generated chapter map and summary against the finished body.

## Figures

Do not batch-insert textbook figures merely because the prose says "如图". This project's established default is text-only notes. Add a figure only when the user requests it or when a specific diagram is indispensable; use a clean crop with readable labels rather than a whole-page screenshot.

## Formula compatibility

Apply [obsidian-markdown.md](obsidian-markdown.md). Use actual MathJax validation for every completed chapter.
