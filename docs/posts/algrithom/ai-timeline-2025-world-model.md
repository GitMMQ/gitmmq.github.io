---
title: "AI 技术编年史 2025：世界模型 World Model — 机器人与自动驾驶的新范式"
date: 2025-01-15 10:00:00
categories:
  - algrithom
tags:
  - AI Timeline
  - World Model
  - 世界模型
  - 自动驾驶
  - 机器人
description: "2025 年初，世界模型从学术概念走向机器人与 AV 工程主线：预测未来状态、在想象中规划动作。中英文对照，涵盖架构、趋势、优缺点与开源生态。"
---

# 世界模型 World Model：机器人与自动驾驶的新范式 | World Models for Robotics and Autonomous Driving

> **English Title:** AI Technology Timeline 2025 — World Models: A New Paradigm for Robotics and AV

---

## 一、背景 | Background

**English**

In early 2025, **World Model** moved from a niche research term to a central engineering pillar for **robotics**, **autonomous driving (AV)**, and **embodied AI**. A world model is an internal simulator: given current observations and a candidate action, it predicts **future states** of the environment—objects, agents, physics, and semantics—without executing the action in the real world.

The concept traces to model-based reinforcement learning and video prediction (e.g., Dreamer, GAIA-1). After OpenAI's **Sora** (2024) demonstrated that diffusion transformers can generate coherent spatiotemporal scenes, industry focus shifted from "generate pretty video" to **generate actionable futures** for planning and control.

**Key terms explained:**

| Term | Meaning |
|------|---------|
| **World Model** | A learned model of environment dynamics: \(s_{t+1} = f(s_t, a_t)\) or latent equivalents |
| **Latent dynamics** | Predictions in compressed representation space rather than raw pixels |
| **Imagination rollouts** | Monte Carlo or gradient-based planning by simulating many futures in the model |
| **Tokenization** | Discretizing video/state into tokens (e.g., Cosmos-Tokenizer) for transformer training |

**中文**

2025 年初，**世界模型（World Model）** 从学术概念跃升为 **机器人**、**自动驾驶（AV）** 与 **具身智能** 的工程主线。世界模型是一种「内部模拟器」：给定当前观测与候选动作，它在不真正执行动作的前提下，预测环境的 **未来状态**——物体、智能体、物理规律与语义关系。

该概念源于基于模型的强化学习与视频预测（Dreamer、GAIA-1 等）。OpenAI **Sora**（2024）证明扩散 Transformer 能生成连贯的时空场景后，产业焦点从「生成好看视频」转向 **生成可用于规划与控制的未来**。

**关键词解释：**

| 术语 | 含义 |
|------|------|
| **世界模型** | 对环境动力学的学习：\(s_{t+1} = f(s_t, a_t)\) 或其潜空间形式 |
| **潜空间动力学** | 在压缩表示而非原始像素上预测未来 |
| **想象 rollout** | 在模型中模拟多条未来轨迹以做规划 |
| **Tokenizer** | 将视频/状态离散为 token（如 Cosmos-Tokenizer），供 Transformer 训练 |

2025 年 1 月，NVIDIA 发布 **Cosmos** 世界基础模型系列，Google DeepMind 强化 Genie 2 交互式世界，Waymo 与 Tesla 在公开演讲中均将「预测 + 规划」列为 L4 核心路径。世界模型与 2024 年的 Sora 形成承接：从 **生成** 到 **仿真与决策**。

**Why 2025, not earlier?** Three conditions aligned: (1) **petabyte-scale driving video** from commercial fleets became legally usable for training; (2) **diffusion transformers** stabilized long clips beyond 5 seconds; (3) **differentiable simulators** (Genesis, Isaac) could export trajectories that match neural predictions for finetuning. Without any one pillar, world models remained academic curiosities.

**与预测模块的区别：** 传统 AV **prediction** 只 forecast 其他 agent 轨迹；世界模型 additionally 建模 **ego 动作后果** 与 **传感器观测演化**，可反向用于 **数据增强** 与 ** counterfactual 测试**（「若晚 0.5 秒刹车会怎样」）。

**中文补充：** 对机器人而言，世界模型缓解 **稀疏奖励**——在想象中完成 thousands of grasp attempts 再选最优，比纯 RL 摸黑探索 sample-efficient 一个数量级。2025 产业报告普遍将 world model 与 **VLA（Vision-Language-Action）** 并列为具身智能双核。

---

## 二、架构 | Architecture

**English**

Typical 2025 world-model stacks share a **perception → tokenization → dynamics → planner** pipeline:

```
Sensors (camera / LiDAR / proprioception)
        ↓
Encoder (ViT, BEV, or multimodal fusion)
        ↓
Tokenizer / Latent compressor (Cosmos-Tokenizer, VQ-VAE)
        ↓
Dynamics model (DiT, autoregressive, or JEPA-style)
        ↓
Action-conditioned rollouts → cost / reward → MPC or policy
        ↓
Low-level controller (trajectory, joint torques)
```

**Architectural variants:**

