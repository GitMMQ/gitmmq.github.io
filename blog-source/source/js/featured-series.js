(function () {
  'use strict';

  function parsePageConfig() {
    var el = document.querySelector('script.next-config[data-name="page"]');
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return null;
    }
  }

  function mountFeaturedSeries() {
    var page = parsePageConfig();
    if (!page || !page.isHome) return;

    var container = document.querySelector('.main-inner.index.posts-expand');
    if (!container || document.querySelector('.featured-series')) return;

    var box = document.createElement('section');
    box.className = 'featured-series';
    box.setAttribute('aria-label', '精选系列');
    box.innerHTML =
      '<h2 class="featured-series-title">精选系列</h2>' +
      '<div class="featured-series-grid">' +
      '<a class="featured-series-card" href="/posts/3131a1c6.html">' +
      '<h3>Hermes × OpenClaw</h3>' +
      '<p>12 篇中英文对照：架构、部署、记忆、技能与 MCP 生态。</p>' +
      '<span class="featured-series-link">从总览开始 →</span>' +
      '</a>' +
      '<a class="featured-series-card" href="/posts/agent-dev-learning-roadmap-index.html">' +
      '<h3>Agent 开发学习路线</h3>' +
      '<p>五层能力模型，14 篇从 Python/TS 到 LangGraph 与工程化。</p>' +
      '<span class="featured-series-link">查看路线 →</span>' +
      '</a>' +
      '<a class="featured-series-card" href="/tags/%E6%8A%80%E6%9C%AF%E7%BC%96%E5%B9%B4%E5%8F%B2/">' +
      '<h3>AI 技术编年史</h3>' +
      '<p>2021–2026 关键 AI 里程碑，按年独立成篇。</p>' +
      '<span class="featured-series-link">浏览编年史 →</span>' +
      '</a>' +
      '</div>' +
      '<p class="featured-series-more"><a href="/series/">查看全部系列索引 →</a></p>';

    container.insertBefore(box, container.firstChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountFeaturedSeries);
  } else {
    mountFeaturedSeries();
  }
})();
