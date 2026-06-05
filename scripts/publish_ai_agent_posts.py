#!/usr/bin/env python3
"""Publish docs/ai-agents/*.md as Hexo-style static blog posts."""

from __future__ import annotations

import hashlib
import html
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import markdown
from markdown.extensions.tables import TableExtension

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "ai-agents"
TEMPLATE_POST = ROOT / "posts" / "e601e6a8.html"
CATEGORY = "mechine"
TZ = timezone(timedelta(hours=8))
BASE_DATE_BATCH1 = datetime(2026, 6, 5, 11, 0, 0, tzinfo=TZ)
BASE_DATE_BATCH2 = datetime(2026, 6, 6, 10, 0, 0, tzinfo=TZ)
TOTAL_POST_COUNT = 372  # 360 original + 4 batch1 + 8 batch2
ORIGINAL_TAG_COUNT = 18
MECHINE_CATEGORY_COUNT = 44  # 32 original + 12 AI agent series
TAG_CLOUD_SIZE = {
    12: ('24px', '#363636'),
    1: ('12px', '#ccc'),
}

SERIES_SHORT = {
    "hermes-openclaw-overview.md": "总览",
    "memory-system.md": "记忆",
    "gateway.md": "Gateway",
    "security-model.md": "安全",
    "skills-learning-loop.md": "技能",
    "tools-execution-environments.md": "工具",
    "workspace-context-prompt.md": "工作区",
    "automation-cron-heartbeat.md": "自动化",
    "model-provider-cost.md": "模型",
    "multi-agent-delegation.md": "多Agent",
    "plugins-mcp-ecosystem.md": "插件MCP",
    "deploy-migrate-operations.md": "部署",
}

