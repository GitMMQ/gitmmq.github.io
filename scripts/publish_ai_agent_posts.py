#!/usr/bin/env python3
"""Publish docs/ai-agents/*.md as Hexo-style static blog posts."""

from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import markdown
from markdown.extensions.tables import TableExtension

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "ai-agents"
TEMPLATE_POST = ROOT / "posts" / "e601e6a8.html"
CATEGORY = "mechine"
TZ = timezone(timedelta(hours=8))
BASE_DATE = datetime(2026, 6, 5, 11, 0, 0, tzinfo=TZ)

POSTS = [
    {
        "md": "hermes-openclaw-overview.md",
        "title": "Agent Hermes 与 OpenClaw（龙虾）：架构、应用与对比",
        "description": "系统介绍 Agent Hermes 与 OpenClaw（龙虾）的架构设计、典型应用场景与优缺点对比，中英文对照。",
        "excerpt_zh": "本文对比 Agent Hermes 与 OpenClaw（龙虾）两大个人 AI Agent 框架的架构哲学、应用场景与优缺点，采用中英文对照形式。",
        "excerpt_en": "A bilingual comparison of Agent Hermes and OpenClaw (Lobster): architecture, use cases, and pros & cons.",
        "tags": "AI Agent;Hermes;OpenClaw",
    },
    {
        "md": "memory-system.md",
        "title": "Agent Hermes 与 OpenClaw 记忆系统深度解析",
        "description": "深度解析 Hermes 四层记忆与 OpenClaw Workspace 文件记忆体系的设计、检索机制与最佳实践，中英文对照。",
        "excerpt_zh": "对比 Hermes 四层记忆（SQLite FTS5 + 技能渐进披露）与 OpenClaw Markdown 工作区文件记忆体系。",
        "excerpt_en": "Deep dive into Hermes four-layer memory vs OpenClaw workspace Markdown memory.",
        "tags": "AI Agent;Memory;Hermes;OpenClaw",
    },
    {
        "md": "gateway.md",
        "title": "Agent Hermes 与 OpenClaw Gateway 架构深度解析",
        "description": "对比 OpenClaw Gateway 控制平面与 Hermes GatewayRunner 的消息路由、授权、投递与部署模式，中英文对照。",
        "excerpt_zh": "OpenClaw「Gateway 即产品」与 Hermes「Agent 引擎消息前端」的架构对比与生产部署指南。",
        "excerpt_en": "Gateway architecture comparison: OpenClaw control plane vs Hermes GatewayRunner.",
        "tags": "AI Agent;Gateway;Hermes;OpenClaw",
    },
    {
        "md": "security-model.md",
        "title": "Agent Hermes 与 OpenClaw 安全模型深度解析",
        "description": "对比 OpenClaw 身份先行安全模型与 Hermes 七层纵深防御：审批、沙箱、SSRF、供应链与生产硬化清单，中英文对照。",
        "excerpt_zh": "OpenClaw「身份先行」与 Hermes「七层纵深防御」安全模型对比及生产硬化清单。",
        "excerpt_en": "Security model comparison: OpenClaw access-control-first vs Hermes defense-in-depth.",
        "tags": "AI Agent;Security;Hermes;OpenClaw",
    },
]


def post_id(slug: str) -> str:
    return hashlib.md5(slug.encode()).hexdigest()[:8]


def strip_front_matter(text: str) -> str:
    if text.startswith("# "):
        lines = text.splitlines()
        # drop title line and optional metadata line
        start = 1
        if len(lines) > 1 and lines[1].startswith("# "):
            start = 2
        if len(lines) > start and lines[start].strip() == "---":
            start += 1
        return "\n".join(lines[start:]).lstrip("\n")
    return text


def md_to_html(md_text: str) -> str:
    text = strip_front_matter(md_text)

    def mermaid_replacer(match: re.Match[str]) -> str:
        code = html.escape(match.group(1).strip())
        return (
            '<div class="note"><p><strong>架构图（Mermaid 源码）</strong> / '
            '<em>Architecture diagram (Mermaid source)</em></p>'
            f'<pre><code>{code}</code></pre></div>'
        )

    text = re.sub(r"```mermaid\s*\n(.*?)```", mermaid_replacer, text, flags=re.DOTALL)
    body = markdown.markdown(
        text,
        extensions=[TableExtension(), "fenced_code", "nl2br", "sane_lists"],
    )
    # Hexo-style header anchors for h2/h3
    body = re.sub(
        r"<h2 id=\"([^\"]+)\">(.*?)</h2>",
        lambda m: (
            f'<h2 id="{m.group(1)}">'
            f'<a href="#{m.group(1)}" class="headerlink" title="{html.unescape(m.group(2))}"></a>'
            f"{m.group(2)}</h2>"
        ),
        body,
        flags=re.DOTALL,
    )
    body = re.sub(
        r"<h3 id=\"([^\"]+)\">(.*?)</h3>",
        lambda m: (
            f'<h3 id="{m.group(1)}">'
            f'<a href="#{m.group(1)}" class="headerlink" title="{html.unescape(m.group(2))}"></a>'
            f"{m.group(2)}</h3>"
        ),
        body,
        flags=re.DOTALL,
    )
    return body


