# AI Agent 知识库索引

> **站点**：https://www.fastolf.com · **全站索引**：`docs/posts-index.json`（385 篇）

---

## 核心原则

**所有博文源稿在 `docs/`，`blog-source/source/_posts/` 100% 由 sync 生成，禁止手改。**

```bash
cd blog-source && ./deploy-to-root.sh
```

---

## 文档地图

| 路径 | 篇数 | manifest 系列 | 编辑方式 |
|------|------|---------------|----------|
| `docs/posts/<cat>/` | 354 | `posts` | front matter |
| `docs/ai-agents/` | 12 | `ai-agents` | 正文 md + manifest 元数据 |
| `docs/agent-dev/` | 17 | `agent-dev` | front matter |
| `docs/claude-code/` | 1 | `claude-code` | manifest 固定 slug |
| `docs/records/` | 1 | `records` | front matter + slug_map |

**合计 385 篇**，索引见 `docs/posts-index.json`（sync 时自动刷新）。

---

## sync-manifest.json 系列

| id | mode | dir |
|----|------|-----|
| ai-agents | registry | ai-agents |
| claude-code | fixed_slug | claude-code |
| agent-dev | front_matter | agent-dev |
| records | front_matter + slug_map | records |
| posts | front_matter + recursive | posts |

---

## 按任务编辑

| 任务 | 编辑位置 |
|------|----------|
| 历史/普通博文 | `docs/posts/<category>/<slug>.md` |
| Hermes × OpenClaw | `docs/ai-agents/<file>.md` + manifest |
| Agent 开发路线 | `docs/agent-dev/<file>.md` |
| Claude Code | `docs/claude-code/intro-bilingual.md` |
| 基准环境 | `docs/records/baseline-environment.md` |

---

## 新增博文

**普通博文**：在 `docs/posts/<category>/` 创建 md → `./deploy-to-root.sh`

**ai-agents 新篇**：创建 md → 在 `sync-manifest.json` 的 `ai-agents.posts` 注册 → build

**agent-dev 新篇**：创建 md（含 front matter）→ build（glob 自动发现）

---

## 分类目录（docs/posts/）

`algrithom` `data` `framework` `git` `hexo` `java` `markdown` `mechine` `mysql` `node` `pattern` `python` `quant` `records` `redis`

---

## 工具

| 脚本 | 用途 |
|------|------|
| `blog-source/sync_docs.py` | 构建前同步（清空并重写 _posts） |
| `blog-source/tools/migrate_all_posts_to_docs.py` | 一次性迁移（已完成） |
| `blog-source/tools/html_to_markdown.py` | HTML → Markdown 转换 |

---

## 统计

| 指标 | 值 |
|------|-----|
| 全站博文 | 385 |
| docs 源稿 | 385 |
| manifest 系列 | 5 |
