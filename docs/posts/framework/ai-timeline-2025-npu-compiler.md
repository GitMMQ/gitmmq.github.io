---
title: "AI 技术编年史 2025：NPU 算子编译器 — Operator Compiler for NPUs"
date: 2025-11-10 10:00:00
categories:
  - framework
tags:
  - AI Timeline
  - NPU Compiler
  - 编译器
  - 算子
  - MLIR
description: "2025 年 11 月，NPU 算子编译器成为端侧与智算落地瓶颈：图优化、算子融合、跨芯片 IR。中英文对照。"
---

# NPU 算子编译器 | NPU Operator Compiler

> **English Title:** AI Technology Timeline 2025 — NPU Operator Compiler

---

## 一、背景 | Background

**English**

November 2025 elevated the **NPU operator compiler** from backend tooling to **strategic infrastructure**. As edge LLMs (May 2025 timeline) and datacenter NPUs proliferated, the bottleneck shifted from FLOPS to **how fast new operators** (RoPE variants, MLA attention, custom activations) **map to silicon** with acceptable latency and power.

An **operator** is a primitive compute kernel—matmul, conv, layer norm, softmax. An **NPU compiler** lowers high-level graphs (ONNX, PyTorch ExportedProgram, MLIR) into **vendor-specific microcode**, applying **fusion**, **tiling**, **quantization**, and **memory scheduling**. Poor compilation can waste 50%+ of theoretical TOPS—making compiler teams as critical as CUDA was for GPUs.

**Keywords:**

| Term | Definition |
|------|------------|
| **IR (Intermediate Representation)** | Portable graph format between framework and hardware |
| **Operator fusion** | Merge ops (e.g., matmul+bias+relu) to cut memory traffic |
| **Tiling** | Split tensors to fit on-chip SRAM |
| **Codegen** | Generate machine-specific kernel source or binaries |
| **Bringing-up** | Enable new chip with full op coverage + perf parity |

**中文**

2025 年 11 月，**NPU 算子编译器** 从后端工具升格为 **战略基础设施**。端侧 LLM（2025 年 5 月）与数据中心 NPU 普及后，瓶颈从 FLOPS 转向 **新算子**（RoPE 变体、MLA 注意力、定制激活）**多快映射到硅** 且 latency/功耗可接受。

**算子** 是原语计算核——matmul、conv、layer norm、softmax。**NPU 编译器** 将高层图（ONNX、PyTorch ExportedProgram、MLIR）lower 为 **厂商微码**，做 **融合**、**tiling**、**量化**、**内存调度**。编译差可浪费 50%+ 理论 TOPS——编译团队与当年 CUDA 对 GPU 同样关键。

**关键词：**

| 术语 | 定义 |
|------|------|
| **IR** | 框架与硬件间可移植图格式 |
| **算子融合** | 合并算子（如 matmul+bias+relu）减内存 traffic |
| **Tiling** | 切分 tensor 适配片上 SRAM |
| **Codegen** | 生成机器相关内核源码或二进制 |
| **Bring-up** | 新芯片全算子覆盖 + 性能 parity |

---

## 二、架构 | Architecture

**English**

```
Front-end import
  PyTorch 2.x export / ONNX / JAX
        ↓
Graph optimization (constant fold, layout convert)
        ↓
Hardware-agnostic IR (MLIR linalg, tensor, affine)
        ↓
Target-specific lowering
  ├── Intel NPU plugin (OpenVINO)
  ├── Qualcomm QNN / Hexagon SDK
  ├── Apple Core ML + ANE backend
  └── Ascend / Cambricon / custom ASIC paths
        ↓
Operator library + autotuning (AutoTVM, Halide-style)
        ↓
Runtime (memory pools, async queues, profiling)
```

**2025 compiler feature checklist:**

- **Dynamic shapes** for variable sequence length LLM decode
- **Mixed precision** INT4 weights + INT16 accumulators
- **Subgraph partitioning** CPU fallback for unsupported ops
- **AOT vs JIT:** Phones prefer AOT; research prefers JIT autotune

**中文**

```
前端导入
  PyTorch 2.x export / ONNX / JAX
        ↓
图优化（常量折叠、layout 转换）
        ↓
硬件无关 IR（MLIR linalg、tensor、affine）
        ↓
Target 专用 lowering
  ├── Intel NPU plugin（OpenVINO）
  ├── 高通 QNN / Hexagon SDK
  ├── Apple Core ML + ANE backend
  └── 昇腾 / 寒武纪 / 定制 ASIC 路径
        ↓
算子库 +  autotuning（AutoTVM、Halide 风格）
        ↓
运行时（内存池、异步队列、 profiling）
```

**2025 编译器功能清单：**

- **动态 shape** 适配变长 LLM decode
- **混合精度** INT4 权重 + INT16 累加
- **子图划分** 不支持算子 CPU fallback
- **AOT vs JIT：** 手机偏 AOT；研究偏 JIT autotune

---

