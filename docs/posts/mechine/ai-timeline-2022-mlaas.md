---
title: "2022 AI 编年史：大模型即服务 MLaaS"
date: 2022-07-15 10:00:00
categories:
  - "mechine"
tags:
  - "AI Timeline"
  - "MLaaS"
  - "AI API"
  - "Cloud AI"
  - "Foundation Model"
description: "2022 年 MLaaS 大模型即服务商业模式成熟，详解 OpenAI API、Azure AI、定价模型与产业影响，中英文对照。"
---

# 2022 AI 编年史：大模型即服务 MLaaS | AI Timeline 2022: MLaaS

---

## 一、背景与核心概念 | Background & Core Concepts

**English**

**MLaaS** (Machine Learning as a Service) — in its 2022 incarnation — specifically meant **Foundation Model as a Service (FMaaS)**: accessing billion-parameter models via **REST/gRPC APIs** without owning GPUs, training infrastructure, or ML expertise. This represented a fundamental shift from traditional MLaaS (AutoML tabular prediction, SageMaker custom training) to **"intelligence on tap."**

The 2022 MLaaS landscape was dominated by:

| Provider | Flagship API | Pricing Model (2022) |
|---|---|---|
| **OpenAI** | GPT-3, Codex, DALL·E, Whisper | Per-token / per-image |
| **Google Cloud** | PaLM API (limited), Vertex AI | Per-character / per-request |
| **Microsoft Azure** | Azure OpenAI Service | Enterprise contract + per-token |
| **Cohere** | Generate, Embed, Classify | Per-token |
| **AI21 Labs** | Jurassic-2 | Per-token |
| **Hugging Face** | Inference API / Endpoints | Per-hour GPU / freemium |
| **Replicate** | SD, LLaMA precursors | Per-second GPU |
| **Stability AI** | DreamStudio API | Per-generation credit |

Key concepts:

- **Token-based pricing**: LLM APIs charge per **input token** (prompt) and **output token** (completion). GPT-3 davinci: ~$0.02/1K tokens (2022 rates).
- **Rate limiting**: Requests per minute (RPM) and tokens per minute (TPM) tiers based on account level.
- **Fine-tuning API**: OpenAI offered GPT-3 fine-tuning as a managed service — upload JSONL, pay training + inference premium.
- **Embedding API**: Text → vector for semantic search, clustering, and RAG (before "RAG" became mainstream in 2023).
- **Multi-tenancy**: Shared model serving with logical isolation; latency vs. dedicated deployment trade-off.

Why MLaaS exploded in 2022:

1. Training GPT-3-class models costs **$5M–$12M** — only viable for hyperscalers.
2. API access lets startups build products in **days** (Jasper, Copy.ai, Harvey precursors).
3. **Azure OpenAI** (announced 2022, expanded 2023) brought enterprise compliance (SOC2, private VNet) to foundation models.

**中文**

**MLaaS**（机器学习即服务）—— 在 2022 年的语境下 —— 特指 **基础模型即服务（FMaaS）**：通过 **REST/gRPC API** 调用十亿级参数模型，无需自购 GPU、训练基础设施或深厚 ML 经验。这标志着从传统 MLaaS（AutoML 表格预测、SageMaker 自定义训练）向 **「按需取用智能」** 的根本转变。

2022 年 MLaaS 格局由以下玩家主导：

| 提供商 | 旗舰 API | 定价模式（2022） |
|---|---|---|
| **OpenAI** | GPT-3、Codex、DALL·E、Whisper | 按 token / 按图像 |
| **Google Cloud** | PaLM API（有限）、Vertex AI | 按字符 / 按请求 |
| **Microsoft Azure** | Azure OpenAI Service | 企业合同 + 按 token |
| **Cohere** | Generate、Embed、Classify | 按 token |
| **AI21 Labs** | Jurassic-2 | 按 token |
| **Hugging Face** | Inference API / Endpoints | 按 GPU 小时 / 免费增值 |
| **Replicate** | SD、LLaMA 前身 | 按 GPU 秒 |
| **Stability AI** | DreamStudio API | 按生成次数积分 |

关键概念：

