---
title: Agent 开发学习路线全览：五层能力模型与 14 篇技术博客索引
date: 2026-06-05 18:10:00
categories:
  - framework
tags:
  - Agent
  - 学习路线
  - LLM
  - 索引
  - AI
---

从「能调一次 API」到「能上线、能评估、能运维」，Agent 开发需要跨越语言栈、模型能力、编排框架、工具集成与工程化五条战线。本页是 **Agent 开发学习路线** 系列的 master index：将能力拆成 **五层模型、14 篇独立博文**，每篇约 1500–2500 字、含可运行示例与系列内上下篇链接，可单独阅读，也可按下文推荐顺序串成 2–4 周自学计划。

**适用读者**：有基础编程经验、希望系统补齐 LLM Agent 全栈能力的后端、全栈与 ML 工程师；不要求先通读 LangChain 文档，但建议具备 HTTP/JSON 与命令行使用经验。

## 五层能力模型

| 层级 | 聚焦 | 系列篇目 |
|------|------|----------|
| **第一层：编程基础** | 类型安全、异步 I/O、结构化输出 | Python、TypeScript/Node.js |
| **第二层：大模型基础** | 提示词、API、记忆与 RAG 数据面 | Prompt、API、Embedding |
| **第三层：Agent 框架** | 编排、多 Agent、状态与 Handoff | LangChain/LangGraph、OpenAI SDK、CrewAI/AutoGen |
| **第四层：工具集成** | 标准化工具协议与企业系统对接 | MCP、Function Calling、REST/OAuth/Webhook |
| **第五层：工程化** | 部署、异步基础设施、质量闭环 | Docker/DevOps、Redis/队列、评估与测试 |

**第一层**解决「运行时与数据契约」：Agent 代码大量依赖 `async/await`、流式响应与 Pydantic/Zod 校验，语言基本功不到位会在工具调用与状态持久化处反复踩坑。**第二层**解决「模型行为与知识注入」：同一套业务逻辑，Prompt 与 RAG 设计差一个档次，幻觉与成本会差一个数量级。**第三层**是多数团队的选型焦点：用图（LangGraph）还是 Handoff（OpenAI SDK）还是角色剧组（CrewAI），取决于任务是否需要确定性分支与人机协同。**第四层**把 Agent 从聊天玩具接到 CRM、工单与内部 API；MCP 与 Function Calling 分工在于「能力发现/隔离」与「单次工具契约」。**第五层**则回答上线后的问题：镜像与密钥、队列削峰、评测集防回归——没有这一层，Demo 很难变成可 SLO 的服务。

## 14 篇系列目录

### 第一层：编程基础

1. **[Agent 开发基础：Python 3.10+ 必备技能（类型注解 / 异步 / Pydantic）](/posts/agent-dev-python-foundation.html)**  
   异步 I/O、Pydantic 与类型注解，把 Python 用到主流 Agent 框架的预期水平。

2. **[Agent 全栈开发：TypeScript 与 Node.js 实战指南](/posts/agent-dev-typescript-nodejs.html)**  
   对话 UI、SSE 流式与 B 端控制台场景下的 TS 全栈 Agent 实践。

### 第二层：大模型基础

3. **[Agent 开发必修课：Prompt Engineering 系统性设计](/posts/agent-dev-prompt-engineering.html)**  
   角色、约束、Few-shot 与工具边界写法，是 Agent 可靠性的底座。

4. **[主流大模型 API 调用实战：OpenAI / Claude / DeepSeek / 通义千问](/posts/agent-dev-llm-api-guide.html)**  
   多厂商 SDK、流式、重试与用量控制，统一「你请求模型」这一侧。

5. **[Agent 记忆系统：Embedding 与向量检索实战（Chroma / Milvus / Qdrant）](/posts/agent-dev-embedding-vector-search.html)**  
   向量库选型与 RAG 流水线，解决上下文有限而业务记忆无限的问题。

### 第三层：Agent 框架

6. **[Agent 框架核心：LangChain 与 LangGraph 面试必考知识点](/posts/agent-dev-langchain-langgraph.html)**  
   LCEL、Tool 绑定、ReAct 与图 State/Checkpoint，生态内最通用的编排基座。

7. **[OpenAI Agents SDK 实战：Agent 定义、Handoff 与 Guardrails](/posts/agent-dev-openai-agents-sdk.html)**  
   官方轻量多 Agent 运行时，与 Responses API、Tracing 深度集成。

8. **[多 Agent 协作框架：CrewAI 角色扮演 vs AutoGen 对话驱动](/posts/agent-dev-crewai-autogen.html)**  
   角色化「剧组」与对话式群聊两种多 Agent 心智模型对比选型。

### 第四层：工具集成

9. **[MCP 协议实战：让 Agent 连接一切外部工具（Model Context Protocol）](/posts/agent-dev-mcp-protocol.html)**  
   标准化工具发现与进程隔离，把能力从 Host 应用中抽离。

