---
title: "AI 技术编年史 2026：修正缩放定律与软硬协同 MoE"
date: 2026-02-10 10:00:00
categories:
  - "algrithom"
tags:
  - "AI Timeline"
  - "Scaling Laws"
  - "MoE"
  - "Mixture of Experts"
description: "2026 年大模型缩放定律修正与硬件-软件协同 MoE（HW-SW MoE）架构详解：背景、架构、趋势、优缺点、应用场景与 GitHub 生态，中英文对照。"
---

# AI 技术编年史 2026：修正缩放定律与软硬协同 MoE | Revised Scaling Laws & HW-SW MoE

---

## 一、背景 | Background

**English**

Classical **neural scaling laws** (Kaplan et al., Chinchilla) predicted smooth power-law improvements in loss as compute, data, and parameters increased. By 2026, frontier labs reported **systematic deviations**: diminishing returns beyond ~10²⁵ FLOPs without architectural changes, **data exhaustion** for high-quality web text, and **inference cost walls** that made dense 1T+ models economically impractical for most deployments.

The industry response was twofold: **revised scaling laws** incorporating MoE sparsity, retrieval, and synthetic data quality tiers; and **hardware–software co-designed MoE (HW-SW MoE)**, where expert routing, memory hierarchy, and interconnect topology were optimized jointly. Models like sparse-gate transformers with **128–256 experts** (8–16 active per token) became the default frontier architecture, achieving **3–5× better training FLOPs efficiency** and **2–4× lower inference latency** versus dense equivalents at matched quality.

Researchers also documented **compute-optimal frontiers** that differ by deployment target: training-optimal expert counts exceed inference-optimal counts, leading to **two-stage releases** — train wide, distill routing for serve. Open benchmarks (FlagPerf, MLPerf MoE tracks) made these trade-offs auditable instead of marketing claims.

**中文**

经典 **神经缩放定律**（Kaplan、Chinchilla）预测随算力、数据与参数量增加，损失呈平滑幂律改善。到 2026 年，前沿实验室报告 **系统性偏离**：无架构变更时超过约 10²⁵ FLOPs 收益递减、高质量网页文本 **数据枯竭**，以及 **推理成本墙** 使密集 1T+ 模型对多数部署不经济。

产业对策有二：**修正缩放定律** — 纳入 MoE 稀疏性、检索与合成数据质量分级；**软硬协同 MoE（HW-SW MoE）** — 专家路由、存储层次与互连拓扑联合优化。稀疏门控 Transformer 配 **128–256 专家**（每 token 激活 8–16 个）成为默认前沿架构，在同等质量下实现 **训练 FLOPs 效率提升 3–5 倍**、**推理延迟降低 2–4 倍**。

研究者还记录 **因部署目标而异的算力最优前沿**：训练最优专家数常大于推理最优，催生 **两阶段发布** — 宽训练、蒸馏路由再服务。开放 benchmark（FlagPerf、MLPerf MoE 赛道）使这些权衡可审计，而非营销话术。

---

## 二、架构 | Architecture

**English**

**HW-SW MoE architecture (2026 reference design):**

```
Token Input
    ↓
Shared Dense Layers（共享密集层，embedding + early fusion）
    ↓
Router Network（路由网络，top-k gating, load-balancing aux loss）
    ↓
Expert Pool（专家池）
    ├── Group A → GPU cluster（大 FFN experts）
    ├── Group B → NPU tiles（量化 INT4/FP8 experts）
    └── Group C → CPU offload（cold / rare experts）
    ↓
All-to-All / Hierarchical AllReduce（跨节点专家通信）
    ↓
Output Projection + Shared Head
```

**Revised scaling law (informal 2026 form):**

\[
L \propto C^{-\alpha} \cdot D_{\text{eff}}^{-\beta} \cdot E_{\text{active}}^{-\gamma} \cdot Q_{\text{synth}}^{-\delta}
\]

Where \(D_{\text{eff}}\) is quality-weighted effective data, \(E_{\text{active}}\) is active expert capacity, and \(Q_{\text{synth}}\) captures verified synthetic data contribution (capped to prevent collapse).

**Software innovations:** **Expert parallelism (EP)** with **capacity buffers**; **dynamic expert pruning** at inference; **speculative routing** predicting next-layer experts; **FP8/INT4 expert weights** with per-channel scales. **Hardware innovations:** **NVLink/PCIe-aware expert placement**; **on-chip SRAM expert caches** on custom accelerators; **MoE-aware compilers** (FlagOS, XLA MoE passes) fusing all-to-all with matmul.

