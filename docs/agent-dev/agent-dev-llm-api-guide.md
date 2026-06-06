---
title: 主流大模型 API 调用实战：OpenAI / Claude / DeepSeek / 通义千问
date: 2026-06-05 17:15:00
categories:
  - framework
tags:
  - LLM
  - API
  - OpenAI
  - Claude
  - Agent
---

> **English Title:** Mainstream LLM API Guide — OpenAI, Claude, DeepSeek & Qwen

掌握 Prompt Engineering 之后，下一步是把设计好的提示词真正「跑起来」。无论是构建对话机器人、文档问答，还是多步 Agent，底层都离不开对大模型 HTTP API 的熟练调用。本文聚焦 OpenAI、Claude、DeepSeek、通义千问四大主流服务的**统一心智模型**、计费与上下文管理、流式输出实现，以及各厂商 Python 调用示例，为后续 Embedding 检索与 Function Calling 专题打下基础。

*After mastering Prompt Engineering, the next step is running your prompts in production. Whether you're building chatbots, document Q&A, or multi-step agents, everything depends on fluent LLM HTTP API usage. This article covers a **unified mental model**, billing, context management, streaming, and Python examples for four major providers.*

---

## 1. 统一心智模型 | Unified Mental Model

无论哪家厂商，一次 Chat Completion 调用的本质结构相同。把差异抽象掉之后，你只需要记住下面这张「通用蓝图」：

| 概念 | 说明 |
| --- | --- |
| **Endpoint** | `POST /v1/chat/completions` 或厂商等价路径 |
| **Messages** | `[{role, content}, ...]` 有序对话数组 |
| **Model** | 模型标识符，决定能力、价格与上下文上限 |
| **Parameters** | `temperature`、`max_tokens`、`stream`、`tools` 等 |
| **Response** | 非流式返回完整 `message`；流式返回增量 `delta` |

一次典型调用的生命周期是：**组装 messages → 发送 HTTP 请求 → 解析 choices → 提取 content 或 tool_calls → 记录 usage**。Agent 开发中，这个循环会被执行数十次，因此封装统一的 Provider 层是工程化的第一步。

**关键洞察：** DeepSeek 与通义千问均提供 **OpenAI 兼容接口**（Compatible Mode），只需替换 `base_url` 和 `api_key`，即可复用 `openai` 官方 SDK。Claude 使用独立的 Messages API，字段名略有不同（如 `max_tokens` 为必填），但语义完全对应。这意味着你的业务代码可以做到「一套抽象，多家后端」。

角色（role）的约定也趋于统一：`system` 设定行为边界，`user` 承载用户输入，`assistant` 是模型历史回复，`tool` 则用于回传工具执行结果——这是 Function Calling 闭环的基础。

---

## 2. Token 计费与成本优化 | Token Billing

所有主流 API 均按 **Token** 计费，而非按请求次数。计费公式为：

> **总费用 = 输入 tokens × 输入单价 + 输出 tokens × 输出单价**

输入包含完整的 messages 历史（含 system prompt），输出则是模型生成的文本。同一对话轮次越多，输入 token 会线性增长——这是长对话 Agent 成本失控的主要原因。

**五条实用优化策略：**

1. **精简 System Prompt** — 去掉冗余指令和重复示例，每多 500 token 系统提示，在千次调用后都是可观支出
2. **控制输出长度** — 设置合理的 `max_tokens`，并在 prompt 中明确要求简洁回答，避免模型「话痨」
3. **模型路由（Model Routing）** — 分类、摘要等简单任务用轻量模型（`gpt-4o-mini`、`deepseek-chat`），复杂推理再上旗舰
4. **Prompt Caching** — OpenAI 与 Claude 均支持对重复前缀缓存，系统提示不变时可显著降低输入成本
5. **批量 API（Batch）** — 非实时场景（如离线评估、数据标注）使用 Batch 接口，通常享 50% 折扣

响应体中的 `usage` 字段（`prompt_tokens`、`completion_tokens`）是成本监控的第一数据源。生产环境务必对每次调用打点，按 model、user、feature 维度聚合，才能做有效的 FinOps。

---

## 3. 上下文窗口与截断策略 | Context Window

每个模型都有上下文上限（Context Window），超出后 API 会直接报错。Agent 场景中，多轮对话 + 工具返回 + RAG 文档很容易触顶。

| 策略 | 适用场景 | 优缺点 |
| --- | --- | --- |
| **滑动窗口** | 短对话客服 | 实现简单，但丢失早期关键信息 |
| **摘要压缩** | 长会话助手 | 保留语义，额外消耗一次 LLM 调用 |
| **RAG 检索** | 知识库问答 | 只注入相关片段，下篇 Embedding 专题详解 |
| **截断尾部** | 超长单文档 | 保留首尾，丢弃中间，适合日志分析 |

**常见陷阱：** 不同厂商对 token 的计算方式略有差异——中文通常 1–2 个汉字对应 1 token，英文约 4 字符 1 token。不要凭字符数估算，应使用各 SDK 提供的 token 计数工具（如 `tiktoken`）在发送前预检。另外，输入越长，首字延迟（TTFT）往往越高，需要在「信息完整」与「响应速度」之间权衡。

---

## 4. 流式响应（SSE）| Streaming Implementation

