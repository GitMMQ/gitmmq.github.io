#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BLOG_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$BLOG_DIR"
npm run clean
npm run build

python3 - "$ROOT_DIR" "$BLOG_DIR/public" <<'PY'
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[1])
public_dir = Path(sys.argv[2])
preserve = {
    ".git", "blog-source", ".github", "README.md",
    "docs", "scripts",
    "baidusitemap.xml", "sitemap.txt", "sitemap.xml",
}
legacy_index_files = [
    root / "categories" / "index.html",
    root / "tags" / "index.html",
]
legacy_backups = {
    path: path.read_bytes() for path in legacy_index_files if path.exists()
}

for item in root.iterdir():
    if item.name in preserve:
        continue
    if item.is_dir():
        shutil.rmtree(item)
    else:
        item.unlink()

for item in public_dir.iterdir():
    target = root / item.name
    if item.is_dir():
        shutil.copytree(item, target)
    else:
        shutil.copy2(item, target)

for path, data in legacy_backups.items():
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

print(f"Deployed generated site from {public_dir} to {root}")
PY

echo "Deployed generated site to repository root."
