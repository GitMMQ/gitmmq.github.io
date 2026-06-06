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

python3 - "$BLOG_DIR/public" <<'PY'
import re
import sys
from pathlib import Path

public = Path(sys.argv[1])
mermaid_markers = ("language-mermaid", 'class="mermaid"', "class='mermaid'")
script_patterns = [
    re.compile(r'\s*<script class="next-config" data-name="mermaid"[^>]*></script>\s*'),
    re.compile(r'\s*<script src="/js/third-party/tags/mermaid.js"[^>]*></script>\s*'),
]

for html in public.rglob("*.html"):
    text = html.read_text(encoding="utf-8")
    if any(marker in text for marker in mermaid_markers):
        continue
    new_text = text
    for pattern in script_patterns:
        new_text = pattern.sub("\n", new_text)
    if new_text != text:
        html.write_text(new_text, encoding="utf-8")

sitemap = public / "sitemap.xml"
if sitemap.exists():
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))
    (public / "sitemap.txt").write_text("\n".join(dict.fromkeys(urls)) + "\n", encoding="utf-8")

print("Post-processed HTML (mermaid trim) and sitemap.txt")
PY

python3 "$BLOG_DIR/deploy_public_to_root.py"

echo "Deployed generated site to repository root."
