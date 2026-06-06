---
title: Agent 框架核心：LangChain 与 LangGraph 面试必考知识点
date: 2026-06-05 17:25:00
categories:
  - framework
tags:
  - LangChain
  - LangGraph
  - Agent
  - LLM
  - AI
---

> **English Title:** LangChain & LangGraph Essentials for Agent Development — Interview Must-Knows

你已读过 [LLM Agent 架构全景](/posts/llm-agent-architecture-langchain-guide.html) 与 [LangGraph 生产实践](/posts/langgraph-production-agent-guide.html)，本文不再重复生态鸟瞰或部署细节，而是把 **面试与上手** 最常考的两块——**LangChain 的 Runnable / LCEL / Agent 循环** 与 **LangGraph 的图运行时**——压缩成可背诵、可写代码的知识清单。

前置知识建议：已完成 [Embedding 与向量检索](/posts/agent-dev-embedding-vector-search.html)，理解 RAG 如何把检索结果注入 Prompt；模型调用见系列中的 API 实战文。下文默认使用 OpenAI 兼容的 `ChatOpenAI`，换 DeepSeek / Qwen 只需改构造参数。

---

## 0. 30 秒心智模型

```text
用户输入 → LCEL 链（可选 RAG）→ Agent：LLM + bind_tools
                ↓ 多轮 tool call
         AgentExecutor（黑盒循环）  或  LangGraph（显式图 + Checkpoint）
                ↓
           最终 AIMessage / 结构化输出
```

面试官常顺着这条线追问：**消息类型有哪些、谁执行工具、状态存在哪、如何防死循环**。下面按模块拆开。

---

## 1. LCEL：链式组合的核心语法

**LCEL（LangChain Expression Language）** 把任意组件统一为 `Runnable`：`invoke` / `batch` / `stream` 接口一致，便于替换模型、加日志、做评测。

| 运算符 | 含义 | 典型用途 |
| --- | --- | --- |
| `\|` | 顺序管道 | `prompt \| llm \| parser` |
| `RunnablePassthrough.assign` | 并行写入字段 | RAG 里同时保留 `question` 与 `context` |
| `RunnableLambda` | 任意 Python 函数 | 格式化、校验、路由前处理 |

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是简洁的技术助手。"),
    ("human", "{question}"),
])
chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()

print(chain.invoke({"question": "什么是 LCEL？"}))
# chain.stream(...) 同样可用
```

**面试要点：** LCEL 的价值是 **组合性 + 可观测性**（LangSmith 自动 trace 每个 Runnable），不是「又一种 DSL」。`RunnableConfig` 里的 `callbacks`、`tags` 用于链路追踪；`configurable_fields` 支持运行时换模型。

**常考扩展：**

- **并行与分支：** `RunnableParallel({"ctx": retriever, "q": RunnablePassthrough()})` 再 `| prompt` 是 RAG 标准写法；`with_fallbacks([primary, backup])` 用于模型降级。
- **输入输出契约：** 链的输入/输出类型在编译期可推断（`get_input_schema`），便于写单元测试与 JSON 校验。
- **与 Agent 的关系：** Agent 内部仍是 Runnable；`AgentExecutor` 是对「agent Runnable + 工具执行循环」的包装，不是另一套 API。

手写 `for` 循环拼 prompt 也能跑，但失去统一 `stream`、批量评测与 Trace 切片，团队规模一大就难以维护——这是 LCEL 的工程理由，而非语法炫技。

---

## 2. Tool 定义与绑定（bind_tools）

Tool 是 Agent 与外部世界的契约：名称、描述、参数 Schema 直接影响模型是否 **选对工具、填对参数**。

```python
from langchain_core.tools import tool

@tool
def search_docs(query: str, top_k: int = 3) -> str:
    """在内部知识库检索文档。query 为自然语言问题，top_k 为返回条数。"""
    return f"mock hits for: {query}"

tools = [search_docs]
llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)
```

**要点：**

- 描述要写清 **何时调用、输入含义、失败时返回什么**，比函数名更重要。
- `bind_tools` 后模型输出 `tool_calls`；由 **ToolNode** 或自定义节点执行并写回 `ToolMessage`。
- 结构化工具可用 Pydantic `BaseModel` 或 `@tool` 自动生成 JSON Schema。
- **错误即 Observation：** 工具抛错应捕获后返回可读字符串，让模型改参数重试，而不是让整个 Agent 崩溃。

```python
from langchain_core.messages import ToolMessage

