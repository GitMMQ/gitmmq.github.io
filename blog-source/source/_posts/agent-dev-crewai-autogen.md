---
title: 多 Agent 协作框架：CrewAI 角色扮演 vs AutoGen 对话驱动
date: 2026-06-05 17:35:00
categories:
  - framework
tags:
  - CrewAI
  - AutoGen
  - Agent
  - 多Agent
  - LLM
---

> **English Title:** Multi-Agent Frameworks — CrewAI Role-Playing vs AutoGen Conversation-Driven

当你已经会用单 Agent 完成「读文档 → 调工具 → 写答案」的闭环，下一步往往是把任务拆给多个专长不同的智能体。CrewAI 用**角色与流程**组织协作，AutoGen（现 AG2）用**对话与消息传递**驱动协作。二者都能做多 Agent，但心智模型、成本曲线和工程落点截然不同。本文帮你建立选型依据，并给出可运行的最小示例。

---

## 1. 何时需要多 Agent，何时单 Agent 足够

**单 Agent 更合适的场景：**

- 任务边界清晰，工具链固定（例如：查库 + 生成 SQL + 执行）
- 对话轮次可控，上下文在一两次工具调用内能收敛
- 团队希望最小依赖、最短上线路径

**多 Agent 更值得投入的场景：**

- 流程天然分阶段，且每阶段需要**不同的系统提示与约束**（调研 / 写作 / 审校）
- 需要**对抗式或交叉验证**（一个生成、一个挑错）
- 人类要在环中审批中间产物，再交给下一角色继续
- 单 Agent 的 prompt 已经臃肿，出现角色混淆、越权调用工具等问题

经验法则：若你只是把同一段 system prompt 复制三份并改名，多半还没赚到多 Agent 的收益；若各阶段的可观测输出、失败重试、人工卡点已经定义清楚，多 Agent 框架能显著降低编排代码的复杂度。

---

## 2. CrewAI：角色、目标与流程编排

CrewAI 的核心抽象是**剧组（Crew）**：每个 `Agent` 有明确的 `role`（职责）、`goal`（要达成的结果）、`backstory`（行为风格与专业背景）。`Task` 描述具体交付物，并绑定到执行者。`Crew` 把多个 Task 按 **Process** 串起来执行。

| 概念 | 作用 |
| --- | --- |
| `role` | 对外身份，影响模型如何组织语言与优先级 |
| `goal` | 可验收的目标，宜写清输出形态 |
| `backstory` | 约束语气、方法论、禁忌（相当于软性 system） |
| `Task` | 单次工作单元，可指定 `agent`、`context`（上游任务输出） |
| `Process.sequential` | 严格按任务顺序执行，上一任务输出注入下一任务 |
| `Process.hierarchical` | 由 Manager Agent 分配子任务并汇总（适合动态分工） |

CrewAI 更贴近「**岗位说明书 + 流水线**」：你事先定义谁做什么、顺序如何，运行时较少出现「自由闲聊」。这对内容生产、竞品分析、报告生成等**流程稳定**的业务非常友好。

---

## 3. AutoGen / AG2：对话驱动的 GroupChat

AutoGen 将每个参与者建模为 **ConversableAgent**：既能调用 LLM，也能执行代码、调用函数。多 Agent 协作的典型模式是 **GroupChat**：所有消息进入共享频道，由 `GroupChatManager`（或新版中的 group chat 运行器）决定下一位发言者。

协作机制可以概括为：

1. **Message passing** — Agent A 的回复作为消息对象传给 B，可附带 `tool_calls` 与执行结果
2. **Speaker selection** — 轮询、`auto`（由 LLM 根据上下文选下一位）、或自定义函数
3. **Nested chat** — 子对话解决子问题，再把摘要回传主频道（控制上下文膨胀）

AG2（AutoGen 0.4+）在 API 上有所演进，但思想不变：**用对话历史作为共享状态机**，适合探索性任务、辩论式推理、需要多轮协商才能收敛的方案设计。代价是消息链更长，Token 与终止条件必须显式治理。

---

## 4. 对比一览

| 维度 | CrewAI | AutoGen / AG2 |
| --- | --- | --- |
| 协作隐喻 | 岗位 + 流水线 | 会议室群聊 |
| 状态载体 | Task 输出、`context` 链 | 共享 message 列表 |
| 流程可控性 | 高（sequential / hierarchical） | 中（依赖发言策略） |
| 动态分工 | hierarchical + Manager | GroupChat speaker 策略 |
| 人类在环 | 可在 Task 间插入审批 | `UserProxyAgent` 随时介入 |
| 学习曲线 | 低，YAML 感强 | 中，需理解消息与 Manager |
| 典型风险 | 角色模板化、任务拆太碎 | 对话发散、轮次失控 |

