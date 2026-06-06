# Qi Blog 项目说明

> 个人技术博客 [www.fastolf.com](https://www.fastolf.com) 的源码与文档仓库  
> 作者：Meng Qi · 构建工具：Hexo 8 + NexT 8.27 · 部署：GitHub Pages

---

## 1. 项目定位

本仓库同时承担两个角色：

| 角色 | 说明 |
|------|------|
| **静态站点** | 仓库根目录是已生成的 HTML 站点，由 GitHub Pages 直接托管 |
| **内容工程** | `docs/` 存放 **全部 385 篇**博文源稿；`blog-source/source/_posts/` 仅由 sync 生成 |

全站博文均由 `docs/sync-manifest.json` 管理，索引见 `docs/posts-index.json`。

---

## 2. 目录结构

```
gitmmq.github.io/
├── README.md                 # 快速入门（面向人类开发者）
├── AGENTS.md                 # AI Agent 操作指南（面向 Cursor 等工具）
│
├── blog-source/              # ★ Hexo 源项目
│   ├── sync_docs.py          # docs/ → _posts/（清空并重写）
│   ├── .sync-generated.txt   # 本次 sync 产出清单
│   ├── deploy-to-root.sh
│   └── source/
│       └── _posts/           # ⚠ 生成目录，禁止手改
│
├── docs/                     # ★ 全部博文源稿（385 篇）
│   ├── sync-manifest.json    # 同步注册表（5 个系列）
│   ├── posts-index.json      # 全站索引（sync 自动刷新）
│   ├── posts/                # 历史博文（354 篇，按分类分目录）
│   ├── ai-agents/            # 12 篇
│   ├── agent-dev/            # 17 篇
│   ├── claude-code/          # 1 篇
│   └── records/              # 1 篇（基准环境）
├── .github/workflows/
│   └── deploy.yml            # push blog-source/docs 变更时自动构建部署
│
└── [生成站点]                # 以下目录由构建产出，勿手工编辑
    ├── index.html
    ├── posts/                # 385 篇 HTML 博文
    ├── categories/           # 15 个分类
    ├── tags/                 # 标签页
    ├── archives/             # 归档页
    ├── lib/ css/ js/ images/
    ├── search.xml            # 本地搜索索引
    ├── sitemap.xml
    └── CNAME                 # → www.fastolf.com
```

---

## 3. 发布管线（单一 Hexo 构建）

所有 **385 篇**博文统一经 manifest 驱动 sync：

```
docs/                              blog-source/source/_posts/
├── posts/<cat>/*.md      ──►     *.md（354 篇，保留文件名）
├── ai-agents/*.md        ──►     {hash}.md（12 篇）
├── agent-dev/*.md        ──►     语义 slug（17 篇）
├── claude-code/*.md      ──►     cd4fe79f.md
├── records/*.md          ──►     c8f01db4.md
         │
         └── sync_docs.py ← sync-manifest.json（5 系列）
                    ↓ 清空 _posts 后全量写入
              hexo generate → 根目录静态站点
                    ↓
              posts-index.json 自动刷新
```

- **同步脚本**：`blog-source/sync_docs.py`（`npm run sync`）
- **构建入口**：`blog-source/deploy-to-root.sh` 或 `npm run build`
- **permalink**：`posts/:name.html`（`:name` = 文件名去掉 `.md`）
- **URL 稳定**：ai-agents 用 md5 短 hash（如 `3131a1c6`），agent-dev 用语义 slug

### 编辑策略

| 内容类型 | 编辑位置 |
|----------|----------|
| 历史 / 普通博文 | `docs/posts/<category>/*.md` |
| Hermes × OpenClaw | `docs/ai-agents/*.md` + manifest |
| Agent 开发路线 | `docs/agent-dev/*.md` |
| Claude Code | `docs/claude-code/intro-bilingual.md` |
| 基准环境 | `docs/records/baseline-environment.md` |

**禁止**编辑 `blog-source/source/_posts/`——该目录每次 sync 清空并重写。

---

## 4. 博文分类

| 分类 slug | 说明 | 大致篇数 |
|-----------|------|----------|
| `algrithom` | 算法 | 多 |
| `framework` | 框架 / Agent 开发路线 | 含 agent-dev 系列 |
| `mechine` | AI / 机器学习 / Agent 产品 | 含 Hermes × OpenClaw |
| `java` `python` `node` | 语言 | — |
| `data` `mysql` `redis` | 数据存储 | — |
| `pattern` `quant` | 设计模式、量化 | — |
| `git` `hexo` `markdown` | 工具链 | — |
| `records` | 随笔记录 | — |

---

## 5. 本地开发

### 环境要求

- Node.js 22.x
- Python 3.10+（发布脚本、迁移脚本）
- npm

### 启动预览

```bash
cd blog-source
npm install
npm run server
# → http://localhost:4000
```

### 构建并部署到根目录

```bash
cd blog-source
./deploy-to-root.sh   # Linux/macOS；Windows 可用 Git Bash 或 WSL
git add -A
git commit -m "Site updated"
git push
```

### 从旧 HTML 反向迁移

```bash
cd blog-source
npm run migrate    # 读取根目录 posts/*.html → 写入 source/_posts/*.md
npm run build
```

---

## 6. CI/CD

`.github/workflows/deploy.yml` 在以下情况触发：

- push 到 `master` 且变更路径含 `blog-source/**` 或 `docs/**`
- 手动 `workflow_dispatch`

流程：`npm ci` → `sync_docs.py` → `hexo generate` → 复制到根目录 → 自动 commit & push。

---

## 7. 构建定制项

| 定制 | 位置 | 作用 |
|------|------|------|
| Mermaid 渲染 | `_config.yml` highlight exclude + `_config.next.yml` mermaid | 博文内嵌流程图 |
| Mermaid innerHTML 修复 | `deploy-to-root.sh` 内 Python 补丁 | 防止 HTML 实体被错误解析 |
| 动画降级 | `overrides/js/motion.js` | anime.js 加载失败时安全降级 |
| 启动脚本 | `overrides/js/next-boot.js` | NexT 引导逻辑 |
| 遗留索引保留 | `deploy-to-root.sh` | 保留旧版 categories/tags index |

---

## 8. 文档与知识库索引

| 文档 | 路径 | 读者 |
|------|------|------|
| 文档总索引 | [docs/README.md](./README.md) | 所有人 |
| AI 知识库 | [docs/knowledge-base/INDEX.md](./knowledge-base/INDEX.md) | AI Agent |
| Hermes × OpenClaw | [docs/ai-agents/README.md](./ai-agents/README.md) | 开发者 |
| Agent 开发路线 | [docs/agent-dev/README.md](./agent-dev/README.md) | 学习者 |
| AI 操作指南 | [AGENTS.md](../AGENTS.md) | Cursor 等 AI 工具 |

---

## 9. 常见维护场景

### 新增普通博文

1. 在 `docs/posts/<category>/` 创建 `my-post.md`（含 front matter）
2. `./deploy-to-root.sh`（`posts-index.json` 自动更新）

### 更新 Hermes × OpenClaw 文档

1. 编辑 `docs/ai-agents/<article>.md`
2. `cd blog-source && ./deploy-to-root.sh`
3. 提交 `docs/` 与生成站点

### 更新 Agent 开发路线

1. 编辑 `docs/agent-dev/agent-dev-*.md`
2. 同步更新 `docs/agent-dev/README.md` 或 `agent-dev-learning-roadmap-index.md`（如有目录变动）
3. `./deploy-to-root.sh` 构建

---

## 10. 外部链接

- 线上站点：https://www.fastolf.com
- GitHub：https://github.com/gitmmq/gitmmq.github.io
- OpenClaw 文档：https://docs.openclaw.ai/
- Hermes Agent 文档：https://hermes-agent.nousresearch.com/docs/
