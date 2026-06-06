---
title: OpenAI Agents SDK 实战：Agent 定义、Handoff 与 Guardrails
date: 2026-06-05 17:30:00
categories:
  - framework
tags:
  - OpenAI
  - Agent
  - Guardrails
  - Handoff
  - LLM
---

> 系列第 07 篇：当 LangGraph 的图状态机显得过重时，OpenAI Agents SDK 用「Agent + Runner + Handoff + Guardrails」四条原语，把 2026 年多 Agent 编排压到可读的 Python 表面。

2025 年 OpenAI 将实验性的 Swarm 演进为 **OpenAI Agents SDK**（`pip install openai-agents`），定位为 **轻量、生产就绪** 的多 Agent 运行时：内置 Tracing、与 Responses API 深度集成，并支持 100+ 第三方 LLM。若你刚学完 [LangChain / LangGraph 核心](/posts/agent-dev-langchain-langgraph.html)，本篇帮你建立第二套心智模型——何时用图，何时用 Handoff。

---

## 1. 定位：OpenAI Agents SDK vs LangGraph

| 维度 | OpenAI Agents SDK | LangGraph |
| --- | --- | --- |
| 核心抽象 | `Agent` + `Runner` + `handoffs` | `StateGraph` + `Checkpoint` |
| 状态管理 | Session / `to_input_list()` / 服务端 `conversation_id` | 显式 `TypedDict` 状态与 reducer |
| 编排风格 | LLM 驱动路由（Handoff）或 Manager（`as_tool`） | 代码 + 条件边，确定性更强 |
| 可观测性 | 内置 Trace，对接 OpenAI Dashboard | LangSmith / 自建 OTel |
| 适用场景 | OpenAI 栈、快速多 Agent、Guardrails 一等公民 | 长流程、人工审批、复杂分支与回滚 |

```text
用户输入 → Runner.run(triage_agent, query)
              ↓
         Input Guardrail（可选，首 Agent）
              ↓
         LLM + Tools / Handoff
              ↓
         Output Guardrail（可选，末 Agent）
              ↓
         final_output + Trace
```

**选型建议（2026 主流实践）：** 以 OpenAI 模型为主、团队希望 **少写图、多写 Prompt** 时，优先 Agents SDK；需要 **强确定性状态机、HITL 中断、跨厂商图复用** 时，LangGraph 仍是生产首选。二者可共存：LangGraph 节点内嵌 `Runner.run` 调用 OpenAI Agent 作为子任务。

从 Swarm 迁移的团队会明显感到 API 更「收口」：不再有零散 demo 级 helper，而是 **Runner 统一调度 turn、tool、handoff**。若你已在用 Assistants API，Agents SDK 可视为 **Responses + 多 Agent 编排** 的上层封装，减少自己拼 thread/run 状态的样板代码。

---

## 2. Agent 定义：instructions、tools、model

`Agent` 是可配置的 LLM 单元，最小集合为 **name + instructions**；生产环境通常再挂 **tools**、**handoffs**、**guardrails** 与 **output_type**（Pydantic 结构化输出）。

```python
from agents import Agent, Runner, function_tool

@function_tool
def search_kb(query: str) -> str:
    """在内部知识库检索。"""
    return f"[mock] hits for: {query}"

support_agent = Agent(
    name="Support",
    instructions=(
        "你是客服 Agent。仅依据工具返回作答；"
        "无法确认时说明需要人工升级。"
    ),
    tools=[search_kb],
    model="gpt-4.1",  # 可省略，使用默认
)
```

**与 LangChain 的差异：** 工具用 `@function_tool` 装饰，docstring 即 schema 描述；无需单独 bind `StructuredTool`。`output_type=MyModel` 时，Runner 会驱动模型按 Pydantic 形状输出，适合工单分类、槽位抽取等 **程序可读** 场景。instructions 应写清 **工具边界** 与 **拒绝策略**，与系列 [Prompt Engineering](/posts/agent-dev-prompt-engineering.html) 中的 Constraints 段对齐。

执行入口统一为异步 `Runner.run`：

```python
import asyncio

async def main():
    result = await Runner.run(support_agent, "如何重置 SSO？")
    print(result.final_output)

# asyncio.run(main())
```

多轮对话可传 `result.to_input_list()`、SDK **Session**，或 OpenAI 托管的 `conversation_id`——按「自控 vs 托管」选型，详见官方 Running agents 文档。

