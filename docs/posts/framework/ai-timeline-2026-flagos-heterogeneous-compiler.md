---
title: "AI 技术编年史 2026：FlagOS 开放异构 AI 编译器"
date: 2026-05-10 10:00:00
categories:
  - "framework"
tags:
  - "AI Timeline"
  - "FlagOS"
  - "AI Compiler"
  - "Heterogeneous Computing"
description: "2026 年 FlagOS 开放异构 AI 编译器：跨 GPU/NPU/CPU 的统一编译栈，背景、架构、趋势与 GitHub 生态，中英文对照。"
---

# AI 技术编年史 2026：FlagOS 开放异构 AI 编译器 | FlagOS Open Heterogeneous AI Compiler

---

## 一、背景 | Background

**English**

By 2026, production AI workloads routinely spanned **NVIDIA GPUs, AMD accelerators, Huawei Ascend, Apple NPUs, Intel Gaudi, and custom AI chips** — yet developers faced **N fragmented software stacks** (CUDA, ROCm, CANN, Core ML, one-off vendor SDKs). Model teams spent more time on **porting kernels** than on algorithms. China's **BAAI / FlagOpen** initiative released **FlagOS** as an **open heterogeneous AI compiler and runtime OS**, aiming for a **"write once, run on any AI chip"** abstraction without sacrificing top-tier performance on any single vendor.

FlagOS built on lessons from TVM, MLIR, and PyTorch 2.x `torch.compile`, but added **vendor-neutral intermediate representation (FlagIR)**, **auto-scheduling across memory hierarchies**, and **policy-driven partitioning** for mixed GPU+NPU clusters. Early adopters included cloud providers offering **"heterogeneous AI instances"** billed by unified **Effective AI FLOPs (EAF)** rather than raw GPU hours.

Western hyperscalers initially treated FlagOS as **niche**, but by H2 2026 several added **read-only FlagIR import** for hybrid fleets serving APAC sovereign cloud requirements — a geopolitical driver as important as raw performance.

**中文**

2026 年生产 AI 工作负载常跨 **NVIDIA GPU、AMD、华为 Ascend、Apple NPU、Intel Gaudi 与定制 AI 芯片**，开发者却面对 **N 套碎片化软件栈**（CUDA、ROCm、CANN、Core ML、厂商 SDK）。模型团队 **移植算子** 的时间常超过算法本身。中国 **BAAI / FlagOpen** 发布 **FlagOS** 作为 **开放异构 AI 编译器与运行时 OS**，目标 **「一次编写，任意 AI 芯片运行」** 且不在任一厂商上牺牲顶尖性能。

FlagOS 汲取 TVM、MLIR、PyTorch 2 `torch.compile` 经验，新增 **厂商中立中间表示 FlagIR**、**跨存储层次自动调度** 与 **混合 GPU+NPU 集群策略分区**。早期采用者包括以统一 **有效 AI FLOPs（EAF）** 计费的云 **异构 AI 实例**。

西方 hyperscaler 起初视 FlagOS 为 **小众**，但 2026 下半年多家增加 **只读 FlagIR 导入** 以服务亚太主权云混合集群 — 地缘政治驱动力与 raw 性能同等重要。

---

## 二、架构 | Architecture

**English**

**FlagOS stack layers:**

```
Frontends（前端）
  ├── PyTorch 2.x（torch.export → FlagIR）
  ├── ONNX / StableHLO import
  └── Custom DSL（FlagScript, optional）

FlagIR（中间表示）
  ├── Graph-level ops（matmul, conv, MoE all-to-all）
  ├── Loop / tile annotations
  └── Memory scope + affinity tags

Compiler Middle-End
  ├── Graph optimization（fusion, constant fold, layout）
  ├── Auto-tuning scheduler（Ansor-style + vendor hints）
  └── Heterogeneous partitioner（cost model → device placement）

Backends（后端）
  ├── NVPTX / CUDA
  ├── ROCm HIP
  ├── Ascend CANN bridge
  ├── Metal / Core ML
  └── CPU LLVM + AMX/NEON

Runtime（运行时）
  ├── Unified memory pool（optional unified virtual addressing）
  ├── Async stream orchestration
  └── Profiler → EAF metrics export
```

