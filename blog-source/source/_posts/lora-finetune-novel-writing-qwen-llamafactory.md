---
title: LoRA 微调小说写作小模型：Qwen-1.8B-Chat + LLaMA Factory 同款文风续写
date: 2026-06-05 15:30:00
categories:
  - mechine
tags:
  - LoRA
  - 微调
  - Qwen
  - LLaMA Factory
  - 小说
---

大模型「会写」和「写得像你」是两回事。通用模型能讲故事，但很难稳定复现某一本书的文风、句式、叙事节奏和人物口吻。

这篇文章用 **Qwen-1.8B-Chat + LLaMA Factory + LoRA**，在消费级 GPU 上微调一个小模型，让它学会你指定小说的写作风格，实现**同款风格续写**。

## 我们要让模型学会什么

小说风格不是单一维度，训练数据要覆盖这些层面：

| 维度 | 说明 | 数据体现 |
| --- | --- | --- |
| 文风 | 用词习惯、修辞密度、叙述视角 | 原文段落本身 |
| 句式 | 长短句交替、断句节奏、对话与描写比例 | 连续上下文 |
| 叙事节奏 | 铺垫—冲突—转折的信息密度 | 多轮续写样本 |
| 人物口吻 | 不同角色说话方式、语气词、口头禅 | 带角色标注的对话 |

LoRA 只更新少量参数，适合在 1.8B 小模型上**注入风格**，而不是重新学一遍中文。

## 方案概览

```text
小说原文 (.txt)
    ↓ 切分 + 构造指令样本
训练集 (alpaca/sharegpt json)
    ↓ LLaMA Factory LoRA SFT
Qwen-1.8B-Chat + LoRA 适配器
    ↓ 加载推理
同款风格续写 / 对话写作
```

**为什么选 Qwen-1.8B-Chat？**

- 体量小，6GB 显存即可 LoRA 微调
- 中文能力强，适合小说语料
- 与 LLaMA Factory 的 `qwen` 模板原生兼容

**为什么选 LoRA？**

- 只训练低秩矩阵，显存占用低
- 适配器文件通常几十到几百 MB，方便切换不同「文风」
- 不破坏基座模型的通用能力

## 环境准备

```bash
# 建议 Python 3.10+
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"

# 可选：4bit 量化训练（显存更省）
pip install bitsandbytes
```

硬件建议：

| 配置 | 全参数 | LoRA | QLoRA (4bit) |
| --- | --- | --- | --- |
| 6GB 显存 | ❌ | ✅ | ✅ 推荐 |
| 12GB+ 显存 | ❌ | ✅ 舒适 | ✅ |

## 第一步：把小说变成训练数据

核心思路：**不要只丢原文**，要构造「指令 → 风格化输出」的监督样本。

### 1. 清洗与切分原文

```python
import json
import re
from pathlib import Path

def load_novel(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"\s+", "\n", text.strip())
    return text

def split_chunks(text: str, chunk_size: int = 800, overlap: int = 120):
    """按字数切分，保留上下文重叠，利于学习叙事节奏。"""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks
```

### 2. 构造三类训练样本

**A. 文风续写（主样本）**

```json
{
  "instruction": "请用以下小说的文风续写故事，保持叙述视角、句式节奏和用词习惯一致。",
  "input": "前情：\n{context}",
  "output": "{continuation}",
  "system": "你是一位擅长模仿指定小说文风的写作助手，注重叙事节奏与人物口吻。"
}
```

**B. 人物口吻对话**

```json
{
  "instruction": "请以【{character}】的口吻回应对话，保持该角色一贯的说话方式。",
  "input": "场景：{scene}\n对方说：{line}",
  "output": "{reply}",
  "system": "你正在扮演小说中的角色，回答必须符合人物性格和语言习惯。"
}
```

**C. 风格改写（强化句式）**

```json
{
  "instruction": "将下面这段文字改写成目标小说的文风，不改变情节，只调整措辞、节奏和修辞。",
  "input": "{neutral_text}",
  "output": "{styled_text}",
  "system": "你是文风迁移助手，输出应贴近目标小说的叙述风格。"
}
```

### 3. 生成数据集脚本

```python
def build_style_samples(chunks: list[str]) -> list[dict]:
    samples = []
    for i in range(len(chunks) - 1):
        context = chunks[i]
        continuation = chunks[i + 1][:500]  # 续写目标不宜过长
        samples.append({
            "instruction": "请用以下小说的文风续写故事，保持叙述视角、句式节奏和用词习惯一致。",
            "input": f"前情：\n{context}",
            "output": continuation,
            "system": "你是一位擅长模仿指定小说文风的写作助手，注重叙事节奏与人物口吻。"
        })
    return samples

chunks = split_chunks(load_novel("novel.txt"))
dataset = build_style_samples(chunks)

Path("data/novel_style.json").write_text(
    json.dumps(dataset, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"生成 {len(dataset)} 条样本")
```

数据量建议：

- **最少**：500 条高质量样本（约 3～5 万字小说）
- **推荐**：2000～5000 条（多章节、多场景）
- 样本要覆盖：叙述段、对话段、高潮段、日常段

## 第二步：注册数据集

在 `LLaMA-Factory/data/dataset_info.json` 中添加：

```json
"novel_style": {
  "file_name": "novel_style.json",
  "columns": {
    "prompt": "instruction",
    "query": "input",
    "response": "output",
    "system": "system"
  }
}
```

## 第三步：LoRA 微调配置

新建 `examples/train_lora/qwen1_8b_novel_lora.yaml`：