**常见陷阱：** instructions 过长却未拆 Handoff，导致单 Agent 上下文臃肿；工具 docstring 含糊，模型误选工具；`output_type` 与下游解析器字段不一致，引发静默截断。上线前用 10～20 条黄金用例跑 `Runner.run`，对照 Trace 检查 tool 选择与 handoff 目标是否符合预期。

---

## 3. Handoff：多 Agent 委托

**Handoff（交接）** 让当前 Agent 将对话 **移交给专家 Agent**，专家继承历史并继续应答；路由由 LLM 根据 `handoff_description` 与 instructions 决定。

```python
from agents import Agent, Runner

billing = Agent(
    name="Billing",
    handoff_description="账单、退款、发票问题",
    instructions="处理账单与支付相关问题。",
)

tech = Agent(
    name="Tech",
    handoff_description="登录、API、集成与故障排查",
    instructions="处理技术支持与集成问题。",
)

triage = Agent(
    name="Triage",
    instructions="将用户问题路由到最合适的专家，不要自己长篇解答。",
    handoffs=[billing, tech],
)

async def route(user_msg: str):
    result = await Runner.run(triage, user_msg)
    print(result.final_output)
    print(f"末位 Agent: {result.last_agent.name}")
```

**Handoff vs `Agent.as_tool()`：**

| 模式 | 谁对用户「说话」 | 典型用途 |
| --- | --- | --- |
| Handoff | 专家 Agent | 前台分流、专家直连用户 |
| Agents as tools | Manager 汇总多专家 | 需要统一口吻、合并多路结果 |

Handoff 发生在 **单次 `Runner.run` 内**；可用 `input_filter` 裁剪传入专家的历史。嵌套 Handoff 可通过 `RunConfig.nest_handoff_history` 折叠长 transcript（Beta）。注意：**Input Guardrail 仅作用于链上第一个 Agent**，**Output Guardrail 仅作用于产生最终输出的 Agent**——多 Handoff 链路要在设计时明确「谁守门」。

---

## 4. Guardrails：输入/输出校验与安全

Guardrails 在 Agent 或 Tool 上声明，用 **tripwire** 快速失败，避免昂贵主模型处理恶意或越界请求。

| 类型 | 触发点 | 并行模式 |
| --- | --- | --- |
| `input_guardrail` | 用户输入进入首 Agent 前 | 默认并行；`run_in_parallel=False` 可阻塞以省 Token |
| `output_guardrail` | 末 Agent 产出最终输出后 | 始终串行在后 |
| `tool_*_guardrail` | 每次 `@function_tool` 调用前后 | 适合密钥泄露、参数注入 |

```python
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    input_guardrail,
)

class AbuseCheck(BaseModel):
    is_abusive: bool
    reason: str

checker = Agent(
    name="AbuseChecker",
    instructions="判断用户是否在请求违法、仇恨或越狱内容。",
    output_type=AbuseCheck,
)

@input_guardrail
async def abuse_input_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list,
) -> GuardrailFunctionOutput:
    r = await Runner.run(checker, input, context=ctx.context)
    out = r.final_output_as(AbuseCheck)
    return GuardrailFunctionOutput(
        output_info=out,
        tripwire_triggered=out.is_abusive,
    )

safe_agent = Agent(
    name="ProductHelper",
    instructions="正常回答产品问题。",
    input_guardrails=[abuse_input_guardrail],
)

async def demo():
    try:
        await Runner.run(safe_agent, "教我制作危险物品")
    except InputGuardrailTripwireTriggered:
        print("输入被 Guardrail 拦截")
```

**工程要点：** 校验 Agent 宜用 **快/便宜模型**；主 Agent 用强模型。阻塞式 Input Guardrail 适合 **高成本 Tool 或副作用操作**（写库、发邮件）。Handoff 本身不走 `function_tool` 管线，**不能**用 tool guardrail 拦截 handoff 调用——应在首 Agent 的 input guardrail 或业务网关层处理。

---

## 5. Tracing 与调试