POSTS = [
    {
        "md": "hermes-openclaw-overview.md",
        "title": "Agent Hermes 与 OpenClaw（龙虾）：架构、应用与对比",
        "description": "系统介绍 Agent Hermes 与 OpenClaw（龙虾）的架构设计、典型应用场景与优缺点对比，中英文对照。",
        "excerpt_zh": "本文对比 Agent Hermes 与 OpenClaw（龙虾）两大个人 AI Agent 框架的架构哲学、应用场景与优缺点，采用中英文对照形式。",
        "excerpt_en": "A bilingual comparison of Agent Hermes and OpenClaw (Lobster): architecture, use cases, and pros & cons.",
        "tags": "AI Agent;Hermes;OpenClaw",
        "batch": 1,
        "hour_offset": 0,
    },
    {
        "md": "memory-system.md",
        "title": "Agent Hermes 与 OpenClaw 记忆系统深度解析",
        "description": "深度解析 Hermes 四层记忆与 OpenClaw Workspace 文件记忆体系的设计、检索机制与最佳实践，中英文对照。",
        "excerpt_zh": "对比 Hermes 四层记忆（SQLite FTS5 + 技能渐进披露）与 OpenClaw Markdown 工作区文件记忆体系。",
        "excerpt_en": "Deep dive into Hermes four-layer memory vs OpenClaw workspace Markdown memory.",
        "tags": "AI Agent;Memory;Hermes;OpenClaw",
        "batch": 1,
        "hour_offset": 1,
    },
    {
        "md": "gateway.md",
        "title": "Agent Hermes 与 OpenClaw Gateway 架构深度解析",
        "description": "对比 OpenClaw Gateway 控制平面与 Hermes GatewayRunner 的消息路由、授权、投递与部署模式，中英文对照。",
        "excerpt_zh": "OpenClaw「Gateway 即产品」与 Hermes「Agent 引擎消息前端」的架构对比与生产部署指南。",
        "excerpt_en": "Gateway architecture comparison: OpenClaw control plane vs Hermes GatewayRunner.",
        "tags": "AI Agent;Gateway;Hermes;OpenClaw",
        "batch": 1,
        "hour_offset": 2,
    },
    {
        "md": "security-model.md",
        "title": "Agent Hermes 与 OpenClaw 安全模型深度解析",
        "description": "对比 OpenClaw 身份先行安全模型与 Hermes 七层纵深防御：审批、沙箱、SSRF、供应链与生产硬化清单，中英文对照。",
        "excerpt_zh": "OpenClaw「身份先行」与 Hermes「七层纵深防御」安全模型对比及生产硬化清单。",
        "excerpt_en": "Security model comparison: OpenClaw access-control-first vs Hermes defense-in-depth.",
        "tags": "AI Agent;Security;Hermes;OpenClaw",
        "batch": 1,
        "hour_offset": 3,
    },
    {
        "md": "skills-learning-loop.md",
        "title": "Agent Hermes 与 OpenClaw 技能系统与学习闭环全解析",
        "description": "全面对比 SKILL.md 标准、渐进式披露、Skills Hub/ClawHub、skill_manage 自生成与 Skill Workshop 提案队列，中英文对照。",
        "excerpt_zh": "Hermes 闭环学习自动沉淀技能 vs OpenClaw 手动编写与 Skill Workshop 提案审核。",
        "excerpt_en": "Skills systems compared: Hermes auto-learning loop vs OpenClaw ClawHub and Skill Workshop.",
        "tags": "AI Agent;Skills;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 0,
    },
    {
        "md": "tools-execution-environments.md",
        "title": "Agent Hermes 与 OpenClaw 工具链与执行环境全解析",
        "description": "系统讲解 Hermes 70+ 工具与 6 种执行后端、OpenClaw tools.profile 与沙箱策略，中英文对照。",
        "excerpt_zh": "工具集、终端后端、Docker 持久沙箱、浏览器自动化与后台进程管理全面对比。",
        "excerpt_en": "Tools, toolsets, execution backends, sandboxing, and browser automation compared.",
        "tags": "AI Agent;Tools;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 1,
    },
    {
        "md": "workspace-context-prompt.md",
        "title": "Agent Hermes 与 OpenClaw 工作区文件与 Prompt 组装全解析",
        "description": "深度解析 SOUL/AGENTS/HEARTBEAT 等 Bootstrap 文件、Prompt 分层与 contextVisibility，中英文对照。",
        "excerpt_zh": "OpenClaw 8 大 Bootstrap 文件与 Hermes Prompt 三层组装、前缀缓存稳定性设计。",
        "excerpt_en": "Workspace bootstrap files, prompt tiers, and context assembly compared.",
        "tags": "AI Agent;Prompt;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 2,
    },
    {
        "md": "automation-cron-heartbeat.md",
        "title": "Agent Hermes 与 OpenClaw 自动化调度与主动巡检全解析",
        "description": "Cron 调度、HEARTBEAT 主动巡检、no-agent 模式与 wakeAgent 门控、context_from 流水线，中英文对照。",
        "excerpt_zh": "Hermes cronjob 全生命周期与 OpenClaw HEARTBEAT.md 主动巡检模式对比。",
        "excerpt_en": "Cron automation, HEARTBEAT proactive checks, and pipeline chaining compared.",
        "tags": "AI Agent;Cron;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 3,
    },
    {
        "md": "model-provider-cost.md",
        "title": "Agent Hermes 与 OpenClaw 模型 Provider 与 Token 成本优化全解析",
        "description": "18+ Provider 配置、fallback、credential pool、Prompt 缓存与上下文压缩的成本优化策略，中英文对照。",
        "excerpt_zh": "模型切换、多 Provider 容灾、Anthropic 前缀缓存与 Cron Token 成本控制。",
        "excerpt_en": "Model providers, fallback, prompt caching, and token cost optimization.",
        "tags": "AI Agent;Model;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 4,
    },
    {
        "md": "multi-agent-delegation.md",
        "title": "Agent Hermes 与 OpenClaw 多 Agent 路由与子代理委派全解析",
        "description": "多 Agent 工作区隔离、session.dmScope、delegate_task 与 sessions_spawn 风险治理，中英文对照。",
        "excerpt_zh": "个人助理 vs 团队 Agent 模式，子代理并行与会话隔离最佳实践。",
        "excerpt_en": "Multi-agent routing, sub-agent delegation, and session isolation compared.",
        "tags": "AI Agent;Multi-Agent;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 5,
    },
    {
        "md": "plugins-mcp-ecosystem.md",
        "title": "Agent Hermes 与 OpenClaw 插件体系与 MCP 生态全解析",
        "description": "插件发现机制、MCP 双向集成、渠道插件与供应链安全策略全面对比，中英文对照。",
        "excerpt_zh": "Hermes MCP 客户端/服务端与 OpenClaw 进程内插件、plugins.allow 白名单对比。",
        "excerpt_en": "Plugin systems and bidirectional MCP integration compared.",
        "tags": "AI Agent;MCP;Plugins;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 6,
    },
    {
        "md": "deploy-migrate-operations.md",
        "title": "Agent Hermes 与 OpenClaw 部署迁移与运维实战指南",
        "description": "安装初始化、hermes claw migrate、openclaw onboard、渠道配置、doctor/audit 运维清单，中英文对照。",
        "excerpt_zh": "从安装到生产的完整路径：迁移、渠道接入、Gateway 服务化与故障排查。",
        "excerpt_en": "Install, migrate, channel setup, and operations runbooks compared.",
        "tags": "AI Agent;Deploy;Hermes;OpenClaw",
        "batch": 2,
        "hour_offset": 7,
    },
]


