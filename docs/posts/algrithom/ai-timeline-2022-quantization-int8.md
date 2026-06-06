---
title: "2022 AI 编年史：INT8 量化与稀疏推理"
date: 2022-06-08 10:00:00
categories:
  - "algrithom"
tags:
  - "AI Timeline"
  - "Quantization"
  - "INT8"
  - "Sparse Inference"
  - "Model Compression"
description: "2022 年 INT8 量化与稀疏推理技术成熟，详解 PTQ、QAT、剪枝与 TensorRT/ONNX 部署链路，中英文对照。"
---

# 2022 AI 编年史：INT8 量化与稀疏推理 | AI Timeline 2022: INT8 Quantization & Sparse Inference

---

## 一、背景与核心概念 | Background & Core Concepts

**English**

As foundation models grew to billions of parameters in 2022, **model compression** became essential for practical deployment. Two complementary techniques dominated: **quantization** (reducing numerical precision) and **sparsity** (zeroing out unimportant weights). Together they address the "**memory wall**" and "**compute wall**" that limit inference on edge devices, mobile phones, and cost-sensitive cloud serving.

**Quantization** maps floating-point weights and activations (FP32/FP16) to lower-bit integers. **INT8** (8-bit signed integer, range −128 to 127) became the industry sweet spot — offering ~4× memory reduction vs. FP32 with typically <1% accuracy loss for CNNs and acceptable trade-offs for Transformers.

Two main approaches:

1. **Post-Training Quantization (PTQ)**: Calibrate scale/zero-point factors on a small representative dataset after training. Fast, no retraining needed. Tools: TensorRT, ONNX Runtime, PyTorch `quantize_dynamic`.
2. **Quantization-Aware Training (QAT)**: Simulate quantization during training with fake-quantize nodes so the model learns to be robust to precision loss. Better accuracy, higher training cost.

Key terms:

- **Scale (s) and Zero-point (z)**: Affine mapping \(x_{int} = \text{round}(x_{fp} / s) + z\).
- **Per-channel vs per-tensor**: Finer granularity (per output channel) improves accuracy for conv/linear layers.
- **Symmetric vs asymmetric**: Symmetric uses z=0, simpler hardware; asymmetric handles biased distributions.
- **Dynamic quantization**: Quantize weights statically, activations on-the-fly per batch.
- **Static quantization**: Pre-compute activation ranges for both weights and activations.

**Sparsity** exploits the observation that many weights are near-zero:

- **Unstructured sparsity**: Individual weights set to zero (hard to accelerate without specialized hardware).
- **Structured sparsity (2:4 pattern)**: NVIDIA Ampere **Sparse Tensor Cores** require exactly 2 non-zero values per 4-element group — enabling ~2× speedup on A100.
- **Pruning**: Remove weights/channels/heads, then optionally fine-tune to recover accuracy.

**中文**

随着 2022 年基础模型增至数十亿参数，**模型压缩** 成为实际部署的关键。**量化**（降低数值精度）与 **稀疏化**（置零不重要权重）是两大互补技术，共同应对限制边缘设备、手机与成本敏感云端推理的 **「内存墙」** 与 **「算力墙」**。

**量化** 将浮点权重与激活（FP32/FP16）映射为低位整数。**INT8**（8 位有符号整数，范围 −128 至 127）成为产业甜蜜点 —— 相比 FP32 约 4× 内存缩减，CNN 精度损失通常 <1%，Transformer 有可接受折中。

两种主要方法：

1. **训练后量化（PTQ）**：训练后用小代表性数据集校准 scale/zero-point。快速、无需重训。工具：TensorRT、ONNX Runtime、PyTorch `quantize_dynamic`。
2. **量化感知训练（QAT）**：训练中用伪量化节点模拟量化，使模型适应精度损失。精度更好、训练成本更高。

关键术语：

- **缩放（s）与零点（z）**：仿射映射 \(x_{int} = \text{round}(x_{fp} / s) + z\)。
- **逐通道 vs 逐张量**：更细粒度（逐输出通道）提升卷积/线性层精度。
- **对称 vs 非对称**：对称 z=0，硬件简单；非对称处理有偏分布。
- **动态量化**：权重静态量化，激活按 batch 即时量化。
- **静态量化**：预计算权重与激活的范围。

**稀疏化** 利用大量权重接近零的观察：

- **非结构化稀疏**：单个权重置零（无专用硬件难以加速）。
- **结构化稀疏（2:4 模式）**：NVIDIA Ampere **稀疏张量核心** 要求每 4 元组恰好 2 个非零 —— A100 上约 2× 加速。
- **剪枝（Pruning）**：移除权重/通道/注意力头，可选微调恢复精度。

