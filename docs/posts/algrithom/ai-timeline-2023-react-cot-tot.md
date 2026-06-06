---
title: "2023 AI 编年史：ReAct、CoT 与 ToT 推理范式"
date: 2023-05-10 10:00:00
categories:
  - "algrithom"
tags:
  - "AI Timeline"
  - "ReAct"
  - "Chain-of-Thought"
  - "Tree of Thoughts"
  - "Reasoning"
description: "2023 年 AI 编年史：Chain-of-Thought（CoT）、ReAct（推理+行动）、Tree of Thoughts（ToT）三大 LLM 推理范式的技术原理与应用，中英文对照。"
---

# 2023 AI 编年史：ReAct、CoT 与 ToT 推理范式 | AI Timeline 2023: ReAct, CoT, and ToT

---

## 一、背景 | Background

**English**

In **May 2023**, as LLM applications grew beyond simple Q&A, three **reasoning paradigms** dominated research and engineering: **Chain-of-Thought (CoT)**, **ReAct (Reasoning + Acting)**, and **Tree of Thoughts (ToT)**. Together they transformed LLMs from pattern matchers into systems capable of multi-step reasoning, tool use, and deliberate search.

These paradigms emerged because standard prompting fails on tasks requiring arithmetic, logical deduction, or external information retrieval. CoT (Wei et al., 2022) showed that asking models to "think step by step" dramatically improves accuracy. ReAct (Yao et al., 2022) interleaved reasoning with tool calls. ToT (Yao et al., 2023) added tree search over reasoning paths.

Key terms:
- **CoT (Chain-of-Thought)**: Prompting technique that elicits intermediate reasoning steps before the final answer.
- **ReAct**: Framework alternating Thought → Action → Observation cycles with external tools.
- **ToT (Tree of Thoughts)**: Search algorithm exploring multiple reasoning branches and backtracking.
- **Self-Consistency**: Sampling multiple CoT paths and taking the majority vote.
- **Zero-Shot CoT**: Adding "Let's think step by step" without examples.

**中文**

**2023 年 5 月**，随着 LLM 应用超越简单问答，三种 **推理范式** 主导研究与工程：**思维链（CoT）**、**ReAct（推理+行动）** 与 **思维树（ToT）**。它们将 LLM 从模式匹配器转变为具备多步推理、工具调用与审慎搜索能力的系统。

这些范式出现是因为标准 Prompt 在需要算术、逻辑推导或外部信息检索的任务上失败。CoT（Wei 等，2022）表明让模型「逐步思考」可大幅提升准确率。ReAct（Yao 等，2022）将推理与工具调用交替进行。ToT（Yao 等，2023）在推理路径上加入树搜索。

关键词解释：
- **CoT（思维链）**：引导模型在最终答案前输出中间推理步骤的 Prompt 技术。
- **ReAct**：Thought → Action → Observation 循环与外部工具交替的框架。
- **ToT（思维树）**：探索多条推理分支并回溯的搜索算法。
- **Self-Consistency（自洽性）**：采样多条 CoT 路径，取多数投票。
- **Zero-Shot CoT**：无示例，仅添加「Let's think step by step」。

---

## 二、架构 | Architecture

### 2.1 Chain-of-Thought (CoT) | 思维链

**English**

CoT elicits a **reasoning chain** before the final answer:

```
Prompt: "Roger has 5 tennis balls. He buys 2 cans of 3 balls each.
         How many does he have? Let's think step by step."

Model Output:
  Step 1: Roger starts with 5 balls.
  Step 2: 2 cans × 3 balls = 6 new balls.
  Step 3: 5 + 6 = 11 balls total.
  Answer: 11
```

**Variants**:
| Variant | Mechanism | When to Use |
|---|---|---|
| Zero-Shot CoT | "Let's think step by step" | Quick, no examples needed |
| Few-Shot CoT | Provide 2–8 solved examples | Complex domains |
| Auto-CoT | LLM generates its own examples | Scale without manual labeling |
| Self-Consistency | Sample N chains, majority vote | High-stakes accuracy |

**中文**