def series_links_html() -> str:
    links = [
        f'<a href="/posts/{post_id(md)}.html">{label}</a>'
        for md, label in SERIES_SHORT.items()
    ]
    return (
        "<p>系列文章（12 篇）："
        + " · ".join(links)
        + "</p>"
        + "<p><em>12-article series: Hermes × OpenClaw bilingual technical docs.</em></p>"
    )


def published_at(meta: dict) -> datetime:
    base = BASE_DATE_BATCH1 if meta.get("batch", 1) == 1 else BASE_DATE_BATCH2
    return base + timedelta(hours=meta.get("hour_offset", 0))


def already_indexed(content: str, pid: str) -> bool:
    return f"/posts/{pid}.html" in content


def tag_dir_name(tag: str) -> str:
    if re.fullmatch(r"[\x00-\x7f]+", tag):
        return tag.replace(" ", "-")
    return tag


def tag_href(tag: str) -> str:
    name = tag_dir_name(tag)
    if re.fullmatch(r"[\x00-\x7f]+", tag):
        return f"/tags/{name}/"
    return f"/tags/{quote(name)}/"


def collect_tag_posts(rendered_posts: list[dict]) -> dict[str, list[dict]]:
    tag_posts: dict[str, list[dict]] = defaultdict(list)
    for post in rendered_posts:
        for tag in post["tags"].split(";"):
            tag = tag.strip()
            if tag:
                tag_posts[tag].append(post)
    for tag in tag_posts:
        tag_posts[tag].sort(key=lambda p: p["published"], reverse=True)
    return dict(tag_posts)


def post_tags_html(tags: str) -> str:
    links = [
        f'<a href="{tag_href(tag.strip())}" rel="tag"># {html.escape(tag.strip())}</a>'
        for tag in tags.split(";")
        if tag.strip()
    ]
    return (
        "\n          <div class=\"post-tags\">\n              "
        + "\n              ".join(links)
        + "\n          </div>\n"
    )


def tag_cloud_link(tag: str, count: int) -> str:
    size, color = TAG_CLOUD_SIZE.get(count, ('15.6px', '#a7a7a7'))
    if count >= 8:
        size, color = ('24px', '#363636')
    elif count >= 3:
        size, color = ('19.2px', '#818181')
    return (
        f'<a href="{tag_href(tag)}" style="font-size: {size}; color: {color}">'
        f"{html.escape(tag)}</a>"
    )


def tag_articles_html(posts: list[dict]) -> str:
    by_year: dict[str, list[dict]] = defaultdict(list)
    for post in posts:
        by_year[post["published"].strftime("%Y")].append(post)

    blocks: list[str] = []
    for year in sorted(by_year, reverse=True):
        blocks.append(
            f"""    <div class="collection-year">
      <span class="collection-header">{year}</span>
    </div>
"""
        )
        for post in by_year[year]:
            blocks.append(
                archive_article_block(
                    pid=post["pid"],
                    title=post["title"],
                    published=post["published"],
                )
            )
    return "".join(blocks)


def patch_sidebar_site_state(content: str, *, tag_count: int | None = None) -> str:
    content = re.sub(
        r"(<div class=\"site-state-item site-state-posts\">.*?<span class=\"site-state-item-count\">)\d+(</span>)",
        rf"\g<1>{TOTAL_POST_COUNT}\g<2>",
        content,
        count=1,
        flags=re.DOTALL,
    )
    if tag_count is not None:
        content = re.sub(
            r"(<div class=\"site-state-item site-state-tags\">.*?<span class=\"site-state-item-count\">)\d+(</span>)",
            rf"\g<1>{tag_count}\g<2>",
            content,
            count=1,
            flags=re.DOTALL,
        )
    return content


