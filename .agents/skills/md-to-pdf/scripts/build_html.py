from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


SKILL_DIR = Path(__file__).resolve().parents[1]
STYLE_PATH = SKILL_DIR / "assets" / "note-style.css"
MATHJAX_PATH = SKILL_DIR / "assets" / "tex-svg-full.js"


def load_markdown():
    try:
        return importlib.import_module("markdown")
    except ModuleNotFoundError:
        cache_root = Path(
            os.environ.get(
                "LOCALAPPDATA",
                str(Path.home() / "AppData" / "Local"),
            )
        ) / "Codex" / "md-to-pdf" / "python"
        sys.path.insert(0, str(cache_root))
        try:
            return importlib.import_module("markdown")
        except ModuleNotFoundError:
            cache_root.mkdir(parents=True, exist_ok=True)
            print(f"Installing Markdown parser into {cache_root}", file=sys.stderr)
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--target",
                    str(cache_root),
                    "markdown>=3.5,<4",
                ]
            )
            importlib.invalidate_caches()
            sys.path.insert(0, str(cache_root))
            return importlib.import_module("markdown")


markdown = load_markdown()


def natural_key(path: Path) -> list[object]:
    return [
        (0, int(part)) if part.isdigit() else (1, part.casefold())
        for part in re.split(r"(\d+)", str(path))
    ]


def strip_frontmatter(text: str) -> str:
    return re.sub(r"\A---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)


def protect_fragments(text: str) -> tuple[str, list[tuple[str, str]]]:
    protected: list[tuple[str, str]] = []

    def store(kind: str, rendered: str) -> str:
        token = f"CODEXPROTECTEDTOKEN{len(protected):05d}"
        protected.append((kind, rendered))
        return token

    def code_block(match: re.Match[str]) -> str:
        language = match.group(1).strip()
        code = match.group(2).rstrip("\n")
        class_name = f' class="language-{html.escape(language)}"' if language else ""
        rendered = f"<pre><code{class_name}>{html.escape(code)}</code></pre>"
        return f"\n\n{store('code', rendered)}\n\n"

    text = re.sub(r"(?ms)^```([^\n]*)\n(.*?)^```\s*$", code_block, text)

    def inline_code(match: re.Match[str]) -> str:
        return store("code-inline", f"<code>{html.escape(match.group(1))}</code>")

    text = re.sub(r"(?<!`)`([^`\n]+)`(?!`)", inline_code, text)

    def display_math(match: re.Match[str]) -> str:
        formula = html.escape(match.group(1).strip())
        rendered = f'<div class="math display">\\[{formula}\\]</div>'
        return f"\n\n{store('display', rendered)}\n\n"

    text = re.sub(r"(?s)\$\$(.+?)\$\$", display_math, text)
    text = re.sub(
        r"(?s)\\\[(.+?)\\\]",
        display_math,
        text,
    )

    def inline_math(match: re.Match[str]) -> str:
        formula = html.escape(match.group(1))
        return store("inline", f'<span class="math inline">\\({formula}\\)</span>')

    text = re.sub(r"(?<!\\)\$(?!\$)([^\n$]+?)(?<!\\)\$", inline_math, text)
    text = re.sub(
        r"(?s)\\\((.+?)\\\)",
        inline_math,
        text,
    )
    return text, protected


def restore_fragments(rendered: str, protected: list[tuple[str, str]]) -> str:
    for index, (kind, value) in enumerate(protected):
        token = f"CODEXPROTECTEDTOKEN{index:05d}"
        if kind == "display":
            rendered = re.sub(
                rf"<p>\s*{token}\s*</p>",
                lambda _match, replacement=value: replacement,
                rendered,
                flags=re.IGNORECASE,
            )
        rendered = rendered.replace(token, value)
    return rendered


def safe_stem(value: str, *, replace_spaces: bool = True) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value)
    value = value.strip()
    if replace_spaces:
        value = re.sub(r"\s+", "-", value)
    value = value.strip(". -")
    return value or "document"


