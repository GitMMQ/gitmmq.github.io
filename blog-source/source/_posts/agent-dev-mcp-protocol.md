---
title: MCP 协议实战：让 Agent 连接一切外部工具（Model Context Protocol）
date: 2026-06-05 17:40:00
categories:
  - framework
tags:
  - MCP
  - Agent
  - Anthropic
  - 工具集成
  - LLM
---

> **English Title:** MCP in Practice — Connecting Agents to External Tools via Model Context Protocol

多 Agent 框架解决了「谁来做」，但 Agent 仍要对接数据库、工单系统、Git、Notion 等外部能力。过去每家 IDE 各自写插件、每家框架各自封装 Tool，集成成本重复且不可移植。**Model Context Protocol（MCP）** 由 Anthropic 提出并开源，用统一的 JSON-RPC 语义描述「能读什么、能调什么、能注入什么提示模板」，让 **Host（宿主应用）** 通过 **Client** 连接任意 **Server**，一次实现、多处复用。2026 年 Cursor、Claude Desktop、LangChain 等已原生或半原生支持 MCP，它正在成为 Agent 工具层的「USB-C」。

---

## 1. 什么是 MCP，为何成为 2026 事实标准

MCP 不是又一个 Agent 框架，而是 **宿主与工具之间的协议层**。它解决三类痛点：

| 痛点 | MCP 的回应 |
| --- | --- |
| N×M 集成 | 每个数据源/服务实现一个 MCP Server，任意 Host 即插即用 |
| 上下文碎片化 | **Resources** 把文件、schema、文档块以 URI 暴露给模型 |
| 工具 schema 不一致 | **Tools** 统一为带 JSON Schema 的可调用能力，由协议协商 |

与 OpenAI 的 Function Calling 相比：Function Calling 定义的是「模型在一次补全里如何声明调用」；MCP 定义的是「**进程外** 的能力如何被发现、鉴权、执行与回传」。二者互补——Host 常把 MCP Tool 映射为模型侧的 function，但 MCP 还额外标准化了资源读取与可复用 Prompt 模板。

2026 年 MCP 成为主流的原因很务实：**供应链统一**（社区已有 GitHub、Postgres、Slack 等 Server）、**安全边界清晰**（Server 独立进程、可限权）、**厂商共建**（Anthropic 规范 + 多 Host 实现）。当你要为团队内部系统开放给 Cursor/Claude 时，优先写 MCP Server 往往比为每个客户端各写一套插件更划算。

若你已在用 [主流模型 API](/posts/agent-dev-llm-api-guide.html) 的 `tools` 字段，可以把 MCP 理解为 **把 Tool 实现从应用进程里抽出去**：Host 只负责把 `tools/list` 映射进模型请求，真正执行发生在 Server 进程。这样换模型供应商时，业务集成层不必重写。

---

## 2. 架构：Host、Client、Server

```text
┌─────────────┐     MCP      ┌─────────────┐     业务 API    ┌──────────────┐
│    Host     │ ◄──────────► │ MCP Client  │ ◄──────────────► │ MCP Server   │
│ Cursor/IDE  │  JSON-RPC   │ (内置/库)   │  stdio / HTTP   │ Git/DB/...   │
└─────────────┘             └─────────────┘                 └──────────────┘
       │
       ▼
   LLM（Claude/GPT 等）
```

- **Host**：面向用户的应用（Cursor、Claude Desktop、自定义 Agent 服务）。负责会话、模型调用、把 MCP 能力呈现给 LLM。
- **Client**：Host 内的协议实现，维护与 Server 的连接、能力发现（`tools/list`、`resources/list`）、调用转发。
- **Server**：暴露具体能力的最小单元，通常独立进程。通过 **stdio**（本地子进程）或 **HTTP/SSE**（远程服务）与 Client 通信。

一次典型交互：`initialize` 握手 → `tools/list` 发现工具 → 模型决定调用 → `tools/call` 执行 → 结果作为 tool 消息回到 Host。Resources 走 `resources/read`，不必经过模型的 function 通道，适合注入大段只读上下文。

**传输选型**：本地开发首选 **stdio**——Host 以子进程启动 Server，无网络暴露，调试简单。团队共享或 SaaS 化时用 **Streamable HTTP / SSE**，便于水平扩展与集中鉴权，但需额外处理连接保活与版本兼容。同一业务可同时提供两种 Transport，由部署环境选择。

---

## 3. 三大原语：Resources、Tools、Prompts

| 原语 | 用途 | 典型例子 |
| --- | --- | --- |
| **Resources** | 只读、可订阅的上下文片段 | `file:///repo/README.md`、`postgres://schema/users` |
| **Tools** | 模型可调用的副作用操作 | `create_issue`、`run_query`、`send_message` |
| **Prompts** | 可参数化的提示模板 | `code_review(repo, diff)`，由 Host 填充后送入模型 |

**Resources** 适合「让模型看见」：文档、配置、表结构。URI 与 MIME 类型由 Server 声明，Host 可按需拉取，避免把整个仓库塞进 system prompt。

**Tools** 适合「让模型做事」：每个 Tool 有 `name`、`description`、`inputSchema`（JSON Schema）。描述质量直接影响模型选工具的准确率——与系列 [Prompt Engineering](/posts/agent-dev-prompt-engineering.html) 中的工具边界写法一致。

**Prompts** 适合「标准化工作流」：把反复使用的评审、迁移、排障模板注册到 Server，团队共享同一套指令骨架，减少各项目复制粘贴 system prompt。