流式输出通过 **Server-Sent Events（SSE）** 逐块推送 `delta`，让用户在模型尚未生成完毕时就能看到文字逐字出现，显著降低感知延迟。对聊天类 Agent 而言，流式几乎是标配。

```python
from openai import OpenAI

client = OpenAI()
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "用三句话介绍 Agent"}],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
```

**后端实现要点：** 设置响应头 `Content-Type: text/event-stream`、`Cache-Control: no-cache`；若经过 Nginx 反向代理，需加 `X-Accel-Buffering: no` 禁用缓冲。Claude 流式使用 `client.messages.stream()`，事件类型为 `content_block_delta`，逻辑相同。

**前端消费：** 可用 `fetch` 配合 `ReadableStream` 逐行解析 `data: {...}` 行；注意处理连接中断与 `[DONE]` 结束标记，并在 UI 层做打字机效果与取消按钮。

---

## 5. Function Calling 预览 | Tool Use Preview

工具调用（Tool Use / Function Calling）是 Agent 与外部世界交互的核心机制。各厂商的实现已高度趋同：

- **OpenAI / DeepSeek / Qwen** — 请求中传 `tools` 数组，响应 `choices[0].message.tool_calls`
- **Claude** — 请求中传 `tools`，响应 `content` 块类型为 `tool_use`

模型**不会**直接执行你的函数。它只返回结构化 JSON：「调用哪个工具、传什么参数」。你的代码负责真正执行（查数据库、调 API），再把结果以 `role: tool` 的消息塞回 `messages`，发起下一轮请求——形成 **LLM → Tool → LLM** 的闭环。系列第 10 篇《Function Calling / Tool Use》将用完整示例拆解这一流程。

---

## 6. 厂商对比 | Provider Comparison

| 维度 | OpenAI | Claude (Anthropic) | DeepSeek | 通义千问 (Qwen) |
| --- | --- | --- | --- | --- |
| **旗舰模型** | gpt-4o | claude-sonnet-4 | deepseek-chat / reasoner | qwen-max / qwen-plus |
| **上下文** | 128K | 200K | 64K–128K | 128K–1M |
| **兼容接口** | 原生标准 | 独立 Messages API | OpenAI 兼容 | OpenAI 兼容 |
| **工具调用** | ✅ tools | ✅ tools | ✅ tools | ✅ tools |
| **流式** | ✅ SSE | ✅ SSE | ✅ SSE | ✅ SSE |
| **性价比** | 中高 | 中高 | 极高 | 高（国内低延迟） |
| **特色** | 生态最全、Assistants API | 长文本、安全对齐强 | 推理模型强、价格极低 | 中文优化、DashScope 全家桶 |

选型建议：**国际化产品优先 OpenAI/Claude**；**成本敏感或国内部署选 DeepSeek/Qwen**；开发阶段可用兼容接口快速切换，避免供应商锁定。

---

## 7. 各厂商 Python 调用示例 | Code Examples

### 7.1 OpenAI

```python
from openai import OpenAI

client = OpenAI()  # 环境变量 OPENAI_API_KEY
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是简洁的技术助手。"},
        {"role": "user", "content": "什么是 Token？"},
    ],
)
print(resp.choices[0].message.content)
print(resp.usage)  # 记录 token 消耗
```

### 7.2 Claude (Anthropic)

```python
import anthropic

client = anthropic.Anthropic()  # ANTHROPIC_API_KEY
msg = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    system="你是简洁的技术助手。",
    messages=[{"role": "user", "content": "什么是 Token？"}],
)
print(msg.content[0].text)
print(msg.usage)
```

### 7.3 DeepSeek（OpenAI 兼容）

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com",
)
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "什么是 Token？"}],
)
print(resp.choices[0].message.content)
```

### 7.4 通义千问（DashScope 兼容模式）

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
resp = client.chat.completions.create(
    model="qwen-plus",
    messages=[{"role": "user", "content": "什么是 Token？"}],
)
print(resp.choices[0].message.content)
```

---

## 8. 实战要点 | Production Tips

1. **API Key 走环境变量或密钥管理服务** — 绝不硬编码到 Git 仓库
2. **重试与指数退避** — 对 429（限流）和 5xx 使用 `tenacity` 等库自动重试
3. **合理超时** — 推理模型（如 deepseek-reasoner）耗时长，设置 60–120s timeout
4. **抽象 Provider 层** — 统一 `chat(messages) -> str` 接口，方便 A/B 测试与 fallback
5. **可观测性先行** — 记录 latency、token、model、error_code，接入 LangSmith 或自建日志

---

## 9. 总结 | Conclusion

四大 API 的调用范式已高度趋同：**Messages 数组进，文本或 tool_calls 出**。差异主要在定价、上下文长度、区域延迟与生态集成。Agent 开发者的务实策略是：用 OpenAI 兼容层统一 DeepSeek 与 Qwen，Claude 单独封装 Messages API，上层实现模型路由与成本监控。掌握本文内容后，你已具备构建「能对话、能流式、能记账」的 LLM 应用基础能力。

---

**系列导航 Series Navigation：**

- 上一篇：[Prompt Engineering 系统性设计](/posts/agent-dev-prompt-engineering.html)
- 下一篇：[Embedding 与向量检索](/posts/agent-dev-embedding-vector-search.html)