10. **[Function Calling 深度解析：Tool Use 参数设计、并行调用与错误处理](/posts/agent-dev-function-calling.html)**  
    Schema、并行 Tool 与失败语义，让模型「知道该调什么、怎么调」。

11. **[Agent 外部世界集成：RESTful API、OAuth 认证与 Webhook 处理](/posts/agent-dev-api-integration.html)**  
    把 Agent 接到企业 REST、OAuth 与异步 Webhook 业务系统。

### 第五层：工程化

12. **[Agent 应用部署：Docker 容器化与基础 DevOps 实践](/posts/agent-dev-docker-devops.html)**  
    可复现镜像、密钥注入、CI 与可观测性，从笔记本 Demo 到可运维服务。

13. **[Agent 异步基础设施：Redis 缓存与消息队列实战](/posts/agent-dev-redis-message-queue.html)**  
    会话状态、限流、任务队列与多 Worker，支撑高并发 Agent 服务。

14. **[Agent 质量闭环：LLM 评估、回归测试与线上监控](/posts/agent-dev-llm-evaluation-testing.html)**  
    评测集、自动化回归与指标看板，让迭代可度量、可回滚。

## 推荐学习顺序

```
                    ┌─────────────────────────────────────┐
                    │  可选先读：架构全景 / LangGraph 生产  │
                    └─────────────────┬───────────────────┘
                                      ▼
  [01 Python] ──► [02 TS/Node] ──► [03 Prompt] ──► [04 API] ──► [05 Embedding]
                                      │
                                      ▼
              [06 LangChain/LangGraph] ──► [07 OpenAI SDK] ──► [08 CrewAI/AutoGen]
                                      │
                                      ▼
         [09 MCP] ──► [10 Function Calling] ──► [11 API 集成]
                                      │
                                      ▼
              [12 Docker] ──► [13 Redis/队列] ──► [14 评估与测试]
```

- **纵向主线**：01→05 打基础，06→08 选 1–2 个框架深入，09→11 接工具与业务，12→14 上线与质量。
- **横向选修**：只做 Python 后端可跳过 02；已有前端栈可 02 与 01 对调阅读顺序。
- **框架层不必三篇全读**：06 为通用基线；若团队已标准化 OpenAI 栈，07 优先；若业务是「多角色分工报告」，08 优先。
- **工具层建议 09→10→11 顺序**：先理解 MCP 传输与发现，再深化 Function Calling 参数设计，最后落到企业 API 的 OAuth 与 Webhook。

## 按角色快速选课

| 角色 | 建议路径 | 可精简 |
|------|----------|--------|
| **后端 / 数据工程师** | 01 → 03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13 → 14 | 02（无前端需求时） |
| **全栈 / 产品工程师** | 02 → 03 → 04 → 07 → 10 → 11 → 12 | 08（无多 Agent 需求时）；05 按需补 RAG |
| **ML / 算法工程师** | 03 → 04 → 05 → 06 → 14 → 08 | 01/02 若已熟练；工程篇 12–13 按团队分工 |

**后端**应保证 05（RAG/记忆）与 11（业务 API）不跳：生产 Agent 几乎都需要检索与写操作幂等。**全栈**可把 02 作入口，用 07 快速出可演示的多 Agent 原型，再在 12 补部署。**ML** 可把 14 提前：评测与回归是模型迭代的安全网；08 用于探索多 Agent 论文式工作流，与 06 的图编排形成对照。

每篇文末均有「上一篇 / 下一篇」链接；若从本索引跳入中间某篇，建议至少回读该层前置一篇（例如读 10 前先扫 09 的 MCP 与 04 的 `tools` 字段）。

## 延伸阅读（系列外深度文）

若希望先建立全局图景再逐篇精读，建议配合以下两篇（与系列 06 互补，不重复展开 LCEL 细节）：

- **[LLM Agent 架构全景：LangChain 生态设计与实践（中英文对照）](/posts/llm-agent-architecture-langchain-guide.html)** — ReAct、RAG、多 Agent 模式与生态选型鸟瞰。  
- **[LangGraph 深度指南：从图状态机到生产级 Agent（中英文对照）](/posts/langgraph-production-agent-guide.html)** — PostgresSaver、Studio、监控与生产部署细节。

## 学习节奏建议

| 阶段 | 篇目 | 目标产出 |
|------|------|----------|
| 第 1 周 | 01–05 | 能独立调用多模型 API，完成最小 RAG Demo |
| 第 2 周 | 06–08 + 架构全景 | 选定主框架，画出一张 Agent 状态或 Handoff 图 |
| 第 3 周 | 09–11 | 至少 1 个 Tool + 1 个业务 API 或 MCP Server 联调通过 |
| 第 4 周 | 12–14 | Docker 部署 + 基础评测集，具备可演示的端到端链路 |

---

按上表从第一层起步，或先读架构全景再按 slug 跳转对应博文，即可系统补齐 Agent 全栈能力。系列持续更新，欢迎从任意一篇收藏本索引以便回溯。祝学习顺利。
