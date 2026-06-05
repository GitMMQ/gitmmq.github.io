---
title: Agent 全栈开发：TypeScript 与 Node.js 实战指南
date: 2026-06-05 17:05:00
categories:
  - node
tags:
  - TypeScript
  - Node.js
  - Agent
  - LangChain.js
  - LLM
---

在 Agent 学习路线的第一层，[Python 开发基础](/posts/agent-dev-python-foundation.html) 负责数据清洗、脚本化实验与模型侧胶水；而 **TypeScript + Node.js** 则天然承接「Web 前端 + API + 流式对话」的全栈链路。若你的产品形态是对话界面、SaaS 控制台或需要快速迭代的 B 端工具，TS 往往是投入产出比更高的路径。本文聚焦如何用类型安全的 JS 生态构建可上线的 Agent 应用。

---

## 1. 为什么 Agent 开发离不开 TypeScript？

Agent 的核心难点不是调一次 Chat API，而是 **工具 Schema、多轮状态、流式 UI** 在前后端之间反复传递。模型输出的 Tool Call 本质是 JSON，字段多一个、少一个都会导致执行失败；会话里还要叠加 `tool_calls`、`tool_results` 与人工确认节点。TypeScript 的价值在于：

| 能力 | 在 Agent 中的体现 |
| --- | --- |
| 类型安全 | Tool 参数、模型返回的 JSON 在编译期即可发现字段错误 |
| 前后端同构 | `zod` / 接口定义可在 React 与 API Route 间复用 |
| 生态对齐 | Vercel AI SDK、LangChain.js、OpenClaw 均以 TS 为一等公民 |

当工具从 3 个增长到 30 个时，没有类型的项目会在「模型幻觉 + 运行时解析失败」上付出成倍调试成本。此外，**Discriminated Union** 可精确建模「用户消息 / 助手消息 / 工具结果」等联合类型，配合 `satisfies` 能在重构时让编译器替你检查遗漏分支——这在多 Agent、多步骤编排里尤为省事。

---

## 2. 主流框架速览

| 框架 | 定位 | 典型场景 |
| --- | --- | --- |
| **LangChain.js** | 链式编排、RAG、Tool Agent | 需要 LangGraph 互通、复杂检索流水线 |
| **Vercel AI SDK** | UI 流式、`useChat`、多 Provider | Next.js / React 产品级对话界面 |
| **Mastra** | TS 原生 Agent 工作流 | 步骤编排、评估、可观测性一体化 |
| **OpenClaw** | 自托管 Gateway + 插件 | 本地常驻助手、IM 通道、Plugin SDK 扩展 |

**LangChain.js** 提供 `createReactAgent`、`RunnableSequence` 等与 Python 版概念对齐的 API，适合已有 LangGraph 经验、需要跨语言迁移的团队。**Vercel AI SDK** 把 `streamText`、`generateObject` 与 React Hook 打通，多模型通过 `@ai-sdk/*` 适配器切换，是 Next.js 场景的事实标准。**Mastra** 强调工作流、评估与 Tracing 在同一 TS 仓库内完成，适合从零搭建可观测的 Agent 平台。**OpenClaw** 则以本地 Gateway 守护进程为控制面，通过 WebSocket 连接 IM 通道与 Plugin，适合「个人助手常驻本机」而非纯 Web SaaS 的形态。

选型建议：**产品 Web 对话优先 AI SDK**；**研究型编排优先 LangChain.js**；**需要 7×24 本机助手与多渠道** 可评估 OpenClaw 的 Gateway 架构。三者并非互斥——例如在 Next.js 中用 AI SDK 做 UI 流，后台用 LangChain.js 跑 RAG 管道，是常见组合。

---

## 3. TypeScript 模式：Schema 即契约

工具定义应「单一数据源」：用 **Zod** 描述参数，再推导 TS 类型，避免手写两份 Schema。

```typescript
import { z } from "zod";
import { tool } from "ai";

const SearchArgs = z.object({
  query: z.string().min(1),
  limit: z.number().int().max(10).default(5),
});

type SearchArgs = z.infer<typeof SearchArgs>;

export const searchTool = tool({
  description: "搜索内部知识库",
  parameters: SearchArgs,
  execute: async ({ query, limit }) => {
    const hits = await kb.search(query, limit);
    return { items: hits };
  },
});
```

除 Zod 外，也可用 **interface + 运行时校验** 的折中：对外导出 `interface SearchArgs`，内部用 `SearchArgsSchema.parse(raw)` 兜底。LangChain.js 侧可用 `StructuredTool` + `zodToJsonSchema` 生成 OpenAI 兼容的 function schema；OpenClaw Plugin SDK 则常用 **TypeBox** 描述 `parameters`，与 Gateway 的 JSON Schema 校验对齐。原则不变：**Schema 只维护一份**，JSON Schema、TS 类型与文档都从它派生。

LangChain.js 绑定工具的最小示例如下，注意 `schema` 与 `func` 签名由 Zod 推断保持一致：

```typescript
import { z } from "zod";
import { tool } from "@langchain/core/tools";

const getWeather = tool(
  async ({ city }) => {
    return await weatherApi.fetch(city);
  },
  {
    name: "get_weather",
    description: "查询城市天气",
    schema: z.object({ city: z.string() }),
  }
);
```

---

## 4. Node.js 异步：流式与 SSE

