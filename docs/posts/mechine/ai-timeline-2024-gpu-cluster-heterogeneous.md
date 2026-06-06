---
title: "AI 技术编年史 2024：万卡异构智算集群"
date: 2024-07-15 10:00:00
categories:
  - "mechine"
tags:
  - "AI Timeline"
  - "GPU Cluster"
  - "Heterogeneous Computing"
  - "InfiniBand"
  - "Distributed Training"
description: "2024 年万卡 GPU 集群与异构智算成为大模型训练基座：NVLink、InfiniBand、3D 并行与国产算力生态。"
---

# 万卡异构智算集群 | 10k GPU Heterogeneous AI Clusters

---

## 一、背景与核心概念 | Background and Core Concepts

**English**

Training frontier LLMs in 2024 required **10,000+ GPU clusters** — a scale once reserved for national labs. Meta's Llama 3 reportedly trained on **16k H100s**; xAI's Colossus reached **100k H100s** by late 2024. **Heterogeneous computing** adds complexity: mixing H100, A100, AMD MI300X, and domestic accelerators (Huawei Ascend, Cambricon) within unified scheduling layers.

Key concepts:

- **3D Parallelism**: data parallel (DP) + tensor parallel (TP) + pipeline parallel (PP) + expert parallel (EP) for MoE
- **Network fabric**: InfiniBand NDR 400G, NVLink NVSwitch for intra-node, fat-tree topology
- **Checkpointing**: distributed async checkpoint to parallel filesystem (Lustre, GPFS)
- **Fault tolerance**: spot instances, straggler mitigation, hot spare nodes
- **Power and cooling**: 10k GPUs ≈ 7–15 MW; liquid cooling mandatory

**中文**

2024 年训练前沿大模型需 **万卡级 GPU 集群**——曾为国家级实验室专属。Meta Llama 3 据称用 **1.6 万 H100**；xAI Colossus 年底达 **10 万 H100**。**异构智算**增加复杂度：H100、A100、AMD MI300X 与昇腾、寒武纪等国产芯片在同一调度层混合。

核心概念：3D 并行（DP+TP+PP+EP）；InfiniBand NDR、NVLink NVSwitch；分布式 checkpoint；容错与 straggler；万卡功耗约 7–15 MW，液冷必备。

| 术语 | 说明 |
|---|---|
| MFU | Model FLOPs Utilization，有效算力利用率 |
| All-Reduce | 梯度同步集合通信 |
| ZeRO | 分片优化器状态降显存 |
| Pod | 典型 256–2048 GPU 物理单元 |

### 1.1 规模对照 | Scale Reference

**English**

| Cluster | GPUs (approx.) | Notable use (2024) |
|---|---|---|
| Meta Llama 3 | ~16,000 H100 | Dense + MoE pretrain |
| xAI Colossus | ~100,000 H100 | Grok training |
| Microsoft Azure AI | Multi-10k regions | OpenAI + enterprise |
| 国内智算中心 | 万卡昇腾/寒武纪 | 行业大模型 |

A single H100 consumes ~700W TDP; **10k GPUs ≈ 7 MW** before CPU, networking, and cooling overhead — datacenter site selection became a **power contract** negotiation.

**中文**

| 集群 | GPU（约） | 2024 用途 |
|---|---|---|
| Meta Llama 3 | ~1.6 万 H100 | 稠密+MoE 预训练 |
| xAI Colossus | ~10 万 H100 | Grok |
| 微软 Azure AI | 区域级万卡 | OpenAI+企业 |
| 国内智算 | 万卡国产芯片 | 行业大模型 |

单 H100 约 700W TDP；**万卡约 7 MW**（不含 CPU、网络、冷却）——选址成**电力合同**谈判。

---

## 二、架构设计 | Architecture

**English**

Typical 10k GPU cluster architecture:

