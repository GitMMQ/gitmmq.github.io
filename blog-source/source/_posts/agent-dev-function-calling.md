---
title: Function Calling 深度解析：Tool Use 参数设计、并行调用与错误处理
date: 2026-06-05 17:45:00
categories:
  - framework
tags:
  - Function Calling
  - Tool Use
  - Agent
  - OpenAI
  - LLM
---

> **English Title:** Function Calling Deep Dive — Tool Schema Design, Parallel Calls & Error Handling

MCP 把工具暴露成标准协议之后，模型侧如何「选中工具、填好参数、消化结果」仍是 Agent 落地的核心。Function Calling（也称 Tool Use）不是让 LLM 直接执行代码，而是让模型输出**结构化调用意图**，由你的运行时真正执行并回传结果。本文从闭环流程、JSON Schema 设计、错误重试、并行调用、结果回灌到 OpenAI / Claude / Gemini 差异，给出可上线的 Python 示例，衔接系列中的 MCP 与 API 集成专题。

*After MCP standardizes tool exposure, the model still must select tools, fill parameters, and consume results. Function Calling lets the LLM emit structured call intents while your runtime executes them. This article covers the full loop, schema design, retries, parallelism, and provider differences.*

---

## 1. Function Calling 如何工作 | The Agent Loop

一次完整的工具调用闭环可以概括为四步：

```text
Model → tool_call(s) → Execute → tool_result → Model → …
```

| 阶段 | 谁负责 | 产出 |
| --- | --- | --- |
| **1. 决策** | LLM | `tool_calls`：工具名 + JSON 参数 |
| **2. 执行** | 你的代码 | 调用 API、查库、跑脚本 |
| **3. 回灌** | 你的代码 | `role: tool` 消息，携带 `tool_call_id` 与结果 |
| **4. 续写** | LLM | 自然语言回答，或再次发起 `tool_call` |

**关键认知：** 模型是「调度员」，不是「执行器」。它根据 `tools` 定义里的 `description` 与 `parameters`（JSON Schema）推断该调哪个函数；你注册的真实 Python/HTTP 函数才接触生产数据。多轮 Agent 就是在 `messages` 数组末尾不断追加 `assistant`（含 tool_calls）与 `tool`（含 result），直到模型不再请求工具、只返回最终文本。

典型消息序列如下：

```python
messages = [
    {"role": "system", "content": "你是助手，可用天气与搜索工具。"},
    {"role": "user", "content": "北京今天天气怎样？"},
    # 模型返回 assistant，带 tool_calls
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_abc",
            "type": "function",
            "function": {"name": "get_weather", "arguments": '{"city": "北京"}'},
        }],
    },
    # 你执行后回灌
    {
        "role": "tool",
        "tool_call_id": "call_abc",
        "content": '{"temp_c": 28, "condition": "晴"}',
    },
]
# 再次 chat.completions.create(messages=messages, tools=tools)
```

---

## 2. JSON Schema 参数设计 | Tool Parameter Design

`tools[].function.parameters` 遵循 JSON Schema 子集。设计质量直接决定模型能否一次填对参数。

**推荐实践：**

1. **`name`** — 动词 + 名词，如 `search_documents`、`create_ticket`，避免 `do_stuff`
2. **`description`** — 写清「何时用、何时不用、边界」；这是模型选工具的第一信号
3. **必填字段** — 用 `required: ["query"]`，减少漏填
4. **枚举约束** — 对固定选项用 `enum`，比自由字符串更稳
5. **控制粒度** — 宁可多个小工具，也不要一个「万能」工具塞满可选参数

```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_kb",
        "description": "在用户问题涉及产品文档、API 说明时检索知识库。不用于闲聊或实时新闻。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "检索关键词，尽量保留用户原意",
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回条数，默认 5",
                    "minimum": 1,
                    "maximum": 20,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}]
```

**常见陷阱：** `arguments` 在 API 里是**字符串化的 JSON**，必须先 `json.loads` 再校验；Schema 过于复杂（深层 `oneOf`）会降低填参成功率；字段名与业务代码不一致会导致静默失败——建议在执行前用 Pydantic 做二次校验。

---

## 3. 错误处理与重试 | Error Handling & Retries

