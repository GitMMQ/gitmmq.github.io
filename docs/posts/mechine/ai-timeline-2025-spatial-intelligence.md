---
title: "AI 技术编年史 2025：空间智能 Spatial Intelligence — 李飞飞的新前沿"
date: 2025-02-10 10:00:00
categories:
  - mechine
tags:
  - AI Timeline
  - Spatial Intelligence
  - 空间智能
  - 李飞飞
  - 3D
description: "2025 年 2 月，李飞飞提出空间智能是 AI 下一 frontier：理解、生成与推理 3D 世界。中英文对照解析架构、趋势与落地场景。"
---

# 空间智能 Spatial Intelligence：李飞飞提出的 AI 新前沿 | Spatial Intelligence: Fei-Fei Li's New AI Frontier

> **English Title:** AI Technology Timeline 2025 — Spatial Intelligence

---

## 一、背景 | Background

**English**

In February 2025, **Fei-Fei Li** articulated **Spatial Intelligence** as the next major capability beyond language-centric LLMs. While large language models excel at symbols and text, humans and robots operate in **3D space**—understanding geometry, depth, affordances, occlusion, and physical interaction. Spatial intelligence means an AI system can **perceive**, **reason about**, and **act within** structured 3D environments, not merely describe them in words.

Li's World Labs (founded 2024) and Stanford HAI research positioned spatial AI as complementary to **world models**: language gives abstraction; space gives grounding. The 2025 narrative connected spatial intelligence to AR/VR, robotics, autonomous systems, and scientific visualization—any domain where "where" matters as much as "what."

**Key terms:**

| Term | Definition |
|------|------------|
| **Spatial Intelligence** | Ability to infer 3D structure, relations, and dynamics from 2D or 3D inputs |
| **Affordance** | What actions an object or surface enables (graspable, walkable, pushable) |
| **NeRF / 3DGS** | Neural representations reconstructing or rendering 3D scenes from images |
| **Embodied grounding** | Linking linguistic concepts to physical coordinates and trajectories |

**中文**

2025 年 2 月，**李飞飞** 将 **空间智能（Spatial Intelligence）** 定义为超越语言中心 LLM 的下一能力 frontier。大语言模型擅长符号与文本，而人类与机器人在 **三维空间** 中行动——理解几何、深度、 affordance、遮挡与物理交互。空间智能指 AI 能 **感知、推理并在** 结构化 3D 环境中 **行动**，而非仅用文字描述。

Li 创立的 World Labs（2024）与斯坦福 HAI 研究将空间 AI 与 **世界模型** 互补：语言提供抽象，空间提供接地。2025 叙事将空间智能关联到 AR/VR、机器人、自动驾驶与科学可视化——凡「在哪里」与「是什么」同等重要的领域。

**关键词：**

| 术语 | 定义 |
|------|------|
| **空间智能** | 从 2D/3D 输入推断 3D 结构、关系与动力学 |
| **Affordance** | 物体或表面支持的动作（可抓、可走、可推） |
| **NeRF / 3DGS** | 从图像重建或渲染 3D 场景的神经表示 |
| **具身接地** | 将语言概念链接到物理坐标与轨迹 |

**Historical arc:** Computer vision progressed from **2D classification** (ImageNet) → **detection/segmentation** → **NeRF/3DGS reconstruction** → **2025 spatial reasoning** where models answer relational questions (behind, inside, reachable). Language-only LLMs hit a ceiling on robotics benchmarks until depth-aware encoders became standard in VLMs.

**Metric scale 为何 critical：** 没有米制尺度，AR overlay 会「飘」；机器人抓取误差 >2 cm 即失败。2025 产品强调 **SLAM + learned depth + IMU** 融合，误差 <1% 场景深度作为商用门槛。

**中文补充：** 空间智能与 **数字孪生** 天然耦合——工厂、城市、手术室先有三维模型，再叠 AI 推理。中国「空间计算」产业政策与 2025 空间智能叙事相互强化，推动 3D 采集设备成本继续下探。

---

## 二、架构 | Architecture

**English**

2025 spatial-intelligence systems typically combine **reconstruction**, **understanding**, and **generation**:

