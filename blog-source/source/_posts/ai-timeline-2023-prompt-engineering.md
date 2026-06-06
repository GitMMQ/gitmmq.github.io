---
title: "2023 AI 编年史：提示工程 Prompt Engineering"
date: 2023-02-10 10:00:00
categories:
  - "framework"
tags:
  - "AI Timeline"
  - "Prompt Engineering"
  - "LLM"
  - "Few-Shot"
  - "Chain-of-Thought"
description: "2023 年 AI 编年史：提示工程从暗知识变为显式方法论，涵盖 Zero-Shot、Few-Shot、CoT、角色设定与 Prompt 模板设计，中英文对照。"
---

# 2023 AI 编年史：提示工程 | AI Timeline 2023: Prompt Engineering

---

## 一、背景 | Background

**English**

In **February 2023**, as millions experimented with ChatGPT, a new discipline crystallized: **Prompt Engineering** — the art and science of crafting inputs to elicit desired outputs from LLMs without changing model weights.

Before prompt engineering, interacting with GPT-3 required ML expertise. ChatGPT democratized access, but users quickly discovered that vague prompts yield vague answers. By February, "prompt engineer" job postings appeared on LinkedIn, prompt marketplaces like PromptBase launched, and researchers published systematic studies on prompt design patterns.

Key terms:
- **Prompt**: The input text (instruction + context + examples) sent to an LLM.
- **Zero-Shot**: Asking the model to perform a task with no examples — relying entirely on pretraining knowledge.
- **Few-Shot (In-Context Learning)**: Providing 1–5 input-output examples in the prompt to guide behavior.
- **System Prompt**: A persistent instruction that sets the model's role, tone, and constraints.
- **Temperature**: A sampling parameter controlling randomness (0 = deterministic, 1 = creative).

**中文**

**2023 年 2 月**，当数百万人试用 ChatGPT 时，一门新学科结晶为 **提示工程（Prompt Engineering）**——在不改变模型权重的前提下，通过精心设计输入来引导 LLM 输出期望结果的艺术与科学。

在提示工程出现之前，使用 GPT-3 需要 ML 专业知识。ChatGPT 降低了门槛，但用户很快发现模糊提示只会得到模糊回答。到 2 月，LinkedIn 上出现「提示工程师」招聘，PromptBase 等提示词市场上线，研究者发表系统性 Prompt 设计模式研究。

关键词解释：
- **Prompt（提示词）**：发送给 LLM 的输入文本（指令 + 上下文 + 示例）。
- **Zero-Shot（零样本）**：不提供示例，完全依赖预训练知识完成任务。
- **Few-Shot（少样本/上下文学习）**：在 Prompt 中提供 1–5 个输入-输出示例引导行为。
- **System Prompt（系统提示）**：设定模型角色、语气与约束的持久指令。
- **Temperature（温度）**：控制采样随机性的参数（0 = 确定性，1 = 创造性）。

---

## 二、架构 | Architecture

### 2.1 Prompt 结构模型 | Prompt Structure Model

**English**

A well-engineered prompt follows a layered architecture:

```
┌─────────────────────────────────────┐
│  System Prompt（角色 / 约束 / 格式）   │
├─────────────────────────────────────┤
│  Context（背景知识 / RAG 检索结果）    │
├─────────────────────────────────────┤
│  Few-Shot Examples（可选示例）        │
├─────────────────────────────────────┤
│  User Query（用户实际问题）           │
├─────────────────────────────────────┤
│  Output Format Spec（JSON / Markdown）│
└─────────────────────────────────────┘
```

**Design principles**:
1. **Be specific**: "Summarize in 3 bullet points" beats "Summarize this."
2. **Assign a role**: "You are a senior Python developer reviewing code."
3. **Specify format**: "Return JSON with keys: title, summary, tags."
4. **Use delimiters**: `"""`, `###`, XML tags to separate sections.
5. **Chain prompts**: Break complex tasks into sequential steps.

**中文**

精心设计的 Prompt 遵循分层架构：最上层为 **System Prompt**（角色/约束/格式），其下为 **Context**（背景知识或 RAG 检索结果），再下为可选 **Few-Shot 示例**，然后是 **User Query**，最底层指定 **Output Format**（JSON/Markdown 等）。

设计原则：① **具体明确**——「用 3 个要点总结」优于「总结」；② **赋予角色**——「你是资深 Python 开发者」；③ **指定格式**——「返回 JSON，键为 title、summary、tags」；④ **使用分隔符**——`"""`、`###`、XML 标签；⑤ **链式 Prompt**——复杂任务拆为顺序步骤。

### 2.2 核心 Prompt 模式 | Core Prompt Patterns

| 模式 Pattern | 说明 Description | 示例 Example |
|---|---|---|
| **Zero-Shot** | 无示例，直接指令 | "Translate to French: Hello" |
| **Few-Shot** | 提供输入-输出对 | "English→Chinese: cat→猫, dog→?" |
| **CoT** | 要求逐步推理 | "Let's think step by step" |
| **Role Prompting** | 设定专家角色 | "You are a patent attorney..." |
| **Self-Consistency** | 多次采样取多数 | Generate 5 answers, pick most common |
| **ReAct** | 推理 + 行动交替 | Thought → Action → Observation |
| **Tree of Thoughts** | 分支探索多条路径 | Evaluate multiple reasoning branches |

### 2.3 Prompt 工程工具链 | Prompt Engineering Toolchain

**English**

By mid-2023, a toolchain emerged around prompt development:

