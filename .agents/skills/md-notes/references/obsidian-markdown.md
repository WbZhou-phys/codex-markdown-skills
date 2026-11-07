# Obsidian Markdown and MathJax

Apply these rules to every note written or edited by this skill.

## Formula delimiters

Use:

```markdown
行内公式：$E=mc^2$

$$
E=mc^2
\tag{1.1}
$$
```

Do not use TeX document delimiters:

```text
\[ ... \]
\( ... \)
```

They do not render reliably in Obsidian reading mode.

## Blockquotes containing display math

Keep the complete display equation on the same line as the blockquote marker:

```markdown
> **教材脚注**
>
> $$m!\approx m^m e^{-m}\sqrt{2\pi m}$$
>
> 当 $m$ 很大时，取对数得到后续近似。
```

Avoid:

```markdown
> $$
formula without blockquote marker
$$
```

The middle line ends the blockquote and can break formula pairing.

## Formula tags

One tagged line inside a single `$$...$$` block:

```markdown
$$
\begin{aligned}
a &= b+c \\
d &= e+f
\end{aligned}
\tag{1.2.3}
$$
```

Multiple independently numbered lines:

```markdown
$$
\begin{align}
a &= b \tag{1.2.3}\\
d &= e \tag{1.2.4}
\end{align}
$$
```

Never put `\tag` inside `aligned`.

## Tables containing formulas

Markdown parsers treat `|` as a cell separator even inside `$...$`. Do not write:

```markdown
| 液气 | $p-p_c\propto \pm|\rho-\rho_c|^\delta$ |
```

Write:

```markdown
| 液气 | $p-p_c\propto \pm\lvert\rho-\rho_c\rvert^\delta$ |
```

Other naturally widening commands such as `\left\lvert` and `\right\rvert` are acceptable.

## Images

- Resolve links relative to the note file.
- Use the attachment directory already used by the project.
- Keep filenames descriptive and stable.
- Verify each target exists after moving or renaming attachments.
- Add a short caption below explanatory figures when the project style uses captions.

## Markdown text

- Use real Markdown emphasis (`**bold**`) rather than escaped literal asterisks.
- Do not introduce HTML entities such as `&#x20;`.
- Use fenced `text` blocks for ASCII concept diagrams.
- Keep blank lines around tables, equations, blockquotes, and fenced blocks.
- Avoid one enormous display block containing several independently tagged equations unless it uses a valid `align` environment.

## Final checks

1. Run `scripts/validate_notes.py`.
2. Search for `\[`, `\]`, `\(`, `\)`, `&#x20;`, and unfinished `TODO`.
3. Render with MathJax through the `md-to-pdf` skill when formulas matter.
4. Inspect at least one formula-heavy page and one wide-table page for clipping or broken columns.