# ToolNode 执行后，消息序列为：
# HumanMessage → AIMessage(tool_calls=[...]) → ToolMessage(tool_call_id=...) → AIMessage(最终回答)
```

**面试陷阱：** 混淆 `functions` 旧 API 与 `bind_tools` / `tool_calls` 新 API；当前主流是 OpenAI 式 tool calling，Claude 走同一套 `langchain-anthropic` 适配层。

---

## 3. Agent Executor 与 ReAct 循环

经典 **ReAct**：Thought → Action（tool + args）→ Observation → 循环，直到模型不再发起 tool call 或达到 `max_iterations`。

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你有 search_docs。无法回答时说明原因。"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(ChatOpenAI(model="gpt-4o-mini"), tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)

result = executor.invoke({"input": "LangGraph 和 AgentExecutor 区别？", "chat_history": []})
```

**面试常问：**

| 概念 | 一句话 |
| --- | --- |
| `agent_scratchpad` | 存放本轮已发生的 tool 调用与结果，供模型继续推理 |
| `max_iterations` | 防止死循环；生产必须设 |
| `handle_parsing_errors` | 模型输出非合法 tool JSON 时的降级策略 |
| 与 LangGraph 关系 | AgentExecutor 是 **封装好的 ReAct 循环**；LangGraph 可手写同等逻辑并加分支、持久化 |

**局限（必答）：** 状态全在内存、难以精确插入人工节点、复杂分支要用 LangGraph。

**消息类型速记表（必背）：**

| 类型 | 谁产生 | 作用 |
| --- | --- | --- |
| `HumanMessage` | 用户 / 上游 | 任务输入 |
| `AIMessage` | 模型 | 文本或 `tool_calls` |
| `ToolMessage` | 工具执行器 | 携带 `tool_call_id` 与执行结果 |
| `SystemMessage` | 开发者 | 角色与约束（部分模型放首条） |

`early_stopping_method="generate"` 可在达到 `max_iterations` 时让模型强行总结，避免直接抛异常——生产可观测性要记录 **停止原因**（正常结束 / 超步 / 解析失败）。

---

## 4. LangGraph：State、Node、Edge、条件路由

LangGraph 把流程建模为 **有向图**，共享 `State`，节点返回 **部分状态更新**，框架负责 merge。

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    resp = ChatOpenAI(model="gpt-4o-mini").invoke(state["messages"])
    return {"messages": [resp]}

def should_continue(state: State) -> str:
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END

graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))  # langgraph.prebuilt
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")
app = graph.compile()
```

| 术语 | 作用 |
| --- | --- |
| **State** | 全流程共享；常用 `add_messages` 追加消息 |
| **Node** | 纯函数 `(state) -> partial_state` |
| **Edge** | 固定下一跳 |
| **conditional_edges** | 根据 state 动态选路（ReAct 的「是否再调工具」） |
| **compile()** | 生成可 `invoke/stream` 的 `CompiledGraph` |
| **子图 subgraph** | 把多 Agent 团队封装为单节点，对外仍是一个 State 更新 |

`START` / `END` 是哨兵节点；条件函数返回的字符串必须与 `conditional_edges` 第三参数字典的 **键** 一致，否则运行时报路由错误——面试手写代码时极易漏写映射表。

---

## 5. Checkpointing 与 Human-in-the-Loop（HITL）

**Checkpointing** 把每一步 State 持久化（内存 `MemorySaver` 或 Postgres `PostgresSaver`），支持：

- 进程崩溃后 **从上次节点恢复**
- 多轮对话 **thread_id** 隔离会话
- **时间旅行** 调试（LangGraph Studio）

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "user-42"}}
app.invoke({"messages": [HumanMessage("查一下部署文档")]}, config)
```

**HITL** 常用 `interrupt_before=["sensitive_tool"]`：图在指定节点前暂停，人工审批后 `app.invoke(None, config)` 继续。面试要区分：**HITL 是图级中断**，不是 Prompt 里写「请人类确认」。

典型审批流：

```text
agent 节点 →（interrupt_before tools）→ 等待人工 API 写入 state
         → 同一 thread_id 再次 invoke → tools 节点执行 → agent
```

`checkpoint_id` 与 `thread_id` 要纳入多租户设计：同一用户多设备、客服转接场景都依赖 thread 隔离。内存 `MemorySaver` 仅适合本地调试；生产用 Postgres / Redis 等后端，细节见 [LangGraph 生产指南](/posts/langgraph-production-agent-guide.html)。

---

## 6. LangChain vs LangGraph：何时用哪个？

| 场景 | 推荐 | 理由 |
| --- | --- | --- |
| 单 Agent + 少量工具、快速验证 | LangChain `AgentExecutor` | 样板少、上手快 |
| 多分支、子图、循环上限精细控制 | LangGraph | 显式图 = 可测试、可观测 |
| 要持久化会话 / 崩溃恢复 | LangGraph + Checkpointer | AgentExecutor 无一等持久化 |
| 审批、合规闸门 | LangGraph `interrupt` | 节点级暂停 |
| 纯 RAG 问答链 | LCEL 即可 | 不必上图 |

