---
title: LangGraph 深度指南：从图状态机到生产级 Agent（中英文对照）
date: 2026-06-05 16:30:00
categories:
  - framework
tags:
  - LangGraph
  - LangChain
  - Agent
  - LLM
  - AI
---

> **English Title:** LangGraph Deep Dive — From Graph State Machines to Production-Grade Agents

如果你已经用 LangChain 写过 ReAct Agent，却在生产环境遇到 **状态丢失、崩溃无法恢复、无法人工审批、循环失控** 等问题，LangGraph 就是为此而生的。本文从架构原理到可运行代码，带你系统掌握 LangGraph。

*If you've built ReAct agents with LangChain but hit **state loss, crash recovery gaps, missing human approval, and runaway loops** in production, LangGraph was built for exactly these problems. This article covers architecture and runnable code to help you master LangGraph systematically.*

---

## 1. LangGraph 是什么？| What Is LangGraph?

**中文：** LangGraph 是 LangChain 团队开发的 **有向图状态机运行时**，将 Agent 工作流建模为：

- **State（状态）** — 贯穿全流程的共享数据结构
- **Node（节点）** — 处理步骤（LLM 调用、工具执行、自定义函数）
- **Edge（边）** — 节点间的流转逻辑（含条件分支）

**English:** LangGraph is a **directed graph state-machine runtime** from the LangChain team. It models agent workflows with:

- **State** — Shared data structure flowing through the pipeline
- **Node** — Processing steps (LLM calls, tool execution, custom functions)
- **Edge** — Transition logic between nodes (including conditional branches)

```text
         ┌──────────┐
         │  START   │
         └────┬─────┘
              ▼
         ┌──────────┐
         │ Planner  │  ← 分析任务、制定计划
         └────┬─────┘
              ▼
         ┌──────────┐     No
    ┌────│ Need Tool?├──────┐
    │Yes └────┬─────┘      │
    ▼        │             ▼
┌────────┐   │        ┌──────────┐
│  Tool  │   │        │ Response │
└───┬────┘   │        └──────────┘
    ▼        │
┌────────┐   │
│Evaluator├──┘ (retry / done / human review)
└────────┘
```

与 LangChain 的 `create_agent` 相比，LangGraph 是 **底层运行时** 而非高层封装——你获得完全的控制权，代价是更多样板代码。

*Compared to LangChain's `create_agent`, LangGraph is a **low-level runtime**, not a high-level wrapper — you get full control at the cost of more boilerplate.*

---

## 2. 核心概念详解 | Core Concepts

### 2.1 State — 状态模式

**中文：** State 通常用 `TypedDict` 定义，每个节点读取并返回状态更新。LangGraph 自动合并（merge）各节点的返回值。

**English:** State is typically defined with `TypedDict`. Each node reads and returns state updates; LangGraph automatically merges node outputs.

```python
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # 消息列表，自动追加
    step_count: int                           # 循环计数器
    needs_human: bool                         # 是否需要人工审批
```

`add_messages` 是 LangGraph 内置的 reducer：新消息追加到列表，而非覆盖。

*`add_messages` is a built-in reducer: new messages are appended, not overwritten.*

### 2.2 Node — 节点函数

**中文：** 节点是普通 Python 函数，接收当前 State，返回 State 更新字典。

**English:** A node is a plain Python function that receives the current State and returns a state update dict.

```python
def call_llm(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],
        "step_count": state["step_count"] + 1,
    }

def call_tool(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_result = execute_tool(last_message.tool_calls)
    return {"messages": [tool_result]}
```

### 2.3 Edge — 条件路由

**中文：** 条件边根据 State 动态决定下一个节点，这是 LangGraph 超越简单 Chain 的关键能力。

**English:** Conditional edges dynamically choose the next node based on State — LangGraph's key advantage over simple chains.

```python
def should_continue(state: AgentState) -> str:
    if state["step_count"] > 10:
        return "end"                    # 超过最大步数，强制结束
    if state["needs_human"]:
        return "human_review"           # 需要人工审批
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"                  # 有工具调用，执行工具
    return "end"                        # 无工具调用，结束
```

---