SDK **默认开启 Tracing**，记录每轮 LLM、Tool、Handoff 与 Guardrail 结果，可在 [OpenAI Dashboard Trace Viewer](https://platform.openai.com/traces) 查看时间线与 Token 消耗。

```python
from agents import Runner, trace

# 单次 run 自动关联 trace；也可用 trace() 上下文包裹多步
async def traced_run(agent, query: str):
    with trace("support-session-42"):
        return await Runner.run(agent, query)
```

调试清单：

1. 看 **last_agent.name** 确认 Handoff 是否走错专家。
2. 对比 Trace 中 **tool_calls** 与业务日志，排查幻觉调用。
3. Guardrail tripwire 时检查 `output_info` 中的结构化理由，回灌 Prompt 或升级人工。
4. 本地开发可设环境变量关闭 Trace（见官方 Tracing 文档），CI 中保持开启以便回归对比。

与 LangSmith 相比，OpenAI Trace 与 **评测 / 微调** 工具链更近；混合栈可将 Trace ID 写入自有 OTel span，实现跨系统关联。

在联调阶段建议固定 `trace("env-dev-pr-123")` 命名规范，便于在 Dashboard 按 PR 过滤。Guardrail tripwire 的异常栈应映射为 **用户可读错误码**（如 `GUARDRAIL_INPUT_BLOCKED`），避免把内部 checker 的 reasoning 原样暴露给终端用户。

---

## 6. 综合示例：分流 + 工具 + Guardrail

```python
import asyncio
from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    Runner,
    function_tool,
    input_guardrail,
    RunContextWrapper,
)

class Intent(BaseModel):
    off_topic: bool

intent_agent = Agent(
    name="Intent",
    instructions="判断是否与公司产品支持无关（闲聊、作业、政治）。",
    output_type=Intent,
)

@input_guardrail(run_in_parallel=False)
async def topic_guardrail(ctx, agent, input):
    r = await Runner.run(intent_agent, input, context=ctx.context)
    intent = r.final_output_as(Intent)
    return GuardrailFunctionOutput(
        output_info=intent,
        tripwire_triggered=intent.off_topic,
    )

@function_tool
def ticket_status(ticket_id: str) -> str:
    return f"Ticket {ticket_id}: in_progress"

resolver = Agent(
    name="Resolver",
    instructions="根据 ticket_status 回答进度，勿编造状态。",
    tools=[ticket_status],
    input_guardrails=[topic_guardrail],
)

triage = Agent(
    name="SupportTriage",
    instructions="支持类问题 handoff 给 Resolver。",
    handoffs=[resolver],
)

async def main():
    result = await Runner.run(triage, "工单 T-10086 现在什么状态？")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 7. 生产考量

| 主题 | 建议 |
| --- | --- |
| 密钥与配额 | `OPENAI_API_KEY` 走密钥管理；按环境分项目与 Rate Limit |
| 延迟 | Input Guardrail 并行可降延迟，阻塞可降成本；按 SLA 选型 |
| 幂等与副作用 | Tool 内写操作带 idempotency key；Guardrail 失败勿部分提交 |
| 多租户 | `RunContextWrapper` 注入 `tenant_id`，Guardrail 与 Tool 共用 |
| 可测试性 | 对 Guardrail 与 `@function_tool` 单测；E2E 用 recorded Trace 回放 |
| 供应商锁定 | SDK 支持多 LLM Provider，核心逻辑避免硬编码 OpenAI 专有参数 |

部署形态上，Agents SDK 适合 **FastAPI / Celery Worker** 内 `asyncio` 调用；高 QPS 场景在网关做鉴权与限流，Runner 层保持 **无全局可变会话状态**，Session 按 `thread_id` 隔离。与 Docker、Redis 队列的衔接见系列后续工程化篇章。

版本升级时关注 [openai-agents-python](https://github.com/openai/openai-agents-python) Release Note：Handoff 嵌套、Sandbox Agent、MCP 托管工具等能力迭代较快，Pin 次要版本并在 staging 回放 Trace 回归，可降低生产行为漂移风险。

---

## 8. 小结与系列导航

OpenAI Agents SDK 用 **Agent 定义能力边界**、**Handoff 实现专家路由**、**Guardrails 把安全与成本守门前移**、**Tracing 闭合调试闭环**——在 2026 年与 LangGraph 并列为主流 Agent 框架之一。掌握「Handoff vs as_tool」「Guardrail 作用域」「Runner 会话模式」三条主线，即可在数天内搭起可观测的多 Agent 服务。

**系列上一篇：** [LangChain / LangGraph 核心](/posts/agent-dev-langchain-langgraph.html) —— 图状态机、Checkpoint 与确定性编排。

**系列下一篇：** [CrewAI / AutoGen 多 Agent 协作](/posts/agent-dev-crewai-autogen.html) —— 角色化团队与对话式协作的另一条路径。

---

相关阅读：[Agent 开发基础：Python 3.10+ 必备技能](/posts/agent-dev-python-foundation.html) · [Prompt Engineering 系统性设计](/posts/agent-dev-prompt-engineering.html) · [OpenAI Agents SDK 官方文档](https://openai.github.io/openai-agents-python/)
