---
title: Agent 开发基础：Python 3.10+ 必备技能（类型注解 / 异步 / Pydantic）
date: 2026-06-05 17:00:00
categories:
  - python
tags:
  - Python
  - Agent
  - Pydantic
  - async
  - LLM
---

> 本系列第一篇：在写 LangGraph / CrewAI 之前，先把 Python 3.10+ 的语言特性打牢——它们是 Agent 工程化的地基。

如果你已经读过 [LLM Agent 架构全景](/posts/llm-agent-architecture-langchain-guide.html) 或 [LangGraph 生产指南](/posts/langgraph-production-agent-guide.html)，下一步往往不是换框架，而是把 **Python 本身** 用到框架设计者的预期水平。Agent 代码本质是「高并发 I/O + 松散 JSON + 长生命周期状态」——Python 3.10+ 的类型系统、异步模型和 Pydantic 恰好覆盖这三块。

下文默认运行环境 **Python ≥ 3.10**（推荐 3.11+，可使用 `TaskGroup`、`ExceptionGroup`）。示例力求可直接粘贴运行；涉及外部服务处用 `asyncio.sleep` 模拟。

---

## 1. 为什么 Python 是 Agent 开发的事实标准？

| 维度 | 说明 |
| --- | --- |
| 生态密度 | LangChain、LangGraph、CrewAI、LlamaIndex、AutoGen 均以 Python 为第一公民 |
| 迭代速度 | Prompt / Tool / Graph 改动频繁，动态语言 + REPL 降低实验成本 |
| 模型侧同源 | 多数推理服务 SDK、微调脚本、评测管线默认 Python |
| 互操作 | 通过 HTTP/gRPC 暴露服务后，Node/Go 可消费，但 **编排层** 仍多在 Python |

```text
用户请求 → Agent 编排 (Python) → LLM API
                ↓
         Tool: 搜索 / DB / 代码执行
                ↓
         结构化输出校验 (Pydantic)
```

**LangChain** 提供 LCEL 管道与海量集成，适合快速搭 RAG 和 ReAct；**LangGraph** 在其之上提供图状态机、Checkpoint、人工审批，是 2026 生产 Agent 的首选运行时；**CrewAI** 用「角色 + 目标」描述多 Agent 协作，降低团队分工建模成本。三者的官方示例、中间件、LangSmith Trace 插件几乎都以 Python 发布，社区 Issue 与 Stack Overflow 解答也集中在此语言。

2026 年的主流路径是：**Python 做 Agent 大脑与编排，TypeScript/Go 做边缘 API 与前端**。这不是说 Python 性能最强，而是 **生态位** 已经锁定：换语言意味着重写 Tool 适配层与评测脚本。本系列后续会讲 Node 侧实践；本篇专注 Python 地基。

---

## 2. 类型注解：Agent State 的「契约」

LangGraph 的 `StateGraph`、CrewAI 的 Task 输出、PydanticAI 的依赖注入，都假设你能用类型描述 **图状态** 与 **工具 I/O**。没有类型时，十个节点各自往 `state` 里塞不同形状的 dict，一周后就没人敢改字段名。

Python 3.10+ 的三个高频构造：

| 构造 | Agent 场景 |
| --- | --- |
| `TypedDict` | LangGraph 共享状态、可增量 merge 的字段 |
| `Annotated[..., reducer]` | 消息列表追加、计数器累加等 reducer |
| `Generic[T]` | 可复用的 `ToolResult[T]`、`MemoryStore[T]` |

```python
from dataclasses import dataclass
from typing import Annotated, Generic, TypedDict, TypeVar

T = TypeVar("T")

def append_messages(existing: list, new: list) -> list:
    return existing + new

class AgentState(TypedDict):
    messages: Annotated[list[dict], append_messages]
    step_count: int
    pending_tool: str | None  # 3.10+ 联合类型写法

@dataclass
class ToolResult(Generic[T]):
    ok: bool
    data: T
    error: str | None = None
```

`TypedDict` 适合 **可部分更新** 的图状态：节点只返回变更字段，框架负责 merge。`Annotated[..., reducer]` 告诉 LangGraph「这个字段不要覆盖，要交给 reducer 合并」——消息历史就是最典型的例子。`Generic[T]` 则用于封装工具返回值，让搜索工具返回 `ToolResult[list[str]]`、数据库工具返回 `ToolResult[Row]`，调用方一眼能看懂。

