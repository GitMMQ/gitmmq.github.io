---
title: "2023 AI 编年史：vLLM 与 PagedAttention 推理引擎"
date: 2023-08-08 10:00:00
categories:
  - "framework"
tags:
  - "AI Timeline"
  - "vLLM"
  - "PagedAttention"
  - "Inference"
  - "Serving"
description: "2023 年 AI 编年史：vLLM 推理引擎与 PagedAttention 算法的技术原理、24× 吞吐提升与 LLM 服务化工程，中英文对照分析。"
---

# 2023 AI 编年史：vLLM 与 PagedAttention | AI Timeline 2023: vLLM Inference Engine

---

## 一、背景 | Background

**English**

In **August 2023**, **vLLM** — an open-source LLM inference engine from UC Berkeley's Sky Computing Lab — revolutionized LLM serving with **PagedAttention**. The v1 release demonstrated **up to 24× higher throughput** than Hugging Face Transformers and **3.5× higher** than Text Generation Inference (TGI), making production LLM deployment practical and affordable.

Before vLLM, serving LLMs suffered from **KV cache memory waste**: each request pre-allocated a contiguous memory block for its KV cache, but sequences vary in length — causing 60–80% memory fragmentation. PagedAttention borrowed **virtual memory paging** from operating systems to solve this.

Key terms:
- **vLLM**: High-throughput LLM inference and serving engine.
- **PagedAttention**: Algorithm managing KV cache in non-contiguous memory blocks (pages).
- **KV Cache**: Stored key-value tensors from attention layers, reused during generation.
- **Continuous Batching**: Dynamically adding/removing requests from GPU batches mid-inference.
- **Throughput**: Tokens generated per second across all concurrent requests.
- **TTFT (Time to First Token)**: Latency from request submission to first output token.

**中文**

**2023 年 8 月**，UC Berkeley Sky Computing Lab 的开源 LLM 推理引擎 **vLLM** 以 **PagedAttention** 算法革新了 LLM 服务。v1 版本展示 **比 Hugging Face Transformers 高 24 倍吞吐**、**比 TGI 高 3.5 倍**，使生产级 LLM 部署切实可行且成本可控。

vLLM 之前，LLM 服务受 **KV Cache 内存浪费** 困扰：每个请求预分配连续 KV Cache 内存块，但序列长度不一——导致 60–80% 内存碎片。PagedAttention 借鉴操作系统 **虚拟内存分页** 解决此问题。

关键词解释：
- **vLLM**：高吞吐 LLM 推理与服务引擎。
- **PagedAttention**：以非连续内存块（页）管理 KV Cache 的算法。
- **KV Cache**：注意力层缓存的 Key-Value 张量，生成时复用。
- **Continuous Batching（连续批处理）**：推理过程中动态增减 GPU batch 中的请求。
- **Throughput（吞吐量）**：所有并发请求每秒生成的 token 数。
- **TTFT（首 token 时间）**：从提交请求到首个输出 token 的延迟。

---

## 二、架构 | Architecture

### 2.1 PagedAttention 原理 | PagedAttention Mechanism

**English**

Traditional KV cache allocation vs PagedAttention:

```
Traditional（内存浪费）:
  Request A: [████████████░░░░░░░░]  12 tokens used, 20 allocated
  Request B: [██████░░░░░░░░░░░░░░]   6 tokens used, 20 allocated
  Request C: [████████████████████]  20 tokens used, 20 allocated
  Waste: 14 + 14 = 28 slots unused out of 60

PagedAttention（按需分配）:
  Physical KV Cache Blocks: [B1][B2][B3][B4][B5][B6][B7][B8]
  Request A Block Table: B1 → B2 → B3        (3 blocks, 12 tokens)
  Request B Block Table: B4 → B5             (2 blocks,  6 tokens)
  Request C Block Table: B6 → B7 → B8 → B1   (4 blocks, 20 tokens)
  Waste: near zero — blocks allocated on demand
```

**Key design**:
- KV cache split into fixed-size **blocks** (e.g., 16 tokens per block)
- Each request maintains a **block table** mapping logical → physical blocks
- Blocks shared via **Copy-on-Write** for parallel sampling (beam search)
- Memory manager allocates/frees blocks like OS page frames

**中文**

传统 KV Cache 预分配固定大小连续块，大量空间浪费；PagedAttention 将 KV Cache 切分为固定大小 **块**（如每块 16 token），每个请求维护 **块表**（逻辑→物理映射），按需分配，浪费接近零。通过 **Copy-on-Write** 共享块支持并行采样。

### 2.2 vLLM 系统架构 | vLLM System Architecture

```
Client Requests
      ↓
┌─────────────────────────────────┐
│  API Server（OpenAI-compatible）  │
│  /v1/completions, /v1/chat       │
├─────────────────────────────────┤
│  Scheduler                       │
│  ├── Continuous Batching         │
│  ├── Preemption（可选）           │
│  └── Priority Queues             │
├─────────────────────────────────┤
│  Model Executor                  │
│  ├── PagedAttention Kernel       │
│  ├── FlashAttention Integration  │
│  └── Tensor Parallelism          │
├─────────────────────────────────┤
│  Block Manager                   │
│  ├── GPU Block Pool              │
│  └── CPU Swap（溢出到 CPU）       │
└─────────────────────────────────┘
      ↓
  GPU（CUDA / ROCm）
```

### 2.3 性能对比 | Performance Comparison

