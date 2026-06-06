---
title: "2022 AI 编年史：扩散模型 Stable Diffusion 与 DALL·E 2"
date: 2022-01-20 10:00:00
categories:
  - "algrithom"
tags:
  - "AI Timeline"
  - "Diffusion Models"
  - "Stable Diffusion"
  - "DALL-E 2"
  - "AIGC"
description: "2022 年扩散模型爆发：从 DALL·E 2 到 Stable Diffusion 开源，详解 DDPM、潜空间扩散、Classifier-Free Guidance 等核心概念，中英文对照。"
---

# 2022 AI 编年史：扩散模型 Stable Diffusion 与 DALL·E 2 | AI Timeline 2022: Diffusion Models

---

## 一、背景与核心概念 | Background & Core Concepts

**English**

2022 was the year **text-to-image generation** moved from research curiosity to mainstream culture. Two systems defined the arc: **DALL·E 2** (OpenAI, April 2022) and **Stable Diffusion** (Stability AI / CompVis, August 2022). Both are built on **diffusion models** — a class of generative algorithms that learn to reverse a gradual noising process.

**Diffusion models** operate in two phases:

1. **Forward diffusion (noising)**: Starting from a real image \(x_0\), Gaussian noise is added step-by-step over \(T\) timesteps until the signal becomes pure noise.
2. **Reverse diffusion (denoising)**: A neural network \(\epsilon_\theta\) learns to predict and remove noise at each step, reconstructing an image from random noise.

The foundational paper **DDPM** (Denoising Diffusion Probabilistic Models, Ho et al., 2020) showed that this simple Markov chain could match GAN quality on image synthesis. **Score-based models** (Song et al.) provided an equivalent SDE/ODE formulation. By 2022, the key innovations were:

- **Latent Diffusion Models (LDM)**: Run diffusion in a compressed **latent space** (via a VAE encoder/decoder) rather than pixel space — dramatically reducing compute.
- **Cross-attention conditioning**: Inject text embeddings from a **CLIP** text encoder so the denoising network is **text-conditioned**.
- **Classifier-Free Guidance (CFG)**: Train the model both with and without conditioning, then at inference blend conditional and unconditional predictions to sharpen prompt adherence.

**DALL·E 2** uses a **unCLIP** architecture: a **prior** maps text → CLIP image embedding, a **decoder** maps embedding → image via diffusion. Access was API-only and invite-gated.

**Stable Diffusion** (SD 1.x) open-sourced the full pipeline: **VAE** + **U-Net denoiser** + **CLIP text encoder**, trained on LAION subsets. Running on consumer GPUs (~6–8 GB VRAM) made local AIGC feasible for millions of developers.

**中文**

2022 年是 **文生图（Text-to-Image）** 从实验室走向大众文化的关键一年。两大系统划定了技术轨迹：**DALL·E 2**（OpenAI，2022 年 4 月）与 **Stable Diffusion**（Stability AI / CompVis，2022 年 8 月）。二者均基于 **扩散模型（Diffusion Models）** —— 通过逆向「逐步加噪」过程学习生成图像。

**扩散模型** 分两阶段运作：

1. **前向扩散（加噪）**：从真实图像 \(x_0\) 出发，经 \(T\) 步逐步叠加高斯噪声，直至信号变为纯噪声。
2. **反向扩散（去噪）**：神经网络 \(\epsilon_\theta\) 学习预测并去除每步噪声，从随机噪声重建图像。

奠基论文 **DDPM**（Denoising Diffusion Probabilistic Models，Ho 等，2020）证明这一简单马尔可夫链可达 GAN 级图像合成质量。**Score-based models**（Song 等）给出了等价的 SDE/ODE 表述。到 2022 年，关键创新包括：

- **潜空间扩散（Latent Diffusion Models, LDM）**：在 VAE 编码器压缩的 **潜空间** 而非像素空间做扩散，大幅降低算力需求。
- **交叉注意力条件化（Cross-attention）**：将 **CLIP** 文本编码器输出的嵌入注入去噪网络，实现 **文本条件生成**。
- **无分类器引导（Classifier-Free Guidance, CFG）**：训练时同时使用/不使用条件，推理时混合条件与无条件预测，强化提示词遵从度。

**DALL·E 2** 采用 **unCLIP** 架构：**先验网络** 将文本映射为 CLIP 图像嵌入，**解码器** 通过扩散将嵌入还原为图像。仅以 API 形式提供，需邀请码。

**Stable Diffusion**（SD 1.x）开源完整流水线：**VAE** + **U-Net 去噪器** + **CLIP 文本编码器**，在 LAION 子集上训练。消费级 GPU（约 6–8 GB 显存）即可运行，使本地 AIGC 对数百万开发者成为现实。