def preserve_blockquote_linebreaks(rendered: str) -> str:
    def update_blockquote(match: re.Match[str]) -> str:
        content = match.group(2)

        def update_paragraph(paragraph: re.Match[str]) -> str:
            inner = paragraph.group(2).replace("\n", "<br>\n")
            return f"{paragraph.group(1)}{inner}{paragraph.group(3)}"

        content = re.sub(
            r"(?s)(<p\b[^>]*>)(.*?)(</p>)",
            update_paragraph,
            content,
        )
        return f"{match.group(1)}{content}{match.group(3)}"

    return re.sub(
        r"(?s)(<blockquote\b[^>]*>)(.*?)(</blockquote>)",
        update_blockquote,
        rendered,
    )


def absolute_local_uri(source_dir: Path, value: str) -> str:
    decoded = html.unescape(value)
    parsed = urlsplit(decoded)
    if parsed.scheme or parsed.netloc or not parsed.path or decoded.startswith("#"):
        return value
    candidate = Path(unquote(parsed.path))
    if not candidate.is_absolute():
        candidate = source_dir / candidate
    candidate = candidate.resolve()
    if not candidate.exists():
        return value
    suffix = f"?{parsed.query}" if parsed.query else ""
    suffix += f"#{parsed.fragment}" if parsed.fragment else ""
    return candidate.as_uri() + suffix


def rewrite_local_references(rendered: str, source_dir: Path) -> str:
    media_pattern = re.compile(
        r'(?i)(<(?:img|video|audio|source)\b[^>]*?\b(?:src|poster)=["\'])([^"\']+)(["\'])'
    )
    link_pattern = re.compile(r'(?i)(<a\b[^>]*?\bhref=["\'])([^"\']+)(["\'])')

    def rewrite(match: re.Match[str]) -> str:
        return (
            f"{match.group(1)}"
            f"{absolute_local_uri(source_dir, match.group(2))}"
            f"{match.group(3)}"
        )

    return link_pattern.sub(rewrite, media_pattern.sub(rewrite, rendered))


def discover_sources(source: Path, recursive: bool) -> list[Path]:
    if source.is_file():
        if source.suffix.lower() != ".md":
            raise ValueError(f"Expected a Markdown file: {source}")
        return [source]
    if not source.is_dir():
        raise ValueError(f"Source does not exist: {source}")
    pattern = "**/*.md" if recursive else "*.md"
    excluded = {".git", ".obsidian", "node_modules", ".md-to-pdf-build"}
    files = [
        path
        for path in source.glob(pattern)
        if path.is_file() and not any(part in excluded for part in path.parts)
    ]
    files.sort(key=natural_key)
    if not files:
        raise ValueError(f"No Markdown files found under {source}")
    return files


def assign_stems(source: Path, files: list[Path], used: set[str]) -> list[str]:
    chapter_numbers = [re.search(r"第\s*0*(\d+)\s*章", path.name) for path in files]
    use_chapters = source.is_dir() and all(chapter_numbers)
    stems: list[str] = []
    for index, path in enumerate(files, start=1):
        if use_chapters:
            stem = f"chapter-{int(chapter_numbers[index - 1].group(1)):02d}"
        elif source.is_dir():
            relative = path.relative_to(source).with_suffix("").as_posix()
            stem = safe_stem(relative.replace("/", "-"))
        else:
            stem = safe_stem(path.stem, replace_spaces=False)
        base = stem
        suffix = 2
        while stem in used:
            stem = f"{base}-{suffix}"
            suffix += 1
        used.add(stem)
        stems.append(stem)
    return stems


def make_page(title: str, body: str, style: str, args: argparse.Namespace) -> str:
    template = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__TITLE__</title>
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['\\(', '\\)']],
        displayMath: [['\\[', '\\]']],
        processEscapes: true,
        tags: 'ams'
      },
      svg: { fontCache: 'local', scale: 0.94 },
      startup: { pageReady: () => MathJax.startup.defaultPageReady() }
    };
  </script>
  <script defer src="__MATHJAX_URI__"></script>
  <style>__STYLE__</style>
</head>
<body>
  <div class="document-meta">
    <span><strong>__SERIES_LABEL__</strong></span>
    <span>__SERIES_NOTE__</span>
  </div>
  __BODY__