- **按 Token 定价**：LLM API 对 **输入 token**（提示）与 **输出 token**（补全）分别计费。GPT-3 davinci：约 $0.02/1K tokens（2022 年费率）。
- **速率限制**：每分钟请求数（RPM）与每分钟 token 数（TPM）按账户等级分层。
- **微调 API**：OpenAI 提供 GPT-3 托管微调 —— 上传 JSONL，支付训练费 + 推理溢价。
- **嵌入 API**：文本 → 向量，用于语义搜索、聚类与 RAG（2023 年前「RAG」尚未 mainstream）。
- **多租户**：共享模型服务与逻辑隔离；延迟 vs. 专属部署的权衡。

2022 年 MLaaS 爆发的原因：

1. 训练 GPT-3 级模型成本 **500万–1200 万美元** —— 仅超大规模云厂商可承担。
2. API 接入使创业公司 **数天** 内构建产品（Jasper、Copy.ai、Harvey 等前身）。
3. **Azure OpenAI**（2022 年宣布，2023 年扩展）将企业合规（SOC2、私有 VNet）引入基础模型。

---

## 二、架构设计 | Architecture

### 2.1 MLaaS 服务架构 | MLaaS Service Architecture

**English**

```
Client Application (Web/Mobile/Backend)
    ↓ HTTPS (API Key / OAuth)
API Gateway
    ├── Authentication & billing metering
    ├── Rate limiting & abuse detection
    ├── Request routing & load balancing
    └── Content moderation filter
    ↓
Model Serving Layer
    ├── Batched inference (dynamic batching)
    ├── KV-cache for autoregressive LLMs
    ├── Multi-GPU tensor parallelism
    └── Model version management (A/B)
    ↓
GPU Cluster (A100/H100)
    ↓
Response (JSON: text, embeddings, images, usage stats)
```

| Component | Function | 2022 State |
|---|---|---|
| **Dynamic batching** | Aggregate concurrent requests | Reduces per-request cost 2–5× |
| **KV-cache** | Store attention keys/values | Critical for LLM latency |
| **Content filter** | Block harmful outputs | OpenAI Moderation API |
| **Usage tracking** | Token count for billing | `usage.prompt_tokens` in response |
| **Dedicated deployment** | Single-tenant GPU | Azure/OpenAI enterprise tier |

**中文**

MLaaS 架构：客户端 → API 网关（认证、计费、限流、内容审核）→ 模型服务层（动态批处理、KV-cache、多 GPU 并行）→ GPU 集群 → JSON 响应（含 usage 统计）。动态批处理将单次请求成本降低 2–5×，KV-cache 是 LLM 低延迟的关键。

### 2.2 定价经济学 | Pricing Economics

| 模型 Model | 输入价格 Input (2022) | 输出价格 Output | 等效成本 Equivalent |
|---|---|---|---|
| GPT-3 davinci | $0.02/1K tokens | $0.02/1K tokens | ~$20/1M tokens |
| GPT-3 curie | $0.002/1K tokens | $0.002/1K tokens | ~$2/1M tokens |
| Codex | $0.02/1K tokens | — | Per completion |
| DALL·E 2 (1024) | — | $0.02/image | Per image |
| text-embedding-ada-002 | $0.0001/1K tokens | — | ~$0.10/1M tokens |

---

## 三、2022 年趋势 | Trends in 2022

**English**

1. **Wrapper startups boom**: Thin UI layers on GPT-3 API reached unicorn valuations (Jasper $1.5B valuation, Oct 2022).
2. **Embedding-first products**: Semantic search, code search, and recommendation rebuilt on embedding APIs before chat UX matured.
3. **Enterprise gatekeeping**: Azure OpenAI required application approval — creating exclusivity and long waitlists.
4. **Open-source counterweight**: Self-hosted SD + LLaMA precursors offered escape from per-token billing.
5. **Multi-modal API bundles**: OpenAI unified text, code, image, and speech under one platform and API key.
6. **Cost optimization industry**: Prompt compression, caching, and smaller model routing emerged as engineering disciplines.

**中文**

1. **套壳创业潮**：GPT-3 API 薄 UI 层公司达独角兽估值（Jasper 2022 年 10 月估值 15 亿美元）。
2. **嵌入优先产品**：语义搜索、代码搜索在聊天 UX 成熟前已基于嵌入 API 重建。
3. **企业门禁**：Azure OpenAI 需申请审批 —— 制造稀缺性与长等待名单。
4. **开源制衡**：自托管 SD + LLaMA 前身提供逃离按 token 计费的路径。
5. **多模态 API 捆绑**：OpenAI 将文本、代码、图像、语音统一于一个平台与 API Key。
6. **成本优化产业**：提示压缩、缓存与小模型路由成为工程学科。