---

## 二、架构设计 | Architecture

### 2.1 Stable Diffusion 流水线 | Stable Diffusion Pipeline

**English**

```
Text Prompt
    ↓
CLIP Text Encoder → text embeddings (77 tokens × 768-dim)
    ↓
Random noise z_T ∈ R^{64×64×4}  (latent space)
    ↓
U-Net Denoiser (iterative, T steps)
    ├── Self-attention (spatial)
    ├── Cross-attention (text ↔ latent)
    └── ResNet blocks + timestep embedding
    ↓
VAE Decoder → 512×512 RGB image
```

| Component | Role | Key Detail |
|---|---|---|
| **VAE** | Compress 512×512 → 64×64×4 latent | 8× spatial downsampling |
| **U-Net** | Predict noise ε at each timestep | ~860M params (SD 1.4/1.5) |
| **CLIP ViT-L/14** | Text → conditioning vector | Frozen during SD training |
| **Scheduler** | DDIM / PNDM / Euler steps | 20–50 steps for inference |
| **CFG scale** | Guidance strength (typically 7–12) | Higher = more literal to prompt |

**中文**

```
文本提示词
    ↓
CLIP 文本编码器 → 文本嵌入（77 token × 768 维）
    ↓
随机噪声 z_T ∈ R^{64×64×4}（潜空间）
    ↓
U-Net 去噪器（迭代 T 步）
    ├── 自注意力（空间）
    ├── 交叉注意力（文本 ↔ 潜变量）
    └── ResNet 块 + 时间步嵌入
    ↓
VAE 解码器 → 512×512 RGB 图像
```

### 2.2 DALL·E 2 vs Stable Diffusion | 架构对比

| 维度 Dimension | DALL·E 2 | Stable Diffusion |
|---|---|---|
| 架构 Architecture | unCLIP（prior + decoder） | LDM（VAE + U-Net） |
| 开源 Open source | ❌ API only | ✅ 权重 + 代码 |
| 训练数据 Training data | 未公开 Not disclosed | LAION-2B / LAION-5B 子集 |
| 分辨率 Resolution | Up to 1024×1024 | 512×512（1.x） |
| 本地部署 Local deploy | ❌ | ✅ 6 GB+ GPU |
| 商业许可 License | OpenAI ToS | CreativeML Open RAIL-M |

### 2.3 关键算法术语 | Key Algorithm Terms

| 术语 Term | 含义 Meaning |
|---|---|
| **DDPM** | 去噪扩散概率模型，定义前向/反向马尔可夫链 |
| **DDIM** | 确定性采样器，可用更少步数加速推理 |
| **Latent space** | VAE 压缩后的低维表示，扩散在此进行 |
| **Noise schedule** | 控制每步加噪量的 β 序列 |
| **Timestep embedding** | 将扩散步数 t 编码注入 U-Net |
| **Inpainting / img2img** | 以现有图像为条件的变体生成模式 |

---

## 三、2022 年技术趋势 | Trends in 2022

**English**

1. **Closed → Open**: DALL·E 2 proved quality; Stable Diffusion proved openness wins adoption. Within weeks, Hugging Face, Automatic1111, and ComfyUI built thriving ecosystems.
2. **DreamBooth & textual inversion**: Personalization techniques let users fine-tune on 3–5 photos to generate custom subjects — foreshadowing LoRA (April 2022 paper).
3. **ControlNet precursors**: Edge maps, depth, and pose as conditioning signals emerged in community forks before formal papers (2023).
4. **Safety & copyright debates**: LAION dataset provenance, deepfake risks, and artist opt-out movements shaped policy discussions globally.
5. **Resolution race**: SD 2.x (768px), Midjourney v4, and Imagen (Google, not fully released) pushed photorealism boundaries.

**中文**

1. **封闭 → 开放**：DALL·E 2 证明质量可行；Stable Diffusion 证明开放赢得采用率。数周内 Hugging Face、Automatic1111、ComfyUI 形成繁荣生态。
2. **DreamBooth 与文本反演**：用 3–5 张照片微调生成定制主体，预示 LoRA 微调范式（2022 年 4 月论文）。
3. **ControlNet 前奏**：社区分支率先以边缘图、深度图、姿态作为条件信号，正式论文见于 2023 年。
4. **安全与版权争议**：LAION 数据来源、深度伪造风险、艺术家退出运动引发全球政策讨论。
5. **分辨率竞赛**：SD 2.x（768px）、Midjourney v4、Imagen（Google，未完全公开）推动照片级真实感边界。

---

## 四、优缺点分析 | Pros and Cons