**Key innovation — Policy-driven compilation:** Users declare **SLA JSON** (max latency, max power, preferred vendors); FlagOS selects schedules and chip mix automatically. **Open plugin API** lets silicon vendors ship closed-source micro-kernels while keeping IR and scheduler open.

**中文**

**FlagOS 分层：** 前端（PyTorch/ONNX）→ **FlagIR** → 中端（图优化、自动调优、异构分区）→ 多后端（CUDA/HIP/CANN/Metal/LLVM）→ 运行时（统一内存、流编排、EAF 分析）。

**策略驱动编译：** 用户声明 SLA JSON；FlagOS 自动选调度与芯片组合。**开放插件 API** 允许厂商闭源微内核、开源 IR 与调度器。

---

## 三、趋势 | Trends

**English**

1. **FlagOS in major Chinese clouds** — default compiler path for Ascend + GPU hybrid pools.
2. **Upstream PyTorch integration discussions** — optional FlagOS backend beside Inductor.
3. **MoE-first optimizations** — all-to-all + expert matmul fusion passes (see cross-chip operator post).
4. **Carbon-aware scheduling** — compile-time + runtime shift to lower-power chips when SLA allows.
5. **Certification programs** — "FlagOS Compatible" badge for AI chip startups.
6. **Edge-server split** — single FlagIR graph partitioned across phone NPU + edge TPU + cloud GPU.

**中文**

1. 国内主流云 **默认 FlagOS 路径** 服务 Ascend+GPU 混合池。
2. **PyTorch 上游集成** 讨论 — Inductor 旁可选 FlagOS 后端。
3. **MoE 优先优化** — all-to-all 与专家 matmul 融合。
4. **碳感知调度** — SLA 允许时切低功耗芯片。
5. **认证计划** — AI 芯片创业公司的 FlagOS Compatible 标识。
6. **端-边-云切分** — 单 FlagIR 图分区至多设备。

---

## 四、优缺点 | Pros and Cons

**English**

**Pros:** Reduced vendor lock-in; faster porting of new models; unified profiling; strategic autonomy for regions with mixed domestic/international silicon; open community tuning recipes.

**Cons:** **Peak performance gap** vs. hand-tuned vendor SDKs (5–15% on some kernels); **debugging complexity** across partition boundaries; **plugin trust** for closed vendor blobs; **adoption chicken-and-egg** — chips need FlagOS, FlagOS needs chips.

**中文**

**优点：** 降低厂商锁定；新模型移植更快；统一 profiling；混合国产/国际硅片的战略自主；开放调优配方。

**缺点：** 对手工 SDK **峰值性能差距**（部分 kernel 5–15%）；分区边界 **调试复杂**；闭源插件 **信任** 问题；芯片与 FlagOS **鸡生蛋**  adoption。

---

## 五、应用场景 | Use Cases

| 场景 | 说明 |
|---|---|
| 国产智算中心 | Ascend 为主、GPU 为辅的统一训练栈 |
| 跨云迁移 | 同一 FlagIR 产物部署 AWS + 私有云 |
| MoE 大模型训练 | 自动分区专家到不同芯片类型 |
| 移动端+云端 | 图分区：NPU 跑 encoder，云端跑 decoder |
| 芯片 bring-up | 新 AI 芯片仅实现后端插件即可跑 ResNet/LLM |
| 科研复现 | 统一 EAF 指标对比公平性 |

---

## 六、GitHub 生态 | GitHub Ecosystem

