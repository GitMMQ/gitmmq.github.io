#!/usr/bin/env python3
"""Sync docs/ markdown sources into Hexo _posts/ before build.

Manifest: docs/sync-manifest.json
All _posts/ files are generated — do not edit by hand.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MANIFEST = DOCS / "sync-manifest.json"
OUTPUT = Path(__file__).resolve().parent / "source" / "_posts"
GENERATED_LIST = Path(__file__).resolve().parent / ".sync-generated.txt"
POSTS_INDEX = DOCS / "posts-index.json"


def post_id(slug: str) -> str:
    return hashlib.md5(slug.encode()).hexdigest()[:8]


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def write_post(filename: str, front_matter: list[str], body: str) -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / filename
    path.write_text("\n".join(front_matter) + "\n\n" + body.strip() + "\n", encoding="utf-8")
    return path


def parse_batch_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


def registry_date(meta: dict, batches: dict[str, str]) -> str:
    base = parse_batch_date(batches[str(meta["batch"])])
    return (base + timedelta(hours=meta["hour_offset"])).strftime("%Y-%m-%d %H:%M:%S")


def output_filename(series_dir: Path, md_path: Path, slug_map: dict[str, str]) -> str:
    rel = md_path.relative_to(series_dir).as_posix()
    target = slug_map.get(rel, slug_map.get(md_path.name, md_path.name))
    return target if target.endswith(".md") else f"{target}.md"


def iter_series_markdown(series: dict) -> list[Path]:
    series_dir = DOCS / series["dir"]
    exclude = set(series.get("exclude", []))
    pattern = "**/*.md" if series.get("recursive") else "*.md"
    paths: list[Path] = []
    for md_path in sorted(series_dir.glob(pattern)):
        if md_path.name in exclude:
            continue
        paths.append(md_path)
    return paths


def sync_registry(series: dict) -> tuple[list[str], list[dict]]:
    written: list[str] = []
    index: list[dict] = []
    series_dir = DOCS / series["dir"]
    category = series["category"]
    batches = series["date_batches"]

    for meta in series["posts"]:
        md_path = series_dir / meta["md"]
        if not md_path.exists():
            raise FileNotFoundError(md_path)

        body = md_path.read_text(encoding="utf-8").strip()
        filename = f"{post_id(meta['md'])}.md"
        slug = filename[:-3]
        date = registry_date(meta, batches)

        front_matter = [
            "---",
            f"title: {yaml_quote(meta['title'])}",
            f"date: {date}",
            "categories:",
            f"  - {yaml_quote(category)}",
            "tags:",
        ]
        front_matter.extend(f"  - {yaml_quote(tag)}" for tag in meta["tags"])
        front_matter.append("---")

        write_post(filename, front_matter, body)
        written.append(filename)
        index.append(
            {
                "slug": slug,
                "title": meta["title"],
                "category": category,
                "series": series["id"],
                "source": f"{series['dir']}/{meta['md']}",
                "url": f"/posts/{slug}.html",
            }
        )
    return written, index


def sync_fixed_slug(series: dict) -> tuple[list[str], list[dict]]:
    written: list[str] = []
    index: list[dict] = []
    series_dir = DOCS / series["dir"]

    for meta in series["posts"]:
        md_path = series_dir / meta["md"]
        if not md_path.exists():
            raise FileNotFoundError(md_path)

        body = md_path.read_text(encoding="utf-8").strip()
        slug = meta["slug"]
        filename = f"{slug}.md"

        front_matter = [
            "---",
            f"title: {yaml_quote(meta['title'])}",
            f"date: {meta['date']}",
            "categories:",
        ]
        front_matter.extend(f"  - {yaml_quote(cat)}" for cat in meta["categories"])
        front_matter.append("tags:")
        front_matter.extend(f"  - {yaml_quote(tag)}" for tag in meta["tags"])
        front_matter.append("---")

        write_post(filename, front_matter, body)
        written.append(filename)
        index.append(
            {
                "slug": slug,
                "title": meta["title"],
                "category": meta["categories"][0],
                "series": series["id"],
                "source": f"{series['dir']}/{meta['md']}",
                "url": f"/posts/{slug}.html",
            }
        )
    return written, index


def parse_title_from_front_matter(content: str, fallback: str) -> str:
    if not content.startswith("---"):
        return fallback
    parts = content.split("---", 2)
    if len(parts) < 2:
        return fallback
    for line in parts[1].splitlines():
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"')
    return fallback


def parse_category_from_front_matter(content: str) -> str:
    if not content.startswith("---"):
        return "uncategorized"
    parts = content.split("---", 2)
    if len(parts) < 2:
        return "uncategorized"
    fm = parts[1]
    in_categories = False
    for line in fm.splitlines():
        if line.strip() == "categories:":
            in_categories = True
            continue
        if in_categories and line.startswith("  - "):
            return line.replace("  - ", "").strip().strip('"')
        if in_categories and line.strip() and not line.startswith("  "):
            break
    return "uncategorized"


def sync_front_matter(series: dict) -> tuple[list[str], list[dict]]:
    written: list[str] = []
    index: list[dict] = []
    series_dir = DOCS / series["dir"]
    slug_map: dict[str, str] = series.get("slug_map", {})

    for md_path in iter_series_markdown(series):
        content = md_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            raise ValueError(f"post missing front matter: {series['dir']}/{md_path.name}")

        filename = output_filename(series_dir, md_path, slug_map)
        (OUTPUT / filename).write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
        written.append(filename)
        rel = md_path.relative_to(series_dir).as_posix()
        slug = Path(filename).stem
        index.append(
            {
                "slug": slug,
                "title": parse_title_from_front_matter(content, slug),
                "category": parse_category_from_front_matter(content),
                "series": series["id"],
                "source": f"{series['dir']}/{rel}",
                "url": f"/posts/{slug}.html",
            }
        )
    return written, index


def sync_series(series: dict) -> tuple[list[str], list[dict]]:
    mode = series["mode"]
    if mode == "registry":
        return sync_registry(series)
    if mode == "fixed_slug":
        return sync_fixed_slug(series)
    if mode == "front_matter":
        return sync_front_matter(series)
    raise ValueError(f"unknown sync mode: {mode}")


def clear_output() -> None:
    if not OUTPUT.exists():
        OUTPUT.mkdir(parents=True, exist_ok=True)
        return
    for path in OUTPUT.glob("*.md"):
        path.unlink()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    clear_output()

    summary: dict[str, int | str] = {"series": {}, "output": str(OUTPUT)}
    all_written: list[str] = []
    all_index: list[dict] = []

    for series in manifest["series"]:
        written, index = sync_series(series)
        summary["series"][series["id"]] = len(written)
        all_written.extend(written)
        all_index.extend(index)

    summary["total"] = len(all_written)
    GENERATED_LIST.write_text("\n".join(sorted(all_written)) + "\n", encoding="utf-8")
    POSTS_INDEX.write_text(
        json.dumps({"count": len(all_index), "posts": sorted(all_index, key=lambda x: x["slug"])}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
