---
title: "AI 技术编年史 2026：跨芯片统一算子"
date: 2026-06-05 10:00:00
categories:
  - "framework"
tags:
  - "AI Timeline"
  - "Cross-Chip Operator"
  - "FlagOS"
  - "AI Kernel"
description: "2026 年跨芯片统一算子（Cross-Chip Unified Operators）技术：一次定义、多硅片高性能执行，中英文对照。"
---

# AI 技术编年史 2026：跨芯片统一算子 | Cross-Chip Unified Operators

---

## 一、背景 | Background

**English**

Even with compilers like FlagOS and PyTorch Inductor, teams in 2025 still maintained **separate kernel libraries per chip** — cuBLAS on NVIDIA, MIOpen on AMD, ACL on Ascend, MPS on Apple. Operator semantics drifted (e.g., different NaN handling, layout preferences), and **fusion patterns** that worked on GPU failed silently on NPU. In 2026, the **Cross-Chip Unified Operator (CCUO)** specification standardized **semantic contracts** and **reference implementations** for the ~200 operators covering 95% of LLM and vision workloads.

CCUO was stewarded by FlagOpen alongside PyTorch Foundation working groups. Each operator defined: **mathematical semantics**, **numerical tolerance bands**, **layout constraints**, **fusion legality rules**, and **performance portability profiles** (minimum % of vendor peak FLOPs). Chip vendors shipped **CCUO-certified backends**; framework authors targeted CCUO APIs instead of raw vendor BLAS.

Before CCUO, a single **RoPE kernel update** required six vendor PRs and weeks of alignment meetings. After CCUO v1, the same change merged once in FlagIR and propagated through certification farms — **calendar time dropped 70%** for framework teams surveyed in Q2 2026.

**中文**

即便有 FlagOS、PyTorch Inductor，2025 年团队仍为每类芯片维护 **独立算子库** — cuBLAS、MIOpen、ACL、MPS。算子语义漂移（NaN 处理、布局偏好不一），GPU 上有效的 **融合模式** 在 NPU 上静默失败。2026 年 **跨芯片统一算子（CCUO）** 规范标准化覆盖 LLM 与视觉 95% 工作负载的约 200 个算子的 **语义契约** 与 **参考实现**。

CCUO 由 FlagOpen 与 PyTorch 基金会工作组共同维护。每算子定义：**数学语义**、**数值容差带**、**布局约束**、**融合合法性**、**性能可移植 profile**（相对厂商峰值 FLOPs 最低占比）。芯片厂商交付 **CCUO 认证后端**；框架作者面向 CCUO API 而非原始 BLAS。

CCUO 之前，一次 **RoPE kernel 更新** 需六家厂商 PR 与数周对齐会。CCUO v1 后同一变更在 FlagIR 合并一次即经认证农场传播 — Q2 2026 调研框架团队 **日历时间降约 70%**。

---

## 二、架构 | Architecture

**English**

**CCUO three-tier architecture:**

```
Tier 1 — Semantic Spec（语义层，open JSON + MLIR ops）
  └── Op definitions: matmul, softmax, rope, moe_dispatch, etc.

Tier 2 — Portable Reference（可移植参考层）
  ├── MLIR / Triton-like CCUO-DSL kernels
  └── Auto-tune search space shared across backends

Tier 3 — Vendor Backend（厂商后端）
  ├── Hand-optimized microkernels（certified）
  ├── Fallback to Tier 2 if cert missing
  └── Runtime capability negotiation
```

**Fusion compiler integration:**

```
[LayerNorm + Matmul + BiasAdd]  →  single CCUO fused op "fused_linear_norm"
       ↓ FlagOS / Inductor pattern match
Backend selects: GPU warp fusion | NPU graph op | CPU AVX512
```

**MoE-critical operators (2026):** `moe_dispatch`, `moe_combine`, `grouped_matmul`, `topk_softmax` — each with **explicit all-to-all ordering** semantics to prevent deadlock across chips.

**中文**

**CCUO 三层：** 语义规范（开放 JSON/MLIR）→ 可移植参考实现（CCUO-DSL + 共享搜索空间）→ 厂商认证后端（缺失则回退 Tier 2）。

**融合示例：** LayerNorm+Matmul+Bias → 单一 `fused_linear_norm`；编译器按设备选 warp 融合 / NPU 图算 / AVX512。

**MoE 关键算子：** dispatch/combine/grouped_matmul/topk_softmax，含 **显式 all-to-all 顺序** 防跨芯片死锁。

| Operator | Fusion partners | Cross-chip note |
|---|---|---|
| matmul | bias, gelu, rope | Layout NHWC vs NCHW negotiated |
| flash_attn | dropout, mask | SRAM size varies by chip |
| moe_dispatch | topk, all-to-all | Ordering spec mandatory |
| layernorm | linear | Common LLM block fusion |

---

## 三、趋势 | Trends

**English**

1. **PyTorch `torch.library` CCUO namespace** — custom ops register once globally.
2. **CI certification farms** — every backend runs 10k numeric + perf tests nightly.
3. **Operator marketplace** — third parties sell optimized CCUO backends for niche chips.
4. **LLM-specific op packs** — FP8 blockwise matmul, KV-cache append, speculative decode ops.
5. **Open perf leaderboard** — CCUO ops/sec/Watt across chips with unified benchmarks.
6. **Security audits** — supply-chain signing for certified backend binaries.

**中文**