def word_count(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def reading_minutes(chars: int) -> int:
    return max(5, round(chars / 450))


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def iso_local(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def render_post_page(
    template: str,
    *,
    pid: str,
    title: str,
    description: str,
    body_html: str,
    published: datetime,
    chars: int,
    minutes: int,
    prev_href: str | None,
    prev_title: str | None,
    next_href: str | None,
    next_title: str | None,
) -> str:
    url = f"https://www.fastolf.com/posts/{pid}.html"
    date_display = published.strftime("%Y-%m-%d")
    date_title = published.strftime("%Y-%m-%d %H:%M:%S")

    page = template
    page = page.replace("LLM Wiki 介绍：思想、意义、应用场景与优缺点", title)
    page = page.replace("e601e6a8", pid)
    page = page.replace(
        "LLM Wiki 是由 Andrej Karpathy 提出的一种个人知识库构建范式：用 LLM 将原始资料编译为结构化 Wiki 并持续维护，涵盖核心思想、意义、应用场景与优缺点分析，中英文对照。",
        description,
    )
    page = page.replace('content="2026-06-05T10:00:00.000Z"', f'content="{iso_z(published)}"')
    page = page.replace('创建时间：2026-06-05 10:00:00', f"创建时间：{date_title}")
    page = page.replace('datetime="2026-06-05T10:00:00+08:00">2026-06-05', f'datetime="{iso_local(published)}">{date_display}')
    page = page.replace("<span>8500</span>", f"<span>{chars}</span>")
    page = page.replace("<span>18 分钟</span>", f"<span>{minutes} 分钟</span>")
    page = page.replace('Tech;Data;Vision', 'AI Agent;Hermes;OpenClaw')
    page = page.replace("<span class=\"site-state-item-count\">360</span>", "<span class=\"site-state-item-count\">364</span>")

    # Replace article body (first post-body block on the page)
    body_pattern = re.compile(
        r'(<div class="post-body" itemprop="articleBody">\s*)(.*?)(\s*</div>)',
        re.DOTALL,
    )

    def _body_replacer(match: re.Match[str]) -> str:
        return (
            match.group(1)
            + "\n      \n        "
            + body_html
            + "\n\n      \n    "
            + match.group(3)
        )

    page = body_pattern.sub(_body_replacer, page, count=1)

    # post nav
    prev_block = ""
    if prev_href:
        prev_block = (
            f'    <a href="{prev_href}" rel="prev" title="{html.escape(prev_title or "")}">\n'
            f'      <i class="fa fa-chevron-left"></i> {html.escape(prev_title or "")}\n'
            "    </a>"
        )
    next_block = ""
    if next_href:
        next_block = (
            f'    <a href="{next_href}" rel="next" title="{html.escape(next_title or "")}">\n'
            f'      {html.escape(next_title or "")} <i class="fa fa-chevron-right"></i>\n'
            "    </a>"
        )

    nav_pattern = re.compile(r"<div class=\"post-nav\">.*?</div>\s*</div>\s*</footer>", re.DOTALL)
    nav_html = (
        "    <div class=\"post-nav\">\n"
        f"      <div class=\"post-nav-item\">\n{prev_block}</div>\n"
        f"      <div class=\"post-nav-item\">\n{next_block}</div>\n"
        "    </div>\n      </footer>"
    )
    page = nav_pattern.sub(nav_html, page, count=1)
    return page


def home_article_block(
    *,
    pid: str,
    title: str,
    excerpt_html: str,
    published: datetime,
    chars: int,
    minutes: int,
) -> str:
    url = f"/posts/{pid}.html"
    date_display = published.strftime("%Y-%m-%d")
    date_title = published.strftime("%Y-%m-%d %H:%M:%S")
    return f"""
  
  
  <article itemscope itemtype="http://schema.org/Article" class="post-block" lang="zh-Hans">
    <link itemprop="mainEntityOfPage" href="https://www.fastolf.com{url}">

    <span hidden itemprop="author" itemscope itemtype="http://schema.org/Person">
      <meta itemprop="image" content="/images/avatar.gif">
      <meta itemprop="name" content="Meng Qi">
      <meta itemprop="description" content="recording">
    </span>

    <span hidden itemprop="publisher" itemscope itemtype="http://schema.org/Organization">
      <meta itemprop="name" content="Qi">
    </span>
      <header class="post-header">
        <h2 class="post-title" itemprop="name headline">
          
            <a href="{url}" class="post-title-link" itemprop="url">{html.escape(title)}</a>
        </h2>

        <div class="post-meta">
            <span class="post-meta-item">
              <span class="post-meta-item-icon">
                <i class="far fa-calendar"></i>
              </span>
              <span class="post-meta-item-text">发表于</span>
              

              <time title="创建时间：{date_title}" itemprop="dateCreated datePublished" datetime="{iso_local(published)}">{date_display}</time>
            </span>
            <span class="post-meta-item">
              <span class="post-meta-item-icon">
                <i class="far fa-folder"></i>
              </span>
              <span class="post-meta-item-text">分类于</span>
                <span itemprop="about" itemscope itemtype="http://schema.org/Thing">
                  <a href="/categories/mechine/" itemprop="url" rel="index"><span itemprop="name">mechine</span></a>
                </span>
            </span>

          
            <span class="post-meta-item" title="本文字数">
              <span class="post-meta-item-icon">
                <i class="far fa-file-word"></i>
              </span>
              <span>{chars}</span>
            </span>
            <span class="post-meta-item" title="阅读时长">
              <span class="post-meta-item-icon">
                <i class="far fa-clock"></i>
              </span>
              <span>{minutes} 分钟</span>
            </span>

        </div>
      </header>

    
    
    
    <div class="post-body" itemprop="articleBody">

      
          {excerpt_html}

      
    </div>

    
    
    
      <footer class="post-footer">
        <div class="post-eof"></div>
      </footer>
  </article>
"""


def archive_article_block(*, pid: str, title: str, published: datetime) -> str:
    date_display = published.strftime("%m-%d")
    return f"""
  <article itemscope itemtype="http://schema.org/Article">
    <header class="post-header">

      <div class="post-meta">
        <time itemprop="dateCreated"
              datetime="{iso_local(published)}"
              content="{published.strftime('%Y-%m-%d')}">
          {date_display}
        </time>
      </div>

      <div class="post-title">
          <a class="post-title-link" href="/posts/{pid}.html" itemprop="url">
            <span itemprop="name">{html.escape(title)}</span>
          </a>
      </div>

    </header>
  </article>
"""


def category_article_block(*, pid: str, title: str, published: datetime) -> str:
    date_display = published.strftime("%m-%d")
    return f"""
  <article itemscope itemtype="http://schema.org/Article">
    <header class="post-header">
      <div class="post-meta">
        <time itemprop="dateCreated" datetime="{iso_local(published)}" content="{published.strftime('%Y-%m-%d')}">{date_display}</time>
      </div>
      <div class="post-title">
          <a class="post-title-link" href="/posts/{pid}.html" itemprop="url">
            <span itemprop="name">{html.escape(title)}</span>
          </a>
      </div>
    </header>
  </article>
"""


def search_entry(*, pid: str, title: str, excerpt_html: str) -> str:
    return f"""
    <entry>
      <title>{html.escape(title)}</title>
      <link href="/posts/{pid}.html"/>
      <url>/posts/{pid}.html</url>
      
        <content type="html"><![CDATA[{excerpt_html}]]></content>
      
      
      <categories>
          
          <category> mechine </category>
          
      </categories>
      
      
    </entry>
"""


def sitemap_url(pid: str, published: datetime) -> str:
    return f"""
  <url>
    <loc>https://www.fastolf.com/posts/{pid}.html</loc>
    
    <lastmod>{published.strftime('%Y-%m-%d')}</lastmod>
    
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
"""


def main() -> None:
    template = TEMPLATE_POST.read_text(encoding="utf-8")
    rendered_posts = []

    for i, meta in enumerate(POSTS):
        md_path = DOCS / meta["md"]
        md_text = md_path.read_text(encoding="utf-8")
        slug = meta["md"]
        pid = post_id(slug)
        published = BASE_DATE + timedelta(hours=i)
        body_html = md_to_html(md_text)
        chars = word_count(re.sub(r"<[^>]+>", "", body_html))
        minutes = reading_minutes(chars)
        excerpt_html = (
            f"<p>{html.escape(meta['excerpt_zh'])}</p>"
            f"<p><em>{html.escape(meta['excerpt_en'])}</em></p>"
            "<p>系列文章：<a href=\"/posts/"
            + post_id("hermes-openclaw-overview.md")
            + ".html\">总览</a> · "
            "<a href=\"/posts/"
            + post_id("memory-system.md")
            + ".html\">记忆系统</a> · "
            "<a href=\"/posts/"
            + post_id("gateway.md")
            + ".html\">Gateway</a> · "
            "<a href=\"/posts/"
            + post_id("security-model.md")
            + ".html\">安全模型</a></p>"
        )
        rendered_posts.append(
            {
                **meta,
                "pid": pid,
                "published": published,
                "body_html": body_html,
                "chars": chars,
                "minutes": minutes,
                "excerpt_html": excerpt_html,
            }
        )

    # newest first for site lists
    rendered_posts_desc = list(reversed(rendered_posts))

    for idx, post in enumerate(rendered_posts):
        if idx == 0:
            prev_href = "/posts/e601e6a8.html"
            prev_title = "LLM Wiki 介绍：思想、意义、应用场景与优缺点"
        else:
            prev_post = rendered_posts[idx - 1]
            prev_href = f"/posts/{prev_post['pid']}.html"
            prev_title = prev_post["title"]

        if idx < len(rendered_posts) - 1:
            next_post = rendered_posts[idx + 1]
            next_href = f"/posts/{next_post['pid']}.html"
            next_title = next_post["title"]
        else:
            next_href = None
            next_title = None

        html_page = render_post_page(
            template,
            pid=post["pid"],
            title=post["title"],
            description=post["description"],
            body_html=post["body_html"],
            published=post["published"],
            chars=post["chars"],
            minutes=post["minutes"],
            prev_href=prev_href,
            prev_title=prev_title,
            next_href=next_href,
            next_title=next_title,
        )
        out = ROOT / "posts" / f"{post['pid']}.html"
        out.write_text(html_page, encoding="utf-8")
        print(f"Wrote {out.name} ({post['title']})")

    # Update e601e6a8 next link to first article in this series
    first_post = rendered_posts[0]
    llm_post = (ROOT / "posts" / "e601e6a8.html").read_text(encoding="utf-8")
    llm_post = re.sub(
        r'<div class="post-nav-item">\s*<a href="/posts/[^"]+\.html" rel="next"[^>]*>.*?</a></div>',
        (
            f'<div class="post-nav-item">\n'
            f'    <a href="/posts/{first_post["pid"]}.html" rel="next" title="{html.escape(first_post["title"])}">\n'
            f'      {html.escape(first_post["title"])} <i class="fa fa-chevron-right"></i>\n'
            f"    </a></div>"
        ),
        llm_post,
        count=1,
        flags=re.DOTALL,
    )
    (ROOT / "posts" / "e601e6a8.html").write_text(llm_post, encoding="utf-8")

    # index.html - prepend home blocks
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    marker = '  <article itemscope itemtype="http://schema.org/Article" class="post-block" lang="zh-Hans">\n    <link itemprop="mainEntityOfPage" href="https://www.fastolf.com/posts/e601e6a8.html">'
    blocks = "".join(
        home_article_block(
            pid=p["pid"],
            title=p["title"],
            excerpt_html=p["excerpt_html"],
            published=p["published"],
            chars=p["chars"],
            minutes=p["minutes"],
        )
        for p in rendered_posts_desc
    )
    index = index.replace(marker, blocks + "\n" + marker, 1)
    index = index.replace("<span class=\"site-state-item-count\">360</span>", "<span class=\"site-state-item-count\">364</span>")
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    # archives/index.html
    archives = (ROOT / "archives" / "index.html").read_text(encoding="utf-8")
    arch_marker = """  <article itemscope itemtype="http://schema.org/Article">
    <header class="post-header">

      <div class="post-meta">
        <time itemprop="dateCreated"
              datetime="2026-06-05T10:00:00+08:00"
              content="2026-06-05">
          06-05
        </time>
      </div>

      <div class="post-title">
          <a class="post-title-link" href="/posts/e601e6a8.html" itemprop="url">
            <span itemprop="name">LLM Wiki 介绍：思想、意义、应用场景与优缺点</span>
          </a>
      </div>

    </header>
  </article>"""
    arch_blocks = "".join(
        archive_article_block(pid=p["pid"], title=p["title"], published=p["published"])
        for p in rendered_posts_desc
    )
    archives = archives.replace(arch_marker, arch_blocks + arch_marker, 1)
    (ROOT / "archives" / "index.html").write_text(archives, encoding="utf-8")

    # archives/2026/index.html
    arch2026 = (ROOT / "archives" / "2026" / "index.html").read_text(encoding="utf-8")
    arch2026_marker = """  <article itemscope itemtype="http://schema.org/Article">
    <header class="post-header">

      <div class="post-meta">
        <time itemprop="dateCreated"
              datetime="2026-06-05T10:00:00+08:00"
              content="2026-06-05">
          06-05
        </time>
      </div>

      <div class="post-title">
          <a class="post-title-link" href="/posts/e601e6a8.html" itemprop="url">
            <span itemprop="name">LLM Wiki 介绍：思想、意义、应用场景与优缺点</span>
          </a>
      </div>

    </header>
  </article>"""
    arch2026 = arch2026.replace(arch2026_marker, arch_blocks + arch2026_marker, 1)
    (ROOT / "archives" / "2026" / "index.html").write_text(arch2026, encoding="utf-8")

    # categories/mechine/index.html
    cat = (ROOT / "categories" / "mechine" / "index.html").read_text(encoding="utf-8")
    cat_marker = """  <article itemscope itemtype="http://schema.org/Article">
    <header class="post-header">
      <div class="post-meta">
        <time itemprop="dateCreated" datetime="2026-06-05T10:00:00+08:00" content="2026-06-05">06-05</time>
      </div>
      <div class="post-title">
          <a class="post-title-link" href="/posts/e601e6a8.html" itemprop="url">
            <span itemprop="name">LLM Wiki 介绍：思想、意义、应用场景与优缺点</span>
          </a>
      </div>
    </header>
  </article>"""
    cat_blocks = "".join(
        category_article_block(pid=p["pid"], title=p["title"], published=p["published"])
        for p in rendered_posts_desc
    )
    cat = cat.replace(cat_marker, cat_blocks + cat_marker, 1)
    (ROOT / "categories" / "mechine" / "index.html").write_text(cat, encoding="utf-8")

    # search.xml
    search = (ROOT / "search.xml").read_text(encoding="utf-8")
    insert_at = search.index("<entry>\n      <title>LLM Wiki")
    search_entries = "".join(
        search_entry(pid=p["pid"], title=p["title"], excerpt_html=p["excerpt_html"])
        for p in rendered_posts_desc
    )
    search = search[:insert_at] + search_entries + "\n    \n    \n    " + search[insert_at:]
    (ROOT / "search.xml").write_text(search, encoding="utf-8")

    # sitemap.xml + sitemap.txt + baidusitemap.xml
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_insert = sitemap.index("<url>\n    <loc>https://www.fastolf.com/posts/e601e6a8.html</loc>")
    sitemap_urls = "".join(sitemap_url(p["pid"], p["published"]) for p in rendered_posts_desc)
    sitemap = sitemap[:sitemap_insert] + sitemap_urls + sitemap[sitemap_insert:]
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    sitemap_txt = (ROOT / "sitemap.txt").read_text(encoding="utf-8")
    txt_lines = [f"https://www.fastolf.com/posts/{p['pid']}.html\n" for p in rendered_posts_desc]
    sitemap_txt = "".join(txt_lines) + sitemap_txt
    (ROOT / "sitemap.txt").write_text(sitemap_txt, encoding="utf-8")

    baidu = (ROOT / "baidusitemap.xml").read_text(encoding="utf-8")
    baidu_insert = baidu.index("<url>\n    <loc>https://www.fastolf.com/posts/e601e6a8.html</loc>")
    baidu_urls = "".join(
        f"  <url>\n    <loc>https://www.fastolf.com/posts/{p['pid']}.html</loc>\n    <lastmod>{p['published'].strftime('%Y-%m-%d')}</lastmod>\n  </url>\n"
        for p in rendered_posts_desc
    )
    baidu = baidu[:baidu_insert] + baidu_urls + baidu[baidu_insert:]
    (ROOT / "baidusitemap.xml").write_text(baidu, encoding="utf-8")

    print("Updated index, archives, categories, search, sitemaps.")


if __name__ == "__main__":
    main()