CoT 在最终答案前引导 **推理链**：模型逐步列出中间步骤（Roger 有 5 个球 → 买 2 罐各 3 个 = 6 个 → 5+6=11）。变体包括 Zero-Shot CoT（无示例）、Few-Shot CoT（提供 2–8 个已解示例）、Auto-CoT（LLM 自生成示例）与 Self-Consistency（多条路径多数投票）。

### 2.2 ReAct (Reasoning + Acting) | 推理与行动

**English**

ReAct interleaves **internal reasoning** with **external actions**:

```
Question: "What is the elevation of the city where the 2024 Olympics will be held?"

Thought 1: I need to find where the 2024 Olympics are held.
Action 1: Search["2024 Olympics host city"]
Observation 1: Paris, France

Thought 2: Now I need Paris's elevation.
Action 2: Search["Paris elevation meters"]
Observation 2: 35 meters above sea level

Thought 3: I have the answer.
Action 3: Finish[35 meters]
```

**Architecture components**:
- **Thought**: LLM's internal reasoning (not sent to tools)
- **Action**: Tool invocation (Search, Calculator, Code, API)
- **Observation**: Tool output fed back into context
- **Loop**: Repeat until Finish action or max steps

**中文**

ReAct 将 **内部推理** 与 **外部行动** 交替：Thought（LLM 内部推理，不发送给工具）→ Action（工具调用：Search、Calculator、Code、API）→ Observation（工具输出反馈到上下文）→ 循环直至 Finish 或达到最大步数。

### 2.3 Tree of Thoughts (ToT) | 思维树

**English**

ToT treats reasoning as **deliberate search** over a tree:

```
                    [Initial Problem]
                   /        |        \
            [Thought A]  [Thought B]  [Thought C]
              /    \         |          |
         [A1]   [A2]     [B1]        [C1]
          ✗      ✓         ✗           ?
                             
Evaluation: Score each node → prune bad branches → expand promising ones
Strategies: BFS (breadth-first) or DFS (depth-first) over thought nodes
```

**ToT pipeline**:
1. **Decompose**: Break problem into thought steps
2. **Generate**: Propose multiple candidate thoughts per step
3. **Evaluate**: LLM or heuristic scores each candidate
4. **Search**: BFS/DFS with backtracking on low-scoring branches
5. **Answer**: Return best complete reasoning path

**中文**

ToT 将推理视为对树的 **审慎搜索**：分解问题 → 每步生成多个候选思维 → LLM 或启发式评分 → BFS/DFS 搜索并剪枝低分分支 → 回溯 → 返回最优完整推理路径。

### 2.4 三者关系与选型 | Relationship and Selection

```
CoT ──── 纯推理，无外部工具，适合数学/逻辑
  │
  ├── Self-Consistency ──── 提高 CoT 准确率
  │
ReAct ──── CoT + 工具调用，适合需要实时信息的任务
  │
ToT ──── CoT + 搜索，适合需要探索多条路径的复杂规划
```

| 范式 | 外部工具 | 搜索 | 典型任务 |
|---|---|---|---|
| CoT | ❌ | ❌ | 数学、逻辑、常识 |
| ReAct | ✅ | ❌ | 问答、API 调用、代码 |
| ToT | 可选 | ✅ | 规划、创意、博弈 |

---

## 三、趋势 | Trends

**English**

May–August 2023 reasoning trends:

1. **CoT becomes default**: "Let's think step by step" added to virtually every complex prompt.
2. **ReAct → LangChain Agents**: ReAct pattern became the foundation of LangChain Agent executors.
3. **ToT too expensive**: Tree search requires many LLM calls — practical deployments favored ReAct.
4. **Process Reward Models**: OpenAI o1 (2024 preview) trained models to internalize CoT natively.
5. **Graph of Thoughts (GoT)**: Extending ToT to arbitrary graph structures for merge/refine operations.

**中文**

2023 年 5–8 月推理趋势：