## 三、趋势 | Trends

**English**

| Trend | Detail |
|-------|--------|
| **MLIR as lingua franca** | Vendors contribute dialects; reduce one-off translators |
| **LLM-specific op packs** | FlashAttention-2, MLA, RoPE fused kernels standard |
| **Cross-chip IR initiatives** | FlagOS-style unified paths (preview in 2026 timeline) |
| **Compiler + tokenizer co-design** | Cosmos-Tokenizer efficiency depends on NPU gather/scatter |
| **Open-source pressure** | llama.cpp / ExecuTorch force vendors to document backends |
| **Perf regression CI** | Every compiler commit runs golden models on device farm |

**中文**

| 趋势 | 详情 |
|------|------|
| **MLIR 通用语** | 厂商贡献 dialect；减少一次性 translator |
| **LLM 专用算子包** | FlashAttention-2、MLA、RoPE 融合内核标准化 |
| **跨芯片 IR initiative** | FlagOS 类统一路径（2026 时间线 preview） |
| **编译器 + tokenizer 协同设计** | Cosmos-Tokenizer 效率依赖 NPU gather/scatter |
| **开源压力** | llama.cpp / ExecuTorch 迫使厂商文档化 backend |
| **性能回归 CI** | 每次编译器提交在设备农场跑 golden 模型 |

---

## 四、优缺点 | Pros/Cons

**English**

**Pros**

- Unlocks hardware TOPS for real workloads—not marketing peaks
- Faster bring-up of new models when op library extensible
- Fusion + quant reduce power—critical for edge LLM battery life
- Single IR reduces framework fragmentation costs

**Cons**

- Vendor silos persist; "write once run everywhere" still aspirational
- Debugging compiled graphs harder than eager PyTorch
- Autotune compile times hours per new shape bucket
- Security: compiled blobs opaque to audit vs open kernels

**中文**

**优点**

- 释放硬件 TOPS 给真实 workload——非营销峰值
- 可扩展算子库加速新模型 bring-up
- 融合 + 量化降功耗——端侧 LLM 电池关键
- 单一 IR 降框架碎片化成本

**缺点**

- 厂商 silo 仍在；「一次编写到处运行」仍理想
- 编译图比 eager PyTorch 难调试
- autotune 对新 shape bucket 编译需数小时
- 安全：编译 blob 相对开放内核 opaque

---

## 五、应用场景 | Use Cases

**English**

| Scenario | Compiler role |
|----------|---------------|
| **AI PC Copilot** | Compile 7B Q4 model to Intel/AMD NPU nightly OTA |
| **Phone assistant** | Core ML / QNN graph for 3B VLM + 1B text |
| **Automotive ADAS** | Real-time fusion of perception ops on drive NPUs |
| **Cloud inference card** | Ascend/CUDA-alternative compile for LLM serving |
| **Robot edge policy** | 30 Hz VLA policy on Orin-class NPU |
| **Research lab** | MLIR pass prototyping before vendor SDK release |

**中文**

| 场景 | 编译器作用 |
|------|-----------|
| **AI PC Copilot** | 7B Q4 模型 nightly OTA 编译至 Intel/AMD NPU |
| **手机助手** | Core ML / QNN 图跑 3B VLM + 1B 文本 |
| **车载 ADAS** | 感知算子实时融合于 drive NPU |
| **云推理卡** | 昇腾等 LLM serving 编译 |
| **机器人 edge 策略** | Orin 级 NPU 30 Hz VLA |
| **研究 lab** | 厂商 SDK 发布前 MLIR pass 原型 |

---

## 六、GitHub 开源生态 | GitHub

**English**

| Repository | Role |
|------------|------|
| llvm/llvm-project (MLIR) | Shared IR infrastructure for NPU lowering |
| apache/tvm / OpenAI Triton | Autotuning and Pythonic GPU/NPU kernel DSL |
| ggml-org/llama.cpp | Reference for cross-vendor quant + kernel patterns |
| pytorch/executorch | Edge compiler stack integrating vendor backends |
| [NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) | Tokenizer ops stress-test gather/scatter on NPUs |
| openvinotoolkit/openvino | Intel NPU plugin open-source path |

**中文**

| 仓库 | 作用 |
|------|------|
| llvm/llvm-project (MLIR) | NPU lowering 共享 IR 基础设施 |
| apache/tvm / Triton | autotuning 与 Pythonic GPU/NPU 内核 DSL |
| llama.cpp | 跨厂商量化 + 内核模式参考 |
| executorch | 集成厂商 backend 的 edge 编译栈 |
| [NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) | Tokenizer 算子压测 NPU gather/scatter |
| openvino | Intel NPU 插件开源路径 |

---

## 七、参考资料 | References

1. Lattner et al. — MLIR: Scaling compiler infrastructure
2. Chen et al. — Triton: An intermediate language for tiled neural networks
3. Intel / Qualcomm — NPU compiler SDK documentation (2025)
4. PyTorch 2 Export — ExportedProgram for AOTInductor
5. MLSys 2025 — Compiler sessions on LLM inference