```
┌─────────────────────────────────────────────────────────┐
│                   Job Scheduler (Slurm/K8s)              │
│              + AI Orchestrator (Megatron, DeepSpeed)     │
└───────────────────────────┬─────────────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    ▼                       ▼                       ▼
┌─────────┐           ┌─────────┐           ┌─────────┐
│ Pod 1   │  IB NDR   │ Pod 2   │  IB NDR   │ Pod N   │
│ 256 GPU │◄─────────►│ 256 GPU │◄─────────►│ 256 GPU │
│ NVSwitch│           │ NVSwitch│           │ NVSwitch │
└─────────┘           └─────────┘           └─────────┘
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            ▼
              Parallel Filesystem (Lustre / DAOS)
              Object Store (S3-compatible checkpoints)
```

**Heterogeneous layer**: scheduler maps jobs to GPU SKUs by memory, FP8 support, and interconnect bandwidth; **gradient accumulation** bridges slower nodes.

**中文**

典型万卡架构：Slurm/K8s 调度 + Megatron/DeepSpeed 编排 → 多 Pod（每 Pod 256 GPU、NVSwitch）→ InfiniBand 全互联 → Lustre/DAOS 并行文件系统。异构层按显存、FP8、带宽映射任务；梯度累积桥接慢节点。

### 2.1 并行策略选择 | Parallelism Selection

| 模型规模 | 推荐策略 |
|---|---|
| 7B–70B dense | TP(8) + DP + ZeRO-3 |
| 400B+ dense | TP + PP + DP |
| MoE (8×7B) | EP + TP + DP |
| 多模态 | 分离 vision/text 并行组 |

### 2.2 国产异构栈 | Domestic Heterogeneous Stack

**English**: Ascend 910B clusters use CANN + MindSpeed; scheduling bridges via **FlagOS**-style abstraction layers emerging in 2025–2026 roadmaps.

**中文**：昇腾 910B 用 CANN + MindSpeed；FlagOS 类抽象层在 2025–2026 路线图中出现。

### 2.3 可靠性工程 | Reliability Engineering

**English**

At 10k scale, **mean time between failure (MTBF)** guarantees daily node loss. Training jobs checkpoint every N minutes to distributed storage; **torch.distributed** elastic hooks restart ranks. **Stragglers** — slow nodes from thermal throttle or bad NIC — are mitigated by gradient accumulation skew tuning and optional node exclusion lists.

**中文**

万卡规模下 **MTBF** 保证每日有节点失效。训练每 N 分钟 checkpoint 到分布式存储；**torch.distributed** 弹性重启 rank。**Straggler**（热节流、坏网卡）通过梯度累积偏斜调优与节点排除列表缓解。

---

## 三、产业趋势 | Industry Trends

**English**

2024 cluster trends:

1. **H100 supply crunch** — lead times drove multi-vendor strategies
2. **Sovereign AI clouds** — nations fund domestic 10k+ clusters
3. **FP8 training** — Transformer Engine on H100 cuts memory and boosts MFU
4. **Inference/Train colocation** — same datacenter serves both workloads
5. **Energy limits** — grid constraints cap cluster expansion in some regions
6. **Open cluster software** — PyTorch FSDP2, Megatron-LM, DeepSpeed MoE mature

**中文**

2024 趋势：H100 供应紧张推动多 vendor；主权 AI 云投资万卡；FP8 训练降显存提 MFU；训推同机房；电网限制扩张；FSDP2、Megatron、DeepSpeed MoE 软件成熟。

---

## 四、优缺点分析 | Pros and Cons

### 4.1 优点 | Advantages

1. **训练速度** — 周级完成万亿 token / Week-scale trillion-token runs
2. **规模定律延续** — 更大集群 → 更强模型 / Scaling laws continue
3. **容错工程成熟** — checkpoint 恢复分钟级 / Resilient long jobs
4. **软件栈统一** — PyTorch 生态主导 / Unified PyTorch stack
5. **异构弹性** — 多 SKU 提高利用率 / Mixed SKUs improve utilization
6. **推理共部署** — 摊薄基础设施 / Shared infra amortization

