---
name: md-to-pdf
description: Export Markdown notes to polished PDFs with protected LaTeX formulas, local assets, configurable typography, page numbers, and repeatable print styling. Use for batches of study notes, reports, or personal-site PDF attachments when a consistent readable layout matters.
---

# Markdown to PDF

Produce a stable, print-ready PDF set from any Markdown project without changing the source files. The default style is a polished A4 note layout with Noto Serif SC, blue section headings, striped tables, highlighted equations, and page footers.

## Workflow

1. Inspect the source for images, linked files, YAML frontmatter, tables, fenced code, and LaTeX delimited with `$...$`, `$$...$$`, `\(...\)`, or `\[...\]`.
2. Resolve script paths from this `SKILL.md`, not from the target project. Use the wrapper so Python and Node are discovered automatically:

   ```powershell
   $skill = Join-Path $HOME ".agents\skills\md-to-pdf"
   & (Join-Path $skill "scripts\export.ps1") `
     -Source "D:\path\to\notes" `
     -OutputDir "D:\path\to\pdf"
   ```

   The source may be one Markdown file or a directory. A single file keeps its original stem unless `-Name` is supplied. For a directory of files named `第1章…`, `第2章…`, outputs use `chapter-01.pdf`, `chapter-02.pdf`, and so on.

3. Customize only what the project needs. `-Css` replaces the bundled style, `-Name` renames a single-file export, and `-PageSize`, `-Landscape`, and `-Offline` control printing:

   ```powershell
   & (Join-Path $skill "scripts\export.ps1") `
     -Source "D:\path\to\report.md" `
     -OutputDir "D:\path\to\pdf" `
     -Name "report" `
     -Css "D:\path\to\custom.css" `
     -PageSize Letter `
     -Landscape `
     -Offline
   ```

   `-Offline` is appropriate only when all images and linked local assets are available. MathJax itself is bundled and never requires the network.

4. For a course-note preset, pass metadata rather than changing the scripts:

   ```powershell
   & (Join-Path $skill "scripts\export.ps1") `
     -Source "<path-to-course-notes>" `
     -OutputDir "output/pdf" `
     -SeriesLabel "COURSE NOTES · Thermodynamics & Statistical Physics" `
     -SeriesNote "汪志诚《热力学·统计物理》（第六版）" `
     -HeaderLeft "THERMODYNAMICS & STATISTICAL PHYSICS" `
     -HeaderRight "课程笔记" `
     -FooterLeft "example.com"
   ```

5. Verify every first page and at least one formula-dense page per batch. Render pages with Poppler when available:

   ```powershell
   pdftoppm -png -r 110 -f 1 -l 1 input.pdf preview
   ```

6. Check for unfinished placeholders, missing formulas, horizontal overflow, clipped tables or images, broken glyphs, and sensitive identifiers. Do not report completion from a successful command alone.

## Critical Requirements

- Protect math spans before running the Markdown parser. Otherwise underscores, asterisks, backslashes, and table pipes inside formulas can be corrupted.
- Preserve single newlines inside blockquotes as `<br>` without enabling global line breaks.
- Load the bundled `assets/tex-svg-full.js` and wait for `MathJax.startup.promise`. This full build keeps TeX extensions such as `\boldsymbol` available offline. MathJax CHTML can look correct in the browser while printing as blank or malformed Type 3 glyphs in Edge.
- Keep formulas vector-based. Do not rasterize the page or formulas unless the user explicitly requests an image-like result.
- Preserve the original Markdown. Write PDFs and intermediate HTML to separate output/build directories.
- Rewrite relative image and local-link targets against the source Markdown directory so nested projects and folder names with spaces remain valid after HTML is moved into the build directory.
- Keep `break-inside: avoid` on equations, table rows, code blocks, images, and callouts. Use `thead { display: table-header-group; }` so wide tables repeat their headers across pages.
- If publishing to a website, replace public `.md` attachment links with `.pdf`, remove publicly served Markdown copies only when the user wants PDF-only distribution, and bump the site asset version.

## Resources

- `scripts/export.ps1` is the normal one-command entry point and discovers a usable Python/Node runtime.
- `scripts/build_html.py` converts Markdown, protects formulas/code, rewrites local assets, applies CSS, and writes a manifest.
- `scripts/print_pdf.cjs` uses local MathJax SVG plus Playwright/Edge, checks for MathJax errors, and prints PDFs.
- `assets/note-style.css` is the retained default layout; override it with `-Css` instead of editing scripts for project-specific styles.
- `assets/tex-svg-full.js` is a self-contained MathJax 3.2.2 TeX-SVG build; `assets/MATHJAX-LICENSE.txt` is its Apache-2.0 license.

When Python cannot import `markdown`, `build_html.py` installs a compatible copy into `%LOCALAPPDATA%\Codex\md-to-pdf\python`. The print script first looks for Playwright in the project and the user's pnpm store, then uses system Edge/Chrome.