1. **Video-centric (Sora lineage):** Diffusion Transformer predicts pixel or token sequences; actions injected via cross-attention or conditioning tokens. Strong for data-rich AV fleets; heavy compute at inference.

2. **Latent JEPA / predictive coding:** Predict in representation space (I-JEPA, V-JEPA 2); lighter inference, better for real-time robotics.

3. **Physics-augmented simulators:** Hybrid of neural dynamics + differentiable physics (Genesis engine) for contact-rich manipulation.

4. **Multi-scale hierarchy:** High-level semantic world model (objects, relations) + low-level motion model (flows, occupancy).

**中文**

2025 年世界模型栈普遍遵循 **感知 → Token 化 → 动力学 → 规划器** 流水线：

```
传感器（相机 / 激光雷达 / 本体感知）
        ↓
编码器（ViT、BEV 或多模态融合）
        ↓
Tokenizer / 潜空间压缩（Cosmos-Tokenizer、VQ-VAE）
        ↓
动力学模型（DiT、自回归或 JEPA 风格）
        ↓
动作条件 rollout → 代价 / 奖励 → MPC 或策略网络
        ↓
底层控制器（轨迹、关节力矩）
```

**架构变体：**

1. **视频中心（Sora 谱系）：** 扩散 Transformer 预测像素或 token 序列；动作经 cross-attention 或条件 token 注入。适合数据丰富的 AV 车队；推理算力高。

2. **潜空间 JEPA / 预测编码：** 在表示空间预测（I-JEPA、V-JEPA 2）；推理更轻，适合实时机器人。

3. **物理增强仿真：** 神经动力学 + 可微物理（Genesis）混合，适合接触丰富的操作任务。

4. **多尺度层次：** 高层语义世界模型（物体、关系）+ 低层运动模型（光流、占据栅格）。

**Cosmos-Tokenizer** 将连续视频压缩为离散 token，使世界模型训练与 LLM 预训练范式对齐；**Genesis** 提供 GPU 加速的可微物理仿真，作为世界模型的「硬约束层」或数据引擎。

---

## 三、趋势 | Trends

**English**

| Trend | Description |
|-------|-------------|
| **From generative video to closed-loop planning** | Models trained not only on passive video but on **action-labeled** trajectories (steering, gripper commands) |
| **Foundation world models** | Pretrain on internet-scale video + sim data; finetune per robot or AV domain |
| **Long-horizon consistency** | 10–60 second coherent rollouts for highway merge and warehouse navigation |
| **Safety via ensemble imagination** | Multiple sampled futures; risk = disagreement or collision probability across rollouts |
| **Edge distillation** | Compress world models to run on vehicle NPUs alongside perception stacks |

**中文**

| 趋势 | 说明 |
|------|------|
| **从生成视频到闭环规划** | 不仅用被动视频训练， increasingly 使用 **带动作标签** 的轨迹（方向盘、夹爪指令） |
| **基础世界模型** | 互联网级视频 + 仿真数据预训练，再按机器人 / AV 领域微调 |
| **长时域一致性** | 10–60 秒连贯 rollout，支撑高速汇入、仓储导航 |
| **想象集成保安全** | 采样多条未来；风险 = rollout 间分歧或碰撞概率 |
| **端侧蒸馏** | 压缩世界模型，与感知栈一起在车载 NPU 上运行 |

2025 年 Q1，产业共识是：纯 **端到端驾驶** 与纯 **模块化栈** 正在融合——世界模型充当 **可学习的中间仿真层**，既保留数据驱动灵活性，又提供可解释的「如果这样做会发生什么」。

---

## 四、优缺点 | Pros/Cons

**English**

**Pros**

- **Sample-efficient planning:** Explore millions of futures in GPU memory before one real-world move
- **Unified representation:** Same model for prediction, anomaly detection, and synthetic data generation
- **Transfer from video pretraining:** Leverage Sora-class models and web video for priors on physics and scenes
- **Interpretability (relative):** Visualized rollouts help engineers debug failure modes

**Cons**

- **Compounding error:** Long rollouts drift; small prediction errors accumulate into unsafe plans
- **Sim-to-real gap:** Learned dynamics may fail on rare objects, weather, or contact physics
- **Compute cost:** Full diffusion rollouts are too slow for 10 Hz control without distillation
- **Evaluation difficulty:** No single metric captures "world understanding"; benchmarks still immature

**中文**

**优点**

- **样本高效规划：** 在 GPU 记忆中探索百万条未来，再执行一次真实动作
- **统一表示：** 同一模型可用于预测、异常检测与合成数据生成
- **视频预训练迁移：** 利用 Sora 级模型与网络视频获得物理与场景先验
- **相对可解释：** 可视化 rollout 便于工程师调试失效模式

**缺点**

- **误差累积：** 长 rollout 漂移；小预测误差叠加为不安全规划
- **仿真到真实鸿沟：** 罕见物体、天气、接触物理上动力学可能失效
- **算力成本：** 完整扩散 rollout 难以支撑 10 Hz 控制，需蒸馏
- **评估困难：** 尚无单一指标衡量「世界理解」；基准仍不成熟

---

## 五、应用场景 | Use Cases

**English**