## 3. 完整示例：带工具调用的 Agent | Full Example

**中文：** 以下是一个最小可运行的 LangGraph Agent，包含 LLM 推理、工具执行和循环控制。

**English:** Below is a minimal runnable LangGraph agent with LLM reasoning, tool execution, and loop control.

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """搜索网络获取信息。"""
    return f"搜索结果: {query} 的相关信息..."

@tool
def calculate(expression: str) -> str:
    """计算数学表达式。"""
    return str(eval(expression))

tools = [search_web, calculate]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

# 构建图
graph = StateGraph(AgentState)
graph.add_node("agent", call_llm)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    "end": END,
    "human_review": "human_review",
})
graph.add_edge("tools", "agent")

app = graph.compile()
result = app.invoke({"messages": [("user", "北京今天天气如何？")], "step_count": 0})
```

---

## 4. 生产级特性 | Production Features

### 4.1 Checkpointing — 状态持久化

**中文：** Checkpointing 将每个状态转换持久化到数据库（SQLite、PostgreSQL 等），实现：

- **崩溃恢复** — 从最后检查点继续执行
- **Time-travel Debugging** — 回溯任意历史状态
- **多用户会话** — 通过 `thread_id` 隔离不同用户

**English:** Checkpointing persists each state transition to a database (SQLite, PostgreSQL, etc.), enabling:

- **Crash recovery** — Resume from the last checkpoint
- **Time-travel debugging** — Replay any historical state
- **Multi-user sessions** — Isolate users via `thread_id`

```python
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string(":memory:")
app = graph.compile(checkpointer=memory)

# 使用 thread_id 隔离会话
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke(input_state, config)
```

### 4.2 Human-in-the-Loop — 人工介入

**中文：** 在关键节点设置 **断点（Breakpoint）**，图执行到此处暂停，等待人工输入后恢复。

**English:** Set **breakpoints** at critical nodes; the graph pauses and resumes after human input.

```python
from langgraph.types import interrupt

def human_review_node(state: AgentState) -> dict:
    # 暂停执行，等待人工审批
    approval = interrupt({
        "question": "是否批准此操作？",
        "action": state["messages"][-1].content,
    })
    if approval == "approved":
        return {"needs_human": False}
    return {"messages": [("system", "操作已被拒绝")]}
```

```python
# 编译时设置断点
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["human_review"],
)

# 恢复执行
app.invoke(None, config)  # 传入 None 从断点继续
```

### 4.3 流式输出 | Streaming

**中文：** LangGraph 支持 Token 级流式输出，改善用户体验。

**English:** LangGraph supports token-level streaming for better UX.

```python
for event in app.stream(input_state, config, stream_mode="messages"):
    node_name, message = event
    print(f"[{node_name}] {message.content}")
```

### 4.4 子图嵌套 | Sub-graph Composition

**中文：** 一个完整的图可以作为另一个图的节点，实现模块化复用。

**English:** A complete graph can become a node in a parent graph for modular reuse.

```python
research_graph = build_research_subgraph()
writing_graph = build_writing_subgraph()

main_graph = StateGraph(MainState)
main_graph.add_node("research", research_graph.compile())
main_graph.add_node("writing", writing_graph.compile())
```

---

## 5. LangGraph vs LangChain vs CrewAI | Comparison

| 维度 Dimension | LangChain | LangGraph | CrewAI |
| --- | --- | --- | --- |
| 抽象层级 Level | 高层 High | 底层 Low | 中高层 Mid-high |
| 状态管理 State | 无原生 No native | 显式持久 Explicit | 内置记忆 Built-in |
| 循环/分支 Loops | 有限 Limited | 原生 Native | 有限 Limited |
| Checkpoint | ❌ | ✅ | ❌ |
| HITL | 中间件 Middleware | 原生 Native | 可选 Optional |
| 上手难度 Learning curve | 低 Low | 高 High | 低 Low |
| 生产就绪 Production | 中 Medium | 高 High | 中 Medium |
| 可观测性 Observability | LangSmith | LangSmith | 第三方 3rd-party |

**选型建议 Selection advice：**

- 简单 RAG / 单轮工具调用 → **LangChain `create_agent`**
- 复杂工作流 / 生产系统 → **LangGraph**
- 快速多 Agent 原型 → **CrewAI**
- 高可靠性 API → **PydanticAI + LangGraph**

---

## 6. 与 LangSmith 集成 | LangSmith Integration

**中文：** LangSmith 为 LangGraph 提供全链路可观测性：

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-agent"
```