工具层错误分三类，处理策略应不同：

| 类型 | 示例 | 策略 |
| --- | --- | --- |
| **可恢复** | 429 限流、网络超时 | 指数退避重试（`tenacity`） |
| **参数错误** | 缺字段、类型不对 | 把错误信息回灌模型，让其修正参数 |
| **业务失败** | 无权限、资源不存在 | 结构化错误写入 `tool` content，让模型向用户解释 |

不要把堆栈直接丢给模型——用简短、可行动的 JSON：

```python
def run_tool(name: str, args: dict) -> str:
    try:
        result = TOOL_REGISTRY[name](**args)
        return json.dumps(result, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": "invalid_args", "message": str(e)})
    except Exception:
        return json.dumps({"error": "internal", "message": "工具暂时不可用，请稍后重试"})
```

**重试层次：**

- **HTTP 层** — 对 LLM API 的 429/5xx 重试（与上一篇 API 指南一致）
- **工具层** — 幂等读操作可重试 2–3 次；写操作慎用自动重试
- **Agent 层** — 同一 `tool_call_id` 只回灌一次结果；若模型重复请求相同调用，可在运行时做去重或缓存

若连续多轮工具失败，应设置 `max_tool_rounds` 上限，避免无限循环烧 Token。

---

## 4. 并行工具调用 | Parallel Tool Calls

现代模型（如 GPT-4o、Claude 3.5+）常在一次 `assistant` 消息中返回**多个** `tool_call`，且彼此无依赖——例如同时查天气与搜新闻。你的执行器应：

1. 解析 `message.tool_calls` 列表
2. **并行**执行（`asyncio.gather` 或线程池）
3. 按相同 `tool_call_id` 逐条回灌 `role: tool` 消息
4. 全部结果就绪后，再发起下一轮 LLM 请求

```python
import asyncio
import json
from openai import OpenAI

client = OpenAI()

async def dispatch_tool(call):
    name = call.function.name
    args = json.loads(call.function.arguments)
    if name == "get_weather":
        return {"temp_c": 25}
    if name == "web_search":
        return {"items": ["..."]}
    raise ValueError(f"unknown tool: {name}")

async def handle_tool_calls(assistant_msg):
    tasks = [dispatch_tool(tc) for tc in assistant_msg.tool_calls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    tool_messages = []
    for call, res in zip(assistant_msg.tool_calls, results):
        if isinstance(res, Exception):
            content = json.dumps({"error": str(res)})
        else:
            content = json.dumps(res, ensure_ascii=False)
        tool_messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": content,
        })
    return tool_messages
```

**注意：** 有依赖关系的调用（先查用户 ID 再查订单）不应依赖模型并行——应在 Schema 层拆成顺序工具，或用编排层（LangGraph 等）显式控制。并行只适用于「彼此独立」的子任务。

---

## 5. 结果解析与回灌 | Parsing & Feeding Back

执行结果回灌时需遵守各厂商约定，否则下一轮请求会 400：

- **OpenAI 兼容** — 每条 `tool` 消息必须带 `tool_call_id`，与 assistant 里 `tool_calls[].id` 一一对应；`content` 建议为字符串（JSON 文本即可）
- **顺序** — 先 append 带 `tool_calls` 的 `assistant`，再 append 所有 `tool` 消息，不要穿插 `user`
- **体积** — 大段检索结果应截断或摘要后再回灌，避免撑爆上下文；可只保留 `title + snippet` 前 N 条

```python
def agent_turn(messages, tools):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )
    msg = resp.choices[0].message
    messages.append(msg.model_dump(exclude_none=True))

    if not msg.tool_calls:
        return msg.content  # 最终答案

    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)
        raw = TOOL_REGISTRY[call.function.name](**args)
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": json.dumps(raw, ensure_ascii=False),
        })
    return agent_turn(messages, tools)  # 递归直至无 tool_calls
```

**解析技巧：** 对模型返回的 `arguments` 做宽松解析（尾随逗号、单引号）可提升鲁棒性，但应在日志中记录原始字符串便于排错。若模型返回了未注册的工具名，回灌 `{"error": "unknown_tool"}` 比直接抛异常更能引导自修正。