| Domain | Use case | World model role |
|--------|----------|------------------|
| **Highway AV** | Lane change, merge | Predict surrounding vehicle reactions; score trajectories |
| **Urban robotaxi** | Jaywalker, construction zones | Semantic future occupancy; conservative planning |
| **Warehouse AMR** | Forklift + human coexistence | Short-horizon interaction prediction |
| **Manipulation** | Pick-place in clutter | Imagine object motion after push or grasp |
| **Humanoid** | Locomotion on uneven terrain | Contact-rich rollout in Genesis-class sim |
| **Training data** | Rare event synthesis | Generate corner-case video for perception finetuning |

**中文**

| 领域 | 场景 | 世界模型作用 |
|------|------|--------------|
| **高速 AV** | 变道、汇入 | 预测周围车辆反应；轨迹打分 |
| **城市 Robotaxi** | 行人横穿、施工区 | 语义未来占据；保守规划 |
| **仓储 AMR** | 叉车与人共存 | 短 horizon 交互预测 |
| **操作臂** |  clutter 中取放 | 想象推/抓后物体运动 |
| **人形机器人** |  uneven 地形行走 | Genesis 类仿真中接触丰富 rollout |
| **训练数据** | 罕见事件合成 | 生成 corner case 视频供感知微调 |

---

## 六、GitHub 开源生态 | GitHub

**English**

| Repository | Relevance |
|------------|-----------|
| [openai/sora](https://github.com/openai/sora) | Reference architecture for spatiotemporal diffusion; inspires world-model tokenization and scaling laws |
| [NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) | Efficient video tokenization for world foundation model pretraining |
| [genesis-embodied-ai/Genesis](https://github.com/genesis-embodied-ai/Genesis) | Universal physics engine for embodied AI; pairs with learned world models for sim2real |

**中文**

| 仓库 | 关联 |
|------|------|
| [openai/sora](https://github.com/openai/sora) | 时空扩散参考架构；影响世界模型 token 化与缩放定律 |
| [NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) | 高效视频 Token 化，支撑世界基础模型预训练 |
| [genesis-embodied-ai/Genesis](https://github.com/genesis-embodied-ai/Genesis) | 具身 AI 通用物理引擎；与学习型世界模型配合做 sim2real |

---

## 七、参考资料 | References

**English**

1. OpenAI — Sora: Video generation models as world simulators (2024–2025 technical reports)
2. NVIDIA — Cosmos World Foundation Models announcement (CES 2025)
3. LeCun et al. — A path towards autonomous machine intelligence (JEPA framework)
4. Ha & Schmidhuber — World Models (original RL formulation)
5. Waymo Research — Scene Flow and prediction stack updates (2025)

**中文**

1. OpenAI — Sora：作为世界模拟器的视频生成模型（2024–2025 技术报告）
2. NVIDIA — Cosmos 世界基础模型发布（CES 2025）
3. LeCun 等 — 通向自主机器智能之路（JEPA 框架）
4. Ha & Schmidhuber — World Models（原始 RL 表述）
5. Waymo Research — 场景流与预测栈更新（2025）

---

## 八、工程落地清单 | Engineering Checklist

**English**

Before deploying a world model in production AV or robotics (2025 vendor checklists):

1. **Horizon budget:** Define prediction seconds vs. control frequency; match model output rate to planner needs (often 2–10 Hz semantic, 50 Hz low-level).
2. **Uncertainty calibration:** Ensemble or dropout-based epistemic estimates; block actions when variance exceeds threshold.
3. **Real-world anchoring:** Periodic sync with live perception—prevent imagination drift over multi-step plans.
4. **Regression corpus:** Store failed rollouts from field incidents; retrain on counterfactual labels.
5. **Compute partition:** Train on GPU cluster; distill to TensorRT / NPU for onboard short-horizon module.

**中文**

生产 AV 或机器人部署世界模型前（2025 厂商清单）：

1. **Horizon 预算：** 明确预测秒数 vs 控制频率；模型输出率匹配规划器（常 2–10 Hz 语义、50 Hz 底层）。
2. **不确定性校准：** 集成或 dropout 认知不确定性；超阈则 block 动作。
3. **真实锚定：** 定期与 live 感知 sync——防多步规划想象漂移。
4. **回归语料：** 存储现场事故失败 rollout；用 counterfactual 标签再训。
5. **算力分区：** 集群训练；蒸馏至 TensorRT/NPU 作 onboard 短 horizon 模块。

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

**总结 | Summary**

**中文：** 2025 年的世界模型是连接 **AIGC 视频能力** 与 **物理世界决策** 的桥梁。其工程价值在于「在想象中试错」；落地瓶颈仍是长 horizon 精度、实时推理与可验证安全。与 Sora、Cosmos、Genesis 的开源与半开源生态共同构成本年度机器人 / AV 算法主线。

**English:** In 2025, world models bridge **generative video** and **physical decision-making**. Their engineering value is trial-and-error in imagination; deployment bottlenecks remain long-horizon accuracy, real-time inference, and verifiable safety. Together with Sora, Cosmos, and Genesis ecosystems, they define the year's robotics and AV algorithm stack.
