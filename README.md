# Qi Blog

Personal blog for [www.fastolf.com](https://www.fastolf.com), built with Hexo and the NexT theme.

## Tech Stack

| Component | Version |
| --- | --- |
| Hexo | 8.x |
| NexT Theme | 8.27 |
| Node.js | 22.x |

## Repository Layout

| Path | Role |
| --- | --- |
| `docs/` | **All 385 post sources** + manifest + index |
| `blog-source/` | Hexo project; `_posts/` is **generated only** |
| Repository root | Generated static site for GitHub Pages |

**Full documentation**: [docs/PROJECT.md](./docs/PROJECT.md)  
**AI Agent guide**: [AGENTS.md](./AGENTS.md)  
**Knowledge base**: [docs/knowledge-base/INDEX.md](./docs/knowledge-base/INDEX.md)

## Content (all in `docs/`)

| Series | Path | Count |
| --- | --- | --- |
| Legacy posts | `docs/posts/<category>/` | 354 |
| Hermes × OpenClaw | `docs/ai-agents/` | 12 |
| Agent Dev Roadmap | `docs/agent-dev/` | 17 |
| Claude Code | `docs/claude-code/` | 1 |
| Records (baseline env) | `docs/records/` | 1 |

**Full index**: [docs/posts-index.json](./docs/posts-index.json) · **Manifest**: [docs/sync-manifest.json](./docs/sync-manifest.json)

## Local Development

```bash
cd blog-source
npm install
npm run server    # sync docs → preview
```

Open http://localhost:4000

## Build and Deploy (single pipeline)

```bash
cd blog-source
./deploy-to-root.sh   # sync_docs.py → hexo build → copy to root
git add -A
git commit -m "Site updated"
git push
```

Changes under `blog-source/**` or `docs/**` trigger GitHub Actions to rebuild automatically.

## Migrate Posts from Legacy HTML

```bash
cd blog-source
npm run migrate
npm run build
```