---

## 八、产业观察与深度解读 | Industry Observations and Deep Dive

**English**

**Supply chain and talent:** By the second half of 2025, enterprises stopped treating this topic as a pilot KPI and moved it into **annual operating plans**. Procurement asked for **three-year TCO**, not demo accuracy. System integrators packaged reference architectures with **SLA-backed support**, mirroring how cloud migrations matured a decade earlier.

**Interoperability:** Open APIs (MCP, ONNX, MLIR dialects where relevant) reduced lock-in, but **data gravity** still tied customers to platforms with the best vertical corpus or compiler backend. Winners combined open runtimes with **proprietary gold datasets** or **silicon-tuned kernels**.

**Risk register (2025 common items):** (1) **Evaluation gap**—public benchmarks no longer predict production; (2) **Security**—prompt injection and tool abuse in agentic stacks; (3) **Regulatory**—algorithm filing, EU AI Act high-risk categories; (4) **Talent**—shortage of engineers who understand both ML and domain workflows.

**Research frontiers carrying into 2026:** Tighter **world-model / spatial / sim** integration; **self-evolving alignment** with human audit; **cross-chip compilers** (see 2026 timeline). Teams that invested in **measurement**—latency, cost per task, failure replay—outperformed teams chasing parameter counts.

**中文**

**供应链与人才：** 2025 年下半年，企业不再将此主题仅作试点 KPI，而是写入 **年度经营计划**。采购要求 **三年 TCO**，而非 demo 准确率。系统集成商打包 **带 SLA 的参考架构**，类似十年前的云迁移成熟路径。

**互操作：** 开放 API（MCP、ONNX、相关 MLIR dialect）降低锁定，但 **数据重力** 仍把客户绑在拥有最佳垂直语料或编译后端的平台上。胜者 = 开放运行时 + **专有 gold 数据** 或 **硅片级调优内核**。

**风险登记（2025 共性）：** (1) **评估鸿沟**——公开 benchmark 不再预测生产；(2) **安全**——Agent 栈提示注入与工具滥用；(3) **监管**——算法备案、EU AI Act 高风险类；(4) **人才**——既懂 ML 又懂领域 workflow 的工程师短缺。

**延续至 2026 的研究前沿：** **世界模型 / 空间 / 仿真** 更紧耦合；带人工 audit 的 **自演化对齐**；**跨芯片编译器**（见 2026 时间线）。投资 **度量**——延迟、单任务成本、失败回放——的团队胜过追逐参数量。

**Glossary reinforcement | 术语 reinforcement**

| EN | 中文 | One-line |
|----|------|----------|
| Foundation model | 基础模型 | Large pretrained model finetuned for downstream tasks |
| Finetune | 微调 | Update weights on domain data |
| RAG | 检索增强生成 | Retrieve docs then generate grounded answers |
| Sim2real | 仿真到真实 | Transfer policies from simulator to physical world |
| TCO | 总拥有成本 | Full cost of ownership over deployment lifetime |

---

## 九、实施路线图（2025 Q2–Q4）| Implementation Roadmap

**English**

| Phase | Actions | Success metric |
|-------|---------|----------------|
| **Assess** | Inventory data, latency, compliance | Gap report signed by domain lead |
| **Pilot** | One workflow, HITL, private eval | >80% task success on golden set |
| **Harden** | SLO, monitoring, rollback | p95 latency and cost per task stable 4 weeks |
| **Scale** | Multi-site rollout, train-the-trainer | Adoption without support ticket spike |

**Team roles:** **Product owner** (workflow), **ML engineer** (model/compiler), **Domain expert** (gold labels), **SRE** (serving)—four roles minimum for production, not a lone prompt engineer.

**中文**

| 阶段 | 行动 | 成功指标 |
|------|------|----------|
| **评估** | 清点数据、延迟、合规 | 领域负责人签字差距报告 |
| **试点** | 单工作流、HITL、私有 eval | 黄金集任务成功率 >80% |
| **加固** | SLO、监控、回滚 | p95 延迟与单任务成本稳定 4 周 |
| **推广** | 多站点、培训 | 支持工单无尖峰 |

**团队角色：** **产品负责人**（工作流）、**ML 工程师**（模型/编译器）、**领域专家**（gold 标注）、**SRE**（serving）——生产最少四人，非 lone prompt engineer。

---

**总结 | Summary**

**中文：** 2025 年 11 月，NPU 算子编译器是 **软硬协同的咽喉**——模型再强，编译不到位则 tok/s 与功耗双双失败。MLIR、ExecuTorch、llama.cpp 推动开放；厂商 backend 仍是差异化战场。

**English:** November 2025 NPU operator compilers are the throat of hardware-software co-design—models fail in production if compilation underdelivers on tok/s and power. MLIR, ExecuTorch, and llama.cpp push openness; vendor backends remain the differentiation battleground.
