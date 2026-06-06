---
title: "AI 技术编年史 2024：具身智能与人形机器人"
date: 2024-04-05 10:00:00
categories:
  - "mechine"
tags:
  - "AI Timeline"
  - "Embodied AI"
  - "Humanoid Robot"
  - "VLA"
  - "Robotics"
description: "2024 年具身智能与人形机器人商业化加速：VLA 模型、Figure、Optimus、宇树与智元的中英文产业解读。"
---

# 具身智能与人形机器人 | Embodied AI and Humanoid Robots

---

## 一、背景与核心概念 | Background and Core Concepts

**English**

**Embodied AI** refers to intelligence grounded in physical interaction — robots, vehicles, and devices that perceive, act, and learn in the real world. In 2024, **humanoid robots** became the public face of embodied AI, driven by advances in **Vision-Language-Action (VLA)** models, sim-to-real transfer, and LLM-based task planning.

Key concepts:

- **VLA models**: unified models mapping camera input + language instructions → motor actions (e.g., RT-2, OpenVLA)
- **Teleoperation + imitation learning**: human demos bootstrap policy learning
- **Sim-to-real**: Isaac Sim, MuJoCo, and domain randomization bridge simulation gaps
- **Foundation models for robotics**: LLMs decompose "clean the kitchen" into sub-skills

2024 milestones included **Figure 01 + OpenAI**, **Tesla Optimus** factory trials, **Unitree H1/G1** price drops, and **Agibot (智元)** mass-production announcements in China.

**中文**

**具身智能**指扎根于物理交互的智能——机器人、车辆、设备在真实世界中感知、行动与学习。2024 年**人形机器人**成为具身智能公众符号，驱动力来自 **VLA（视觉-语言-动作）** 模型、Sim-to-Real 与 LLM 任务规划。

核心概念：VLA 统一模型（RT-2、OpenVLA）；遥操作 + 模仿学习；Isaac Sim 等仿真迁移；LLM 将高层指令分解为子技能。

2024 里程碑：Figure 01 接入 OpenAI、Tesla Optimus 进工厂、宇树 H1/G1 降价、智元量产发布等。

| 术语 | 含义 |
|---|---|
| End-effector | 末端执行器（手、夹爪） |
| Biped locomotion | 双足行走平衡控制 |
| Dexterous manipulation | 灵巧手精细操作 |
| Embodied cognition | 认知依赖身体与环境的理论 |

### 1.1 从深度学习到 VLA | From Deep Learning to VLA

**English**

Classical robotics used modular stacks (SLAM → planning → control) with hand-tuned parameters. 2024's VLA models **unify perception and action in one network**, pretrained on internet-scale vision-language data then fine-tuned on robot trajectories. Google DeepMind's **RT-2** showed transferring web knowledge ("pick up the extinct animal" → dinosaur toy) — a capability impossible with narrow imitation-only policies.

Humanoid form factor returned not from engineering necessity but **environment fit**: warehouses and homes built for bipedal humans; dual arms enable tool use. Tesla, Figure, and Chinese vendors bet humanoids over wheeled arms for **general-purpose** branding.

**中文**

经典机器人用模块化栈（SLAM→规划→控制）与手工调参。2024 VLA 在**单网统一感知与动作**，先 Web 规模 VLM 预训练再机器人轨迹微调。Google **RT-2** 展示 Web 知识迁移（「捡起灭绝动物」→恐龙玩具）——窄模仿策略无法实现。人形回归非工程必然，而是**环境适配**：人机共存空间为双足设计；双臂支持工具。特斯拉、Figure 与中国厂商押注人形而非轮式臂，求**通用**品牌叙事。

---

## 二、架构设计 | Architecture

**English**

A modern humanoid stack layers perception, cognition, and control:

```
Sensors (RGB-D, IMU, Force/Torque, Proprioception)
    ↓
Perception Module (detection, segmentation, SLAM)
    ↓
High-level Planner (LLM / VLM task decomposition)
    ↓
Mid-level Policy (VLA / diffusion policy / RL)
    ↓
Low-level Controller (whole-body MPC, PID, impedance)
    ↓
Actuators (harmonic drives, linear actuators, dexterous hands)
```

**Training loop**: collect teleop data → train policy in sim → fine-tune on real robot → continuous learning from failures.

**中文**

现代人形栈分层：传感器 → 感知 → 高层规划（LLM/VLM）→ 中层策略（VLA/扩散策略/RL）→ 底层控制（MPC、阻抗）→ 执行器。训练闭环：遥操作采集 → 仿真预训练 → 真机微调 → 失败持续学习。

### 2.1 VLA 模型架构 | VLA Model Architecture

| 组件 | 功能 |
|---|---|
| Vision Encoder | ViT / SigLIP 处理多帧图像 |
| Language Encoder | 指令语义理解 |
| Action Head | 输出关节角、末端位姿或 action tokens |
| History Buffer | 短时序上下文 |

**RT-2 范式**：将机器人动作离散化为 token，与 Web 规模 VLM 联合 co-fine-tune，实现 zero-shot 泛化到新物体。

### 2.2 2024 代表性平台 | 2024 Representative Platforms

| 平台 | 亮点 |
|---|---|
| Figure 01 | OpenAI 多模态模型驱动对话 + 操作 |
| Tesla Optimus | 工厂内搬运试点，FSD 团队 overlap |
| Unitree G1 | 约 9.9 万元级定价，开发者友好 |
| 智元 Agibot | 中国量产叙事，远征 A1/A2 |
| 1X NEO | 家用场景，软体安全设计 |

**English**: None achieved **millions of units shipped** in 2024 — all remained pilot / demo / early order phase. The year was about **proof of learning curves**, not mass replacement of factory workers.

