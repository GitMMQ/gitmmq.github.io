#!/usr/bin/env python3
"""Import newly published markdown articles into Hexo source."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = Path(__file__).resolve().parent / "source" / "_posts"


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_post(
    filename: str,
    title: str,
    date: str,
    category: str,
    tags: list[str],
    body: str,
) -> None:
    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"date: {date}",
        "categories:",
        f'  - {yaml_quote(category)}',
        "tags:",
    ]
    lines.extend(f"  - {yaml_quote(tag)}" for tag in tags)
    lines.append("---")
    (OUTPUT / filename).write_text("\n".join(lines) + "\n\n" + body.strip() + "\n", encoding="utf-8")


def import_claude_code() -> None:
    title = "Claude Code 全面介绍：架构设计、应用与优缺点"
    slug = hashlib.md5(title.encode()).hexdigest()[:8]
    body = (ROOT / "docs/claude-code-intro-bilingual.md").read_text(encoding="utf-8")
    write_post(
        f"{slug}.md",
        title,
        "2026-06-05 18:00:00",
        "mechine",
        ["AI Agent", "Claude Code", "Anthropic"],
        body,
    )


def import_baseline_env() -> None:
    from migrate_from_static import migrate_post

    migrate_post(ROOT / "posts/c8f01db4.html")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    import_claude_code()
    import_baseline_env()
    print("Imported Claude Code and baseline environment posts")


if __name__ == "__main__":
    main()