---

## 5. 代码示例

### 5.1 CrewAI：调研 → 撰稿 顺序流程

```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role="行业研究员",
    goal="收集 AI Agent 框架的 3 个对比维度与代表产品",
    backstory="你擅长结构化调研，只输出要点列表，不编造来源。",
    verbose=True,
)

writer = Agent(
    role="技术作者",
    goal="根据调研要点写一篇 800 字中文博客大纲",
    backstory="你面向开发者读者，语言简洁，小节清晰。",
    verbose=True,
)

research_task = Task(
    description="列出 CrewAI、AutoGen、OpenAI Agents SDK 的定位差异（各 3 条）",
    expected_output="Markdown 要点列表",
    agent=researcher,
)

write_task = Task(
    description="基于调研要点生成博客大纲（含 H2 标题）",
    expected_output="Markdown 大纲",
    agent=writer,
    context=[research_task],
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)

result = crew.kickoff()
print(result)
```

### 5.2 AutoGen：双 Agent 群聊直至终止

```python
import os
from autogen import ConversableAgent, GroupChat, GroupChatManager

llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ["OPENAI_API_KEY"]}]}

planner = ConversableAgent(
    name="planner",
    system_message="你负责拆解任务，每次只提出下一步，不直接写长文。",
    llm_config=llm_config,
)

coder = ConversableAgent(
    name="coder",
    system_message="你根据 planner 的步骤写 Python 示例，代码需可运行。",
    llm_config=llm_config,
)

user = ConversableAgent(name="user", human_input_mode="NEVER")

group = GroupChat(agents=[user, planner, coder], messages=[], max_round=6)
manager = GroupChatManager(groupchat=group, llm_config=llm_config)

user.initiate_chat(
    manager,
    message="为「多 Agent 选型」写一段对比结论，并附一个最小 CrewAI 示例。",
)
```

> 生产环境请将 `api_key` 置于环境变量，并为 `coder` 配置沙箱执行；示例仅展示协作形态。

---

## 6. Token 成本与终止策略

多 Agent 的账单通常**高于**单 Agent，因为同一上下文会在多个角色间重复传递。

**控费手段：**

1. **限制轮次** — CrewAI 控制 Task 数量；AutoGen 设置 `max_round` / `max_consecutive_auto_reply`
2. **摘要中间态** — 长调研结果先压缩再交给 Writer，避免全文在多 Agent 间复制
3. **模型分级** — 调研/分类用 mini，终稿/审校用 flagship
4. **早停条件** — 检测 `TERMINATE`、`任务完成` 等关键词，或工具返回成功即结束
5. **可观测性** — 对每次 `kickoff` / 每轮 GroupChat 记录 `prompt_tokens`、`completion_tokens`

**终止策略对照：**

| 框架 | 常见终止方式 |
| --- | --- |
| CrewAI | 所有 Task `completed`；`kickoff` 返回最终输出 |
| AutoGen | `max_round`、关键词、`is_termination_msg` 回调、`UserProxyAgent` 输入 `exit` |

没有显式终止的 GroupChat，很容易在「互相客气」中烧掉数倍 Token——这是 AutoGen 新手最常踩的坑。

---

## 7. 如何选型

**优先 CrewAI，若你：**

- 已有清晰的 SOP（市场调研 → 大纲 → 正文 → 审校）
- 需要给非技术同事展示「岗位分工」图
- 希望默认顺序执行、减少对话跑偏

**优先 AutoGen / AG2，若你：**

- 问题本身需要多轮协商或辩论才能收敛
- 需要灵活的 `UserProxy` 人类审批
- 已有代码执行、函数调用密集的 Agent 生态，希望统一在消息层集成

**仍可考虑单 Agent + 工作流引擎（如 LangGraph）**，当你要精细控制状态图、分支与持久化，而不想被「剧组」或「群聊」隐喻束缚时——系列前一篇 [OpenAI Agents SDK](/posts/agent-dev-openai-agents-sdk.html) 提供了另一种轻量编排路径。

---

## 8. 总结

CrewAI 用**角色扮演 + 任务流水线**降低「分工明确」类业务的编排成本；AutoGen 用**共享对话**释放「协商、迭代、人机共创」类场景的灵活性。二者不是替代关系，而是对不同协作形态的建模。落地时请先画清阶段交付物与终止条件，再选框架；否则多 Agent 只会把单 Agent 的混乱复制多份。

---

**系列导航 Series Navigation：**

- 上一篇：[OpenAI Agents SDK](/posts/agent-dev-openai-agents-sdk.html)
- 下一篇：[MCP 协议与 Server 开发](/posts/agent-dev-mcp-protocol.html)
