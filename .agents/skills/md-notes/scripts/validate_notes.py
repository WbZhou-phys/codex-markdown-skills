#!/usr/bin/env python3
"""Static checks for Obsidian Markdown course notes."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


INLINE_MATH = re.compile(r"(?<!\\)\$([^$\r\n]+?)(?<!\\)\$")
DISPLAY_MATH = re.compile(r"\$\$([\s\S]*?)\$\$")
TAG = re.compile(r"\\tag\{([^}]+)\}")
IMAGE = re.compile(r"!\[[^\]]*\]\((?:<([^>]+)>|([^)\s]+))")
HTML_ENTITY = re.compile(r"&#(?:x[0-9A-Fa-f]+|\d+);|&(?:gt|lt|amp|quot);")
TEXTBOOK_SUMMARY = (
    "### 一、公式速查",
    "### 二、概念脉络",
    "### 三、易错点",
    "### 四、名词中英对照",
)


def strip_fences(text: str) -> str:
    return re.sub(r"(?ms)^\s*```.*?^\s*```\s*$", "", text)


def detect_profile(path: Path, text: str) -> str:
    lowered = str(path).lower()
    if re.search(r"(?m)^讲次\s*:", text) or "固体物理" in lowered:
        return "solid"
    if "\\gr\\" in lowered or "/gr/" in lowered or re.search(
        r"(?m)^\s*-\s*GR\s*$", text
    ):
        return "gr"
    if "热统" in lowered or re.search(r"(?m)^\s*-\s*热统\s*$", text):
        return "thermo"
    return "generic"


def check_math(lines: list[str], errors: list[str]) -> None:
    in_fence = False
    in_display = False
    blockquote_display = False

    for number, line in enumerate(lines, start=1):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        is_blockquote = bool(re.match(r"^\s*>", line))
        if is_blockquote:
            display_marks = len(re.findall(r"(?<!\\)\$\$", line))
            if display_marks % 2:
                blockquote_display = not blockquote_display
        elif blockquote_display:
            errors.append(
                f"line {number}: display math started in a blockquote but this "
                "continuation line lacks the > marker"
            )

        work = line
        if in_display:
            if "$$" not in work:
                continue
            work = work.split("$$", 1)[1]
            in_display = False

        work, _ = re.subn(r"(?<!\\)\$\$.*?(?<!\\)\$\$", "", work)
        remaining_display = len(re.findall(r"(?<!\\)\$\$", work))
        if remaining_display % 2:
            in_display = True
            work = re.sub(r"(?<!\\)\$\$.*$", "", work)

        work = INLINE_MATH.sub("", work)
        if re.search(r"(?<!\\)\$", work):
            errors.append(
                f"line {number}: unresolved inline-math delimiter; keep $...$ on one line"
            )
        if re.search(r"\\[\[\]()]", work):
            errors.append(
                f"line {number}: TeX document delimiter outside math; use $...$ or $$...$$"
            )
        if re.search(r"\\[A-Za-z]+", work):
            errors.append(
                f"line {number}: TeX command appears outside a math span"
            )

    if blockquote_display:
        errors.append("unclosed display-math delimiter inside a blockquote")


def check_tags(text: str, errors: list[str]) -> None:
    tags = TAG.findall(text)
    duplicates = sorted({tag for tag in tags if tags.count(tag) > 1})
    if duplicates:
        errors.append("duplicate formula tags: " + ", ".join(duplicates))

    for block in DISPLAY_MATH.findall(text):
        for aligned in re.findall(
            r"\\begin\{aligned\}([\s\S]*?)\\end\{aligned\}", block
        ):
            if "\\tag{" in aligned:
                errors.append("\\tag{...} occurs inside an aligned environment")

        block_tags = TAG.findall(block)
        if len(block_tags) > 1 and not re.search(
            r"\\begin\{align\*?\}", block
        ):
            errors.append(
                "multiple \\tag commands in one display block without an align environment"
            )


def count_unescaped_pipes(text: str) -> int:
    return len(re.findall(r"(?<!\\)\|", text))


def check_tables(lines: list[str], errors: list[str]) -> None:
    table: list[tuple[int, str]] = []
    in_fence = False

    def flush() -> None:
        if not table:
            return
        counts = [count_unescaped_pipes(INLINE_MATH.sub("", line)) for _, line in table]
        if len(set(counts)) > 1:
            errors.append(
                f"lines {table[0][0]}-{table[-1][0]}: inconsistent Markdown table columns"
            )
        table.clear()

    for number, line in enumerate(lines, start=1):
        if re.match(r"^\s*```", line):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("|"):
            table.append((number, line))
            for formula in INLINE_MATH.findall(line):
                if "|" in formula:
                    errors.append(
                        f"line {number}: literal | inside inline math in a Markdown table; "
                        r"use \lvert ... \rvert"
                    )
        else:
            flush()
    flush()


def check_images(path: Path, text: str, errors: list[str]) -> None:
    without_fences = strip_fences(text)
    for match in IMAGE.finditer(without_fences):
        target = match.group(1) or match.group(2) or ""
        target = unquote(target).strip()
        if not target or re.match(r"^(?:[a-z]+:|#)", target, re.IGNORECASE):
            continue
        image_path = (path.parent / target).resolve()
        if not image_path.exists():
            line = without_fences.count("\n", 0, match.start()) + 1
            errors.append(f"line {line}: image target does not exist: {target}")


def check_profile(path: Path, text: str, profile: str, errors: list[str]) -> str:
    if profile == "auto":
        profile = detect_profile(path, text)

    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        errors.append("missing YAML frontmatter")
    if not re.search(r"(?m)^tags\s*:", text):
        errors.append("frontmatter is missing tags")
    if len(re.findall(r"(?m)^#\s+", text)) != 1:
        errors.append("note must contain exactly one level-1 heading")
    if "TODO" in text:
        errors.append("unfinished TODO placeholder remains")

    if profile in {"thermo", "gr", "textbook"}:
        if "## 本章地图" not in text:
            errors.append("missing ## 本章地图")
        if "## 本章小结" not in text:
            errors.append("missing ## 本章小结")
        for heading in TEXTBOOK_SUMMARY:
            if heading not in text:
                errors.append(f"missing summary subsection: {heading}")
        if not re.search(r"(?m)^created\s*:", text):
            errors.append("textbook profile requires created: in frontmatter")
        forbidden = re.findall(
            r"(?m)^#{1,6}\s+.*(?:自测题|习题索引).*$", strip_fences(text)
        )
        if forbidden:
            errors.append("textbook profile must not include self-test/exercise-index headings")

    if profile == "solid":
        if "## 0. 一页速览" not in text:
            errors.append("solid-state profile requires ## 0. 一页速览")
        if not re.search(r"(?m)^(?:日期|更新)\s*:", text):
            errors.append("solid-state profile requires 日期: or 更新: in frontmatter")
        if not re.search(r"(?m)^讲次\s*:", text):
            errors.append("solid-state profile requires 讲次: in frontmatter")

    return profile


def validate(path: Path, requested_profile: str) -> tuple[str, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return requested_profile, [f"cannot read as UTF-8: {exc}"]

    errors: list[str] = []
    lines = text.splitlines()
    profile = check_profile(path, text, requested_profile, errors)
    check_math(lines, errors)
    check_tags(text, errors)
    check_tables(lines, errors)
    check_images(path, text, errors)

    in_fence = False
    for number, line in enumerate(lines, start=1):
        if re.match(r"^\s*```", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if HTML_ENTITY.search(line):
            errors.append(f"line {number}: HTML entity in Markdown prose")

    return profile, errors


def iter_notes(paths: list[str]) -> list[Path]:
    notes: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            notes.extend(
                item
                for item in sorted(path.rglob("*.md"))
                if ".obsidian" not in item.parts
            )
        else:
            notes.append(path)
    return notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Markdown file(s) or directory")
    parser.add_argument(
        "--profile",
        choices=("auto", "thermo", "gr", "solid", "textbook", "generic"),
        default="auto",
    )
    args = parser.parse_args()

    notes = iter_notes(args.paths)
    if not notes:
        print("No Markdown notes found.", file=sys.stderr)
        return 1

    failures = 0
    for note in notes:
        if not note.exists():
            print(f"FAIL {note}: file does not exist", file=sys.stderr)
            failures += 1
            continue
        profile, errors = validate(note, args.profile)
        if errors:
            failures += 1
            print(f"FAIL {note} [{profile}]")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {note} [{profile}]")

    if failures:
        print(f"\n{failures} note(s) failed validation.", file=sys.stderr)
        return 1
    print(f"\nValidated {len(notes)} note(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