在 LangSmith 控制台可查看：

- 每个节点的输入/输出
- LLM 调用的 Prompt 和 Response
- 工具执行的参数和返回值
- 端到端延迟和 Token 消耗

**English:** LangSmith provides full-chain observability for LangGraph. In the console you can inspect per-node I/O, LLM prompts/responses, tool args/results, and end-to-end latency and token usage.

---

## 7. 生产部署清单 | Production Checklist

**中文：**

| 检查项 | 说明 |
| --- | --- |
| ✅ 终止条件 | `step_count` 上限、超时、Token 预算 |
| ✅ Checkpoint | 生产环境用 PostgreSQL 而非 SQLite |
| ✅ HITL | 资金/删除/外发操作必经审批 |
| ✅ 工具权限 | 最小权限原则，避免 Agent 越权 |
| ✅ 结构化输出 | 关键节点强制 JSON Schema |
| ✅ 错误处理 | 节点内 try/catch + 图级 fallback 边 |
| ✅ 可观测性 | LangSmith Trace + 告警 |
| ✅ 评估集 | Golden Dataset 回归测试 |

**English:**

| Check | Description |
| --- | --- |
| ✅ Termination | `step_count` cap, timeout, token budget |
| ✅ Checkpoint | PostgreSQL in production, not SQLite |
| ✅ HITL | Human approval for financial/delete/outbound ops |
| ✅ Tool permissions | Least privilege; prevent escalation |
| ✅ Structured output | Enforce JSON Schema at critical nodes |
| ✅ Error handling | try/catch in nodes + graph-level fallback edges |
| ✅ Observability | LangSmith traces + alerts |
| ✅ Evaluation | Golden Dataset regression tests |

---

## 8. 常见陷阱 | Common Pitfalls

**中文：**

1. **状态膨胀** — `messages` 列表无限增长，需定期摘要压缩
2. **循环死锁** — 忘记设置 `step_count` 上限，Agent 反复调用同一工具
3. **Checkpoint 膨胀** — 高频写入导致存储暴涨，需设置保留策略
4. **过度设计** — 简单顺序流程不需要 LangGraph，用 LangChain Chain 即可
5. **忽略评估** — 没有 Golden Dataset，Prompt 微调后无法验证回归

**English:**

1. **State bloat** — Unbounded `messages`; summarize periodically
2. **Loop deadlock** — Missing `step_count` cap; agent retries the same tool forever
3. **Checkpoint bloat** — High-frequency writes; set retention policies
4. **Over-engineering** — Simple sequential flows don't need LangGraph
5. **Skipping evaluation** — No Golden Dataset means no regression verification

---

## 9. 总结 | Conclusion

**中文：** LangGraph 的核心价值在于 **将 Agent 工作流从黑盒循环变成可审计、可恢复、可介入的状态机**。学习曲线虽陡，但对于需要生产级可靠性的系统，这是目前最成熟的开源选择。推荐路径：

1. 用 LangChain `create_agent` 验证业务价值
2. 遇到状态/循环/审批需求时迁移到 LangGraph
3. 配合 LangSmith 建设可观测性与评估体系
4. 复杂 Agent 逻辑用 PydanticAI 保证类型安全

**English:** LangGraph's core value is **turning agent workflows from opaque loops into auditable, recoverable, interruptible state machines**. The learning curve is steep, but for production reliability it remains the most mature open-source choice. Recommended path:

1. Validate business value with LangChain `create_agent`
2. Migrate to LangGraph when you need state, loops, or approvals
3. Build observability and evaluation with LangSmith
4. Use PydanticAI for type-safe complex agent logic

---

相关阅读 Related reading：[LLM Agent 架构全景：LangChain 生态设计与实践](/posts/llm-agent-architecture-langchain-guide.html)
