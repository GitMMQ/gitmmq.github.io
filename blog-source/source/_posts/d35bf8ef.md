---
title: "hexo-asset-image问题修改"
disableNunjucks: true
date: 2021-09-26T03:06:24.000Z
updated: 2023-01-05T07:17:49.806Z
categories:
  - "hexo"
tags:
  - "hexo"
  - "hexo-asset-image"
---

<h2 id="修改更新url的代码"><a class="headerlink" href="#修改更新url的代码" title="修改更新url的代码"></a>修改更新url的代码</h2><p>node_modules/hexo-asset-image/index.js</p>
<figure class="highlight js"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/></pre></td><td class="code"><pre><span class="line"><span class="keyword">if</span>(srcArray.<span class="property">length</span> &gt; <span class="number">1</span>)</span><br/><span class="line">           srcArray.<span class="title function_">shift</span>();</span><br/><span class="line">           src = srcArray.<span class="title function_">join</span>(<span class="string">'/'</span>);</span><br/><span class="line"></span><br/><span class="line">           $(<span class="variable language_">this</span>).<span class="title function_">attr</span>(<span class="string">'src'</span>, <span class="string">"/img/"</span> + src);</span><br/><span class="line">           <span class="variable language_">console</span>.<span class="property">info</span>&amp;&amp;<span class="variable language_">console</span>.<span class="title function_">info</span>(<span class="string">"update link as:--&gt;"</span>+<span class="string">"/img/"</span> + src);</span><br/></pre></td></tr></table></figure>
