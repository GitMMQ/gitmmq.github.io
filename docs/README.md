# 文档中心

本目录是 **全站 385 篇博文的唯一源稿**，由 `docs/sync-manifest.json` 统一管理。

> 全站索引：[posts-index.json](./posts-index.json) · 架构：[PROJECT.md](./PROJECT.md) · AI 操作：[AGENTS.md](../AGENTS.md)

---

## 文档地图

```
docs/
├── sync-manifest.json      ★ 5 系列同步注册表
├── posts-index.json        ★ 385 篇全站索引（sync 自动刷新）
├── posts/                  354 篇历史博文（按分类分目录）
├── ai-agents/              12 篇 Hermes × OpenClaw
├── agent-dev/              17 篇 Agent 开发路线
├── claude-code/            1 篇
├── records/                1 篇（基准环境）
└── knowledge-base/         AI Agent 知识库
```

---

## 发布

```bash
cd blog-source && ./deploy-to-root.sh
```

---

## 系列一览

| 系列 | 路径 | 篇数 | 说明 |
|------|------|------|------|
| posts | [posts/](./posts/) | 354 | 历史博文，按分类分目录 |
| ai-agents | [ai-agents/](./ai-agents/) | 12 | 元数据在 manifest |
| agent-dev | [agent-dev/](./agent-dev/) | 17 | 含 front matter |
| claude-code | [claude-code/](./claude-code/) | 1 | 固定 slug |
| records | [records/](./records/) | 1 | slug_map → c8f01db4 |

---

## 面向 AI Agent

1. [knowledge-base/INDEX.md](./knowledge-base/INDEX.md) — 操作规则
2. [posts-index.json](./posts-index.json) — 按 slug 查源路径
