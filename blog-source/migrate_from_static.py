#!/usr/bin/env python3
"""Migrate posts from the legacy static HTML output into Hexo markdown sources."""

from __future__ import annotations

import html
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = ROOT / "posts"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "source" / "_posts"


def extract_meta(soup: BeautifulSoup, prop: str) -> str | None:
    tag = soup.find("meta", property=prop)
    return tag.get("content") if tag and tag.get("content") else None


def extract_title(soup: BeautifulSoup) -> str:
    title_tag = soup.select_one("h1.post-title")
    if title_tag:
        return title_tag.get_text(strip=True)
    og_title = extract_meta(soup, "og:title")
    return og_title or "untitled"


def extract_categories(soup: BeautifulSoup) -> list[str]:
    categories = []
    for link in soup.select('span[itemprop="about"] a[itemprop="url"]'):
        name = link.select_one('[itemprop="name"]')
        if name:
            categories.append(name.get_text(strip=True))
    return categories


def extract_tags(soup: BeautifulSoup) -> list[str]:
    tags = []
    for link in soup.select(".post-tags a[rel='tag']"):
        text = link.get_text(strip=True).lstrip("#").strip()
        if text:
            tags.append(text)
    return tags


def extract_body(soup: BeautifulSoup) -> str:
    body = soup.select_one("div.post-body")
    if not body:
        return ""
    return "".join(str(child) for child in body.children).strip()


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_front_matter(
    title: str,
    date: str | None,
    updated: str | None,
    categories: list[str],
    tags: list[str],
) -> str:
    lines = ["---", f"title: {yaml_quote(title)}", "disableNunjucks: true"]

    if date:
        lines.append(f"date: {date}")
    if updated and updated != date:
        lines.append(f"updated: {updated}")
    if categories:
        lines.append("categories:")
        lines.extend(f"  - {yaml_quote(category)}" for category in categories)
    if tags:
        lines.append("tags:")
        lines.extend(f"  - {yaml_quote(tag)}" for tag in tags)

    lines.append("---")
    return "\n".join(lines)


def migrate_post(html_path: Path) -> None:
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    title = extract_title(soup)
    date = extract_meta(soup, "article:published_time")
    updated = extract_meta(soup, "article:modified_time")
    categories = extract_categories(soup)
    tags = extract_tags(soup)
    body = extract_body(soup)

    slug = html_path.stem
    output_path = OUTPUT_DIR / f"{slug}.md"
    content = f"{build_front_matter(title, date, updated, categories, tags)}\n\n{body}\n"
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html_files = sorted(POSTS_DIR.glob("*.html"))
    migrated = 0

    for html_path in html_files:
        migrate_post(html_path)
        migrated += 1

    print(f"Migrated {migrated} posts to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
