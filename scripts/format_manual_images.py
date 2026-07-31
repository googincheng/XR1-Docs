#!/usr/bin/env python3
"""Normalize XRecer manual image sizing and placement without rewriting prose."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from PIL import Image


IMG_RE = re.compile(
    r'<img src="/img/manual/(?P<name>image\d+\.png)" '
    r'alt="(?P<alt>[^"]+)" (?P<size>width|height)="(?P<value>\d+)"\s*/>'
)
LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>(?:\d+\.\s+|-\s+))(?P<body>.*)$")


def image_width(image_path: Path, name: str, current: int) -> tuple[int, bool]:
    """Return display width and whether the image should remain inline."""
    with Image.open(image_path / name) as image:
        natural_width, natural_height = image.size

    longest_edge = max(natural_width, natural_height)
    if longest_edge <= 90:
        return (24 if longest_edge <= 65 else 48), True
    if longest_edge <= 150:
        return 64, True
    if natural_width <= 400 and natural_height <= 400:
        return min(natural_width, 300), False
    return min(current if current >= 100 else natural_width, 600), False


def format_tag(match: re.Match[str], image_path: Path) -> tuple[str, bool]:
    current = int(match.group("value"))
    width, inline = image_width(image_path, match.group("name"), current)
    class_name = "manual-inline-icon" if inline else "manual-figure"
    tag = (
        f'<img className="{class_name}" '
        f'src="/img/manual/{match.group("name")}" '
        f'alt="{match.group("alt")}" width="{width}"/>'
    )
    return tag, inline


def format_line(line: str, image_path: Path) -> list[str]:
    matches = list(IMG_RE.finditer(line))
    if not matches:
        return [line.rstrip()]

    rebuilt = line
    formatted: list[tuple[str, bool]] = []
    for match in reversed(matches):
        tag, inline = format_tag(match, image_path)
        rebuilt = rebuilt[: match.start()] + tag + rebuilt[match.end() :]
        formatted.insert(0, (tag, inline))

    # Icon-only groups are intentionally kept on one row.
    if all(inline for _, inline in formatted):
        return [rebuilt.rstrip()]

    # A line containing only figures becomes one centered block per image.
    remainder = rebuilt
    for tag, _ in formatted:
        remainder = remainder.replace(tag, "")
    if not remainder.strip():
        return [tag for tag, _ in formatted]

    # Move large screenshots out of prose/list text and place them immediately
    # after the sentence or step that introduces them.
    text = rebuilt
    figures: list[str] = []
    for tag, inline in formatted:
        if not inline:
            text = text.replace(tag, "")
            figures.append(tag)
    text = re.sub(r"\s{2,}", " ", text).rstrip()

    list_match = LIST_RE.match(text)
    if list_match:
        indent = list_match.group("indent")
        figure_indent = indent + "    "
        return [text, "", *(figure_indent + figure for figure in figures)]

    return [text.strip(), "", *figures]


def format_document(source: str, image_path: Path) -> str:
    output: list[str] = []
    for line in source.splitlines():
        output.extend(format_line(line, image_path))

    text = "\n".join(output)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: format_manual_images.py DOCS_DIR IMAGE_DIR")

    docs_dir = Path(sys.argv[1])
    image_dir = Path(sys.argv[2])
    changed = 0
    for document in sorted(docs_dir.glob("*.mdx")):
        source = document.read_text(encoding="utf-8")
        formatted = format_document(source, image_dir)
        if formatted != source:
            document.write_text(formatted, encoding="utf-8")
            changed += 1
    print(f"Formatted images in {changed} MDX files")


if __name__ == "__main__":
    main()
