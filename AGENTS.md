# AGENTS.md — AI Agent 操作指南

> 人类开发者请参阅 [README.md](./README.md) 与 [docs/PROJECT.md](./docs/PROJECT.md)。

## 核心规则

- **385 篇博文源稿全部在 `docs/`**
- **`blog-source/source/_posts/` 禁止手改**（sync 时清空并重写）
- **全站索引**：`docs/posts-index.json`
- **同步清单**：`docs/sync-manifest.json`

## 发布

```bash
cd blog-source && ./deploy-to-root.sh
```

## 源稿位置

| 类型 | 编辑路径 | 篇数 |
|------|----------|------|
| 历史博文 | `docs/posts/<category>/*.md` | 354 |
| Hermes × OpenClaw | `docs/ai-agents/*.md` | 12 |
| Agent 开发 | `docs/agent-dev/*.md` | 17 |
| Claude Code | `docs/claude-code/intro-bilingual.md` | 1 |
| 基准环境 | `docs/records/baseline-environment.md` | 1 |

## manifest 系列（sync-manifest.json）

| id | 说明 |
|----|------|
| `posts` | 递归同步 `docs/posts/**`（保留文件名 → URL） |
| `ai-agents` | registry 模式，输出 `{hash}.md` |
| `agent-dev` | front matter，语义 slug |
| `claude-code` | 固定 `cd4fe79f.md` |
| `records` | `baseline-environment.md` → `c8f01db4.md` |

## 新增博文

```bash
# 普通博文
# 1. 创建 docs/posts/<category>/my-post.md（含 front matter）
# 2. cd blog-source && ./deploy-to-root.sh

# ai-agents 专题
# 1. docs/ai-agents/new.md
# 2. 在 sync-manifest.json 注册
# 3. ./deploy-to-root.sh
```

## 先读

1. [docs/knowledge-base/INDEX.md](./docs/knowledge-base/INDEX.md)
2. [docs/posts-index.json](./docs/posts-index.json) — 按 slug 查源路径
3. [docs/PROJECT.md](./docs/PROJECT.md)

## 约束

- 不手改 `_posts/`、`posts/*.html`
- ai-agents 正文不加 front matter（元数据在 manifest）
- agent-dev / posts 必须含 front matter
- Mermaid 块内避免空行