1. PyTorch **CCUO 命名空间** — 自定义算子一次全局注册。
2. **CI 认证农场** — 每后端 nightly 跑 1 万数值+性能测试。
3. **算子市场** — 第三方为小众芯片售卖 CCUO 后端。
4. **LLM 算子包** — FP8 块 matmul、KV append、投机 decode。
5. **开放性能榜** — 统一 benchmark 的 ops/sec/Watt。
6. **安全审计** — 认证后端二进制供应链签名。

---

## 四、优缺点 | Pros and Cons

**English**

**Pros:** Predictable numerics across chips; faster framework releases; fair benchmark comparisons; reduced duplicate kernel engineering; clearer liability when results differ (spec violation vs. bug).

**Cons:** **Lowest-common-denominator risk** if spec too weak; **slow spec churn** for new ops (e.g., new attention variants); **vendor resistance** to expose peak kernels via open interface; **certification cost** for startups.

**中文**

**优点：** 跨芯片数值可预期；框架发布更快；benchmark 更公平；减少重复 kernel 工程；结果差异责任清晰。

**缺点：** 规范过弱则 **最大公约数** 风险；新算子 **规范迭代慢**；厂商不愿经开放接口暴露峰值 kernel；创业公司 **认证成本**。

---

## 五、应用场景 | Use Cases

| 场景 | English |
|---|---|
| 多芯片 K8s 集群 | Same container image, CCUO runtime picks backend |
| 框架维护者 | One PR for new RoPE variant across all chips |
| Benchmark 机构 | MLPerf with CCUO-certified backends only |
| MoE 训练 | Portable dispatch/combine on GPU+Ascend mix |
| 边缘 OTA | Update CCUO spec layer without full firmware flash |
| 教学/研究 | Students run identical op on CPU/GPU/NPU in lab |

---

## 六、GitHub 生态 | GitHub Ecosystem

| Repository | Role |
|---|---|
| [FlagOpen/FlagOS](https://github.com/FlagOpen/FlagOS) | CCUO spec, reference kernels, certification harness |
| [pytorch/pytorch](https://github.com/pytorch/pytorch) | CCUO op registration, Inductor lowering |
| openxla/xla | StableHLO ↔ CCUO bridging experiments |
| triton-lang/triton | Inspiration for CCUO-DSL syntax |
| FlagOpen/FlagPerf | Cross-chip operator benchmarks |

**Integration with Claude Code / Cursor:** Agent coding tools use CCUO-aware stubs so generated CUDA-like code targets portable DSL when users specify multi-chip deployment (documented in agent-dev guides).

---

## 七、深入探讨 | Extended Discussion

**English**

CCUO **certification** in 2026 is a **multi-week pipeline**: numeric parity tests (atol/rtol per dtype), performance floors (% of vendor peak), fusion legality checks, and **stress tests** (max batch, odd shapes, NaN inputs). Failed backends fall back to Tier-2 reference with **logged performance warning** — training still runs, but MLPerf submissions disqualified.

**Framework maintainers** benefit from **single PR workflow**: adding **FP8 blockwise matmul** updates FlagIR spec, reference kernel, and triggers re-certification across registered backends. **Version skew** is managed via **CCUO schema version** embedded in model checkpoints — runtime refuses load if backend too old.

**MoE operators** (`moe_dispatch`, `moe_combine`) specify **deterministic ordering** of token routing to prevent **deadlock** when experts span chips with asymmetric bandwidth. FlagOS lowers these ops directly; PyTorch Inductor pattern-matches CCUO fusion names.

**中文**

2026 CCUO **认证** 为 **数周流水线**：数值 parity（dtype 级 atol/rtol）、性能下限（厂商峰值 %）、融合合法性、**压测**（max batch、奇 shape、NaN 输入）。失败后端回退 Tier-2 并 **记录性能警告** — 训练仍可跑，但 MLPerf 投稿 disqualify。

**框架维护者** 享受 **单次 PR 工作流**：新增 **FP8 块 matmul** 更新 FlagIR、参考 kernel 并触发已注册后端重认证。**版本 skew** 由 checkpoint 内嵌 **CCUO schema version** 管理 — 后端过旧则拒绝加载。

**MoE 算子** 规定 token 路由 **确定性顺序**，防跨 asymmetric 带宽芯片 **死锁**。FlagOS 直接 lowering；PyTorch Inductor 模式匹配 CCUO 融合名。

### 7.1 典型认证指标 | Typical Certification Metrics

| 测试 Test | 通过标准 Pass criteria |
|---|---|
| matmul INT8 | ≥85% peak TOPS, rtol 1e-2 |
| flash_attn FP16 | ≥80% peak, max error vs ref |
| moe_dispatch | Zero deadlock 10k trials |
| layernorm fusion | Bitwise match FP32 ref on sample |

---

## 八、参考链接 | References

- CCUO specification v1.0 (FlagOpen, 2026 Q1)
- PyTorch Operator Coverage RFC
- MLPerf Inference 2026 CCUO backend rules
- 本系列：[ai-timeline-2026-flagos-heterogeneous-compiler](/posts/ai-timeline-2026-flagos-heterogeneous-compiler.html)

---

**Summary | 总结**

Cross-chip unified operators are the **lingua franca of AI kernels in 2026** — semantic contracts that let compilers and frameworks treat silicon as interchangeable within defined tolerance and performance bands.

跨芯片统一算子是 2026 年 AI kernel 的 **通用语** — 在定义容差与性能带内让编译器与框架将硅片视为可互换。
