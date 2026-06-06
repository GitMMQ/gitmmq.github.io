/* global NexT, CONFIG */

NexT.boot = {};

NexT.boot.closeMobileNav = function() {
  document.body.classList.remove('site-nav-on');
  const toggle = document.querySelector('.site-nav-toggle .toggle');
  if (toggle) toggle.classList.remove('toggle-close');
};

NexT.boot.ensureNavVisible = function() {
  if (!CONFIG.motion?.enable) return;

  const column = document.querySelector('.column');
  if (column) column.style.opacity = '1';

  document.querySelectorAll('.site-brand-container .toggle').forEach(toggle => {
    toggle.style.opacity = '1';
    toggle.style.top = '0px';
  });

  const menuItemTransition = CONFIG.motion.transition?.menu_item;
  document.querySelectorAll('.site-nav .menu-item').forEach(item => {
    if (item.classList.contains('animated')) return;
    if (menuItemTransition) item.classList.add('animated', menuItemTransition);
    else item.classList.add('animated');
  });
};

NexT.boot.registerEvents = function() {

  NexT.utils.registerScrollPercent();
  NexT.utils.registerCanIUseTag();
  NexT.utils.updateFooterPosition();

  // Mobile top menu bar.
  const navToggle = document.querySelector('.site-nav-toggle .toggle');
  navToggle?.addEventListener('click', event => {
    event.currentTarget.classList.toggle('toggle-close');
    const siteNav = document.querySelector('.site-nav');
    if (!siteNav) return;
    siteNav.style.setProperty('--scroll-height', siteNav.scrollHeight + 'px');
    document.body.classList.toggle('site-nav-on');
  });

  document.querySelectorAll('.site-nav .menu-item a[href]').forEach(link => {
    link.addEventListener('click', () => {
      NexT.boot.closeMobileNav();
    });
  });

  document.addEventListener('pjax:success', () => {
    NexT.boot.closeMobileNav();
    NexT.boot.ensureNavVisible();
  });

  document.querySelectorAll('.sidebar-nav li').forEach((element, index) => {
    element.addEventListener('click', () => {
      NexT.utils.activateSidebarPanel(index);
    });
  });

  window.addEventListener('hashchange', () => {
    const tHash = location.hash;
    if (tHash !== '' && !tHash.match(/%\S{2}/)) {
      const target = document.querySelector(`.tabs ul.nav-tabs li a[href="${tHash}"]`);
      target?.click();
    }
  });

  window.addEventListener('tabs:click', e => {
    NexT.utils.registerCodeblock(e.target);
  });
};

NexT.boot.refresh = function() {

  /**
   * Register JS handlers by condition option.
   * Need to add config option in Front-End at 'scripts/helpers/next-config.js' file.
   */
  CONFIG.prism && window.Prism.highlightAll();
  CONFIG.mediumzoom && window.mediumZoom('.post-body :not(a) > img, .post-body > img', {
    background: 'var(--content-bg-color)'
  });
  CONFIG.lazyload && window.lozad('.post-body img').observe();
  if (CONFIG.pangu) {
    // Polyfill for requestIdleCallback if not supported
    if (!window.requestIdleCallback) {
      window.requestIdleCallback = function(cb) {
        cb({
          didTimeout   : false,
          timeRemaining: () => 100
        });
      };
    }
    [...document.getElementsByTagName('main')].forEach(e => window.pangu.spacingNode(e));
  }

  CONFIG.exturl && NexT.utils.registerExtURL();
  NexT.utils.wrapTableWithBox();
  NexT.utils.registerCodeblock();
  NexT.utils.registerTabsTag();
  NexT.utils.registerActiveMenuItem();
  NexT.utils.registerLangSelect();
  NexT.utils.registerSidebarTOC();
  NexT.utils.registerPostReward();
  NexT.utils.registerVideoIframe();
};

NexT.boot.motion = function() {
  const bootstrapMotion = () => {
    NexT.motion.integrator
      .add(NexT.motion.middleWares.header)
      .add(NexT.motion.middleWares.sidebar)
      .add(NexT.motion.middleWares.postList)
      .add(NexT.motion.middleWares.footer)
      .bootstrap();
    NexT.utils.updateSidebarPosition();
  };

  if (!CONFIG.motion.enable) {
    NexT.utils.updateSidebarPosition();
    return;
  }

  if (window.anime?.timeline) {
    bootstrapMotion();
    return;
  }

  NexT.utils.getScript({
    url: '/lib/animejs/lib/anime.min.js',
    integrity: 'sha256-XL2inqUJaslATFnHdJOi9GfQ60on8Wx1C2H8DYiN1xY='
  }).then(bootstrapMotion).catch(bootstrapMotion);
};

document.addEventListener('DOMContentLoaded', () => {
  NexT.boot.registerEvents();
  NexT.boot.refresh();
  NexT.boot.motion();
});
