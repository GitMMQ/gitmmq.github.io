# Qi Blog

Personal blog for [www.fastolf.com](https://www.fastolf.com), built with Hexo and the NexT theme.

## Tech Stack

| Component | Version |
| --- | --- |
| Hexo | 8.x |
| NexT Theme | 8.27 |
| Node.js | 22.x |

## Project Layout

- `blog-source/` — Hexo source project (posts, theme config, build scripts)
- Repository root — Generated static site deployed to GitHub Pages

## Local Development

```bash
cd blog-source
npm install
npm run server
```

Open http://localhost:4000

## Build and Deploy

```bash
cd blog-source
./deploy-to-root.sh
git add -A
git commit -m "Site updated"
git push
```

Pushes that change files under `blog-source/` also trigger the GitHub Actions workflow to rebuild and deploy automatically.

## Migrate Posts from Legacy HTML

If you need to re-import posts from the old static HTML output at the repository root:

```bash
cd blog-source
npm run migrate
npm run build
```