配合 `mypy` 或 Pyright，能在 **改 State 字段时** 提前发现节点返回值与图定义不一致——比运行到一半才 `KeyError` 便宜得多。建议在 CI 中对 `agent/` 目录开启 `--strict` 或等价配置，把类型债务拦在合并请求之前。

---

## 3. async/await：并发 Tool 与流式 LLM

Agent 一轮循环往往要：调 LLM（秒级）→ 并行查多个 API → 写库 → 再调 LLM。同步写法在 FastAPI / uvicorn 下会占满线程池，并发上来后延迟陡增；`asyncio` 让你在 **单线程** 里挂起等待，把 CPU 让给其它协程。

LangChain 的 `ainvoke`、`astream_events` 与 OpenAI SDK 的 `AsyncOpenAI` 都是为这种模型设计的。务必整条链路统一 async：中间夹杂一次同步 `requests.get`，就会阻塞整个事件循环。

```python
import asyncio
from collections.abc import AsyncIterator

async def call_search(query: str) -> str:
    await asyncio.sleep(0.1)  # 模拟 HTTP
    return f"results for {query}"

async def stream_llm(prompt: str) -> AsyncIterator[str]:
    for chunk in ["Hello", ", ", "world"]:
        yield chunk
        await asyncio.sleep(0.05)

async def agent_turn(user: str) -> str:
    # 并行执行多个 Tool
    weather, news = await asyncio.gather(
        call_search(f"weather {user}"),
        call_search(f"news {user}"),
    )
    parts: list[str] = []
    async for token in stream_llm(f"{weather}\n{news}"):
        parts.append(token)
    return "".join(parts)

# asyncio.run(agent_turn("Shanghai"))
```

注意：`asyncio.gather` 适合 **无依赖** 的 Tool；有依赖时用顺序 `await` 或 `asyncio.TaskGroup`（3.11+），任一子任务失败时可按组取消。流式响应用 `async for` 消费，便于边生成边推送给前端 SSE，同时把首 token 时间（TTFT）压进产品指标。

若必须调用同步 SDK（例如部分老版向量库），使用 `await asyncio.to_thread(blocking_fn, *args)` 把阻塞丢进线程池，避免「假 async」。

---

## 4. dataclass vs Pydantic：为什么 Agent I/O 选 Pydantic

LLM 返回的是 **近似 JSON 的文本**：Markdown 代码块包裹、尾逗号、注释、字段名大小写混乱都是日常。`@dataclass` 适合 **你完全控制构造过程** 的内部结构体；一旦数据来自模型或外部 HTTP，缺少运行时校验就等于把 bug 推迟到业务深处。

| | `@dataclass` | `pydantic.BaseModel` |
| --- | --- | --- |
| 运行时校验 | 无（除非手写 `__post_init__`） | 内置，可配置 `extra="forbid"` |
| JSON Schema | 需额外生成 | 原生，便于 OpenAI `response_format` |
| 嵌套 / 联合类型 | 手动 | `Field`、`model_validator` 一条龙 |
| 性能 | 更轻 | v2 用 Rust 核心，生产可接受 |

```python
from pydantic import BaseModel, Field, field_validator

class ToolCall(BaseModel):
    name: str
    arguments: dict[str, object]

class AgentOutput(BaseModel):
    thought: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    final_answer: str | None = None

    @field_validator("tool_calls")
    @classmethod
    def cap_tools(cls, v: list[ToolCall]) -> list[ToolCall]:
        if len(v) > 5:
            raise ValueError("too many tool calls in one turn")
        return v

# 模拟 LLM 脏输出
raw = {"thought": "查天气", "tool_calls": [{"name": "search", "arguments": {"q": "北京"}}]}
out = AgentOutput.model_validate(raw)
```

对比一段 **仅 dataclass** 的写法——能跑，但无法拒绝多余字段，也不会在 `arguments` 不是 dict 时立刻报错：

```python
from dataclasses import dataclass

@dataclass
class ToolCallDc:
    name: str
    arguments: dict

# 脏数据静默通过
bad = ToolCallDc(name="search", arguments="not-a-dict")  # 运行时不报错
```

**实践建议：** 图内部状态可用 `TypedDict`（偏 LangGraph 惯例）；**对外 API、Tool 参数、LLM 结构化输出** 一律 Pydantic。校验失败时捕获 `ValidationError`，把 `errors()` 格式化成自然语言 Observation 喂回模型，往往比硬编码「输出格式错误」更能触发自我纠正。

