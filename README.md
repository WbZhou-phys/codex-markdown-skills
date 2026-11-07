# Codex Markdown Skills

Two skills for building rigorous Markdown study notes and exporting them as polished, formula-safe PDFs.

This repository follows the open [Agent Skills](https://agentskills.io/) layout and can be used as a repository-scoped or user-level Codex skill collection.

## Included skills

### `md-notes`

Creates and revises Obsidian Markdown course notes from textbooks, lecture slides, and existing note conventions. It covers source inventories, derivations, figure decisions, Obsidian formula syntax, chapter summaries, and a static validation script with generic, textbook, general-relativity, and solid-state profiles.

### `md-to-pdf`

Converts one Markdown file or a directory of notes into styled PDFs without changing the source files. It protects LaTeX before parsing Markdown, renders formulas with a bundled offline MathJax SVG build, rewrites local assets, repeats table headers across pages, and checks for leaked placeholders or formula-rendering errors before printing.

## Repository layout

```text
.agents/skills/
├── md-notes/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/
│   ├── references/
│   └── scripts/validate_notes.py
└── md-to-pdf/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── assets/
    ├── scripts/
    ├── package.json
    └── requirements.txt
```

## Use with Codex

### Repository-scoped

Clone this repository and open it in Codex. Codex discovers skills under `.agents/skills/` automatically:

```powershell
git clone https://github.com/WbZhou-phys/codex-markdown-skills.git
cd codex-markdown-skills
```

Invoke a skill explicitly with `$md-notes` or `$md-to-pdf`, or let Codex select one based on your request.

### User-level installation

Codex supports symlinked skill folders. Link both skills into your user skill directory.

Windows PowerShell:

```powershell
$source = "C:\path\to\codex-markdown-skills\.agents\skills"
$target = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force $target | Out-Null

foreach ($name in @("md-notes", "md-to-pdf")) {
    New-Item -ItemType Junction -Path (Join-Path $target $name) `
        -Target (Join-Path $source $name)
}
```

macOS or Linux:

```bash
source="$PWD/.agents/skills"
target="$HOME/.agents/skills"
mkdir -p "$target"
ln -s "$source/md-notes" "$target/md-notes"
ln -s "$source/md-to-pdf" "$target/md-to-pdf"
```

Restart Codex if the skills do not appear immediately.

## Dependencies

`md-notes` requires Python 3.10 or newer.

`md-to-pdf` requires:

- Python 3.10 or newer;
- Node.js 20 or newer;
- Playwright for Node.js;
- Microsoft Edge, Google Chrome, or Chromium.

Install the PDF dependencies from the skill directory:

```powershell
cd .agents\skills\md-to-pdf
python -m pip install -r requirements.txt
npm install  # or: pnpm install
```

`build_html.py` also attempts to install the Python Markdown parser into a local cache when it is not already available. Playwright drives an installed Edge/Chrome executable, so no separate browser download is normally required.

## Example

Validate a note:

```powershell
$skill = Join-Path $HOME ".agents\skills\md-notes"
python (Join-Path $skill "scripts\validate_notes.py") `
  "D:\Notes\Physics\chapter-01.md" --profile auto
```

Export a Markdown file to PDF:

```powershell
$skill = Join-Path $HOME ".agents\skills\md-to-pdf"
& (Join-Path $skill "scripts\export.ps1") `
  -Source "D:\Notes\Physics\chapter-01.md" `
  -OutputDir "D:\Notes\PDF"
```

## Third-party notices

The bundled MathJax build in `.agents/skills/md-to-pdf/assets/` is distributed under the Apache License 2.0; see `MATHJAX-LICENSE.txt` in the same directory.

## License

MIT. See [LICENSE](LICENSE).