**中文**

**2026 HW-SW MoE 参考架构** 如上：共享密集层 → 路由网络（top-k + 负载均衡辅助损失）→ 分组专家池（GPU 大 FFN / NPU 量化 / CPU 冷专家）→ 分层通信 → 输出投影。

**修正缩放定律** 引入有效数据 \(D_{\text{eff}}\)、激活专家容量 \(E_{\text{active}}\) 与经核验合成数据贡献 \(Q_{\text{synth}}\)（设上限防 collapse）。

**软件创新：** 专家并行（EP）与容量缓冲、推理动态专家剪枝、投机路由、FP8/INT4 专家权重。**硬件创新：** 互连感知专家放置、定制加速器片上 SRAM 专家缓存、MoE 感知编译器（FlagOS、XLA MoE pass）融合 all-to-all 与 matmul。

| 维度 | Dense 1T | HW-SW MoE 400B/2T total |
|---|---|---|
| 训练 FLOPs/token | 高 | 低（稀疏激活） |
| 推理内存 | 全参数加载 | 仅热专家 + 缓存 |
| 通信开销 | 低 | all-to-all（需拓扑优化） |
| 质量 @ 同等算力 | 基准 | +5–15%（Chinchilla-optimal 专家数） |

---

## 三、趋势 | Trends

**English**

1. **Chinchilla-optimal MoE** — Active experts and total experts tuned per compute budget, not fixed 8-of-64.
2. **Retrieval-augmented MoE (RA-MoE)** — Static knowledge in vector DB; experts specialize in reasoning styles.
3. **Multi-stage scaling** — Pretrain dense core → expand to MoE → distill to edge MoE-lite.
4. **Open-weight MoE stacks** — Qwen-MoE, Mixtral successors with public routing analysis tools.
5. **Scaling law dashboards** — Real-time fit of loss vs. FLOPs/data during training; early stopping on law breakpoints.
6. **Regulatory attention** — Transparency on active parameters vs. total parameters for compute reporting.

**中文**

1. **Chinchilla 最优 MoE** — 按算力预算调 active/total 专家数，非固定 8/64。
2. **检索增强 MoE** — 静态知识入向量库；专家专精推理风格。
3. **多阶段缩放** — 密集核心预训练 → 扩展 MoE → 蒸馏至边缘 MoE-lite。
4. **开源 MoE 栈** — Qwen-MoE、Mixtral 后继及公开路由分析工具。
5. **缩放定律仪表盘** — 训练时实时拟合 loss–FLOPs/数据，在拐点早停。
6. **监管关注** — 激活参数 vs 总参数透明度用于算力申报。

---

## 四、优缺点 | Pros and Cons

**English**

**Pros:** Better compute efficiency; modular expert updates (swap finance expert without full retrain); natural path to **conditional computation** aligned with user intent; hardware vendors ship MoE-optimized chips.

**Cons:** **Load imbalance** and **routing collapse** if aux losses mis-tuned; **all-to-all latency** dominates on large clusters; **debugging difficulty** — which expert failed?; **evaluation non-determinism** from routing noise; **checkpoint size** still large despite sparse activation.

**中文**

**优点：** 算力效率更高；专家模块化热更新；条件计算与用户意图对齐；芯片厂商推出 MoE 优化硅片。

**缺点：** 辅助损失不当导致 **负载失衡/路由 collapse**；大集群 **all-to-all 延迟** 主导；**调试困难**；路由噪声带来评估非确定性；checkpoint 体积仍大。

---

## 五、应用场景 | Use Cases

| 场景 | 中文 | English |
|---|---|---|
| 超大规模预训练 | 万卡集群训练 frontier MoE | Frontier pretrain on 10k+ GPU clusters |
| 低成本推理 API | 仅加载 10–20% 专家权重 | Serve with 10–20% expert weights hot |
| 行业专家混合 | 法律/医疗/代码专家可插拔 | Pluggable domain experts |
| 边缘 MoE-lite | 2–4 本地专家 + 云端路由 | On-device experts + cloud fallback |
| 研究复现 | 开源 MoE 验证修正 scaling law | Reproduce revised laws at 1B–70B scale |
| 多租户 SaaS | 租户专属 expert adapter | Per-tenant expert adapters |

---

## 六、GitHub 生态 | GitHub Ecosystem

