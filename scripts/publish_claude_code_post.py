#!/usr/bin/env python3
"""Publish Claude Code bilingual article to Hexo static site."""

import hashlib
import re
from pathlib import Path

import markdown
from markdown.extensions.tables import TableExtension

ROOT = Path("/workspace")
MD_SOURCE = ROOT / "docs/claude-code-intro-bilingual.md"
TEMPLATE = ROOT / "posts/e601e6a8.html"

TITLE = "Claude Code 全面介绍：架构设计、应用与优缺点"
CATEGORY = "mechine"
DATE_ISO = "2026-06-05T18:00:00+08:00"
DATE_DISPLAY = "2026-06-05"
DATE_ARCHIVE = "06-05"
DESCRIPTION = (
    "Claude Code 是 Anthropic 推出的智能体编程工具，本文系统介绍其架构设计、"
    "应用场景、优缺点及设计启示，中英文对照。"
    "A Comprehensive Introduction to Claude Code."
)
POST_SLUG = hashlib.md5(TITLE.encode()).hexdigest()[:8]
POST_FILE = f"{POST_SLUG}.html"
POST_URL = f"/posts/{POST_FILE}"
FULL_URL = f"https://www.fastolf.com{POST_URL}"
WORD_COUNT = "9200"
READ_MINUTES = "20"


def slugify_heading(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip()
    return text


def add_headerlinks(html: str) -> str:
    def repl_heading(match: re.Match[str]) -> str:
        level = match.group(1)
        content = match.group(2)
        title = slugify_heading(content)
        anchor = title.replace(" ", "-")
        return (
            f'<h{level} id="{anchor}">'
            f'<a href="#{anchor}" class="headerlink" title="{title}"></a>'
            f"{content}</h{level}>"
        )

    html = re.sub(r"<h([23])>(.*?)</h\1>", repl_heading, html, flags=re.DOTALL)
    return html


def format_code_blocks(html: str) -> str:
    def repl_pre(match: re.Match[str]) -> str:
        code = match.group(1)
        lines = code.strip("\n").split("\n")
        line_html = "".join(f'<span class="line">{line}</span><br>' for line in lines)
        return (
            '<figure class="highlight plaintext"><table><tr><td class="code">'
            f"<pre>{line_html}</pre></td></tr></table></figure>"
        )

    return re.sub(r"<pre><code>(.*?)</code></pre>", repl_pre, html, flags=re.DOTALL)


def convert_markdown_to_html(md_text: str) -> str:
    md_text = re.sub(r"^# .+\n\n", "", md_text, count=1)
    html = markdown.markdown(
        md_text,
        extensions=["extra", TableExtension(), "nl2br", "sane_lists"],
    )
    html = add_headerlinks(html)
    html = format_code_blocks(html)
    html = html.replace("<!-- blockquote -->\n", "")
    intro = (
        "<p>本文系统介绍 <strong>Claude Code</strong> 的架构设计、应用场景、优缺点及设计启示，"
        "采用<strong>中英文对照</strong>形式。</p>"
        "<p><em>This article provides a comprehensive bilingual introduction to Claude Code—"
        "Anthropic's agentic coding tool—covering architecture, applications, pros &amp; cons, "
        "and design insights.</em></p><hr>"
    )
    return intro + html


def build_post_html(template: str, body_html: str) -> str:
    html = template
    html = html.replace("e601e6a8.html", POST_FILE)
    html = html.replace("LLM Wiki 介绍：思想、意义、应用场景与优缺点", TITLE)
    html = html.replace(
        "LLM Wiki 是由 Andrej Karpathy 提出的一种个人知识库构建范式：用 LLM 将原始资料编译为结构化 Wiki 并持续维护，涵盖核心思想、意义、应用场景与优缺点分析，中英文对照。",
        DESCRIPTION,
    )
    html = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{FULL_URL}">',
        html,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{FULL_URL}">',
        html,
    )
    html = re.sub(
        r'<meta property="article:published_time" content="[^"]*">',
        f'<meta property="article:published_time" content="{DATE_ISO}">',
        html,
    )
    html = re.sub(
        r'<meta property="article:modified_time" content="[^"]*">',
        f'<meta property="article:modified_time" content="{DATE_ISO}">',
        html,
    )
    html = re.sub(
        r'<time title="创建时间：[^"]*" itemprop="dateCreated datePublished" datetime="[^"]*">[^<]*</time>',
        f'<time title="创建时间：{DATE_DISPLAY} 18:00:00" itemprop="dateCreated datePublished" datetime="{DATE_ISO}">{DATE_DISPLAY}</time>',
        html,
        count=1,
    )
    html = re.sub(
        r"<span>\d+</span>\s*\n\s*<span class=\"post-meta-item\" title=\"阅读时长\">",
        f"<span>{WORD_COUNT}</span>\n            <span class=\"post-meta-item\" title=\"阅读时长\">",
        html,
        count=1,
    )
    html = re.sub(r"<span>\d+ 分钟</span>", f"<span>{READ_MINUTES} 分钟</span>", html, count=1)
    html = html.replace(
        f'<link itemprop="mainEntityOfPage" href="https://www.fastolf.com/posts/{POST_FILE}">',
        f'<link itemprop="mainEntityOfPage" href="{FULL_URL}">',
    )

    body_pattern = re.compile(
        r'(<div class="post-body" itemprop="articleBody">\s*)(.*?)(\s*</div>\s*\n\s*\n\s*\n\s*<footer class="post-footer">)',
        re.DOTALL,
    )
    html = body_pattern.sub(rf"\1\n\n      \n        {body_html}\n\n    \3", html, count=1)

    nav_pattern = re.compile(r'<div class="post-nav">.*?</div>\s*</div>', re.DOTALL)
    html = nav_pattern.sub(
        """<div class="post-nav">
      <div class="post-nav-item">
    <a href="/posts/e601e6a8.html" rel="prev" title="LLM Wiki 介绍：思想、意义、应用场景与优缺点">
      <i class="fa fa-chevron-left"></i> LLM Wiki 介绍：思想、意义、应用场景与优缺点
    </a></div>
      <div class="post-nav-item">
    </div>
    </div>""",
        html,
        count=1,
    )
    return html