---

## 6. 厂商差异 | OpenAI vs Claude vs Gemini

| 维度 | OpenAI / 兼容 API | Claude (Anthropic) | Gemini (Google) |
| --- | --- | --- | --- |
| **工具声明** | `tools[].type=function` | `tools[].name` + `input_schema` | `function_declarations` |
| **模型输出** | `message.tool_calls` | `content` 块 `type: tool_use` | `functionCall` parts |
| **结果回灌** | `role: tool` + `tool_call_id` | `role: user` 块 `tool_result` | `functionResponse` part |
| **并行** | 单条 assistant 多 call | 支持多 `tool_use` 块 | 支持多 function call |
| **强制调用** | `tool_choice: required` | `tool_choice: any` | `mode: ANY` |

Claude 把工具结果放在 **user** 角色里，且需 `tool_use_id` 关联；Gemini 则在同一次 `generateContent` 的 parts 数组里交替 `functionCall` 与 `functionResponse`。若你做统一 Provider 抽象，建议在内部归一化为：

```python
@dataclass
class ToolInvocation:
    id: str
    name: str
    arguments: dict

@dataclass  
class ToolResult:
    id: str
    content: str
```

上层 Agent 只处理 `ToolInvocation` / `ToolResult`，底层适配各 SDK 差异。DeepSeek、通义千问等 OpenAI 兼容端可直接复用 `openai` 客户端，仅改 `base_url`。

---

## 7. 完整 Python 示例 | Runnable Example

下面是一个最小可运行的「天气 + 计算」双工具 Agent（同步版，便于理解闭环）：

```python
import json
from openai import OpenAI

client = OpenAI()

def get_weather(city: str) -> dict:
    return {"city": city, "temp_c": 26, "condition": "多云"}

def calc(expression: str) -> dict:
    # 生产环境请用安全表达式解析器，勿直接 eval
    return {"result": eval(expression, {"__builtins__": {}}, {})}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市当前天气",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc",
            "description": "计算数学表达式，如 (3+5)*2",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
]

REGISTRY = {"get_weather": get_weather, "calc": calc}

def run_agent(user_input: str, max_rounds: int = 5) -> str:
    messages = [
        {"role": "system", "content": "你是助手，按需调用工具。"},
        {"role": "user", "content": user_input},
    ]
    for _ in range(max_rounds):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:
            return msg.content or ""
        for call in msg.tool_calls:
            fn = REGISTRY[call.function.name]
            args = json.loads(call.function.arguments)
            out = fn(**args)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(out, ensure_ascii=False),
            })
    return "超过最大工具轮次"

if __name__ == "__main__":
    print(run_agent("上海天气如何？另外算一下 (12+8)*3"))
```

---

## 8. 实战要点 | Production Tips

1. **工具幂等** — 写操作带 `idempotency_key`，防止模型重试导致重复下单
2. **审计日志** — 记录每次 `tool_call` 的 name、args、latency、success，便于回放与合规
3. **人机确认** — 删数据、转账类工具在执行前插入 HITL 审批，不要全自动
4. **与 MCP 的关系** — MCP Server 暴露能力，Function Calling 是模型侧的「遥控器」；二者常组合：MCP 提供工具清单，LLM 通过 `tools` 数组选择调用（见上一篇 MCP 专题）
5. **测试** — 用固定 `messages` fixture 测 Schema 校验与错误回灌，而非只测最终自然语言

---

## 9. 总结 | Conclusion

Function Calling 的本质是**结构化意图 + 运行时执行 + 结果回灌**的循环。Schema 写得越清晰，并行与错误处理越规范，Agent 就越稳定。厂商 API 表面不同，但心智模型一致：把工具当函数签名暴露给模型，把执行权握在自己手里。掌握本文后，你已能搭建「能选工具、能并行、能容错」的 Tool Use 层；下一步是把工具背后的 REST/OAuth/Webhook 接到真实业务系统。

---

**系列导航 Series Navigation：**

- 上一篇：[MCP 协议与 Server 开发](/posts/agent-dev-mcp-protocol.html)
- 下一篇：[API 集成（REST/OAuth/Webhook）](/posts/agent-dev-api-integration.html)