| Repository | Contribution |
|---|---|
| [pytorch/pytorch](https://github.com/pytorch/pytorch) | `torch.distributed` EP, FSDP+MoE, FP8 kernels |
| [FlagOpen/FlagOS](https://github.com/FlagOpen/FlagOS) | Cross-chip MoE all-to-all fusion, NPU expert kernels |
| Megatron-LM / DeepSpeed-MoE forks | Reference HW-SW MoE training recipes |
| Hugging Face `transformers` | MoE model configs, load-balancing loss utils |
| EleutherAI `lm-evaluation-harness` | MoE-aware eval with routing stats |

**中文：** PyTorch 提供 EP 与 FP8；FlagOS 跨芯片融合通信；Megatron/DeepSpeed 提供训练配方；Transformers 与 lm-eval 支持 MoE 评估。

---

## 七、深入探讨 | Extended Discussion

**English**

The **2026 Chinchilla-optimal MoE** recipe treats **total experts** \(E_{\text{total}}\) and **active experts** \(k\) as first-class hyperparameters alongside learning rate and batch size. Empirical fits show that for a fixed compute budget, **under-routing** (too few active experts) wastes capacity, while **over-routing** (too many active) erases sparsity benefits and increases communication. Labs publish **routing heatmaps** in model cards so downstream deployers know which experts must be colocated.

**Training stability** techniques matured: **z-loss** on router logits prevents collapse to a single expert; **expert capacity factor** buffers handle token overflow; **auxiliary load-balancing loss** coefficients scheduled warm-up/down. **Checkpoint surgery** — adding experts mid-training from domain-specific continued pretrain — became routine for enterprise vertical models without full retrain from scratch.

**Inference economics** drove HW-SW MoE adoption: cloud APIs quote **effective active parameters** for pricing; edge devices ship **expert subsets** per locale (e.g., Chinese-heavy experts in APAC SKU). FlagOS and PyTorch 2.7+ expose **`torch.distributed.moe` APIs** documented in vendor playbooks.

**中文**

**2026 Chinchilla 最优 MoE** 将 **总专家数** 与 **激活数 k** 与学习率、batch 同级调参。经验拟合显示固定算力下 **路由不足** 浪费容量，**过度路由** 则抹平稀疏收益并增通信。实验室在 model card 发布 **路由热力图**，供部署方知悉须 colocate 的专家。

**训练稳定性** 技术成熟：router **z-loss** 防 collapse；**专家容量因子** 缓冲溢出；负载均衡损失系数 **warm-up/down**。**Checkpoint 手术** —  mid-training 增专家做领域续训 — 成企业 vertical 模型常规，无需从零预训练。

**推理经济学** 推动 HW-SW MoE：云 API 按 **有效激活参数** 计价；边缘设备按区域发 **专家子集**（如亚太 SKU 中文 heavy 专家）。FlagOS 与 PyTorch 2.7+ 暴露文档化的 **`torch.distributed.moe` API**。

### 7.1 修正定律与数据策略 | Revised Laws and Data Strategy

**English:** Synthetic and retrieval-augmented tokens enter scaling fits with **diminishing coefficients** — synthetic alone cannot substitute T0 human anchor beyond ~40% without benchmark regression on "real-world holdout" suites. MoE pairs naturally with **tiered data**: route code-heavy tokens to code-specialized experts via **co-trained router hints**.

**中文：** 合成与 RAG token 以 **递减系数** 进入缩放拟合 — 纯合成无法在无 real holdout 回归的情况下替代超过约 40% T0 人类锚点。MoE 与 **分级数据** 天然配对：经 **协同训练路由 hint** 将 code-heavy token 导向 code 专家。

---

## 八、参考链接 | References

- Fedus et al., Switch Transformers (JMLR)
- DeepSeek-MoE / Qwen2-MoE technical reports
- Patel et al., "Revisiting Scaling Laws for Sparse Models" (2025)
- FlagOS MoE compiler whitepaper
- 本系列：[ai-timeline-2026-flagos-heterogeneous-compiler](/posts/ai-timeline-2026-flagos-heterogeneous-compiler.html)

---

**Summary | 总结**

2026's scaling story is **sparse, co-designed, and data-quality-aware** — HW-SW MoE is the practical path to continue capability gains without linear FLOPs explosion.

2026 年的缩放叙事 **稀疏、协同设计、数据质量感知** — HW-SW MoE 是在 FLOPs 非线性爆炸下延续能力增长的务实路径。