```yaml
### model
model_name_or_path: Qwen/Qwen-1_8B-Chat
trust_remote_code: true

### method
stage: sft
do_train: true
finetuning_type: lora
lora_rank: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target: all

### dataset
dataset: novel_style
template: qwen
cutoff_len: 2048
max_samples: 10000
overwrite_cache: true
preprocessing_num_workers: 4

### output
output_dir: saves/qwen1_8b_novel_lora
logging_steps: 10
save_steps: 200
plot_loss: true
overwrite_output_dir: true

### train
per_device_train_batch_size: 2
gradient_accumulation_steps: 8
learning_rate: 2.0e-4
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.05
bf16: true
ddp_timeout: 180000000

### eval
val_size: 0.05
per_device_eval_batch_size: 1
eval_strategy: steps
eval_steps: 200
```

参数说明：

| 参数 | 建议值 | 作用 |
| --- | --- | --- |
| `lora_rank` | 8～32 | 越大表达能力越强，显存越高 |
| `cutoff_len` | 2048 | 覆盖更长上下文，利于学叙事节奏 |
| `learning_rate` | 1e-4 ~ 3e-4 | 风格学习常用偏高学习率 |
| `num_train_epochs` | 2～5 | 样本少可多轮，注意过拟合 |

显存不足时，改用 QLoRA：

```yaml
finetuning_type: lora
quantization_bit: 4
```

## 第四步：启动训练

```bash
cd LLaMA-Factory

# 单卡训练
CUDA_VISIBLE_DEVICES=0 llamafactory-cli train examples/train_lora/qwen1_8b_novel_lora.yaml

# 或使用 Web UI
llamafactory-cli webui
```

训练时关注：

1. **loss 稳定下降**：通常在 0.5～1.5 区间收敛
2. **验证集 loss 不再下降时停止**：避免只会「背诵」训练集
3. **抽查生成**：用同一 prompt 对比第 1 epoch 和第 3 epoch 输出

## 第五步：推理与同款风格写作

### 命令行推理

```bash
CUDA_VISIBLE_DEVICES=0 llamafactory-cli chat \
  --model_name_or_path Qwen/Qwen-1_8B-Chat \
  --adapter_name_or_path saves/qwen1_8b_novel_lora \
  --template qwen \
  --finetuning_type lora
```

### Python 加载

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = "Qwen/Qwen-1_8B-Chat"
lora = "saves/qwen1_8b_novel_lora"

tokenizer = AutoTokenizer.from_pretrained(base, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    base, device_map="auto", trust_remote_code=True
)
model = PeftModel.from_pretrained(model, lora)
model.eval()

prompt = """请用训练小说的文风续写以下内容，保持叙事节奏和人物口吻：

前情：
雨停之后，巷口的青石板还泛着潮气。她站在门廊下，没有回头。"""

messages = [
    {"role": "system", "content": "你是一位擅长模仿指定小说文风的写作助手。"},
    {"role": "user", "content": prompt},
]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)

outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.8, top_p=0.9)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))
```

### 导出合并模型（可选）

```bash
CUDA_VISIBLE_DEVICES=0 llamafactory-cli export \
  --model_name_or_path Qwen/Qwen-1_8B-Chat \
  --adapter_name_or_path saves/qwen1_8b_novel_lora \
  --template qwen \
  --finetuning_type lora \
  --export_dir exports/qwen1_8b_novel_merged \
  --export_size 2 \
  --export_legacy_format false
```

## 效果调优：四个实战技巧

### 1. 用「多粒度」样本，不要只续写

只喂「上文 → 下文」容易学会情节复述，学不会口吻。建议三类样本比例为：

- 文风续写 60%
- 角色对话 25%
- 风格改写 15%

### 2. 控制续写目标长度

`output` 建议 200～600 字。太长会稀释风格信号，太短学不到叙事节奏。

### 3. 推理温度按任务切换

| 任务 | temperature | top_p |
| --- | --- | --- |
| 仿写/续写 | 0.7～0.9 | 0.85～0.95 |
| 角色对话 | 0.8～1.0 | 0.9 |
| 风格改写 | 0.5～0.7 | 0.8 |

### 4. 多适配器管理不同文风

```text
saves/
├── qwen1_8b_wuxia_lora/     # 武侠风
├── qwen1_8b_romance_lora/   # 言情风
└── qwen1_8b_scifi_lora/     # 科幻风
```

推理时切换 `adapter_name_or_path` 即可，基座模型不用重复加载。

## 常见问题

**Q：生成内容像训练集原文拼凑？**

过拟合。减少 epoch、增大 `lora_dropout`、扩充样本多样性。

**Q：风格像了，但逻辑不通？**

1.8B 容量有限，复杂长篇规划能力弱。建议用于**段落级续写**，而非整章大纲生成。

**Q：对话口吻不像某个角色？**

增加带角色名的对话样本，并在 `instruction` 中显式写出角色身份。

**Q：显存不够？**

启用 `quantization_bit: 4`，或将 `per_device_train_batch_size` 设为 1、`gradient_accumulation_steps` 调大。

## 总结

用 Qwen-1.8B-Chat + LLaMA Factory 做 LoRA 微调，是在有限算力下实现「同款文风写作」的务实路线：

1. 把小说切成**风格监督样本**，而不只是原文堆砌
2. 覆盖文风、句式、节奏、口吻四个维度
3. LoRA 低成本注入风格，基座能力保留
4. 推理时通过 prompt + 温度控制输出质量

小模型不会替代顶尖大模型的全局构思能力，但在**风格化续写、角色对话、章节仿写**这类任务上，微调后的 1.8B 往往比未微调的 7B 更「像你」。

如果你要针对某本具体小说做数据集，核心就一句话：**让模型看到的每一条样本，都在回答「如何用这种风格写」**。