**记忆口诀：** LangChain 管 **组件与链**；LangGraph 管 **有状态、可恢复的编排运行时**。二者可共存：节点内仍用 LangChain 的 model、tool、retriever。

---

## 7. Runnable 综合示例（迷你 ReAct 图）

```python
# 编译后的一次调用
out = app.invoke(
    {"messages": [HumanMessage("用 search_docs 查 LCEL")]},
    {"configurable": {"thread_id": "demo-1"}},
)
for m in out["messages"]:
    print(type(m).__name__, getattr(m, "content", "")[:80])
```

生产前检查清单：**max 步数 / token 预算**、**tool 超时**、**checkpointer 后端**、**thread_id 与租户隔离**、LangSmith `LANGCHAIN_TRACING_V2=true`。

**与 Embedding 系列衔接：** 检索链用 LCEL（`retriever | format_docs | prompt | llm`），Agent 链在检索结果之上再 `bind_tools` 做「查不到就调搜索 / 工单」类决策；向量库本身不是 LangGraph 的一部分，但常作为图中的独立 `retrieve` 节点，便于单独缓存与评测。

---

## 8. 面试 FAQ 速记

**Q1：LCEL 和直接写 Python 函数拼 prompt 有什么区别？**  
统一 Runnable 接口，便于 stream、batch、组合与追踪；换模型只改链中一段。

**Q2：`bind_tools` 之后谁执行工具？**  
模型只生成 `tool_calls`；执行器（AgentExecutor / ToolNode）负责调用并注入 `ToolMessage`。

**Q3：LangGraph 的 State 为什么用 `Annotated[list, add_messages]`？**  
定义 **reducer**：新消息追加而非覆盖，避免多节点写同一字段时丢历史。

**Q4：conditional_edges 和 AgentExecutor 内部路由有何不同？**  
前者 **显式、可单测**；后者黑盒在 executor 里，分支逻辑难定制。

**Q5：Checkpoint 存的是什么？**  
每个 super-step 后的完整 State 快照 + 元数据，用于恢复与 HITL 续跑。

**Q6：为什么生产 Agent 常从 AgentExecutor 迁到 LangGraph？**  
要 **持久化、人工审批、精确循环控制、多 Agent 子图**——这些在图里是一等公民。

**Q7：和 CrewAI / AutoGen 比？**  
LangChain/LangGraph 偏 **可编程编排与生态集成**；CrewAI 偏角色剧本，AutoGen 偏对话式多 Agent。选型看团队是否要细粒度控制图与 Checkpoint。

**Q8：`stream` 在图里怎么用？**  
`app.stream(inputs, config)` 按 **节点完成** 产出事件，适合 SSE 推前端；与 LLM token 级 `stream` 可嵌套在节点内部。

**Q9：如何测试 Agent？**  
对 LCEL 链 mock LLM；对 LangGraph 测 **条件路由函数** 与单节点逻辑，再集成测 golden thread；避免只测最终字符串（易 flaky）。

**常见踩坑：**

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 无限调同一工具 | 描述含糊或 Observation 为空 | 收紧 tool docstring；限制 `max_iterations` |
| 丢历史 | State 字段未用 reducer | `add_messages` 等 Annotated reducer |
| HITL 无法续跑 | thread_id 不一致 | 客户端持久化 `configurable.thread_id` |
| Token 爆炸 | scratchpad 无裁剪 | 摘要节点或只保留最近 N 条 ToolMessage |

---

## 9. 小结

掌握 **LCEL 组合 → Tool 绑定 → ReAct 循环 → 图 State/Node/Edge → Checkpoint/HITL → 场景选型**，足以应对大多数 Agent 框架面试题。实现时先用 LangChain 跑通工具链，再在 LangGraph 里把「是否继续调工具」「是否人工审批」画成显式边——这与 [架构全景文](/posts/llm-agent-architecture-langchain-guide.html) 的 ReAct / 图状态机划分一致，而 [生产指南](/posts/langgraph-production-agent-guide.html) 可继续深入 PostgresSaver、Studio 与监控。

下一篇将对比 [OpenAI Agents SDK](/posts/agent-dev-openai-agents-sdk.html) 的声明式 Agent 与 Handoff，帮助你在「LangChain 生态」与「官方 SDK」之间做技术选型。

---

## 系列导航

- 上一篇：[Embedding 与向量检索](/posts/agent-dev-embedding-vector-search.html)
- 下一篇：[OpenAI Agents SDK](/posts/agent-dev-openai-agents-sdk.html)
