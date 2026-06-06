---
title: "LoRA 微调小说写作小模型：Qwen-1.8B-Chat + LLaMA Factory 同款文风续写"
disableNunjucks: true
date: 2026-06-05T07:30:00.000Z
categories:
  - "mechine"
tags:
  - "LoRA"
  - "微调"
  - "Qwen"
  - "LLaMA Factory"
  - "小说"
---

<p>大模型「会写」和「写得像你」是两回事。通用模型能讲故事，但很难稳定复现某一本书的文风、句式、叙事节奏和人物口吻。</p>
<p>这篇文章用 <strong>Qwen-1.8B-Chat + LLaMA Factory + LoRA</strong>，在消费级 GPU 上微调一个小模型，让它学会你指定小说的写作风格，实现<strong>同款风格续写</strong>。</p>
<h2 id="我们要让模型学会什么"><a class="headerlink" href="#我们要让模型学会什么" title="我们要让模型学会什么"></a>我们要让模型学会什么</h2><p>小说风格不是单一维度，训练数据要覆盖这些层面：</p>
<table>
<thead>
<tr>
<th>维度</th>
<th>说明</th>
<th>数据体现</th>
</tr>
</thead>
<tbody><tr>
<td>文风</td>
<td>用词习惯、修辞密度、叙述视角</td>
<td>原文段落本身</td>
</tr>
<tr>
<td>句式</td>
<td>长短句交替、断句节奏、对话与描写比例</td>
<td>连续上下文</td>
</tr>
<tr>
<td>叙事节奏</td>
<td>铺垫—冲突—转折的信息密度</td>
<td>多轮续写样本</td>
</tr>
<tr>
<td>人物口吻</td>
<td>不同角色说话方式、语气词、口头禅</td>
<td>带角色标注的对话</td>
</tr>
</tbody></table>
<p>LoRA 只更新少量参数，适合在 1.8B 小模型上<strong>注入风格</strong>，而不是重新学一遍中文。</p>
<h2 id="方案概览"><a class="headerlink" href="#方案概览" title="方案概览"></a>方案概览</h2><figure class="highlight text"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/></pre></td><td class="code"><pre><span class="line">小说原文 (.txt)</span><br/><span class="line">    ↓ 切分 + 构造指令样本</span><br/><span class="line">训练集 (alpaca/sharegpt json)</span><br/><span class="line">    ↓ LLaMA Factory LoRA SFT</span><br/><span class="line">Qwen-1.8B-Chat + LoRA 适配器</span><br/><span class="line">    ↓ 加载推理</span><br/><span class="line">同款风格续写 / 对话写作</span><br/></pre></td></tr></table></figure>
<p><strong>为什么选 Qwen-1.8B-Chat？</strong></p>
<ul>
<li>体量小，6GB 显存即可 LoRA 微调</li>
<li>中文能力强，适合小说语料</li>
<li>与 LLaMA Factory 的 <code>qwen</code> 模板原生兼容</li>
</ul>
<p><strong>为什么选 LoRA？</strong></p>
<ul>
<li>只训练低秩矩阵，显存占用低</li>
<li>适配器文件通常几十到几百 MB，方便切换不同「文风」</li>
<li>不破坏基座模型的通用能力</li>
</ul>
<h2 id="环境准备"><a class="headerlink" href="#环境准备" title="环境准备"></a>环境准备</h2><figure class="highlight bash"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/></pre></td><td class="code"><pre><span class="line"><span class="comment"># 建议 Python 3.10+</span></span><br/><span class="line">git <span class="built_in">clone</span> --depth 1 https://github.com/hiyouga/LLaMA-Factory.git</span><br/><span class="line"><span class="built_in">cd</span> LLaMA-Factory</span><br/><span class="line">pip install -e <span class="string">".[torch,metrics]"</span></span><br/><span class="line"></span><br/><span class="line"><span class="comment"># 可选：4bit 量化训练（显存更省）</span></span><br/><span class="line">pip install bitsandbytes</span><br/></pre></td></tr></table></figure>
<p>硬件建议：</p>
<table>
<thead>
<tr>
<th>配置</th>
<th>全参数</th>
<th>LoRA</th>
<th>QLoRA (4bit)</th>
</tr>
</thead>
<tbody><tr>
<td>6GB 显存</td>
<td>❌</td>
<td>✅</td>
<td>✅ 推荐</td>
</tr>
<tr>
<td>12GB+ 显存</td>
<td>❌</td>
<td>✅ 舒适</td>
<td>✅</td>
</tr>
</tbody></table>
<h2 id="第一步：把小说变成训练数据"><a class="headerlink" href="#第一步：把小说变成训练数据" title="第一步：把小说变成训练数据"></a>第一步：把小说变成训练数据</h2><p>核心思路：<strong>不要只丢原文</strong>，要构造「指令 → 风格化输出」的监督样本。</p>
<h3 id="1-清洗与切分原文"><a class="headerlink" href="#1-清洗与切分原文" title="1. 清洗与切分原文"></a>1. 清洗与切分原文</h3><figure class="highlight python"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/><span class="line">8</span><br/><span class="line">9</span><br/><span class="line">10</span><br/><span class="line">11</span><br/><span class="line">12</span><br/><span class="line">13</span><br/><span class="line">14</span><br/><span class="line">15</span><br/><span class="line">16</span><br/><span class="line">17</span><br/><span class="line">18</span><br/><span class="line">19</span><br/><span class="line">20</span><br/></pre></td><td class="code"><pre><span class="line"><span class="keyword">import</span> json</span><br/><span class="line"><span class="keyword">import</span> re</span><br/><span class="line"><span class="keyword">from</span> pathlib <span class="keyword">import</span> Path</span><br/><span class="line"></span><br/><span class="line"><span class="keyword">def</span> <span class="title function_">load_novel</span>(<span class="params">path: <span class="built_in">str</span></span>) -&gt; <span class="built_in">str</span>:</span><br/><span class="line">    text = Path(path).read_text(encoding=<span class="string">"utf-8"</span>)</span><br/><span class="line">    text = re.sub(<span class="string">r"\s+"</span>, <span class="string">"\n"</span>, text.strip())</span><br/><span class="line">    <span class="keyword">return</span> text</span><br/><span class="line"></span><br/><span class="line"><span class="keyword">def</span> <span class="title function_">split_chunks</span>(<span class="params">text: <span class="built_in">str</span>, chunk_size: <span class="built_in">int</span> = <span class="number">800</span>, overlap: <span class="built_in">int</span> = <span class="number">120</span></span>):</span><br/><span class="line">    <span class="string">"""按字数切分，保留上下文重叠，利于学习叙事节奏。"""</span></span><br/><span class="line">    chunks = []</span><br/><span class="line">    start = <span class="number">0</span></span><br/><span class="line">    <span class="keyword">while</span> start &lt; <span class="built_in">len</span>(text):</span><br/><span class="line">        end = <span class="built_in">min</span>(start + chunk_size, <span class="built_in">len</span>(text))</span><br/><span class="line">        chunks.append(text[start:end])</span><br/><span class="line">        <span class="keyword">if</span> end == <span class="built_in">len</span>(text):</span><br/><span class="line">            <span class="keyword">break</span></span><br/><span class="line">        start = end - overlap</span><br/><span class="line">    <span class="keyword">return</span> chunks</span><br/></pre></td></tr></table></figure>
<h3 id="2-构造三类训练样本"><a class="headerlink" href="#2-构造三类训练样本" title="2. 构造三类训练样本"></a>2. 构造三类训练样本</h3><p><strong>A. 文风续写（主样本）</strong></p>
<figure class="highlight json"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/></pre></td><td class="code"><pre><span class="line"><span class="punctuation">{</span></span><br/><span class="line">  <span class="attr">"instruction"</span><span class="punctuation">:</span> <span class="string">"请用以下小说的文风续写故事，保持叙述视角、句式节奏和用词习惯一致。"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"input"</span><span class="punctuation">:</span> <span class="string">"前情：\n{context}"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"output"</span><span class="punctuation">:</span> <span class="string">"{continuation}"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"system"</span><span class="punctuation">:</span> <span class="string">"你是一位擅长模仿指定小说文风的写作助手，注重叙事节奏与人物口吻。"</span></span><br/><span class="line"><span class="punctuation">}</span></span><br/></pre></td></tr></table></figure>
<p><strong>B. 人物口吻对话</strong></p>
<figure class="highlight json"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/></pre></td><td class="code"><pre><span class="line"><span class="punctuation">{</span></span><br/><span class="line">  <span class="attr">"instruction"</span><span class="punctuation">:</span> <span class="string">"请以【{character}】的口吻回应对话，保持该角色一贯的说话方式。"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"input"</span><span class="punctuation">:</span> <span class="string">"场景：{scene}\n对方说：{line}"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"output"</span><span class="punctuation">:</span> <span class="string">"{reply}"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"system"</span><span class="punctuation">:</span> <span class="string">"你正在扮演小说中的角色，回答必须符合人物性格和语言习惯。"</span></span><br/><span class="line"><span class="punctuation">}</span></span><br/></pre></td></tr></table></figure>
<p><strong>C. 风格改写（强化句式）</strong></p>
<figure class="highlight json"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/></pre></td><td class="code"><pre><span class="line"><span class="punctuation">{</span></span><br/><span class="line">  <span class="attr">"instruction"</span><span class="punctuation">:</span> <span class="string">"将下面这段文字改写成目标小说的文风，不改变情节，只调整措辞、节奏和修辞。"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"input"</span><span class="punctuation">:</span> <span class="string">"{neutral_text}"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"output"</span><span class="punctuation">:</span> <span class="string">"{styled_text}"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"system"</span><span class="punctuation">:</span> <span class="string">"你是文风迁移助手，输出应贴近目标小说的叙述风格。"</span></span><br/><span class="line"><span class="punctuation">}</span></span><br/></pre></td></tr></table></figure>
<h3 id="3-生成数据集脚本"><a class="headerlink" href="#3-生成数据集脚本" title="3. 生成数据集脚本"></a>3. 生成数据集脚本</h3><figure class="highlight python"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/><span class="line">8</span><br/><span class="line">9</span><br/><span class="line">10</span><br/><span class="line">11</span><br/><span class="line">12</span><br/><span class="line">13</span><br/><span class="line">14</span><br/><span class="line">15</span><br/><span class="line">16</span><br/><span class="line">17</span><br/><span class="line">18</span><br/><span class="line">19</span><br/><span class="line">20</span><br/><span class="line">21</span><br/></pre></td><td class="code"><pre><span class="line"><span class="keyword">def</span> <span class="title function_">build_style_samples</span>(<span class="params">chunks: <span class="built_in">list</span>[<span class="built_in">str</span>]</span>) -&gt; <span class="built_in">list</span>[<span class="built_in">dict</span>]:</span><br/><span class="line">    samples = []</span><br/><span class="line">    <span class="keyword">for</span> i <span class="keyword">in</span> <span class="built_in">range</span>(<span class="built_in">len</span>(chunks) - <span class="number">1</span>):</span><br/><span class="line">        context = chunks[i]</span><br/><span class="line">        continuation = chunks[i + <span class="number">1</span>][:<span class="number">500</span>]  <span class="comment"># 续写目标不宜过长</span></span><br/><span class="line">        samples.append({</span><br/><span class="line">            <span class="string">"instruction"</span>: <span class="string">"请用以下小说的文风续写故事，保持叙述视角、句式节奏和用词习惯一致。"</span>,</span><br/><span class="line">            <span class="string">"input"</span>: <span class="string">f"前情：\n<span class="subst">{context}</span>"</span>,</span><br/><span class="line">            <span class="string">"output"</span>: continuation,</span><br/><span class="line">            <span class="string">"system"</span>: <span class="string">"你是一位擅长模仿指定小说文风的写作助手，注重叙事节奏与人物口吻。"</span></span><br/><span class="line">        })</span><br/><span class="line">    <span class="keyword">return</span> samples</span><br/><span class="line"></span><br/><span class="line">chunks = split_chunks(load_novel(<span class="string">"novel.txt"</span>))</span><br/><span class="line">dataset = build_style_samples(chunks)</span><br/><span class="line"></span><br/><span class="line">Path(<span class="string">"data/novel_style.json"</span>).write_text(</span><br/><span class="line">    json.dumps(dataset, ensure_ascii=<span class="literal">False</span>, indent=<span class="number">2</span>),</span><br/><span class="line">    encoding=<span class="string">"utf-8"</span></span><br/><span class="line">)</span><br/><span class="line"><span class="built_in">print</span>(<span class="string">f"生成 <span class="subst">{<span class="built_in">len</span>(dataset)}</span> 条样本"</span>)</span><br/></pre></td></tr></table></figure>
<p>数据量建议：</p>
<ul>
<li><strong>最少</strong>：500 条高质量样本（约 3～5 万字小说）</li>
<li><strong>推荐</strong>：2000～5000 条（多章节、多场景）</li>
<li>样本要覆盖：叙述段、对话段、高潮段、日常段</li>
</ul>
<h2 id="第二步：注册数据集"><a class="headerlink" href="#第二步：注册数据集" title="第二步：注册数据集"></a>第二步：注册数据集</h2><p>在 <code>LLaMA-Factory/data/dataset_info.json</code> 中添加：</p>
<figure class="highlight json"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/><span class="line">8</span><br/><span class="line">9</span><br/></pre></td><td class="code"><pre><span class="line"><span class="attr">"novel_style"</span><span class="punctuation">:</span> <span class="punctuation">{</span></span><br/><span class="line">  <span class="attr">"file_name"</span><span class="punctuation">:</span> <span class="string">"novel_style.json"</span><span class="punctuation">,</span></span><br/><span class="line">  <span class="attr">"columns"</span><span class="punctuation">:</span> <span class="punctuation">{</span></span><br/><span class="line">    <span class="attr">"prompt"</span><span class="punctuation">:</span> <span class="string">"instruction"</span><span class="punctuation">,</span></span><br/><span class="line">    <span class="attr">"query"</span><span class="punctuation">:</span> <span class="string">"input"</span><span class="punctuation">,</span></span><br/><span class="line">    <span class="attr">"response"</span><span class="punctuation">:</span> <span class="string">"output"</span><span class="punctuation">,</span></span><br/><span class="line">    <span class="attr">"system"</span><span class="punctuation">:</span> <span class="string">"system"</span></span><br/><span class="line">  <span class="punctuation">}</span></span><br/><span class="line"><span class="punctuation">}</span></span><br/></pre></td></tr></table></figure>
<h2 id="第三步：LoRA-微调配置"><a class="headerlink" href="#第三步：LoRA-微调配置" title="第三步：LoRA 微调配置"></a>第三步：LoRA 微调配置</h2><p>新建 <code>examples/train_lora/qwen1_8b_novel_lora.yaml</code>：</p>
<figure class="highlight yaml"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/><span class="line">8</span><br/><span class="line">9</span><br/><span class="line">10</span><br/><span class="line">11</span><br/><span class="line">12</span><br/><span class="line">13</span><br/><span class="line">14</span><br/><span class="line">15</span><br/><span class="line">16</span><br/><span class="line">17</span><br/><span class="line">18</span><br/><span class="line">19</span><br/><span class="line">20</span><br/><span class="line">21</span><br/><span class="line">22</span><br/><span class="line">23</span><br/><span class="line">24</span><br/><span class="line">25</span><br/><span class="line">26</span><br/><span class="line">27</span><br/><span class="line">28</span><br/><span class="line">29</span><br/><span class="line">30</span><br/><span class="line">31</span><br/><span class="line">32</span><br/><span class="line">33</span><br/><span class="line">34</span><br/><span class="line">35</span><br/><span class="line">36</span><br/><span class="line">37</span><br/><span class="line">38</span><br/><span class="line">39</span><br/><span class="line">40</span><br/><span class="line">41</span><br/><span class="line">42</span><br/><span class="line">43</span><br/></pre></td><td class="code"><pre><span class="line"><span class="comment">### model</span></span><br/><span class="line"><span class="attr">model_name_or_path:</span> <span class="string">Qwen/Qwen-1_8B-Chat</span></span><br/><span class="line"><span class="attr">trust_remote_code:</span> <span class="literal">true</span></span><br/><span class="line"></span><br/><span class="line"><span class="comment">### method</span></span><br/><span class="line"><span class="attr">stage:</span> <span class="string">sft</span></span><br/><span class="line"><span class="attr">do_train:</span> <span class="literal">true</span></span><br/><span class="line"><span class="attr">finetuning_type:</span> <span class="string">lora</span></span><br/><span class="line"><span class="attr">lora_rank:</span> <span class="number">16</span></span><br/><span class="line"><span class="attr">lora_alpha:</span> <span class="number">32</span></span><br/><span class="line"><span class="attr">lora_dropout:</span> <span class="number">0.05</span></span><br/><span class="line"><span class="attr">lora_target:</span> <span class="string">all</span></span><br/><span class="line"></span><br/><span class="line"><span class="comment">### dataset</span></span><br/><span class="line"><span class="attr">dataset:</span> <span class="string">novel_style</span></span><br/><span class="line"><span class="attr">template:</span> <span class="string">qwen</span></span><br/><span class="line"><span class="attr">cutoff_len:</span> <span class="number">2048</span></span><br/><span class="line"><span class="attr">max_samples:</span> <span class="number">10000</span></span><br/><span class="line"><span class="attr">overwrite_cache:</span> <span class="literal">true</span></span><br/><span class="line"><span class="attr">preprocessing_num_workers:</span> <span class="number">4</span></span><br/><span class="line"></span><br/><span class="line"><span class="comment">### output</span></span><br/><span class="line"><span class="attr">output_dir:</span> <span class="string">saves/qwen1_8b_novel_lora</span></span><br/><span class="line"><span class="attr">logging_steps:</span> <span class="number">10</span></span><br/><span class="line"><span class="attr">save_steps:</span> <span class="number">200</span></span><br/><span class="line"><span class="attr">plot_loss:</span> <span class="literal">true</span></span><br/><span class="line"><span class="attr">overwrite_output_dir:</span> <span class="literal">true</span></span><br/><span class="line"></span><br/><span class="line"><span class="comment">### train</span></span><br/><span class="line"><span class="attr">per_device_train_batch_size:</span> <span class="number">2</span></span><br/><span class="line"><span class="attr">gradient_accumulation_steps:</span> <span class="number">8</span></span><br/><span class="line"><span class="attr">learning_rate:</span> <span class="number">2.0e-4</span></span><br/><span class="line"><span class="attr">num_train_epochs:</span> <span class="number">3.0</span></span><br/><span class="line"><span class="attr">lr_scheduler_type:</span> <span class="string">cosine</span></span><br/><span class="line"><span class="attr">warmup_ratio:</span> <span class="number">0.05</span></span><br/><span class="line"><span class="attr">bf16:</span> <span class="literal">true</span></span><br/><span class="line"><span class="attr">ddp_timeout:</span> <span class="number">180000000</span></span><br/><span class="line"></span><br/><span class="line"><span class="comment">### eval</span></span><br/><span class="line"><span class="attr">val_size:</span> <span class="number">0.05</span></span><br/><span class="line"><span class="attr">per_device_eval_batch_size:</span> <span class="number">1</span></span><br/><span class="line"><span class="attr">eval_strategy:</span> <span class="string">steps</span></span><br/><span class="line"><span class="attr">eval_steps:</span> <span class="number">200</span></span><br/></pre></td></tr></table></figure>
<p>参数说明：</p>
<table>
<thead>
<tr>
<th>参数</th>
<th>建议值</th>
<th>作用</th>
</tr>
</thead>
<tbody><tr>
<td><code>lora_rank</code></td>
<td>8～32</td>
<td>越大表达能力越强，显存越高</td>
</tr>
<tr>
<td><code>cutoff_len</code></td>
<td>2048</td>
<td>覆盖更长上下文，利于学叙事节奏</td>
</tr>
<tr>
<td><code>learning_rate</code></td>
<td>1e-4 ~ 3e-4</td>
<td>风格学习常用偏高学习率</td>
</tr>
<tr>
<td><code>num_train_epochs</code></td>
<td>2～5</td>
<td>样本少可多轮，注意过拟合</td>
</tr>
</tbody></table>
<p>显存不足时，改用 QLoRA：</p>
<figure class="highlight yaml"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/></pre></td><td class="code"><pre><span class="line"><span class="attr">finetuning_type:</span> <span class="string">lora</span></span><br/><span class="line"><span class="attr">quantization_bit:</span> <span class="number">4</span></span><br/></pre></td></tr></table></figure>
<h2 id="第四步：启动训练"><a class="headerlink" href="#第四步：启动训练" title="第四步：启动训练"></a>第四步：启动训练</h2><figure class="highlight bash"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/></pre></td><td class="code"><pre><span class="line"><span class="built_in">cd</span> LLaMA-Factory</span><br/><span class="line"></span><br/><span class="line"><span class="comment"># 单卡训练</span></span><br/><span class="line">CUDA_VISIBLE_DEVICES=0 llamafactory-cli train examples/train_lora/qwen1_8b_novel_lora.yaml</span><br/><span class="line"></span><br/><span class="line"><span class="comment"># 或使用 Web UI</span></span><br/><span class="line">llamafactory-cli webui</span><br/></pre></td></tr></table></figure>
<p>训练时关注：</p>
<ol>
<li><strong>loss 稳定下降</strong>：通常在 0.5～1.5 区间收敛</li>
<li><strong>验证集 loss 不再下降时停止</strong>：避免只会「背诵」训练集</li>
<li><strong>抽查生成</strong>：用同一 prompt 对比第 1 epoch 和第 3 epoch 输出</li>
</ol>
<h2 id="第五步：推理与同款风格写作"><a class="headerlink" href="#第五步：推理与同款风格写作" title="第五步：推理与同款风格写作"></a>第五步：推理与同款风格写作</h2><h3 id="命令行推理"><a class="headerlink" href="#命令行推理" title="命令行推理"></a>命令行推理</h3><figure class="highlight bash"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/></pre></td><td class="code"><pre><span class="line">CUDA_VISIBLE_DEVICES=0 llamafactory-cli chat \</span><br/><span class="line">  --model_name_or_path Qwen/Qwen-1_8B-Chat \</span><br/><span class="line">  --adapter_name_or_path saves/qwen1_8b_novel_lora \</span><br/><span class="line">  --template qwen \</span><br/><span class="line">  --finetuning_type lora</span><br/></pre></td></tr></table></figure>
<h3 id="Python-加载"><a class="headerlink" href="#Python-加载" title="Python 加载"></a>Python 加载</h3><figure class="highlight python"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/><span class="line">8</span><br/><span class="line">9</span><br/><span class="line">10</span><br/><span class="line">11</span><br/><span class="line">12</span><br/><span class="line">13</span><br/><span class="line">14</span><br/><span class="line">15</span><br/><span class="line">16</span><br/><span class="line">17</span><br/><span class="line">18</span><br/><span class="line">19</span><br/><span class="line">20</span><br/><span class="line">21</span><br/><span class="line">22</span><br/><span class="line">23</span><br/><span class="line">24</span><br/><span class="line">25</span><br/><span class="line">26</span><br/><span class="line">27</span><br/></pre></td><td class="code"><pre><span class="line"><span class="keyword">from</span> transformers <span class="keyword">import</span> AutoModelForCausalLM, AutoTokenizer</span><br/><span class="line"><span class="keyword">from</span> peft <span class="keyword">import</span> PeftModel</span><br/><span class="line"></span><br/><span class="line">base = <span class="string">"Qwen/Qwen-1_8B-Chat"</span></span><br/><span class="line">lora = <span class="string">"saves/qwen1_8b_novel_lora"</span></span><br/><span class="line"></span><br/><span class="line">tokenizer = AutoTokenizer.from_pretrained(base, trust_remote_code=<span class="literal">True</span>)</span><br/><span class="line">model = AutoModelForCausalLM.from_pretrained(</span><br/><span class="line">    base, device_map=<span class="string">"auto"</span>, trust_remote_code=<span class="literal">True</span></span><br/><span class="line">)</span><br/><span class="line">model = PeftModel.from_pretrained(model, lora)</span><br/><span class="line">model.<span class="built_in">eval</span>()</span><br/><span class="line"></span><br/><span class="line">prompt = <span class="string">"""请用训练小说的文风续写以下内容，保持叙事节奏和人物口吻：</span></span><br/><span class="line"><span class="string"></span></span><br/><span class="line"><span class="string">前情：</span></span><br/><span class="line"><span class="string">雨停之后，巷口的青石板还泛着潮气。她站在门廊下，没有回头。"""</span></span><br/><span class="line"></span><br/><span class="line">messages = [</span><br/><span class="line">    {<span class="string">"role"</span>: <span class="string">"system"</span>, <span class="string">"content"</span>: <span class="string">"你是一位擅长模仿指定小说文风的写作助手。"</span>},</span><br/><span class="line">    {<span class="string">"role"</span>: <span class="string">"user"</span>, <span class="string">"content"</span>: prompt},</span><br/><span class="line">]</span><br/><span class="line">text = tokenizer.apply_chat_template(messages, tokenize=<span class="literal">False</span>, add_generation_prompt=<span class="literal">True</span>)</span><br/><span class="line">inputs = tokenizer([text], return_tensors=<span class="string">"pt"</span>).to(model.device)</span><br/><span class="line"></span><br/><span class="line">outputs = model.generate(**inputs, max_new_tokens=<span class="number">512</span>, temperature=<span class="number">0.8</span>, top_p=<span class="number">0.9</span>)</span><br/><span class="line"><span class="built_in">print</span>(tokenizer.decode(outputs[<span class="number">0</span>][inputs[<span class="string">"input_ids"</span>].shape[<span class="number">1</span>]:], skip_special_tokens=<span class="literal">True</span>))</span><br/></pre></td></tr></table></figure>
<h3 id="导出合并模型（可选）"><a class="headerlink" href="#导出合并模型（可选）" title="导出合并模型（可选）"></a>导出合并模型（可选）</h3><figure class="highlight bash"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/><span class="line">5</span><br/><span class="line">6</span><br/><span class="line">7</span><br/><span class="line">8</span><br/></pre></td><td class="code"><pre><span class="line">CUDA_VISIBLE_DEVICES=0 llamafactory-cli <span class="built_in">export</span> \</span><br/><span class="line">  --model_name_or_path Qwen/Qwen-1_8B-Chat \</span><br/><span class="line">  --adapter_name_or_path saves/qwen1_8b_novel_lora \</span><br/><span class="line">  --template qwen \</span><br/><span class="line">  --finetuning_type lora \</span><br/><span class="line">  --export_dir exports/qwen1_8b_novel_merged \</span><br/><span class="line">  --export_size 2 \</span><br/><span class="line">  --export_legacy_format <span class="literal">false</span></span><br/></pre></td></tr></table></figure>
<h2 id="效果调优：四个实战技巧"><a class="headerlink" href="#效果调优：四个实战技巧" title="效果调优：四个实战技巧"></a>效果调优：四个实战技巧</h2><h3 id="1-用「多粒度」样本，不要只续写"><a class="headerlink" href="#1-用「多粒度」样本，不要只续写" title="1. 用「多粒度」样本，不要只续写"></a>1. 用「多粒度」样本，不要只续写</h3><p>只喂「上文 → 下文」容易学会情节复述，学不会口吻。建议三类样本比例为：</p>
<ul>
<li>文风续写 60%</li>
<li>角色对话 25%</li>
<li>风格改写 15%</li>
</ul>
<h3 id="2-控制续写目标长度"><a class="headerlink" href="#2-控制续写目标长度" title="2. 控制续写目标长度"></a>2. 控制续写目标长度</h3><p><code>output</code> 建议 200～600 字。太长会稀释风格信号，太短学不到叙事节奏。</p>
<h3 id="3-推理温度按任务切换"><a class="headerlink" href="#3-推理温度按任务切换" title="3. 推理温度按任务切换"></a>3. 推理温度按任务切换</h3><table>
<thead>
<tr>
<th>任务</th>
<th>temperature</th>
<th>top_p</th>
</tr>
</thead>
<tbody><tr>
<td>仿写/续写</td>
<td>0.7～0.9</td>
<td>0.85～0.95</td>
</tr>
<tr>
<td>角色对话</td>
<td>0.8～1.0</td>
<td>0.9</td>
</tr>
<tr>
<td>风格改写</td>
<td>0.5～0.7</td>
<td>0.8</td>
</tr>
</tbody></table>
<h3 id="4-多适配器管理不同文风"><a class="headerlink" href="#4-多适配器管理不同文风" title="4. 多适配器管理不同文风"></a>4. 多适配器管理不同文风</h3><figure class="highlight text"><table><tr><td class="gutter"><pre><span class="line">1</span><br/><span class="line">2</span><br/><span class="line">3</span><br/><span class="line">4</span><br/></pre></td><td class="code"><pre><span class="line">saves/</span><br/><span class="line">├── qwen1_8b_wuxia_lora/     # 武侠风</span><br/><span class="line">├── qwen1_8b_romance_lora/   # 言情风</span><br/><span class="line">└── qwen1_8b_scifi_lora/     # 科幻风</span><br/></pre></td></tr></table></figure>
<p>推理时切换 <code>adapter_name_or_path</code> 即可，基座模型不用重复加载。</p>
<h2 id="常见问题"><a class="headerlink" href="#常见问题" title="常见问题"></a>常见问题</h2><p><strong>Q：生成内容像训练集原文拼凑？</strong></p>
<p>过拟合。减少 epoch、增大 <code>lora_dropout</code>、扩充样本多样性。</p>
<p><strong>Q：风格像了，但逻辑不通？</strong></p>
<p>1.8B 容量有限，复杂长篇规划能力弱。建议用于<strong>段落级续写</strong>，而非整章大纲生成。</p>
<p><strong>Q：对话口吻不像某个角色？</strong></p>
<p>增加带角色名的对话样本，并在 <code>instruction</code> 中显式写出角色身份。</p>
<p><strong>Q：显存不够？</strong></p>
<p>启用 <code>quantization_bit: 4</code>，或将 <code>per_device_train_batch_size</code> 设为 1、<code>gradient_accumulation_steps</code> 调大。</p>
<h2 id="总结"><a class="headerlink" href="#总结" title="总结"></a>总结</h2><p>用 Qwen-1.8B-Chat + LLaMA Factory 做 LoRA 微调，是在有限算力下实现「同款文风写作」的务实路线：</p>
<ol>
<li>把小说切成<strong>风格监督样本</strong>，而不只是原文堆砌</li>
<li>覆盖文风、句式、节奏、口吻四个维度</li>
<li>LoRA 低成本注入风格，基座能力保留</li>
<li>推理时通过 prompt + 温度控制输出质量</li>
</ol>
<p>小模型不会替代顶尖大模型的全局构思能力，但在<strong>风格化续写、角色对话、章节仿写</strong>这类任务上，微调后的 1.8B 往往比未微调的 7B 更「像你」。</p>
<p>如果你要针对某本具体小说做数据集，核心就一句话：<strong>让模型看到的每一条样本，都在回答「如何用这种风格写」</strong>。</p>