---

## 二、架构与部署链路 | Architecture & Deployment Pipeline

### 2.1 量化部署流水线 | Quantization Deployment Pipeline

**English**

```
Trained Model (FP32/FP16)
    ↓
Calibration dataset (100–1000 samples)
    ↓
┌─────────────────────────────────────┐
│  Quantization Tool                   │
│  ├── PTQ: TensorRT / ONNX Runtime     │
│  ├── QAT: PyTorch FX / TensorFlow     │
│  └── LLM-specific: GPTQ precursors    │
└──────────────┬──────────────────────┘
               ↓
Quantized Model (INT8 weights + INT8/FP16 activations)
    ↓
Runtime Engine
    ├── NVIDIA TensorRT (GPU)
    ├── ONNX Runtime (CPU/GPU)
    ├── OpenVINO (Intel)
    └── TFLite (mobile/edge)
    ↓
Production Inference (lower latency, lower memory)
```

| Stage | FP32 Baseline | INT8 Quantized | Improvement |
|---|---|---|---|
| Model size (ResNet-50) | ~98 MB | ~25 MB | ~4× smaller |
| Inference latency (CPU) | 100 ms | 30–40 ms | ~2.5–3× faster |
| VRAM (BERT-base) | ~440 MB | ~110 MB | ~4× less |
| Accuracy drop (CNN) | baseline | <0.5% top-1 | negligible |
| Accuracy drop (LLM perplexity) | baseline | 1–5% degradation | task-dependent |

**中文**

量化部署流水线：训练模型 → 校准数据集 → 量化工具（PTQ/QAT）→ INT8 模型 → 推理引擎（TensorRT/ONNX Runtime/OpenVINO/TFLite）→ 生产推理。ResNet-50 模型体积约缩减 4×，CPU 延迟约降 2.5–3×。

### 2.2 稀疏推理硬件支持 | Sparse Inference Hardware

| 硬件 Hardware | 稀疏模式 Sparse Pattern | 加速比 Speedup |
|---|---|---|
| NVIDIA A100 (Ampere) | 2:4 structured | ~2× |
| Intel AMX (Sapphire Rapids) | INT8 dot product | ~2–4× vs AVX-512 |
| Apple Neural Engine | INT8 mixed | 端侧 LLM 推理 |
| Qualcomm Hexagon NPU | INT8/INT4 | 手机 AI 加速 |
| Google TPU v4 | BF16/INT8 | 云端训练与推理 |

---

## 三、2022 年趋势 | Trends in 2022

**English**

1. **LLM quantization begins**: Although GPTQ (2023) popularized 4-bit LLM quantization, 2022 saw early INT8 experiments on BERT/T5 serving and research on INT8 Transformer inference.
2. **ONNX as lingua franca**: Most compression tools targeted ONNX intermediate representation for cross-framework deployment.
3. **Cloud cost optimization**: AWS Inferentia2, Google TPU INT8 paths, and Azure ONNX offerings pushed quantization in production MLOps.
4. **Mobile diffusion**: Early attempts to run SD on mobile via INT8/FP16 hybrid — full success came in 2023–2024.
5. **Sparsity + quantization combo**: NVIDIA demonstrated 2:4 sparse INT8 BERT on TensorRT for sub-1ms latency.
6. **Neural architecture search for efficiency**: Once-for-All (OFA) and EfficientNet descendants targeted deployable accuracy-latency Pareto frontiers.

**中文**

1. **LLM 量化起步**：GPTQ（2023）普及 4-bit 量化前，2022 年已有 BERT/T5 INT8 服务实验。
2. **ONNX 通用中间表示**：多数压缩工具以 ONNX 为跨框架部署目标。
3. **云端成本优化**：AWS Inferentia2、Google TPU INT8 路径推动生产 MLOps 量化。
4. **移动端扩散模型**：INT8/FP16 混合运行 SD 的早期尝试 —— 2023–2024 年成熟。
5. **稀疏 + 量化组合**：NVIDIA 在 TensorRT 上演示 2:4 稀疏 INT8 BERT，延迟 <1ms。
6. **高效架构搜索**：OFA、EfficientNet 后继者瞄准可部署的精度-延迟帕累托前沿。

---

## 四、优缺点分析 | Pros and Cons