### 4.2 缺点 | Disadvantages

1. **资本密集** — 万卡 ≈ 数亿美元 / Billions in capex
2. **能耗与碳排** — ESG 压力 / Energy and carbon footprint
3. **运维复杂** — 网络、存储、调度耦合 / Operational complexity
4. **供应商锁定** — NVIDIA 生态依赖 / Vendor concentration risk
5. **异构效率损失** — 跨芯片性能不一致 / Heterogeneity overhead
6. **人才稀缺** — 分布式系统专家少 / Scarce distributed systems talent

---

## 五、典型应用场景 | Use Cases

| 场景 Scenario | 中文说明 | English Description |
|---|---|---|
| 前沿 LLM 预训练 | 1T+ token 基座模型 | Frontier base model pre-training |
| MoE 超大规模 | 混合专家万亿参数 | Trillion-parameter MoE runs |
| 多模态联合训练 | 图文音视频统一 | Multimodal joint training |
| RLHF 大规模 | 并行 rollout + RM | Large-scale alignment training |
| 科学计算 AI | 气候、蛋白质联合 HPC+AI | HPC-AI fusion workloads |
| 云厂商租售 | 按 GPU·时售卖算力 | GPU-hour cloud offerings |

---

## 六、GitHub 与开源生态 | GitHub and Open Source

**English**

Cluster training frameworks:

- **NVIDIA/Megatron-LM**: 3D parallelism reference
- **microsoft/DeepSpeed**: ZeRO, MoE, inference
- **pytorch/pytorch**: FSDP2 native
- **hpcaitech/ColossalAI**: heterogeneous and hybrid parallel
- **ray-project/ray**: distributed orchestration

**中文**

开源框架：Megatron-LM、DeepSpeed、PyTorch FSDP2、ColossalAI、Ray。

| 仓库 | 说明 |
|---|---|
| [NVIDIA/Megatron-LM](https://github.com/NVIDIA/Megatron-LM) | 3D 并行参考实现 |
| [microsoft/DeepSpeed](https://github.com/microsoft/DeepSpeed) | ZeRO / MoE |
| [pytorch/pytorch](https://github.com/pytorch/pytorch) | FSDP2 |
| [hpcaitech/ColossalAI](https://github.com/hpcaitech/ColossalAI) | 异构并行 |

---

## 七、参考链接 | References

- Meta Llama 3 训练基础设施博客
- NVIDIA H100 Tensor Core GPU 架构白皮书
- InfiniBand NDR 400G 规范
- xAI Colossus 集群公开报道
- DeepSpeed ZeRO 论文与文档
- 中国智算中心建设政策文件（2024）

---

## 八、2025 展望 | Outlook for 2025

**English**

Next-generation clusters adopt **GB200 NVL72** rack-scale designs, **FP4/FP6** numerics, and **train-inference disaggregation** on shared fabrics. **Heterogeneous scheduling** (FlagOS-class abstractions) becomes mandatory as export controls diversify chip supply. Energy caps push **dynamic power capping** and **geo-shifting** training jobs to regions with surplus renewables. Mid-size labs rent **8–512 GPU slices** via cloud rather than owning 10k — but frontier labs remain capex-heavy.

**中文**

下一代集群采用 **GB200 NVL72** 机架设计、**FP4/FP6** 数值、**训推分离**共享 fabric。**异构调度**（FlagOS 类抽象）在出口管制分化芯片供应下成刚需。能耗上限推动**动态功耗封顶**与**地理迁移**训练至富余可再生能源区。中型实验室云租 **8–512 GPU** 而非自持万卡——前沿实验室仍重 capex。

---

**English Summary**: 2024 cemented 10k GPU clusters as the training baseline for frontier AI — heterogeneous scheduling and network fabric became as critical as chip FLOPs.

**中文总结**：2024 确立万卡集群为前沿 AI 训练基线——异构调度与网络 fabric 与芯片算力同等关键。
