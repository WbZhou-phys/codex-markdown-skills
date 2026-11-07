# General Relativity Profile

Use this profile for the `GR` project, especially Carroll-based chapter notes.

## Destination and naming

- Obsidian library: `<your Obsidian vault>/GR/`.
- Inspect the existing note folder before writing. The textbook notes currently live under `Spacetime and Geometry 精读/`; the project AGENTS file may state the root directory instead. Follow the established chapter location or ask before reorganizing a library.
- Filename: `第X章 章节名（Carroll 2014）.md`.

## Source hierarchy

- Use the specified Carroll edition as the authority.
- Record sign convention, units (`c=1`, whether `G` or `hbar` is restored), and tensor-index conventions in the opening blockquote.
- When OCR cannot establish an equation number, describe its section instead of inventing a tag.

## Structure

1. YAML frontmatter with `tags` and `created`.
2. H1: `# 第X章　章节名`.
3. Blockquote with textbook, range, and conventions.
4. `## 本章地图`.
5. Main sections `## §x.y　标题`; self-defined subsections may use `### x.y.z`.
6. `## 本章小结` with formula quick reference, concept flow, common errors, and Chinese-English glossary.
7. End at the glossary unless the user explicitly requests exercises.

Use [textbook-chapter-template.md](../assets/textbook-chapter-template.md).

## Mathematical requirements

- Keep Carroll's equation numbers when readable.
- Preserve all index contractions, symmetry operations, signs, and boundary conditions.
- Flag convention hazards explicitly: metric signature, Riemann tensor index order, units, and whether torsion/connection is independent.
- Distinguish coordinate components from geometric objects.
- Check each key result in a familiar limit or against a known identity when possible.

## Markdown and LaTeX safety

- In Markdown notes, use only `$...$` and `$$...$$`.
- For independently numbered equations in one display block, use `align` with one tag per line.
- A single tag applies after `\end{aligned}`, never inside it.
- Avoid Markdown escapes in prose; write `**bold**`, not escaped literals.

Read [obsidian-markdown.md](obsidian-markdown.md) before resolving formula or tag failures.
