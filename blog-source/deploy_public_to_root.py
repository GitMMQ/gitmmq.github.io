#!/usr/bin/env python3
"""Windows-friendly deploy helper: post-process public/ and copy to repo root."""
import re
import shutil
import sys
from pathlib import Path

BLOG_DIR = Path(__file__).resolve().parent
ROOT_DIR = BLOG_DIR.parent
PUBLIC = BLOG_DIR / "public"

MERMAID_PATCH = (
    "newElement.innerHTML = element.innerHTML;",
    "newElement.textContent = element.textContent;",
)
MERMAID_MARKERS = ("language-mermaid", 'class="mermaid"', "class='mermaid'")
MERMAID_SCRIPT_PATTERNS = [
    re.compile(r'\s*<script class="next-config" data-name="mermaid"[^>]*></script>\s*'),
    re.compile(r'\s*<script src="/js/third-party/tags/mermaid.js"[^>]*></script>\s*'),
]
PRESERVE = {
    ".git",
    "blog-source",
    ".github",
    "README.md",
    "docs",
    "scripts",
    "baidusitemap.xml",
    "AGENTS.md",
}


def patch_mermaid_js() -> None:
    path = PUBLIC / "js/third-party/tags/mermaid.js"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(*MERMAID_PATCH), encoding="utf-8")


def copy_overrides() -> None:
    for name in ("motion.js", "next-boot.js"):
        src = BLOG_DIR / "overrides/js" / name
        dst = PUBLIC / "js" / name
        if src.exists():
            shutil.copy2(src, dst)


def trim_mermaid_scripts() -> None:
    for html in PUBLIC.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        if any(marker in text for marker in MERMAID_MARKERS):
            continue
        new_text = text
        for pattern in MERMAID_SCRIPT_PATTERNS:
            new_text = pattern.sub("\n", new_text)
        if new_text != text:
            html.write_text(new_text, encoding="utf-8")


def write_sitemap_txt() -> None:
    sitemap = PUBLIC / "sitemap.xml"
    if not sitemap.exists():
        return
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))
    (PUBLIC / "sitemap.txt").write_text("\n".join(dict.fromkeys(urls)) + "\n", encoding="utf-8")


def deploy_to_root() -> None:
    for item in list(ROOT_DIR.iterdir()):
        if item.name in PRESERVE:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    for item in PUBLIC.iterdir():
        target = ROOT_DIR / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    (ROOT_DIR / ".nojekyll").touch(exist_ok=True)


def main() -> None:
    if not PUBLIC.exists():
        print("public/ not found; run hexo generate first.", file=sys.stderr)
        sys.exit(1)

    patch_mermaid_js()
    copy_overrides()
    trim_mermaid_scripts()
    write_sitemap_txt()
    deploy_to_root()

    sitemap = ROOT_DIR / "sitemap.xml"
    url_count = len(re.findall(r"<loc>", sitemap.read_text(encoding="utf-8"))) if sitemap.exists() else 0
    search_kb = round((ROOT_DIR / "search.xml").stat().st_size / 1024, 1)

    print("Deployed generated site to repository root.")
    print(f"  atom.xml: {(ROOT_DIR / 'atom.xml').exists()}")
    print(f"  robots.txt: {(ROOT_DIR / 'robots.txt').exists()}")
    print(f"  404.html: {(ROOT_DIR / '404.html').exists()}")
    print(f"  series/: {(ROOT_DIR / 'series/index.html').exists()}")
    print(f"  sitemap URLs: {url_count}")
    print(f"  search.xml: {search_kb} KB")


if __name__ == "__main__":
    main()