| Repository | Role |
|---|---|
| [FlagOpen/FlagOS](https://github.com/FlagOpen/FlagOS) | **Core compiler, FlagIR spec, runtime** |
| [pytorch/pytorch](https://github.com/pytorch/pytorch) | torch.export, Inductor comparison baseline |
| apache/tvm / llvm/mlir | IR and scheduling research lineage |
| FlagOpen/FlagPerf | Benchmark suite for heterogeneous chips |
| Vendor plugin repos (Ascend, etc.) | Closed-kernel backends |

**Related tooling:** FlagOS ships **`flagos compile`**, **`flagos run`**, and **`flagos profile --eaf`** CLI tools documented in the main repo README.

**中文：** FlagOpen/FlagOS 为核心；PyTorch 为前端与基线；FlagPerf 为异构 benchmark；厂商插件实现各后端。

---

## 七、深入探讨 | Extended Discussion

**English**

FlagOS competes not by hiding hardware details but by **surfacing them through cost models**. The **heterogeneous partitioner** solves a mixed-integer problem: assign each subgraph to a device minimizing **latency + λ·cost + μ·power** subject to memory and bandwidth constraints. When users update SLA JSON mid-deployment, FlagOS can **recompile and hot-swap** schedules without full model export — critical for **24/7 inference** services.

**Community governance** mirrors LLVM: FlagIR spec changes require RFC + 30-day comment; backend plugins signed by vendors; **FlagPerf** leaderboard updated monthly with **EAF/Watt** metrics preventing ** cherry-picked peak FLOPs** marketing. Chinese **智算中心** procurement began requiring FlagOS compatibility scores alongside raw TOPS.

**Developer experience:** `flagos compile model.pt --sla sla.json --targets ascend,gpu` emits **single artifact bundle** with per-backend shared libraries and **unified profiling trace** viewable in Chrome trace format. PyTorch users often start with **`torch.export`** → FlagOS path when Inductor lacks backend support for their chip.

**中文**

FlagOS 并非隐藏硬件细节，而是通过 **代价模型** 暴露它们。**异构分区器** 解混合整数问题：在内存与带宽约束下为子图分配设备，最小化 **延迟+λ·成本+μ·功耗**。用户 mid-deployment 更新 SLA JSON 时，FlagOS 可 **重编译热替换** 调度 — 对 **7×24 推理** 至关重要。

**社区治理** 镜像 LLVM：FlagIR 变更需 RFC+30 天评议；后端插件厂商签名；**FlagPerf** 月更 **EAF/Watt** 榜，防 ** cherry-pick 峰值 FLOPs** 营销。国内 **智算中心** 采购开始要求 FlagOS 兼容评分 alongside raw TOPS。

**开发者体验：** `flagos compile` 产出 **单一 artifact 包** 含各后端动态库与 **Chrome trace 格式** 统一 profiling。PyTorch 用户在 Inductor 不支持其芯片时常走 **`torch.export` → FlagOS**。

### 7.1 与 PyTorch Inductor 对比 | vs. PyTorch Inductor

| 维度 | Inductor | FlagOS |
|---|---|---|
| 主要目标 | PyTorch 图优化 | 跨厂商异构 |
| 后端 | CPU/CUDA 为主 | GPU+NPU+… 平等 |
| 分区 | 有限 | SLA 驱动全局分区 |
| 开源程度 | 全开源 | IR 开源+厂商插件 |

---

## 八、参考链接 | References

- FlagOpen official site and FlagOS documentation
- BAAI heterogeneous computing whitepaper (2025)
- MLIR dialect design notes for FlagIR
- 本系列：[ai-timeline-2026-cross-chip-operator](/posts/ai-timeline-2026-cross-chip-operator.html)

---

**Summary | 总结**

FlagOS is 2026's open answer to heterogeneous AI silos — a compiler OS that treats chips as pluggable backends under unified FlagIR and EAF metrics.

FlagOS 是 2026 年对异构 AI  silo 的开放回应 — 在统一 FlagIR 与 EAF 指标下将芯片视为可插拔后端的编译器 OS。