Agent 响应必须 **边生成边推送**，否则首字延迟会拖垮体验。用户感知到的「聪明」往往取决于首 token 是否在数百毫秒内出现，而不是最终答案有多长。Node 18+ 原生支持 `ReadableStream`，Fetch API 也可消费上游模型的 SSE；各框架在此基础上封装了 `StreamingTextResponse` 或 Data Stream 协议，把文本 delta、tool call 片段与完成事件编码成前端可解析的帧。

```typescript
// Next.js App Router 示例（Vercel AI SDK）
import { streamText } from "ai";
import { openai } from "@ai-sdk/openai";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const result = streamText({
    model: openai("gpt-4o"),
    messages,
    tools: { search: searchTool },
    maxSteps: 5,
  });
  return result.toDataStreamResponse();
}
```

若不用框架封装，原生 Node 也可用 `res.writeHead(200, { "Content-Type": "text/event-stream" })` 手写 SSE，按 `data: ${JSON.stringify(chunk)}\n\n` 推送 token 与 tool 事件。无论哪种方式，底层注意点一致：**不要**在 `for await` 里执行 CPU 密集计算阻塞事件循环；耗时工具应 `await` 完成后再写入流片段；生产环境设置 `Cache-Control: no-cache`、禁用缓冲（如 Nginx `proxy_buffering off`），必要时加心跳包，避免代理超时断连。客户端断开时，应监听 `req.aborted` 并取消上游 LLM 请求，节省 Token。

---

## 5. 全栈 Agent 架构

```text
┌─────────────┐     SSE/DataStream     ┌──────────────────┐
│ React 客户端 │ ◄──────────────────► │ API Route / Hono │
│ useChat     │                      │ streamText + tools│
└─────────────┘                      └────────┬─────────┘
                                              │
                                     ┌────────▼─────────┐
                                     │ LLM Provider     │
                                     │ Vector DB / MCP  │
                                     └──────────────────┘
```

- **前端**：`useChat` 管理消息列表、loading 与 tool call 卡片；可用 `experimental_toolInvocations` 展示「正在调用搜索…」等中间态。
- **API 层**：JWT 或 Session 鉴权、按用户限流、敏感工具（删库、发邮件）走二次确认或 RBAC 白名单。
- **数据层**：`threadId` 映射 Redis 存最近 N 轮；长期记忆与 RAG 文档块写入向量库（系列第 05 篇《Embedding 与向量检索》展开）。

部署上，Next.js 可一键上 Vercel Edge；也可用 **Hono + Node** 或 **Bun** 获得更低冷启动。关键是把 **模型密钥与 Tool 密钥** 关在服务端，前端只拿会话 Token。若 Agent 需要调用企业内部 REST API，建议在 API 层做 **Tool Gateway**：统一 OAuth 刷新、审计日志与超时重试，避免把业务凭证直接交给 LLM 上下文。MCP（Model Context Protocol）正在成为连接外部工具的标准接口，系列第 09 篇将专门展开；在 TS 栈中可先以 HTTP MCP Server 暴露数据库或工单系统，再由 Agent 通过协议发现工具列表。

---

## 6. Python vs TypeScript：如何取舍？

| 选 Python | 选 TypeScript |
| --- | --- |
| 训练/微调、NumPy 生态、Jupyter 实验 | Next.js 全栈、边缘部署、前端团队主导 |
| LangGraph 复杂图、CrewAI 多 Agent | Vercel AI SDK 流式 UI、OpenClaw 本机 Gateway |
| 数据科学脚本、批处理评估 | 类型安全的 Tool 契约、Monorepo 共享类型 |

实践上常见 **混合架构**：Python 跑离线 RAG 索引、微调与批评估，TS 服务暴露 HTTP/SSE 给产品——用 OpenAPI 或 tRPC 保持契约一致。团队若以前端为主、无重型 ML 管线，可全程 TS；若以 Notebook 探索为主，再逐步把稳定链路迁到 API 层。

---

## 7. 实战要点与常见陷阱

1. **工具粒度**：一个 Tool 只做一件事，描述里写清输入示例与「何时不要调用」。
2. **maxSteps 上限**：`streamText` 的 `maxSteps` 防止 ReAct 死循环烧 Token。
3. **错误可观测**：记录每次 tool 的 input/output 与 latency，便于回放（LangSmith / OpenTelemetry）。
4. **环境变量**：`OPENAI_API_KEY` 等仅存服务端，切勿打进客户端 bundle。
5. **幻觉参数**：对枚举类字段用 `z.enum()` 限制，减少模型编造非法状态。
6. **流式中断**：用户点击「停止」时，前后端都要 abort 上游 fetch，避免幽灵计费与孤儿工具调用。

---

## 延伸阅读

- 上一篇：[Python 3.10+ Agent 开发基础](/posts/agent-dev-python-foundation.html)
- 下一篇：[Prompt Engineering 系统性设计](/posts/agent-dev-prompt-engineering.html)

掌握 TS 全栈栈后，建议继续学习系列中的 **LangChain / LangGraph 核心** 与 **Function Calling**，把类型安全的工具层接到更复杂的编排图上。下一篇将系统讲解 [Prompt Engineering](/posts/agent-dev-prompt-engineering.html)——无论 Python 还是 TypeScript，提示词设计都是 Agent 可靠性的底座。