```
Multi-view images / video / depth / SLAM
              ↓
   3D representation (NeRF, 3D Gaussian Splatting, mesh)
              ↓
   Scene graph + affordance map + semantic voxels
              ↓
   Spatial reasoning module (VLM fine-tuned on 3D QA)
              ↓
   Action: navigation mesh, grasp pose, AR overlay, sim export
```

**Components explained:**

- **3D Gaussian Splatting (3DGS):** Real-time radiance fields; 2025 stacks use 3DGS as interchange format between capture devices and AI models.
- **Spatial VLM:** Vision-language models augmented with depth tokens, point cloud encoders, or BEV features; answer questions like "Can the robot reach the mug behind the laptop?"
- **Generative spatial models:** Text/image → editable 3D scenes (World Labs, Luma, Meta research)—analogous to Sora but output is navigable space.
- **Calibration layer:** Camera intrinsics/extrinsics and metric scale so spatial predictions are not merely pretty but **measurable**.

**中文**

2025 空间智能系统通常组合 **重建、理解与生成**：

```
多视角图像 / 视频 / 深度 / SLAM
              ↓
   3D 表示（NeRF、3D Gaussian Splatting、网格）
              ↓
   场景图 + affordance 图 + 语义体素
              ↓
   空间推理模块（3D QA 微调的 VLM）
              ↓
   动作：导航网格、抓取位姿、AR 叠加、仿真导出
```

**组件说明：**

- **3D Gaussian Splatting：** 实时辐射场；2025 栈以 3DGS 作为采集设备与 AI 模型间的交换格式。
- **空间 VLM：** 视觉语言模型叠加深度 token、点云编码器或 BEV 特征；回答「机器人能否够到笔记本后的杯子？」
- **生成式空间模型：** 文本/图像 → 可编辑 3D 场景——类似 Sora 但输出可导航空间。
- **标定层：** 相机内外参与 metric scale，使空间预测 **可测量** 而非仅美观。

---

## 三、趋势 | Trends

**English**

| Trend | Detail |
|-------|--------|
| **Spatial foundation models** | Pretrain on indoor scans, street views, sim worlds; unified encoder for robotics + AR |
| **Language ↔ space bidirection** | LLM plans in words; spatial module grounds to coordinates; feedback updates language state |
| **Single-image to 3D at production quality** | Feeds e-commerce, game assets, digital twins |
| **Spatial agents** | Agents that navigate simulators (Genesis) using spatial maps, not just text tools |
| **Privacy-preserving spatial capture** | On-device 3D reconstruction for home robots without cloud upload |

**中文**

| 趋势 | 详情 |
|------|------|
| **空间基础模型** | 室内扫描、街景、仿真世界预训练；机器人 + AR 统一编码器 |
| **语言 ↔ 空间双向** | LLM 文字规划；空间模块接地坐标；反馈更新语言状态 |
| **单图到 3D 量产质量** | 服务电商、游戏资产、数字孪生 |
| **空间 Agent** | 在仿真器（Genesis）中基于空间地图导航，而非仅文本工具 |
| **隐私友好空间采集** | 端侧 3D 重建，家庭机器人无需上传云端 |

李飞飞 2025 年公开演讲强调：**空间智能不是 3D 版本的 ChatGPT**，而是让 AI 具备「在世界里思考」的几何与物理直觉——这与同年 world model、具身智能浪潮同频。

---

## 四、优缺点 | Pros/Cons

**English**

**Pros**

- Grounds LLM hallucinations in metric space; reduces impossible robot commands
- Enables shared world representation across human UI, sim, and real robot
- Unlocks AR copilots that understand room layout and object permanence
- Composable with NeRF/3DGS ecosystems already deployed in mapping products

**Cons**

- 3D data scarcity vs. text; labeling and capture remain expensive
- Scale ambiguity from monocular input persists without depth sensors
- Real-time full-scene understanding still GPU-heavy on edge devices
- Standard benchmarks (ScanNet, nuScenes) do not capture open-world spatial reasoning

**中文**

**优点**

- 将 LLM 幻觉接地到 metric 空间；减少不可能执行的机器人指令
- 人机 UI、仿真与真机共享世界表示
- 解锁理解房间布局与物体恒常性的 AR  copilot
- 可与已用于测绘产品的 NeRF/3DGS 生态组合

**缺点**

