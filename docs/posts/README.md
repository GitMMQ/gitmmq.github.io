# 历史博文库

本目录收录 **354 篇**历史博文，按 Hexo 分类分目录存放。构建时由 `sync_docs.py` 同步到 `blog-source/source/_posts/`。

> 全站 385 篇博文索引：[posts-index.json](../posts-index.json)  
> 同步清单：[sync-manifest.json](../sync-manifest.json) → `posts` 系列

## 目录结构

```
docs/posts/
├── algrithom/      算法
├── data/           数据
├── framework/      框架
├── java/           Java
├── mechine/        AI / 机器学习
├── python/         Python
├── node/           Node.js
├── redis/          Redis
├── mysql/          MySQL
├── pattern/        设计模式
├── quant/          量化
├── git/            Git
├── hexo/           Hexo
├── markdown/       Markdown
└── records/        随笔（历史分类，非 docs/records/ 系列）
```

## 编辑规则

1. **编辑位置**：`docs/posts/<category>/<slug>.md`（保留 YAML front matter）
2. **URL 不变**：输出文件名 = 源文件名（如 `742.md` → `/posts/742.html`）
3. **不要**直接改 `blog-source/source/_posts/`（构建时会被清空重写）

## 新增普通博文

```bash
# 1. 创建 docs/posts/<category>/my-new-post.md
# 2. 构建
cd blog-source && ./deploy-to-root.sh
# posts-index.json 会自动更新
```

## 与专题系列的区别

| 路径 | 用途 |
|------|------|
| `docs/posts/` | 历史博文（354 篇），按分类分目录 |
| `docs/ai-agents/` | Hermes × OpenClaw 专题（12 篇） |
| `docs/agent-dev/` | Agent 开发路线（17 篇） |
| `docs/claude-code/` | Claude Code（1 篇） |
| `docs/records/` | 独立专题：基准环境（1 篇，slug `c8f01db4`） |