| 优点 Advantages | 缺点 Disadvantages |
|---|---|
| 照片级质量，复杂场景组合能力强 / Photorealistic quality, strong compositional ability | 手部、文字、对称结构易出错 / Hands, text, symmetry often fail |
| Stable Diffusion 开源可本地运行 / SD is open-source and locally runnable | 训练数据版权与偏见争议 / Training data copyright & bias concerns |
| 潜空间扩散大幅降低算力门槛 / Latent diffusion lowers compute barrier | 推理仍需多步迭代，延迟高于 GAN / Multi-step inference slower than GANs |
| 社区生态（LoRA、ControlNet、ComfyUI）极速扩张 / Rapid community ecosystem growth | 滥用风险：深度伪造、NSFW 内容 / Misuse: deepfakes, NSFW |
| 提示词工程降低创作门槛 / Prompt engineering democratizes creation | 难以精确控制细节布局 / Precise spatial control is hard without extra tools |
| 与 CLIP 语义空间对齐，文本理解好 / Good text understanding via CLIP alignment | 模型体积大（~4 GB 权重），端侧部署困难 / Large weights, hard on edge devices |

---

## 五、典型应用场景 | Use Cases

| 场景 Scenario | 中文说明 | English Description |
|---|---|---|
| 概念艺术与分镜 | 游戏/影视前期快速出视觉方案 | Rapid concept art and storyboarding for games/film |
| 营销素材生成 | 电商 Banner、社交媒体配图批量产出 | Batch marketing visuals for e-commerce and social |
| 建筑设计可视化 | 输入风格描述生成外立面草图 | Architectural facade sketches from style prompts |
| 时尚与产品设计 | 服装款式、配色方案探索 | Fashion and product design exploration |
| 教育插图 | 教科书、科普文章配图 | Educational illustrations for textbooks and science |
| 个人创作与同人 | 本地 SD + LoRA 实现风格化同人图 | Local SD + LoRA for fan art and personal styles |
| 数据增强 | 合成训练图像扩充 CV 数据集 | Synthetic images for computer vision data augmentation |

---

## 六、GitHub 开源项目 | GitHub Projects

| 项目 Project | 说明 Description | 链接 Link |
|---|---|---|
| **CompVis/stable-diffusion** | 原始 LDM 实现与 SD 1.x 权重发布仓库 | [github.com/CompVis/stable-diffusion](https://github.com/CompVis/stable-diffusion) |
| **huggingface/diffusers** | 模块化扩散模型库，统一 Pipeline API | [github.com/huggingface/diffusers](https://github.com/huggingface/diffusers) |
| **AUTOMATIC1111/stable-diffusion-webui** | 最流行的本地 Web UI，插件生态丰富 | [github.com/AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) |
| **comfyanonymous/ComfyUI** | 节点式可视化工作流编辑器 | [github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI) |

```bash
# 使用 Hugging Face Diffusers 快速生成
pip install diffusers transformers accelerate
python -c "
from diffusers import StableDiffusionPipeline
import torch
pipe = StableDiffusionPipeline.from_pretrained(
    'runwayml/stable-diffusion-v1-5', torch_dtype=torch.float16)
pipe = pipe.to('cuda')
image = pipe('a serene lake at sunset, oil painting').images[0]
image.save('output.png')
"
```

---

## 七、总结 | Summary

**中文**：2022 年扩散模型标志着 AIGC 图像生成的 **"iPhone 时刻"** —— DALL·E 2 验证了商业可行性，Stable Diffusion 以开源姿态将能力交到每个人手中。潜空间扩散、CLIP 条件化与 CFG 三大技术组合，奠定了此后 SDXL、ControlNet、视频扩散（2023–2024）的技术基座。

**English**: 2022 diffusion models marked the **"iPhone moment"** for AIGC image generation — DALL·E 2 proved commercial viability, Stable Diffusion democratized capability through open weights. Latent diffusion, CLIP conditioning, and CFG formed the foundation for SDXL, ControlNet, and video diffusion in subsequent years.

---

**参考链接 | References**

- DDPM 论文：[Denoising Diffusion Probabilistic Models (Ho et al., 2020)](https://arxiv.org/abs/2006.11239)
- Latent Diffusion 论文：[High-Resolution Image Synthesis with Latent Diffusion Models (Rombach et al., 2022)](https://arxiv.org/abs/2112.10752)
- DALL·E 2 论文：[Hierarchical Text-Conditional Image Generation (Ramesh et al., 2022)](https://arxiv.org/abs/2204.06125)
- Stable Diffusion 仓库：[github.com/CompVis/stable-diffusion](https://github.com/CompVis/stable-diffusion)
- Hugging Face Diffusers 文档：[huggingface.co/docs/diffusers](https://huggingface.co/docs/diffusers)