def build_home_excerpt() -> str:
    return (
        "<p>本文系统介绍 <strong>Claude Code</strong> 的架构设计、应用场景、优缺点及设计启示，"
        "采用<strong>中英文对照</strong>形式。Claude Code 是 Anthropic 推出的智能体编程工具，"
        "核心哲学是「简单循环 + 厚重基础设施」。</p>"
        "<p><em>A comprehensive bilingual introduction to Claude Code—architecture, applications, "
        "pros &amp; cons, and design insights for agent builders.</em></p>"
        "<p>涵盖九步回合流水线、七级权限系统、五层上下文压缩、MCP/Skills/Hooks/Plugins 扩展机制……</p>"
    )


def build_home_article() -> str:
    return f"""
  <article itemscope itemtype="http://schema.org/Article" class="post-block" lang="zh-Hans">
    <link itemprop="mainEntityOfPage" href="{FULL_URL}">

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
          
            <a href="{POST_URL}" class="post-title-link" itemprop="url">{TITLE}</a>
        </h2>

        <div class="post-meta">
            <span class="post-meta-item">
              <span class="post-meta-item-icon">
                <i class="far fa-calendar"></i>
              </span>
              <span class="post-meta-item-text">发表于</span>
              

              <time title="创建时间：{DATE_DISPLAY} 18:00:00" itemprop="dateCreated datePublished" datetime="{DATE_ISO}">{DATE_DISPLAY}</time>
            </span>
            <span class="post-meta-item">
              <span class="post-meta-item-icon">
                <i class="far fa-folder"></i>
              </span>
              <span class="post-meta-item-text">分类于</span>
                <span itemprop="about" itemscope itemtype="http://schema.org/Thing">
                  <a href="/categories/{CATEGORY}/" itemprop="url" rel="index"><span itemprop="name">{CATEGORY}</span></a>
                </span>
            </span>

          
            <span class="post-meta-item" title="本文字数">
              <span class="post-meta-item-icon">
                <i class="far fa-file-word"></i>
              </span>
              <span>{WORD_COUNT}</span>
            </span>
            <span class="post-meta-item" title="阅读时长">
              <span class="post-meta-item-icon">
                <i class="far fa-clock"></i>
              </span>
              <span>{READ_MINUTES} 分钟</span>
            </span>

        </div>
      </header>

    
    
    
    <div class="post-body" itemprop="articleBody">

      
          {build_home_excerpt()}

      
    </div>

    
    
    
      <footer class="post-footer">
        <div class="post-eof"></div>
      </footer>
  </article>
  
  
  

"""


def build_archive_article() -> str:
    return f"""
  <article itemscope itemtype="http://schema.org/Article">
    <header class="post-header">

      <div class="post-meta">
        <time itemprop="dateCreated"
              datetime="{DATE_ISO}"
              content="{DATE_DISPLAY}">
          {DATE_ARCHIVE}
        </time>
      </div>

      <div class="post-title">
          <a class="post-title-link" href="{POST_URL}" itemprop="url">
            <span itemprop="name">{TITLE}</span>
          </a>
      </div>

    </header>
  </article>
"""


def build_search_entry() -> str:
    excerpt = build_home_excerpt()
    return f"""
    <entry>
      <title>{TITLE}</title>
      <link href="{POST_URL}"/>
      <url>{POST_URL}</url>
      
        <content type="html"><![CDATA[{excerpt}]]></content>
      
      
      <categories>
          
          <category> {CATEGORY} </category>
          
      </categories>
      
      
    </entry>
    
    
    
"""


