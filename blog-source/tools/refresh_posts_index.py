#!/usr/bin/env python3
"""Regenerate docs/posts-index.json from docs/posts/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from migrate_all_posts_to_docs import build_index  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "docs" / "posts-index.json"


def main() -> None:
    posts = build_index()
    INDEX.write_text(
        json.dumps({"count": len(posts), "posts": posts}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"count": len(posts)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