| 优点 Advantages | 缺点 Disadvantages |
|---|---|
| 4× 内存缩减，降低部署成本 / 4× memory reduction | LLM 量化可能导致生成质量下降 / LLM quality may degrade |
| 2–4× 推理加速（CPU/GPU/NPU）/ 2–4× inference speedup | PTQ 对 outlier 激活敏感 / PTQ sensitive to activation outliers |
| 降低云端 GPU 租用费用 / Reduces cloud GPU costs | 逐框架/硬件调优工作量大 / Per-hardware tuning effort |
| 使边缘/移动端部署可行 / Enables edge/mobile deployment | 训练后量化无法修复已学偏置 / PTQ cannot fix learned biases |
| 结构化稀疏有硬件加速支持 / Structured sparsity has HW support | 非结构化稀疏难以实际加速 / Unstructured sparsity hard to speed up |
| 与现有 MLOps 工具链集成成熟 / Mature toolchain integration | 极低比特（INT4/INT2）2022 年尚不成熟 / Sub-INT8 immature in 2022 |

---

## 五、典型应用场景 | Use Cases

| 场景 Scenario | 中文说明 | English Description |
|---|---|---|
| 云端 NLP 服务 | BERT/RoBERTa INT8 降低推理成本 60%+ | INT8 BERT serving cuts cloud costs 60%+ |
| 手机端 CV | TFLite INT8 物体检测与分割 | On-device object detection with TFLite INT8 |
| 推荐系统 Embedding | 向量模型 INT8 压缩，加速召回 | INT8 embedding models for faster retrieval |
| 自动驾驶感知 | TensorRT INT8 目标检测实时推理 | Real-time detection via TensorRT INT8 |
| 工业质检 | 边缘盒子部署量化 CNN | Quantized CNN on edge inspection boxes |
| 语音唤醒 | INT8 关键词 spotting 低功耗 | Low-power keyword spotting with INT8 |
| 大模型服务预热 | FP16→INT8 混合精度降低显存 | Mixed precision reduces VRAM for serving |

---

## 六、GitHub 开源项目 | GitHub Projects

| 项目 Project | 说明 Description | 链接 Link |
|---|---|---|
| **huggingface/transformers** | 内置动态/静态量化支持 | [github.com/huggingface/transformers](https://github.com/huggingface/transformers) |
| **microsoft/onnxruntime** | 跨平台 INT8 推理引擎 | [github.com/microsoft/onnxruntime](https://github.com/microsoft/onnxruntime) |
| **NVIDIA/TensorRT** | GPU 最优 INT8/稀疏推理 | [github.com/NVIDIA/TensorRT](https://github.com/NVIDIA/TensorRT) |
| **pytorch/ao** | PyTorch 官方量化与稀疏工具（torch.ao） | [github.com/pytorch/ao](https://github.com/pytorch/ao) |

```python
# PyTorch 动态 INT8 量化示例
import torch
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased")
quantized = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
# Linear 层权重转为 INT8，推理内存约降 4×
```

---

## 七、总结 | Summary

**中文**：2022 年 **INT8 量化与稀疏推理** 是大模型时代的「隐形基础设施」—— 不如 ChatGPT 耀眼，却决定了 AI 能否以可接受成本到达用户。它为 2023 年 GPTQ/AWQ 4-bit 量化、端侧 LLM 与 NPU 推理浪潮奠定了工程基础，是 **「训练越大、部署越省」** 悖论的关键解法。

**English**: **INT8 quantization and sparse inference** in 2022 were the "invisible infrastructure" of the large-model era — less glamorous than ChatGPT, but decisive for whether AI reaches users at acceptable cost. They laid the engineering foundation for 2023's GPTQ/AWQ 4-bit quantization, on-device LLMs, and NPU inference — the key answer to the paradox of "train bigger, deploy cheaper."

---

**参考链接 | References**

- PyTorch 量化教程：[pytorch.org/docs/stable/quantization](https://pytorch.org/docs/stable/quantization.html)
- ONNX Runtime 量化：[onnxruntime.ai/docs/performance/quantization](https://onnxruntime.ai/docs/performance/quantization.html)
- NVIDIA 2:4 稀疏：[developer.nvidia.com/blog/accelerating-inference-with-sparsity-using-ampere-and-tensorrt](https://developer.nvidia.com/blog/accelerating-inference-with-sparsity-using-ampere-and-tensorrt)
- TensorRT 文档：[docs.nvidia.com/deeplearning/tensorrt](https://docs.nvidia.com/deeplearning/tensorrt/)
- 量化综述：[A Survey of Quantization Methods for Efficient Neural Network Inference (Gholami et al., 2021)](https://arxiv.org/abs/2103.13630)