- **Playground UIs**: OpenAI Playground, Anthropic Console for iterative testing
- **Prompt libraries**: LangChain PromptTemplate, Guidance, LMQL
- **Evaluation**: PromptBench, HELM benchmark for comparing prompt strategies
- **Version control**: PromptLayer, Humanloop for tracking prompt versions in production

**中文**

到 2023 年中，围绕 Prompt 开发的工具链成型：OpenAI Playground 等 **Playground UI** 用于迭代测试；LangChain PromptTemplate 等 **Prompt 库** 提供模板化；PromptBench 等 **评估框架** 对比策略；PromptLayer 等 **版本管理** 工具追踪生产环境 Prompt 变更。

---

## 三、趋势 | Trends

**English**

February–March 2023 trends in prompt engineering:

1. **Prompt as API design**: Developers realized prompts are the new "API contracts" for LLM applications.
2. **Structured output demand**: JSON mode, function calling, and schema-constrained generation became essential.
3. **Prompt injection awareness**: Security researchers exposed how malicious inputs could override system prompts.
4. **Multilingual prompting**: Techniques for consistent quality across Chinese, English, Japanese, etc.
5. **Automated prompt optimization**: Tools like DSPy (Stanford) began automating prompt search.

**中文**

2023 年 2–3 月提示工程趋势：

1. **Prompt 即 API 设计**：开发者意识到 Prompt 是 LLM 应用的「新 API 契约」。
2. **结构化输出需求**：JSON 模式、Function Calling、Schema 约束生成成为刚需。
3. **Prompt 注入意识**：安全研究者揭示恶意输入可覆盖 System Prompt。
4. **多语言 Prompt**：跨中、英、日等语言保持一致质量的技术。
5. **自动化 Prompt 优化**：DSPy（Stanford）等工具开始自动化 Prompt 搜索。

---

## 四、优缺点 | Pros and Cons

### 4.1 优点 | Advantages

1. **零成本适配** — 无需微调即可改变模型行为 / **Zero-cost adaptation** without fine-tuning
2. **即时迭代** — 修改 Prompt 秒级生效 / **Instant iteration** — changes take effect immediately
3. **可解释** — Prompt 文本即文档 / **Interpretable** — prompt text serves as documentation
4. **可组合** — 模块化 Prompt 模板可复用 / **Composable** — modular templates reusable
5. **低门槛** — 非 ML 背景人员可上手 / **Low barrier** — accessible to non-ML practitioners

### 4.2 缺点 | Disadvantages

1. **不稳定** — 微小措辞变化导致输出剧变 / **Fragile** — tiny wording changes cause output shifts
2. **无版本保证** — 模型更新可能破坏现有 Prompt / **No versioning guarantee** — model updates break prompts
3. **上下文浪费** — Few-Shot 示例占用 token 预算 / **Context waste** — examples consume token budget
4. **难以规模化** — 手工 Prompt 无法覆盖数百场景 / **Hard to scale** — manual prompts don't cover hundreds of scenarios
5. **安全漏洞** — Prompt 注入、越狱攻击 / **Security holes** — injection and jailbreak attacks
6. **天花板明显** — 复杂推理仍需微调或 RAG / **Ceiling effect** — complex reasoning needs fine-tuning or RAG

---

## 五、应用场景 | Use Cases

| 场景 Scenario | Prompt 策略 Strategy | 中文说明 |
|---|---|---|
| 代码生成 | Role + Format + Few-Shot | 设定开发者角色，指定语言与风格 |
| 数据分析 | CoT + Structured Output | 逐步推理，输出 JSON 表格 |
| 客服对话 | System Prompt + Context | 角色设定 + 产品知识注入 |
| 内容审核 | Classification Prompt | 零样本分类：安全/不安全 |
| 文档摘要 | Zero-Shot + Length Constraint | 限制字数与要点数量 |
| 多轮对话 | Memory + System Prompt | 上下文记忆 + 持久角色 |
| A/B 测试 | Prompt Versioning | 对比不同 Prompt 版本的转化率 |

---

## 六、GitHub 与开源生态 | GitHub and Open Source

| 项目 Project | 说明 Description |
|---|---|
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | PromptTemplate、Few-Shot、Output Parser |
| [guidance-ai/guidance](https://github.com/guidance-ai/guidance) | 约束生成语法，精确控制输出格式 |
| [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | 声明式 Prompt 优化框架 |
| [microsoft/promptflow](https://github.com/microsoft/promptflow) | 可视化 Prompt 编排与评估 |
| [openai/openai-cookbook](https://github.com/openai/openai-cookbook) | OpenAI 官方 Prompt 最佳实践 |

---

## 七、总结 | Summary

**中文**：2023 年 2 月，提示工程从 ChatGPT 用户的「暗知识」上升为 LLM 应用开发的核心方法论。Zero-Shot、Few-Shot、CoT 等模式构成 Prompt 设计的基础工具箱，但脆弱性、安全漏洞与规模化难题也推动行业向 RAG、微调和 Agent 框架演进。

**English**: In February 2023, prompt engineering evolved from ChatGPT users' tacit knowledge into a core methodology for LLM application development. Zero-Shot, Few-Shot, and CoT patterns form the foundational toolkit, but fragility, security vulnerabilities, and scaling challenges drove the industry toward RAG, fine-tuning, and Agent frameworks.

---

**参考链接 | References**

- OpenAI: [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- 论文: [Language Models are Few-Shot Learners (GPT-3)](https://arxiv.org/abs/2005.14165)
- 论文: [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903)
- Learn Prompting: [learnprompting.org](https://learnprompting.org)