- 相对文本，3D 数据稀缺；标注与采集仍贵
- 单目输入尺度歧义仍在，需深度传感器
- 端侧全场景实时理解仍耗 GPU
- 标准基准（ScanNet、nuScenes）未覆盖开放世界空间推理

---

## 五、应用场景 | Use Cases

**English**

| Scenario | Spatial intelligence role |
|----------|---------------------------|
| **Home robotics** | Room map, object locations, "put away" tasks with occlusion reasoning |
| **Surgical / medical AR** | Register instruments to patient anatomy in 3D |
| **Construction digital twin** | Progress monitoring from site photos → BIM alignment |
| **Autonomous delivery** | Sidewalk geometry, curb cuts, elevator button localization |
| **Education** | Interactive 3D explanations of molecules, astronomy, history sites |
| **Game / metaverse** | Prompt-to-playable level with consistent physics |

**中文**

| 场景 | 空间智能作用 |
|------|--------------|
| **家庭机器人** | 房间地图、物体位置、考虑遮挡的收纳任务 |
| **手术 / 医疗 AR** | 器械与患者解剖 3D 配准 |
| **施工数字孪生** | 工地照片 → BIM 对齐的进度监测 |
| **自动配送** | 人行道几何、缘石坡道、电梯按钮定位 |
| **教育** | 分子、天文、遗址的交互 3D 讲解 |
| **游戏 / 元宇宙** | 提示词 → 物理一致的可玩关卡 |

---

## 六、GitHub 开源生态 | GitHub

**English**

| Repo | Role |
|------|------|
| [genesis-embodied-ai/Genesis](https://github.com/genesis-embodied-ai/Genesis) | Physics-accurate sim environments for spatial agent training and validation |
| [openai/sora](https://github.com/openai/sora) | Spatiotemporal generation informs spatial scene synthesis research |
| [NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) | Tokenizes spatial-temporal data for foundation model pipelines |

**中文**

| 仓库 | 作用 |
|------|------|
| [genesis-embodied-ai/Genesis](https://github.com/genesis-embodied-ai/Genesis) | 物理精确仿真环境，训练与验证空间 Agent |
| [openai/sora](https://github.com/openai/sora) | 时空生成研究影响空间场景合成 |
| [NVIDIA/Cosmos-Tokenizer](https://github.com/NVIDIA/Cosmos-Tokenizer) | 空间时序数据 Token 化，接入基础模型流水线 |

---

## 七、参考资料 | References

1. Fei-Fei Li — Talks and essays on spatial intelligence (World Labs, 2024–2025)
2. World Labs — Large world models product direction
3. Kerbl et al. — 3D Gaussian Splatting for Real-Time Radiance Field Rendering
4. Chen et al. — SpatialVLM / 3D-LLM benchmark papers
5. Meta AI — SceneScript and spatial understanding research

---

## 八、评估基准 | Benchmarks and Metrics

**English**

2025 spatial AI teams track:

| Benchmark | Measures |
|-----------|----------|
| **Spatial VQA** | Relational QA on ScanNet / 3RScan |
| **Embodied navigation SPL** | Success weighted by path length in sim |
| **Grasp success @5mm** | Real robot repeatability with spatial map |
| **3D reconstruction PSNR/SSIM** | NeRF/3DGS quality vs. laser ground truth |
| **Latency** | Full-scene refresh rate on AR glasses SoC |

**中文**

2025 空间 AI 团队跟踪：

| 基准 | 度量 |
|------|------|
| **Spatial VQA** | ScanNet / 3RScan 关系问答 |
| **具身导航 SPL** | 仿真中路径长度加权成功率 |
| **抓取成功 @5mm** | 真机重复性 |
| **重建 PSNR/SSIM** | NeRF/3DGS vs 激光真值 |
| **延迟** | AR 眼镜 SoC 全场景刷新率 |

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

**中文：** 2025 年 2 月，空间智能标志 AI 从「会说话」走向「会在世界里想」。它与世界模型、具身机器人形成三角：预测未来、理解空间、执行动作。落地关键在 metric 精度、实时性与跨模态对齐。

**English:** February 2025 positioned spatial intelligence as AI moving from eloquence to reasoning in the world—forming a triangle with world models and embodied robots: predict, understand space, act. Deployment hinges on metric accuracy, real-time performance, and cross-modal alignment.
