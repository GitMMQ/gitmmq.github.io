#!/usr/bin/env python3
"""Scan docs for tags that differ only by case."""
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def parse_tags(fm: str) -> list[str]:
    tags: list[str] = []
    in_tags = False
    for line in fm.splitlines():
        if re.match(r"^tags\s*:", line):
            in_tags = True
            rest = line.split(":", 1)[1].strip()
            if rest.startswith("["):
                tags.extend(re.findall(r'["\']([^"\']+)["\']', rest))
            elif rest:
                tags.append(rest.strip("\"'"))
            continue
        if in_tags:
            m = re.match(r"^\s*-\s+(.+)$", line)
            if m:
                tags.append(m.group(1).strip().strip("\"'"))
            elif line and not line.startswith(" "):
                in_tags = False
    return tags


def main() -> None:
    groups: dict[str, set[str]] = defaultdict(set)
    for path in DOCS.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
        if not m:
            continue
        for tag in parse_tags(m.group(1)):
            groups[tag.lower()].add(tag)

    dups = {k: sorted(v) for k, v in groups.items() if len(v) > 1}
    print(f"duplicate groups: {len(dups)}")
    for key in sorted(dups):
        print(f"  {dups[key]}")


if __name__ == "__main__":
    main()