def increment_post_count(text: str, delta: int = 1) -> str:
    def repl(match: re.Match[str]) -> str:
        return f'<span class="site-state-item-count">{int(match.group(1)) + delta}</span>'

    return re.sub(r'<span class="site-state-item-count">(\d+)</span>', repl, text, count=1)


def insert_archive_entry(html: str, entry: str) -> str:
    marker = '    <div class="collection-year">\n      <span class="collection-header">2026</span>\n    </div>\n\n  <article itemscope itemtype="http://schema.org/Article">\n    <header class="post-header">\n\n      <div class="post-meta">\n        <time itemprop="dateCreated"\n              datetime="2026-06-05T10:00:00+08:00"'
    if marker in html:
        return html.replace(marker, entry.strip() + "\n\n" + marker, 1)
    year_marker = '    <div class="collection-year">\n      <span class="collection-header">2026</span>\n    </div>'
    if year_marker in html:
        return html.replace(year_marker, year_marker + "\n" + entry, 1)
    raise RuntimeError("archive marker not found")


def update_sitemap(path: Path) -> None:
    if not path.exists():
        return
    sitemap = path.read_text(encoding="utf-8")
    if FULL_URL in sitemap:
        return
    if path.suffix == ".txt":
        sitemap = FULL_URL + "\n" + sitemap
    else:
        urlset_match = re.search(r"<urlset[^>]*>", sitemap)
        if not urlset_match:
            return
        url_entry = (
            f"  <url>\n    <loc>{FULL_URL}</loc>\n"
            f"    <lastmod>{DATE_DISPLAY}</lastmod>\n  </url>\n"
        )
        sitemap = sitemap.replace(urlset_match.group(0), urlset_match.group(0) + "\n" + url_entry, 1)
    path.write_text(sitemap, encoding="utf-8")


def remove_duplicate_entries(text: str, entry_html: str) -> str:
    first = text.find(entry_html.strip())
    if first == -1:
        return text
    second = text.find(entry_html.strip(), first + 1)
    while second != -1:
        text = text[:second] + text[second + len(entry_html.strip()) :]
        second = text.find(entry_html.strip(), first + 1)
    return text


def main() -> None:
    md_text = MD_SOURCE.read_text(encoding="utf-8")
    body_html = convert_markdown_to_html(md_text)
    template = TEMPLATE.read_text(encoding="utf-8")
    post_html = build_post_html(template, body_html)
    (ROOT / f"posts/{POST_FILE}").write_text(post_html, encoding="utf-8")

    index_path = ROOT / "index.html"
    index_html = index_path.read_text(encoding="utf-8")
    marker = (
        '  <article itemscope itemtype="http://schema.org/Article" class="post-block" lang="zh-Hans">\n'
        '    <link itemprop="mainEntityOfPage" href="https://www.fastolf.com/posts/e601e6a8.html">'
    )
    if marker not in index_html:
        raise RuntimeError("index.html marker not found")
    if POST_URL not in index_html:
        index_html = index_html.replace(marker, build_home_article().rstrip() + "\n\n" + marker, 1)
        index_html = increment_post_count(index_html)
    index_path.write_text(index_html, encoding="utf-8")

    archive_entry = build_archive_article()
    for rel_path in ("archives/index.html", "categories/mechine/index.html", "archives/2026/index.html"):
        path = ROOT / rel_path
        html = path.read_text(encoding="utf-8")
        html = remove_duplicate_entries(html, archive_entry)
        if POST_URL not in html:
            html = insert_archive_entry(html, archive_entry)
            if rel_path == "archives/index.html":
                html = increment_post_count(html)
        path.write_text(html, encoding="utf-8")

    search_path = ROOT / "search.xml"
    search_xml = search_path.read_text(encoding="utf-8")
    search_entry = build_search_entry().strip()
    search_xml = re.sub(
        rf"\s*<entry>\s*<title>{re.escape(TITLE)}</title>.*?</entry>",
        "",
        search_xml,
        flags=re.DOTALL,
    )
    search_marker = "    <entry>\n      <title>LLM Wiki 介绍：思想、意义、应用场景与优缺点</title>"
    if POST_URL not in search_xml:
        search_xml = search_xml.replace(search_marker, search_entry + "\n" + search_marker, 1)
    search_path.write_text(search_xml, encoding="utf-8")

    for sitemap_name in ("sitemap.txt", "sitemap.xml", "baidusitemap.xml"):
        update_sitemap(ROOT / sitemap_name)

    llm_post = ROOT / "posts/e601e6a8.html"
    llm_html = llm_post.read_text(encoding="utf-8")
    next_nav = f"""<div class="post-nav-item">
    <a href="{POST_URL}" rel="next" title="{TITLE}">
      {TITLE} <i class="fa fa-chevron-right"></i>
    </a></div>"""
    if POST_URL not in llm_html:
        llm_html = llm_html.replace('<div class="post-nav-item"></div>', next_nav, 1)
    llm_post.write_text(llm_html, encoding="utf-8")

    print(f"Published: {POST_URL}")


if __name__ == "__main__":
    main()
