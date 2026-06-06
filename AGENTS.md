# AGENTS.md

Guidance for AI agents working in this repository.

## Project overview

Qi Blog is a static site for [www.fastolf.com](https://www.fastolf.com), built with Hexo 8.x and the NexT 8.27 theme. There is no backend, database, or Docker stack.

- `blog-source/` — Hexo source (posts, theme config, build scripts)
- Repository root — Pre-built static HTML deployed to GitHub Pages
- `docs/` — Source markdown for article series (imported via Python scripts)
- `scripts/` — One-off Python publish/import utilities

## Cursor Cloud specific instructions

### Prerequisites

- **Node.js 22.x** and npm (CI uses `actions/setup-node@v4` with Node 22)
- **Python 3** (optional; only needed for content publish/migrate scripts)

### Development server (primary workflow)

```bash
cd blog-source
npm run server
```

Open http://localhost:4000. The Hexo dev server watches source files and rebuilds on change.

### Build and deploy output

```bash
cd blog-source
./deploy-to-root.sh   # clean + build + copy public/ to repo root
```

This matches the GitHub Actions deploy workflow (`.github/workflows/deploy.yml`).

### Lint and tests

This repo has **no** ESLint, Prettier, or automated test suite. Verification is:

- `npm run build` — confirms Hexo generates the site
- `npm run server` — confirms the dev server serves pages

### Optional: serve pre-built static site

To test committed output at the repo root (GitHub Pages layout) without Hexo:

```bash
cd /workspace
python3 -m http.server 8080
```

Open http://localhost:8080.

### Python content scripts (optional)

Publish/migrate scripts under `scripts/` and `blog-source/` may need:

```bash
pip install markdown beautifulsoup4
```

These are not required to run or browse the blog.

### Gotchas

- `blog-source/node_modules/` and `blog-source/public/` are gitignored; run `npm ci` in `blog-source/` after clone.
- Some posts reference external CDNs (MathJax, mermaid); diagram rendering can show client-side errors without affecting the Hexo server.
- `hexo deploy` is not configured (`deploy.type: ''` in `_config.yml`); deployment is via `deploy-to-root.sh` + git push or GitHub Actions.
