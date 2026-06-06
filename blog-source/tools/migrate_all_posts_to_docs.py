#!/usr/bin/env python3
"""Migrate legacy _posts into docs/posts/<category>/ and refresh manifest index."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS = ROOT / "blog-source" / "source" / "_posts"
DOCS_POSTS = ROOT / "docs" / "posts"
SYNC_GENERATED = ROOT / "blog-source" / ".sync-generated.txt"
MANIFEST = ROOT / "docs" / "sync-manifest.json"
INDEX = ROOT / "docs" / "posts-index.json"

CATEGORY_LINE = re.compile(r"^\s*-\s+[\"']?([^\"'\n]+)[\"']?\s*$")


def load_synced() -> set[str]:
    if not SYNC_GENERATED.exists():
        return set()
    return {line.strip() for line in SYNC_GENERATED.read_text(encoding="utf-8").splitlines() if line.strip()}


def parse_front_matter(text: str) -> tuple[dict[str, str | list[str]], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_text, body = parts[1], parts[2]
    meta: dict[str, str | list[str]] = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            value = CATEGORY_LINE.match(line)
            if value:
                meta.setdefault(current_key, [])
                if isinstance(meta[current_key], list):
                    meta[current_key].append(value.group(1).strip())
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"')
            current_key = key
            if val:
                meta[key] = val
            else:
                meta[key] = []
    return meta, body


def category_for(meta: dict[str, str | list[str]]) -> str:
    cats = meta.get("categories", [])
    if isinstance(cats, list) and cats:
        return cats[0]
    return "uncategorized"


def slug_map_for_posts() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for md_path in DOCS_POSTS.rglob("*.md"):
        if md_path.name == "README.md":
            continue
        rel = md_path.relative_to(DOCS_POSTS).as_posix()
        if rel != md_path.name:
            mapping[rel] = md_path.name
    return dict(sorted(mapping.items()))


def build_index() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for md_path in sorted(DOCS_POSTS.rglob("*.md")):
        if md_path.name == "README.md":
            continue
        meta, _ = parse_front_matter(md_path.read_text(encoding="utf-8"))
        rel = md_path.relative_to(DOCS_POSTS).as_posix()
        slug = md_path.stem
        title = str(meta.get("title", slug))
        category = category_for(meta)
        entries.append(
            {
                "slug": slug,
                "title": title,
                "category": category,
                "source": f"posts/{rel}",
                "url": f"/posts/{slug}.html",
            }
        )
    return entries


def update_manifest(slug_map: dict[str, str]) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    series = manifest.setdefault("series", [])
    posts_series = next((s for s in series if s.get("id") == "posts"), None)
    payload = {
        "id": "posts",
        "dir": "posts",
        "mode": "front_matter",
        "recursive": True,
        "exclude": ["README.md"],
        "slug_map": slug_map,
    }
    if posts_series:
        posts_series.update(payload)
    else:
        series.append(payload)
    manifest["version"] = 2
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def migrate_legacy() -> dict[str, int]:
    synced = load_synced()
    DOCS_POSTS.mkdir(parents=True, exist_ok=True)
    moved = 0
    skipped = 0

    for src in sorted(POSTS.glob("*.md")):
        if src.name in synced:
            skipped += 1
            continue
        text = src.read_text(encoding="utf-8")
        meta, _ = parse_front_matter(text)
        category = category_for(meta)
        dest_dir = DOCS_POSTS / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        if dest.exists():
            skipped += 1
            continue
        shutil.copy2(src, dest)
        moved += 1

    slug_map = slug_map_for_posts()
    update_manifest(slug_map)
    INDEX.write_text(
        json.dumps({"count": len(build_index()), "posts": build_index()}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"moved": moved, "skipped_synced_or_exists": skipped, "posts_in_docs": len(build_index())}


def main() -> None:
    stats = migrate_legacy()
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