| 引擎 Engine | 吞吐 Throughput | 批处理 Batching | KV Cache |
|---|---|---|---|
| HF Transformers | 1×（基准） | Static | Contiguous |
| TGI (HuggingFace) | ~7× | Continuous | Partial paging |
| **vLLM** | **~24×** | **Continuous** | **PagedAttention** |
| TensorRT-LLM | ~20× | In-flight | Custom |
| llama.cpp | CPU/GGUF | Sequential | Ring buffer |

### 2.4 OpenAI 兼容 API | OpenAI-Compatible API

**English**

vLLM ships with an **OpenAI-compatible REST API**, enabling drop-in replacement:

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-chat-hf",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**中文**

vLLM 内置 **OpenAI 兼容 REST API**，可无缝替换 OpenAI 调用——仅需修改 `base_url` 即可指向本地 vLLM 服务。

---

## 三、趋势 | Trends

**English**

August–December 2023 inference trends:

1. **vLLM as default serving**: Became the go-to engine for self-hosted LLM APIs.
2. **Speculative decoding**: vLLM added draft model acceleration (2–3× latency reduction).
3. **Multi-LoRA serving**: Serve hundreds of LoRA adapters on one base model instance.
4. **Cloud adoption**: AWS, GCP, and Azure integrated vLLM into managed LLM services.
5. **Competition**: TensorRT-LLM, SGLang, and TGI rapidly adopted paging concepts.
6. **Quantization integration**: AWQ, GPTQ, FP8 models served natively in vLLM.

**中文**

2023 年 8–12 月推理趋势：

1. **vLLM 成为默认服务引擎**：自托管 LLM API 的首选。
2. **投机解码**：vLLM 加入 draft model 加速（延迟降低 2–3 倍）。
3. **Multi-LoRA 服务**：单基座实例服务数百 LoRA 适配器。
4. **云厂商采纳**：AWS、GCP、Azure 集成 vLLM 到托管 LLM 服务。
5. **竞争加剧**：TensorRT-LLM、SGLang、TGI 快速采纳分页概念。
6. **量化集成**：AWQ、GPTQ、FP8 模型原生服务。

---

## 四、优缺点 | Pros and Cons

### 4.1 优点 | Advantages

1. **24× 吞吐提升** — 同等 GPU 服务更多用户 / **24× throughput boost**
2. **Near-zero KV waste** — PagedAttention 消除碎片 / **Near-zero KV waste**
3. **OpenAI API 兼容** — 零代码迁移 / **OpenAI API compatible**
4. **Continuous Batching** — 动态批处理提高 GPU 利用率 / **Dynamic batching**
5. **活跃社区** — 快速支持新模型架构 / **Active community**
6. **Multi-LoRA** — 一基座多适配器 / **Multi-LoRA serving**

### 4.2 缺点 | Disadvantages

1. **CUDA 依赖** — 主要优化 NVIDIA GPU / **CUDA-centric**
2. **Prefill 阶段瓶颈** — 长输入 TTFT 仍高 / **Prefill bottleneck**
3. **配置复杂** — tensor parallel、block size 调优 / **Configuration complexity**
4. **新模型延迟支持** — 新架构需等待 vLLM 适配 / **New model support lag**
5. **CPU 推理不支持** — 需 llama.cpp 替代 / **No CPU inference**
6. **内存仍有限** — 超大模型需多卡 tensor parallel / **Memory limits remain**

---

## 五、应用场景 | Use Cases

| 场景 Scenario | vLLM 配置 Config | 中文说明 |
|---|---|---|
| 企业内部 LLM API | 单卡 7B/13B + vLLM | OpenAI 兼容接口替代云端 API |
| 高并发 ChatBot | Continuous Batching | 动态批处理服务数千并发 |
| Multi-LoRA 平台 | 1 base + N adapters | SaaS 平台按客户切换 LoRA |
| RAG 后端 | vLLM + 长上下文 | 高吞吐 RAG 生成服务 |
| 模型评估 | vLLM benchmark | 快速对比不同模型吞吐 |
| 云 GPU 租赁 | vLLM on RunPod/Lambda | 最大化 GPU 利用率降本 |
| 边缘网关 | vLLM + 量化模型 | AWQ/GPTQ 4-bit 本地部署 |

---

## 六、GitHub 与开源生态 | GitHub and Open Source

| 项目 Project | 说明 Description |
|---|---|
| [vllm-project/vllm](https://github.com/vllm-project/vllm) | vLLM 官方仓库（核心引擎） |
| [huggingface/text-generation-inference](https://github.com/huggingface/text-generation-inference) | TGI 竞争方案 |
| [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM) | NVIDIA 优化推理引擎 |
| [sgl-project/sglang](https://github.com/sgl-project/sglang) | 结构化生成 + 高效服务 |
| [ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp) | CPU/边缘推理替代方案 |

---

## 七、总结 | Summary

**中文**：2023 年 8 月，vLLM 与 PagedAttention 将 LLM 推理从「实验室 demo」推向「生产级服务」。通过操作系统级内存管理思想解决 KV Cache 碎片问题，24 倍吞吐提升使自托管 LLM API 在经济上可行，成为 2023 年 LLM 工程化最关键的里程碑之一。

**English**: In August 2023, vLLM and PagedAttention pushed LLM inference from "lab demo" to "production serving." By applying OS-level memory management to KV cache fragmentation, the 24× throughput improvement made self-hosted LLM APIs economically viable — one of 2023's most critical LLM engineering milestones.

---

**参考链接 | References**

- 论文: [Efficient Memory Management for LLM Serving with PagedAttention](https://arxiv.org/abs/2309.06180)
- vLLM 文档: [docs.vllm.ai](https://docs.vllm.ai)
- GitHub: [github.com/vllm-project/vllm](https://github.com/vllm-project/vllm)
- SOSP 2023: vLLM 论文发表于操作系统顶级会议