1. **CoT 成为默认**：几乎每个复杂 Prompt 都加入「逐步思考」。
2. **ReAct → LangChain Agent**：ReAct 模式成为 LangChain Agent 执行器基础。
3. **ToT 成本过高**：树搜索需大量 LLM 调用——实际部署更倾向 ReAct。
4. **过程奖励模型**：OpenAI o1（2024 预览）训练模型内化 CoT。
5. **Graph of Thoughts（GoT）**：将 ToT 扩展为任意图结构以支持合并/精炼操作。

---

## 四、优缺点 | Pros and Cons

### 4.1 CoT

| 优点 Advantages | 缺点 Disadvantages |
|---|---|
| 简单有效，一行 Prompt 即可 | 增加输出 token 数与成本 |
| 显著提升数学/逻辑准确率 | 推理步骤可能出错且传播 |
| 可解释——可见推理过程 | 对简单任务反而降低效率 |

### 4.2 ReAct

| 优点 Advantages | 缺点 Disadvantages |
|---|---|
| 结合 LLM 推理与实时信息 | 工具调用失败导致级联错误 |
| 可扩展——添加新工具即可 | 循环次数难控制，可能死循环 |
| 成为 Agent 框架标准模式 | 延迟高——每步一次 LLM + 工具调用 |

### 4.3 ToT

| 优点 Advantages | 缺点 Disadvantages |
|---|---|
| 复杂规划任务准确率最高 | LLM 调用次数指数增长 |
| 可回溯错误推理路径 | 评估函数设计困难 |
| 适合创意与多方案探索 | 生产环境延迟不可接受 |

---

## 五、应用场景 | Use Cases

| 场景 Scenario | 推荐范式 Paradigm | 中文说明 |
|---|---|---|
| 小学数学应用题 | CoT + Self-Consistency | 逐步计算，多数投票 |
| 实时新闻问答 | ReAct + Search | 搜索最新信息再回答 |
| 旅行规划 | ToT | 探索多条路线，选最优 |
| 代码 Debug | ReAct + Code Interpreter | 写代码 → 执行 → 观察错误 |
| 医疗诊断辅助 | CoT + 专业知识 | 逐步分析症状 |
| 游戏 AI（24点、数独） | ToT + BFS | 搜索可行解空间 |
| 企业数据分析 | ReAct + SQL/Calculator | 查询数据库 → 计算 → 报告 |

---

## 六、GitHub 与开源生态 | GitHub and Open Source

| 项目 Project | 说明 Description |
|---|---|
| [langchain-ai/langchain](https://github.com/langchain-ai/langchain) | ReAct Agent 执行器实现 |
| [princeton-nlp/tree-of-thought-llm](https://github.com/princeton-nlp/tree-of-thought-llm) | ToT 官方实现（Princeton NLP） |
| [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) | 自主 Agent，ReAct 变体 |
| [microsoft/autogen](https://github.com/microsoft/autogen) | 多 Agent 推理框架 |
| [openai/openai-cookbook](https://github.com/openai/openai-cookbook) | CoT 与 Function Calling 示例 |

---

## 七、总结 | Summary

**中文**：2023 年 5 月，CoT、ReAct 与 ToT 三大推理范式定义了 LLM 从「问答机器」到「推理系统」的进化路径。CoT 提供可解释的逐步推理，ReAct 打通 LLM 与外部世界的桥梁，ToT 引入搜索与回溯的 deliberation 能力。它们共同构成 2023 年 AI Agent 与复杂应用的技术基石。

**English**: In May 2023, CoT, ReAct, and ToT defined LLM evolution from "Q&A machines" to "reasoning systems." CoT provides interpretable step-by-step reasoning, ReAct bridges LLMs to the external world, and ToT introduces search and backtracking deliberation. Together they form the technical foundation of 2023 AI Agents and complex applications.

---

**参考链接 | References**

- 论文: [Chain-of-Thought Prompting Elicits Reasoning](https://arxiv.org/abs/2201.11903)
- 论文: [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- 论文: [Tree of Thoughts: Deliberate Problem Solving with LLMs](https://arxiv.org/abs/2305.10601)
- 论文: [Self-Consistency Improves Chain of Thought Reasoning](https://arxiv.org/abs/2203.11171)