---

## 四、优缺点分析 | Pros and Cons

| 优点 Advantages | 缺点 Disadvantages |
|---|---|
| 零基础设施启动 AI 产品 / Zero-infra AI product launch | 按量计费成本随规模线性增长 / Linear cost scaling |
| 始终使用最新模型版本 / Always latest model versions | 供应商锁定与 API 变更风险 / Vendor lock-in risk |
| 内置安全审核与合规 / Built-in moderation & compliance | 数据隐私（提示词经第三方）/ Data privacy concerns |
| 弹性应对流量峰值 / Elastic scaling for traffic spikes | 速率限制阻碍高并发场景 / Rate limits block high concurrency |
| 降低 AI 人才门槛 / Lowers AI talent barrier | 无法深度定制模型内部 / No deep model customization |
| 快速 A/B 多模型对比 / Fast multi-model A/B testing | 网络延迟影响交互体验 / Network latency affects UX |
| 统一计费与监控 / Unified billing and monitoring | 闭源模型透明度不足 / Opaque closed models |

---

## 五、典型应用场景 | Use Cases

| 场景 Scenario | 中文说明 | English Description |
|---|---|---|
| AI 写作助手 | Jasper/Copy.ai 营销文案生成 | Marketing copy generation (Jasper, Copy.ai) |
| 智能客服 | GPT-3 驱动的对话机器人 | GPT-3 powered customer support bots |
| 语义搜索 | Embedding API 构建企业知识库检索 | Enterprise KB search via embeddings |
| 代码助手 | Codex API 集成到 IDE 或 CI | Codex API in IDE or CI pipelines |
| 图像生成 SaaS | DALL·E/SD API 驱动的设计工具 | Design tools powered by image APIs |
| 法律/医疗文档 | 长文档摘要与信息抽取 | Long document summarization and extraction |
| 多语言翻译 | GPT-3 少样本翻译优于传统 NMT | Few-shot translation surpassing traditional NMT |

---

## 六、GitHub 开源项目 | GitHub Projects

| 项目 Project | 说明 Description | 链接 Link |
|---|---|---|
| **openai/openai-cookbook** | OpenAI API 最佳实践与示例 | [github.com/openai/openai-cookbook](https://github.com/openai/openai-cookbook) |
| **openai/openai-python** | 官方 Python SDK | [github.com/openai/openai-python](https://github.com/openai/openai-python) |
| **huggingface/text-generation-inference** | 自托管 LLM  serving，MLaaS 开源替代 | [github.com/huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) |
| **langchain-ai/langchain** | API 编排框架（2022 年晚期起步） | [github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) |

```python
# OpenAI API 基础调用（openai-python SDK）
import openai
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Explain MLaaS in one sentence."}],
)
print(response.choices[0].message.content)
print(f"Tokens used: {response.usage.total_tokens}")
```

---

## 七、总结 | Summary

**中文**：2022 年 **MLaaS** 将基础模型从实验室稀缺资源变为 **可按 Token 计费的公共事业**。它催生了「套壳创业」浪潮，也引发了开源自托管的制衡运动。Azure OpenAI 的企业化路径与 OpenAI 的消费级 API 共同定义了 **「模型即商品」** 的商业范式 —— 为 2023 年 ChatGPT 千万用户爆发提供了分发基础设施。

**English**: **MLaaS** in 2022 turned foundation models from scarce lab resources into a **metered public utility**. It spawned "wrapper startups" and an open-source self-hosting countermovement. Azure OpenAI's enterprise path and OpenAI's consumer API together defined the **"models as commodities"** business paradigm — providing the distribution infrastructure for ChatGPT's explosive growth in 2023.

---

**参考链接 | References**

- OpenAI API 定价：[openai.com/pricing](https://openai.com/pricing)
- OpenAI Cookbook：[github.com/openai/openai-cookbook](https://github.com/openai/openai-cookbook)
- Azure OpenAI Service：[azure.microsoft.com/products/ai-services/openai-service](https://azure.microsoft.com/products/ai-services/openai-service)
- Cohere API 文档：[docs.cohere.com](https://docs.cohere.com)
- Hugging Face Inference Endpoints：[huggingface.co/inference-endpoints](https://huggingface.co/inference-endpoints)