def render_tag_page(template: str, tag: str, posts: list[dict], tag_count: int) -> str:
    slug = tag_dir_name(tag)
    page = template
    page = page.replace("标签: hexo", f"标签: {tag}")
    page = page.replace("https://www.fastolf.com/tags/hexo/index.html", tag_href(tag).rstrip("/") + "/index.html")
    page = page.replace('href="https://www.fastolf.com/tags/hexo/"', f'href="https://www.fastolf.com{tag_href(tag)}"')
    page = page.replace("<title>标签: hexo | Qi", f"<title>标签: {html.escape(tag)} | Qi")
    page = page.replace(
        """        <h2 class="collection-header">hexo
          <small>标签</small>
        </h2>""",
        f"""        <h2 class="collection-header">{html.escape(tag)}
          <small>标签</small>
        </h2>""",
    )

    articles_start = """        </h2>
      </div>

      """
    articles_end = """    </div>
  </div>
  
  
  

"""
    start_idx = page.index(articles_start) + len(articles_start)
    end_idx = page.index(articles_end, start_idx)
    page = page[:start_idx] + tag_articles_html(posts) + page[end_idx:]
    return patch_sidebar_site_state(page, tag_count=tag_count)


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
    tags: str,
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
    page = page.replace("Tech;Data;Vision", tags)
    page = page.replace(
        re.search(r'<span class="site-state-item-count">\d+</span>', page).group(0),
        f'<span class="site-state-item-count">{TOTAL_POST_COUNT}</span>',
    )

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
        post_tags_html(tags)
        + "        <div class=\"post-nav\">\n"
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

    series_html = series_links_html()
    for meta in POSTS:
        md_path = DOCS / meta["md"]
        md_text = md_path.read_text(encoding="utf-8")
        slug = meta["md"]
        pid = post_id(slug)
        published = published_at(meta)
        body_html = md_to_html(md_text)
        chars = word_count(re.sub(r"<[^>]+>", "", body_html))
        minutes = reading_minutes(chars)
        excerpt_html = (
            f"<p>{html.escape(meta['excerpt_zh'])}</p>"
            f"<p><em>{html.escape(meta['excerpt_en'])}</em></p>"
            + series_html
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
            tags=post["tags"],
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

    # index.html - prepend home blocks (idempotent: only missing posts)
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    marker = '  <article itemscope itemtype="http://schema.org/Article" class="post-block" lang="zh-Hans">\n    <link itemprop="mainEntityOfPage" href="https://www.fastolf.com/posts/e601e6a8.html">'
    missing_desc = [p for p in rendered_posts_desc if not already_indexed(index, p["pid"])]
    if missing_desc:
        blocks = "".join(
            home_article_block(
                pid=p["pid"],
                title=p["title"],
                excerpt_html=p["excerpt_html"],
                published=p["published"],
                chars=p["chars"],
                minutes=p["minutes"],
            )
            for p in missing_desc
        )
        index = index.replace(marker, blocks + "\n" + marker, 1)
    index = re.sub(
        r'(<span class="site-state-item-count">)\d+(</span>)',
        rf"\g<1>{TOTAL_POST_COUNT}\g<2>",
        index,
        count=1,
    )
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
    def prepend_archive_blocks(content: str, marker: str, blocks: str) -> str:
        missing = [p for p in rendered_posts_desc if not already_indexed(content, p["pid"])]
        if not missing:
            return content
        new_blocks = "".join(
            archive_article_block(pid=p["pid"], title=p["title"], published=p["published"])
            for p in missing
        )
        return content.replace(marker, new_blocks + marker, 1)

    arch_blocks_all = "".join(
        archive_article_block(pid=p["pid"], title=p["title"], published=p["published"])
        for p in rendered_posts_desc
    )
    archives = prepend_archive_blocks(archives, arch_marker, arch_blocks_all)
    (ROOT / "archives" / "index.html").write_text(archives, encoding="utf-8")

    # archives/2026/index.html — insert before first 2026-06-05 LLM Wiki entry
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
    missing_2026 = [p for p in rendered_posts_desc if not already_indexed(arch2026, p["pid"])]
    if missing_2026:
        new_blocks = "".join(
            archive_article_block(pid=p["pid"], title=p["title"], published=p["published"])
            for p in missing_2026
        )
        arch2026 = arch2026.replace(arch2026_marker, new_blocks + arch2026_marker, 1)
        arch2026 = re.sub(
            r"(太棒了! 目前共计 )\d+( 篇日志)",
            rf"\g<1>{TOTAL_POST_COUNT}\g<2>",
            arch2026,
            count=1,
        )
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
    cat = prepend_archive_blocks(cat, cat_marker, "")
    (ROOT / "categories" / "mechine" / "index.html").write_text(cat, encoding="utf-8")

    # search.xml (idempotent)
    search = (ROOT / "search.xml").read_text(encoding="utf-8")
    missing_search = [p for p in rendered_posts_desc if f"/posts/{p['pid']}.html" not in search]
    if missing_search:
        insert_at = search.index("<entry>\n      <title>LLM Wiki")
        search_entries = "".join(
            search_entry(pid=p["pid"], title=p["title"], excerpt_html=p["excerpt_html"])
            for p in missing_search
        )
        search = search[:insert_at] + search_entries + "\n    \n    \n    " + search[insert_at:]
    (ROOT / "search.xml").write_text(search, encoding="utf-8")

    # sitemap.xml + sitemap.txt + baidusitemap.xml (idempotent)
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    missing_sitemap = [p for p in rendered_posts_desc if f"posts/{p['pid']}.html" not in sitemap]
    if missing_sitemap:
        sitemap_insert = sitemap.index("<url>\n    <loc>https://www.fastolf.com/posts/e601e6a8.html</loc>")
        sitemap_urls = "".join(sitemap_url(p["pid"], p["published"]) for p in missing_sitemap)
        sitemap = sitemap[:sitemap_insert] + sitemap_urls + sitemap[sitemap_insert:]
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    sitemap_txt = (ROOT / "sitemap.txt").read_text(encoding="utf-8")
    for p in rendered_posts_desc:
        url = f"https://www.fastolf.com/posts/{p['pid']}.html\n"
        if url.strip() not in sitemap_txt:
            sitemap_txt = url + sitemap_txt
    (ROOT / "sitemap.txt").write_text(sitemap_txt, encoding="utf-8")

    baidu = (ROOT / "baidusitemap.xml").read_text(encoding="utf-8")
    missing_baidu = [p for p in rendered_posts_desc if f"posts/{p['pid']}.html" not in baidu]
    if missing_baidu:
        baidu_insert = baidu.index("<url>\n    <loc>https://www.fastolf.com/posts/e601e6a8.html</loc>")
        baidu_urls = "".join(
            f"  <url>\n    <loc>https://www.fastolf.com/posts/{p['pid']}.html</loc>\n"
            f"    <lastmod>{p['published'].strftime('%Y-%m-%d')}</lastmod>\n  </url>\n"
            for p in missing_baidu
        )
        baidu = baidu[:baidu_insert] + baidu_urls + baidu[baidu_insert:]
    (ROOT / "baidusitemap.xml").write_text(baidu, encoding="utf-8")

    # tags/index.html + per-tag archive pages
    tag_posts = collect_tag_posts(rendered_posts)
    total_tag_count = ORIGINAL_TAG_COUNT + len(tag_posts)
    tag_template = (ROOT / "tags" / "hexo" / "index.html").read_text(encoding="utf-8")

    tags_index = (ROOT / "tags" / "index.html").read_text(encoding="utf-8")
    tags_index = re.sub(
        r"(目前共计 )\d+( 个标签)",
        rf"\g<1>{total_tag_count}\g<2>",
        tags_index,
        count=1,
    )
    new_tag_links = [
        tag_cloud_link(tag, len(posts))
        for tag, posts in sorted(tag_posts.items())
        if tag_href(tag) not in tags_index
    ]
    if new_tag_links:
        tags_index = tags_index.replace(
            '</div>\n          </div>\n        \n      </div>',
            " " + " ".join(new_tag_links) + '</div>\n          </div>\n        \n      </div>',
            1,
        )
    tags_index = patch_sidebar_site_state(tags_index, tag_count=total_tag_count)
    (ROOT / "tags" / "index.html").write_text(tags_index, encoding="utf-8")

    for tag, posts in tag_posts.items():
        tag_dir = ROOT / "tags" / tag_dir_name(tag)
        tag_dir.mkdir(parents=True, exist_ok=True)
        tag_page = render_tag_page(tag_template, tag, posts, total_tag_count)
        (tag_dir / "index.html").write_text(tag_page, encoding="utf-8")
        print(f"Wrote tag page {tag_href(tag)} ({len(posts)} posts)")

    # categories/index.html — bump mechine post count
    categories_index = (ROOT / "categories" / "index.html").read_text(encoding="utf-8")
    categories_index = re.sub(
        r'(href="/categories/mechine/">mechine</a><span class="category-list-count">)\d+(</span>)',
        rf"\g<1>{MECHINE_CATEGORY_COUNT}\g<2>",
        categories_index,
        count=1,
    )
    categories_index = patch_sidebar_site_state(categories_index, tag_count=total_tag_count)
    (ROOT / "categories" / "index.html").write_text(categories_index, encoding="utf-8")

    # Refresh sidebar counts on key listing pages
    for rel_path in (
        "archives/index.html",
        "archives/2026/index.html",
        "categories/mechine/index.html",
    ):
        path = ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        path.write_text(patch_sidebar_site_state(text, tag_count=total_tag_count), encoding="utf-8")

    print(
        f"Updated site indexes. New posts this run: {len(missing_desc)} on homepage. "
        f"Tags: {total_tag_count}, mechine: {MECHINE_CATEGORY_COUNT}."
    )


if __name__ == "__main__":
    main()
