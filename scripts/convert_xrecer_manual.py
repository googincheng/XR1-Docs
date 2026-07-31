#!/usr/bin/env python3
"""Convert the Pandoc-exported XRecer manual into Docusaurus MDX documents."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


SLUGS = {
    "Overview": "overview",
    "Quick Start": "quick-start",
    "FX Chain": "fx-chain",
    "Live View": "live-view",
    "File Manager": "file-manager",
    "LOOPER": "looper",
    "Global EQ": "global-eq",
    "Global IO": "global-io",
    "TUNER & BPM": "tuner-bpm",
    "CapX": "capx",
    "MIDI": "midi",
    "Expression Pedal": "expression-pedal",
    "FX LOOP": "fx-loop",
    "IR Loader": "ir-loader",
    "设置": "settings",
    "Effect清单": "effect-list",
    "Overdrive": "overdrive",
    "异常处理": "troubleshooting",
    "产品规格(待技术补齐)": "specifications",
    "IO Spec": "io-spec",
    "声明（待补充）": "notices",
}


def normalize_title(raw: str) -> tuple[str, str | None]:
    image = re.search(r"<img\b[^>]*>", raw)
    title = re.sub(r"<img\b[^>]*>", "", raw).strip()
    return title, image.group(0) if image else None


def convert_images(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        source = re.search(r'src="[^"]*/(image\d+\.[^"]+)"', tag)
        if not source:
            return ""
        filename = source.group(1)
        return (
            f'<img src="/img/manual/{filename}" '
            'alt="XRecer 操作界面" width="600"/>'
        )

    return re.sub(r"<img\b[^>]*?/?>", replace, text)


def clean_body(text: str) -> str:
    text = convert_images(text)
    text = re.sub(r"(?m)^###\s+(?=!\[)", "", text)
    text = re.sub(r"\[<u>(.*?)</u>\]\(\\l\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(\\l\)", r"\1", text)
    text = text.replace('class="odd"', 'className="odd"')
    text = text.replace('class="even"', 'className="even"')
    text = text.replace(" ", " ")
    text = re.sub(r"(?m)^\s*<!-- -->\s*$", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_chapters(markdown: str) -> list[tuple[str, str]]:
    lines = markdown.splitlines()
    starts: list[tuple[int, str, str | None]] = []
    for index in range(1, len(lines)):
        if re.fullmatch(r"=+", lines[index].strip()):
            title, leading_image = normalize_title(lines[index - 1])
            if title in SLUGS:
                starts.append((index - 1, title, leading_image))

    chapters: list[tuple[str, str]] = []
    for position, (start, title, leading_image) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        body_lines = lines[start + 2 : end]

        converted: list[str] = []
        cursor = 0
        while cursor < len(body_lines):
            if cursor + 1 < len(body_lines) and re.fullmatch(
                r"-+", body_lines[cursor + 1].strip()
            ):
                heading, heading_image = normalize_title(body_lines[cursor].strip())
                if heading_image:
                    converted.extend([heading_image, ""])
                converted.extend([f"## {heading}", ""])
                cursor += 2
                continue
            converted.append(body_lines[cursor])
            cursor += 1

        body = "\n".join(converted)
        if leading_image:
            body = f"{leading_image}\n\n{body}"
        chapters.append((title, clean_body(body)))
    return chapters


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "usage: convert_xrecer_manual.py MANUAL.md MEDIA_DIR DOCS_DIR STATIC_DIR"
        )

    source = Path(sys.argv[1])
    media_dir = Path(sys.argv[2])
    docs_dir = Path(sys.argv[3])
    static_dir = Path(sys.argv[4])

    chapters = parse_chapters(source.read_text(encoding="utf-8"))
    if [title for title, _ in chapters] != list(SLUGS):
        raise SystemExit("The detected chapter list does not match the expected manual.")

    docs_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)

    intro = """---
sidebar_position: 1
slug: /intro
title: XRecer XR1 效果器说明书
---

# XRecer XR1 效果器说明书

- **版本：** V0.6.1
- **日期：** 2026年05月

本说明书介绍 XRecer XR1 的硬件接口、快速入门、效果链、演出视图、音频与 MIDI 路由，以及各类效果器参数。
"""
    (docs_dir / "intro.mdx").write_text(intro, encoding="utf-8")

    for index, (title, body) in enumerate(chapters, start=2):
        slug = SLUGS[title]
        frontmatter = (
            "---\n"
            f"sidebar_position: {index}\n"
            f"slug: /{slug}\n"
            f"title: {title}\n"
            "---\n\n"
            f"# {title}\n\n"
        )
        (docs_dir / f"{index - 1:02d}-{slug}.mdx").write_text(
            frontmatter + body + "\n", encoding="utf-8"
        )

    for image in media_dir.glob("image*.*"):
        shutil.copy2(image, static_dir / image.name)

    print(f"Wrote {len(chapters) + 1} MDX files and copied media to {static_dir}")


if __name__ == "__main__":
    main()
