#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BLOG_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$BLOG_DIR"
python3 sync_docs.py
npm run clean
npm run build

python3 - "$BLOG_DIR/public/js/third-party/tags/mermaid.js" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
content = path.read_text(encoding="utf-8")
content = content.replace(
    "newElement.innerHTML = element.innerHTML;",
    "newElement.textContent = element.textContent;",
)
path.write_text(content, encoding="utf-8")
PY

OVERRIDES_DIR="$BLOG_DIR/overrides/js"
for file in motion.js next-boot.js; do
  if [ -f "$OVERRIDES_DIR/$file" ]; then
    cp "$OVERRIDES_DIR/$file" "$BLOG_DIR/public/js/$file"
  fi
done

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

# GitHub Pages must skip Jekyll so pre-built static HTML is served as-is.
(root / ".nojekyll").touch(exist_ok=True)

print(f"Deployed generated site from {public_dir} to {root}")
PY

echo "Deployed generated site to repository root."