</body>
</html>
"""
    replacements = {
        "__TITLE__": html.escape(title),
        "__STYLE__": style,
        "__SERIES_LABEL__": html.escape(args.series_label),
        "__SERIES_NOTE__": html.escape(args.series_note),
        "__MATHJAX_URI__": MATHJAX_PATH.resolve().as_uri(),
        "__BODY__": body,
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    return template


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Markdown notes to styled print HTML and a PDF manifest."
    )
    parser.add_argument("source", help="Markdown file or directory to convert")
    parser.add_argument(
        "--output-dir",
        default="output/pdf",
        help="Folder for final PDFs (default: output/pdf)",
    )
    parser.add_argument(
        "--build-dir",
        default=".md-to-pdf-build",
        help="Folder for HTML and manifest (default: .md-to-pdf-build)",
    )
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument(
        "--name",
        help="Output stem override; valid only with a single Markdown file",
    )
    parser.add_argument(
        "--css",
        help="Optional CSS file that replaces the bundled note style",
    )
    parser.add_argument(
        "--page-size",
        choices=["A4", "A3", "Letter", "Legal"],
        default="A4",
    )
    parser.add_argument("--landscape", action="store_true")
    parser.add_argument(
        "--series-label",
        default="COURSE NOTES · Markdown collection",
        help="Blue series label in the first-page metadata band",
    )
    parser.add_argument(
        "--series-note",
        default="Exported with md-to-pdf",
        help="Metadata shown at the right side of the first-page band",
    )
    parser.add_argument("--header-left", default="Markdown notes")
    parser.add_argument("--header-right", default="Course notes")
    parser.add_argument("--footer-left", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    build_dir = Path(args.build_dir).expanduser().resolve()
    html_dir = build_dir / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not MATHJAX_PATH.is_file():
        raise ValueError(f"Bundled MathJax file is missing: {MATHJAX_PATH}")
    style_path = Path(args.css).expanduser().resolve() if args.css else STYLE_PATH
    if not style_path.is_file():
        raise ValueError(f"CSS file does not exist: {style_path}")
    style = style_path.read_text(encoding="utf-8")

    files = discover_sources(source, recursive=not args.no_recursive)
    if args.name and len(files) != 1:
        raise ValueError("--name can only be used when converting exactly one Markdown file")
    stems = (
        [safe_stem(re.sub(r"(?i)\.pdf$", "", args.name), replace_spaces=False)]
        if args.name
        else assign_stems(source, files, used=set())
    )
    items: list[dict[str, object]] = []

    for chapter, (markdown_path, stem) in enumerate(zip(files, stems), start=1):
        text = markdown_path.read_text(encoding="utf-8").replace("\r\n", "\n")
        text = strip_frontmatter(text)
        title_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
        title = title_match.group(1).strip() if title_match else markdown_path.stem

        protected_text, protected = protect_fragments(text)
        body = markdown.markdown(
            protected_text,
            extensions=[
                "tables",
                "sane_lists",
                "footnotes",
                "attr_list",
                "md_in_html",
            ],
            output_format="html5",
        )
        body = preserve_blockquote_linebreaks(body)
        body = restore_fragments(body, protected)
        body = rewrite_local_references(body, markdown_path.parent)

        html_path = html_dir / f"{stem}.html"
        html_path.write_text(make_page(title, body, style, args), encoding="utf-8")
        pdf_path = output_dir / f"{stem}.pdf"
        items.append(
            {
                "index": chapter,
                "stem": stem,
                "title": title,
                "source": str(markdown_path),
                "html": str(html_path),
                "pdf": str(pdf_path),
                "protectedFragments": len(protected),
            }
        )
        print(f"HTML {stem}: {title} ({len(protected)} formulas/code blocks)")

    manifest = {
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": str(source),
        "metadata": {
            "seriesLabel": args.series_label,
            "seriesNote": args.series_note,
            "headerLeft": args.header_left,
            "headerRight": args.header_right,
            "footerLeft": args.footer_left,
            "pageSize": args.page_size,
            "landscape": args.landscape,
            "style": str(style_path),
            "mathjax": str(MATHJAX_PATH),
        },
        "items": items,
    }
    manifest_path = build_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Manifest: {manifest_path}")
    print(f"PDF output: {output_dir}")


if __name__ == "__main__":
    main()
