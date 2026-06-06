#!/usr/bin/env python3
"""One-off helper: convert HTML post body to Markdown for docs migration."""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


def inline_text(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return unescape(str(node))
    if not isinstance(node, Tag):
        return ""
    if node.name == "br":
        return "\n"
    if node.name == "strong":
        return f"**{''.join(inline_text(c) for c in node.children)}**"
    if node.name == "em":
        return f"*{''.join(inline_text(c) for c in node.children)}*"
    if node.name == "code":
        return f"`{''.join(inline_text(c) for c in node.children)}`"
    if node.name == "a":
        return "".join(inline_text(c) for c in node.children)
    return "".join(inline_text(c) for c in node.children)


def block_to_md(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        text = unescape(str(node)).strip()
        return text if text else ""

    if not isinstance(node, Tag):
        return ""

    name = node.name

    if name == "h2":
        return f"## {inline_text(node).strip()}\n"
    if name == "h3":
        return f"### {inline_text(node).strip()}\n"
    if name == "p":
        return f"{inline_text(node).strip()}\n"
    if name == "blockquote":
        lines = []
        for child in node.children:
            text = block_to_md(child).strip()
            if text:
                lines.extend(f"> {line}" if line else ">" for line in text.splitlines())
        return "\n".join(lines) + "\n"
    if name == "ul":
        items = []
        for li in node.find_all("li", recursive=False):
            items.append(f"- {inline_text(li).strip()}")
        return "\n".join(items) + "\n"
    if name == "ol":
        items = []
        for i, li in enumerate(node.find_all("li", recursive=False), 1):
            items.append(f"{i}. {inline_text(li).strip()}")
        return "\n".join(items) + "\n"
    if name == "table":
        rows = []
        for tr in node.find_all("tr"):
            cells = [inline_text(cell).strip() for cell in tr.find_all(["th", "td"])]
            rows.append("| " + " | ".join(cells) + " |")
        if len(rows) >= 2:
            sep = "| " + " | ".join("---" for _ in rows[0].split("|")[1:-1]) + " |"
            rows.insert(1, sep)
        return "\n".join(rows) + "\n"
    if name == "figure":
        pre = node.find("pre")
        if pre:
            code = pre.get_text("\n").rstrip()
            return f"```\n{code}\n```\n"
        return ""
    if name in {"div", "tbody", "thead"}:
        return "".join(block_to_md(c) for c in node.children)

    return "".join(block_to_md(c) for c in node.children)


def html_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    parts = [block_to_md(child).rstrip() for child in soup.children]
    text = "\n\n".join(part for part in parts if part.strip())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    content = src.read_text(encoding="utf-8")
    if content.startswith("---"):
        _, body = content.split("---", 2)[1:]
        body = body.strip()
    else:
        body = content
    dst.parent.mkdir(parents=True, exist_ok=True)
    front_matter = """---
title: 基准环境与最小集环境：概念与实践
date: 2026-06-05 10:00:00
categories:
  - records
tags:
  - 环境管理
  - DevOps
  - 微服务
---

"""
    dst.write_text(front_matter + html_to_markdown(body), encoding="utf-8")
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
