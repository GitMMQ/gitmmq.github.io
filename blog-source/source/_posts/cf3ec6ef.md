---
title: "npm常用命令"
disableNunjucks: true
date: 2021-09-26T03:06:24.000Z
updated: 2022-12-28T07:09:41.142Z
categories:
  - "node"
tags:
  - "node"
  - "npm"
---

<h2 id="安装命令"><a class="headerlink" href="#安装命令" title="安装命令"></a>安装命令</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/></pre></td><td class="code"><pre><span class="line">npm install -g hexo@版本号</span><br/></pre></td></tr></table></figure>
<h2 id="更新版本"><a class="headerlink" href="#更新版本" title="更新版本"></a>更新版本</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/></pre></td><td class="code"><pre><span class="line">npm cache clean -f</span><br/><span class="line">npm install-g n</span><br/><span class="line">n stable</span><br/></pre></td></tr></table></figure>
<h2 id="npm-check-updates安装"><a class="headerlink" href="#npm-check-updates安装" title="npm-check-updates安装"></a>npm-check-updates安装</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/></pre></td><td class="code"><pre><span class="line">npm install -g npm-check-updates</span><br/></pre></td></tr></table></figure>
<h2 id="检查包"><a class="headerlink" href="#检查包" title="检查包"></a>检查包</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/></pre></td><td class="code"><pre><span class="line">npm install -g npm-check</span><br/><span class="line">npm-check</span><br/></pre></td></tr></table></figure>
<h2 id="更新包"><a class="headerlink" href="#更新包" title="更新包"></a>更新包</h2><p>npm update <package></package></p>
<h2 id="检查-package-json-的最新依赖项"><a class="headerlink" href="#检查-package-json-的最新依赖项" title="检查 package.json 的最新依赖项"></a>检查 package.json 的最新依赖项</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/></pre></td><td class="code"><pre><span class="line">npm install -g npm-upgrade</span><br/><span class="line">npm-upgrade</span><br/><span class="line"></span><br/><span class="line">ncu</span><br/></pre></td></tr></table></figure>
<h2 id="更新-package-json-的最新依赖项"><a class="headerlink" href="#更新-package-json-的最新依赖项" title="更新 package.json 的最新依赖项"></a>更新 package.json 的最新依赖项</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/></pre></td><td class="code"><pre><span class="line">ncu -u</span><br/></pre></td></tr></table></figure>
<h2 id="检查包是否最新"><a class="headerlink" href="#检查包是否最新" title="检查包是否最新"></a>检查包是否最新</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/></pre></td><td class="code"><pre><span class="line">ncu &lt;package&gt;</span><br/></pre></td></tr></table></figure>
<h2 id="更新包到最新"><a class="headerlink" href="#更新包到最新" title="更新包到最新"></a>更新包到最新</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/></pre></td><td class="code"><pre><span class="line">npm update &lt;name&gt; -g</span><br/><span class="line"></span><br/><span class="line">ncu -u &lt;package&gt;</span><br/></pre></td></tr></table></figure>
<h2 id="查看全局安装包最新版本"><a class="headerlink" href="#查看全局安装包最新版本" title="查看全局安装包最新版本"></a>查看全局安装包最新版本</h2><figure class="highlight shell"><table><tr><td class="gutter"><pre><span class="line">1</span><br/></pre></td><td class="code"><pre><span class="line">ncu -g</span><br/></pre></td></tr></table></figure>