---

## 5. 上下文管理器：连接与客户端的生命周期

Agent 进程常是 **长驻服务**：一个 uvicorn worker 会处理成千上万次对话。数据库连接池、`httpx.AsyncClient`、Chroma 临时索引、沙箱子进程都必须在 **请求结束或图执行结束** 时释放，否则文件描述符与连接泄漏会在凌晨把生产搞挂。

`with` 语句保证 **正常返回与异常抛出** 都会执行清理；`@contextmanager` / `@asynccontextmanager` 让你把「获取资源 → yield → 释放」封装成可复用的工厂函数。

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

class FakeConn:
    async def close(self) -> None:
        pass

async def open_connection() -> FakeConn:
    return FakeConn()

@asynccontextmanager
async def get_db() -> AsyncGenerator[FakeConn, None]:
    conn = await open_connection()
    try:
        yield conn
    finally:
        await conn.close()

async def do_agent_work(db: FakeConn) -> str:
    return "done"

async def run_with_resources() -> None:
    async with get_db() as db:
        result = await do_agent_work(db)
        assert result == "done"

# asyncio.run(run_with_resources())
```

同步场景用 `with open(...) as f` 读 prompt 模板；异步资源用 `async with`。FastAPI 的 `lifespan` 在应用启动时创建全局 `AsyncClient`、在关闭时 `aclose()`；LangGraph 的 Postgres `checkpointer` 同样应在 lifespan 里初始化一次、全程复用，而不是每个节点 new 一个连接。

---

## 6. 常见陷阱（Agent Python 代码）

上线 Agent 后，约一半稳定性问题出在 **语言层误用**，而非 Prompt。下面这张表来自常见 on-call 复盘：

| 陷阱 | 现象 | 对策 |
| --- | --- | --- |
| 在 async 里调阻塞 SDK | 事件循环卡死，QPS 归零 | `asyncio.to_thread()` 或换 async 客户端 |
| 忽略 `ValidationError` | 脏 JSON 直接 `.get()` 导致静默错误 | Pydantic 校验 + 错误信息回灌 LLM |
| State 无类型 | 节点间字段名拼写错误 | `TypedDict` + CI 跑 mypy |
| 全局可变状态 | 多请求串话 | State  per `thread_id` / `session_id` |
| 无限 `gather` | 一次发起上百 Tool 打爆下游 | 信号量 `Semaphore` 限制并发 |
| 混用 sync/async LangChain | 偶发挂起 | 统一 `ainvoke` / `astream` 链路 |

```python
import asyncio

sem = asyncio.Semaphore(3)

async def fetch(url: str) -> str:
    await asyncio.sleep(0.05)
    return url

async def bounded_tool(url: str) -> str:
    async with sem:
        return await fetch(url)
```

---

另有两处易忽略：**在热路径里 `print` 调试** 会污染结构化日志，应使用 `logging` 或 OpenTelemetry；**把巨大对象塞进 State**（完整网页 HTML、未截断 PDF）会导致 Checkpoint 体积爆炸，应在节点内落盘或向量库，State 只留引用 ID。

---

## 7. 小结与系列导航

掌握 **TypedDict/Annotated 描述状态**、**async 并发 Tool 与流式输出**、**Pydantic 守住 LLM 边界**、**async context manager 管住资源**，你就具备了阅读 LangGraph/CrewAI 源码和写生产 Agent 的语言基础。框架 API 每个季度都在变，但这四块在 2026 依然是最值得投入的学习时间。

建议动手练习：用本文的 `AgentState` + `AgentOutput` 写一个最小 ReAct 循环（不引框架），再对照 LangGraph 官方教程迁移——你会明显感到「原来框架替我做了哪些脏活」。

**系列下一篇：** [Agent 开发基础：TypeScript / Node.js 侧实践](/posts/agent-dev-typescript-nodejs.html) —— 当你的 Agent 需要暴露 REST、对接前端 SSE，或团队主力栈在 Node 时该如何与 Python 编排层分工。

---

相关阅读：[LangGraph 深度指南：从图状态机到生产级 Agent](/posts/langgraph-production-agent-guide.html) · [LLM Agent 架构全景](/posts/llm-agent-architecture-langchain-guide.html)