---

## 4. 动手写一个 MCP Server

### 4.1 Python（FastMCP）

```python
# weather_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
def get_forecast(city: str) -> str:
    """返回指定城市的简要天气预报。"""
    # 实际项目里调用 OpenWeather 等 API
    return f"{city}: 晴，22°C，微风"

if __name__ == "__main__":
    mcp.run()  # 默认 stdio，供 Host 拉起子进程
```

在 Cursor / Claude Desktop 的配置中注册该命令（`python weather_server.py`），Host 启动时会 `initialize` 并列出 `get_forecast`。

### 4.2 TypeScript（官方 SDK）

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "weather", version: "1.0.0" });

server.tool(
  "get_forecast",
  { city: z.string().describe("城市名，如 Shanghai") },
  async ({ city }) => ({
    content: [{ type: "text", text: `${city}: 晴，22°C` }],
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

工程建议：Tool 内只做 **薄适配**（参数校验 + 调用内部 REST/SDK），业务逻辑留在现有服务；Server 侧打结构化日志（`tool_name`、`latency`、`error_code`），便于与 Host 侧 trace 关联。

**Resources 示例思路**：为 Postgres Server 暴露 `postgres://{db}/tables/{name}`，返回 DDL 与采样行；模型写 SQL 前先 `resources/read` 对齐字段类型，再调用 `run_readonly_query` Tool，可显著降低幻觉列名。Prompts 则可注册 `incident_triage(severity, service)`，把 on-call 检查清单固化在 Server 而非各仓库的 `.cursorrules` 里。

---

## 5. 与 Claude / Cursor / LangChain 集成

**Claude Desktop**：在 `claude_desktop_config.json` 的 `mcpServers` 中声明 command 或 URL，重启后即可在对话里使用 Server 提供的 Tools/Resources。

**Cursor**：通过 MCP 设置添加 Server（stdio 或远程）。Agent 在规划任务时会 `tools/list`，再按需 `tools/call`；你可在规则里约束「先查 schema Resource 再写 SQL Tool」。

**LangChain**：使用 `langchain-mcp-adapters` 等包把 MCP Tool 转为 LangChain `StructuredTool`，接入 LCEL 或 LangGraph 节点。典型模式是图中一个 `mcp_tools` 节点负责绑定，与 [LangChain / LangGraph](/posts/agent-dev-langchain-langgraph.html) 一文中的 `bind_tools` 编排衔接——MCP 负责 **能力发现与进程隔离**，LangGraph 负责 **状态与重试**。

集成时注意：**不要把 MCP 当成数据库连接池**。高 QPS 场景应在 Server 内做连接复用与超时；Host 侧对单次 `tools/call` 设置 deadline，避免模型反复重试打爆下游。

在 Cursor Agent 中，常见模式是「**发现 → 调用** 两步」：先 `mcp_get_tools` 拉 schema，再 `mcp_call_tool` 带精确参数，避免参数幻觉。Claude 侧则常把 MCP Tool 与内置联网搜索并存——在 system 或项目说明里写清 **何时必须用内部 MCP、何时用公网**，可减少模型误选工具。LangGraph 里可为 MCP 调用单独设 `retry` 与 `fallback` 边：Tool 超时则转人工节点，而不是让 LLM 无限重试同一 `call`。

---

## 6. 安全与治理

MCP 把能力拆到独立 Server，安全重点从「prompt 里别泄露密钥」升级为 **供应链与权限**：

1. **最小权限**：Server 只暴露必要 Tool；读生产库用只读账号，写操作单独 Server 或二次确认。
2. **传输与身份**：远程 Server 用 HTTPS + mTLS 或 OAuth；勿在仓库提交长期 Token；优先短期凭证与 Secret Manager。
3. **输入校验**：所有 `tools/call` 参数按 JSON Schema 校验，防止 SQL 注入、路径遍历（`../../etc/passwd`）。
4. **人机在环**：破坏性操作（删库、发版、转账）在 Host 层弹窗确认，不要完全交给模型自动 `call`。
5. **审计**：记录 `session_id`、`tool_name`、参数摘要（脱敏）、调用方 Host 版本；便于 SOC2 与事故回溯。
6. **依赖供应链**：只安装可信 MCP Server；stdio 模式等同 **本地代码执行**，务必审查源码与启动命令。

与 [CrewAI / AutoGen](/posts/agent-dev-crewai-autogen.html) 多 Agent 场景结合时：建议 **一个 MCP Server 对应一个信任域**（如「只读分析」与「写操作」分 Server），避免高权限 Tool 被探索性对话误触。

---

## 7. 总结

MCP 用 Host–Client–Server 分层和 Resources / Tools / Prompts 三类原语，把 Agent 工具集成从「每个 Host 写一遍」变成「每个系统写一次 Server」。落地路径清晰：先用 Python 或 TypeScript SDK 为内部 API 包一层薄 Server → 在 Cursor/Claude 验证 → 再接入 LangGraph 做编排与评测。下一篇将深入 **Function Calling / Tool Use** 闭环，讲清模型侧 `tool_calls` 与 MCP `tools/call` 如何配合。

---

**系列导航 Series Navigation：**

- 上一篇：[CrewAI / AutoGen 多 Agent 协作](/posts/agent-dev-crewai-autogen.html)
- 下一篇：[Function Calling / Tool Use](/posts/agent-dev-function-calling.html)