**中文**：2024 **无一实现百万台出货**——均为试点/演示/早期订单。当年重在**学习曲线证明**，非大规模替代产线工人。

---

## 三、产业趋势 | Industry Trends

**English**

2024 embodied AI trends:

1. **Humanoid hype cycle** — billions in funding (Figure, 1X, Sanctuary, Chinese startups)
2. **LLM as robot brain** — natural language tasking replaces rigid state machines
3. **Cost reduction** — Unitree G1 under $16k signaled consumer-adjacent pricing
4. **Manufacturing pilots** — BMW, Tesla test humanoids for repetitive tasks
5. **Data scarcity** — robot data orders of magnitude smaller than web text; synthetic data rising
6. **Safety regulation** — EU AI Act and workplace safety standards emerging

**中文**

2024 趋势：人形机器人融资热潮；LLM 作"机器人大脑"；宇树 G1 低价信号；宝马、特斯拉工厂试点；机器人数据稀缺推动合成数据；欧盟 AI 法案与安全标准酝酿。

---

## 四、优缺点分析 | Pros and Cons

### 4.1 优点 | Advantages

1. **通用形态** — 人形适配人类环境 / Human-shaped for human environments
2. **多模态融合** — VLA 统一感知-语言-动作 / Unified VLA pipelines
3. **LLM 规划** — 自然语言任务接口 / Natural language tasking
4. **仿真加速** — 降低真机试错成本 / Sim reduces real-world trial cost
5. **劳动力补充** — 危险/重复岗位自动化 / Automation for dull/dangerous jobs
6. **研究汇聚** — CV + NLP + 控制交叉创新 / Cross-disciplinary innovation

### 4.2 缺点 | Disadvantages

1. **可靠性不足** — 2024 真机仍易失败 / Fragile real-world performance
2. **成本与维护** — 硬件、维修、能耗高 / High TCO
3. **数据瓶颈** — 缺乏 Web 级机器人数据 / Robot data scarcity
4. **安全风险** — 物理伤害与 liability / Physical safety concerns
5. **泛化有限** — 新环境迁移仍难 / Poor out-of-distribution generalization
6. **炒作 vs 现实** — 演示与量产差距大 / Demo-to-production gap

---

## 五、典型应用场景 | Use Cases

| 场景 Scenario | 中文说明 | English Description |
|---|---|---|
| 工厂搬运 | 产线物料、货架拣选 | Material handling on factory floors |
| 物流仓储 | 与 AGV 协同的灵巧操作 | Warehouse picking with mobility |
| 家庭服务 | 整理、简单清洁（早期试点） | Home tidying and assistive tasks |
| 养老护理 | 辅助起身、物品递送 | Elder care assistance |
| 灾难救援 | 危险环境侦察与操作 | Hazardous environment operations |
| 科研平台 | 算法验证与数据采集 | Research testbeds for VLA |

---

## 六、GitHub 与开源生态 | GitHub and Open Source

**English**

Open robotics ecosystem in 2024:

- **openvla/openvla**: open VLA model weights and training code
- **google-deepmind/open_x_embodiment**: large-scale multi-robot dataset
- **facebookresearch/habitat**: embodied AI simulation
- **unitreerobotics**: Unitree SDK and sim tools
- **ros2**: Robot Operating System middleware

**中文**

开源生态：OpenVLA 模型、Open X-Embodiment 数据集、Habitat 仿真、宇树 SDK、ROS 2 中间件。

| 仓库 | 说明 |
|---|---|
| [openvla/openvla](https://github.com/openvla/openvla) | 开源 VLA 模型 |
| [google-deepmind/open_x_embodiment](https://github.com/google-deepmind/open_x_embodiment) | 跨本体机器人数据 |
| [facebookresearch/habitat-lab](https://github.com/facebookresearch/habitat-lab) | 具身 AI 仿真 |
| [ros2/ros2](https://github.com/ros2/ros2) | 机器人操作系统 |

---

## 七、参考链接 | References

- RT-2: Vision-Language-Action Models (Google DeepMind)
- OpenVLA 论文与模型卡
- Figure AI + OpenAI 合作公告
- Tesla Optimus 2024 进展更新
- 宇树 H1/G1 产品页：[unitree.com](https://www.unitree.com/)
- Isaac Sim 文档：[developer.nvidia.com/isaac/sim](https://developer.nvidia.com/isaac/sim)

---

## 八、2025 展望 | Outlook for 2025

**English**

2025–2026 roadmaps point to **VLA models in consumer robots** (sub-$20k humanoids), **simulation-generated data exceeding human teleop**, and **LLM planners with verifiable skill libraries**. Regulatory frameworks for workplace humanoids (EU Machinery Regulation updates) will clarify liability. Investment may consolidate after 2024 hype — survivors combine **hardware margin + software subscription** (RaaS). Technical moat shifts from walking demos to **reliability metrics**: MTBF, success rate on 1000-task benchmarks, OTA improvement velocity.

**中文**

2025–2026 路线：**VLA 进消费级机器人**（2 万美元以下人形）、**仿真数据超 human teleop**、**LLM 规划+可验证技能库**。 workplace 人形法规（欧盟机械法规更新）将厘清责任。投资或在 2024  hype 后整合——幸存者靠**硬件毛利+软件订阅**（RaaS）。技术护城河从行走 demo 转向**可靠性指标**：MTBF、千任务成功率、OTA 改进速度。

---

**English Summary**: 2024 embodied AI moved from lab demos toward factory pilots — VLA models and LLM planners converged, but reliability and data remain the gating factors for commercial scale.

**中文总结**：2024 具身智能从实验室演示走向工厂试点——VLA 与 LLM 规划汇聚，可靠性与数据仍是规模化门槛。
