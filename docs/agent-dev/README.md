# Agent 开发学习路线索引

> **正文位置**：`docs/agent-dev/agent-dev-*.md`（含 YAML front matter）  
> **同步目标**：`blog-source/source/_posts/agent-dev-*.md`（由 `sync_docs.py` 生成，勿手改）  
> **线上索引页**：[/posts/agent-dev-learning-roadmap-index.html](https://www.fastolf.com/posts/agent-dev-learning-roadmap-index.html)

本系列将 Agent 开发能力拆成 **五层模型、15 篇博文**（14 教程 + 1 索引），每篇约 1500–2500 字。

---

## 五层能力模型

| 层级 | 聚焦 | 系列篇目 |
|------|------|----------|
| **L1 编程基础** | 类型安全、异步 I/O、结构化输出 | Python、TypeScript/Node.js |
| **L2 大模型基础** | 提示词、API、记忆与 RAG | Prompt、API、Embedding |
| **L3 Agent 框架** | 编排、多 Agent、状态与 Handoff | LangChain/LangGraph、OpenAI SDK、CrewAI/AutoGen |
| **L4 工具集成** | 标准化工具协议与企业系统 | MCP、Function Calling、REST/OAuth/Webhook |
| **L5 工程化** | 部署、异步基础设施、质量闭环 | Docker/DevOps、Redis/队列、评估与测试 |

---

## 系列目录

| # | 源文件 | 线上 |
|---|--------|------|
| — | `agent-dev-learning-roadmap-index.md` | [/posts/agent-dev-learning-roadmap-index.html](https://www.fastolf.com/posts/agent-dev-learning-roadmap-index.html) |
| 01 | `agent-dev-python-foundation.md` | [/posts/agent-dev-python-foundation.html](https://www.fastolf.com/posts/agent-dev-python-foundation.html) |
| 02 | `agent-dev-typescript-nodejs.md` | [/posts/agent-dev-typescript-nodejs.html](https://www.fastolf.com/posts/agent-dev-typescript-nodejs.html) |
| 03 | `agent-dev-prompt-engineering.md` | [/posts/agent-dev-prompt-engineering.html](https://www.fastolf.com/posts/agent-dev-prompt-engineering.html) |
| 04 | `agent-dev-llm-api-guide.md` | [/posts/agent-dev-llm-api-guide.html](https://www.fastolf.com/posts/agent-dev-llm-api-guide.html) |
| 05 | `agent-dev-embedding-vector-search.md` | [/posts/agent-dev-embedding-vector-search.html](https://www.fastolf.com/posts/agent-dev-embedding-vector-search.html) |
| 06 | `agent-dev-langchain-langgraph.md` | [/posts/agent-dev-langchain-langgraph.html](https://www.fastolf.com/posts/agent-dev-langchain-langgraph.html) |
| 07 | `agent-dev-openai-agents-sdk.md` | [/posts/agent-dev-openai-agents-sdk.html](https://www.fastolf.com/posts/agent-dev-openai-agents-sdk.html) |
| 08 | `agent-dev-crewai-autogen.md` | [/posts/agent-dev-crewai-autogen.html](https://www.fastolf.com/posts/agent-dev-crewai-autogen.html) |
| 09 | `agent-dev-mcp-protocol.md` | [/posts/agent-dev-mcp-protocol.html](https://www.fastolf.com/posts/agent-dev-mcp-protocol.html) |
| 10 | `agent-dev-function-calling.md` | [/posts/agent-dev-function-calling.html](https://www.fastolf.com/posts/agent-dev-function-calling.html) |
| 11 | `agent-dev-api-integration.md` | [/posts/agent-dev-api-integration.html](https://www.fastolf.com/posts/agent-dev-api-integration.html) |
| 12 | `agent-dev-docker-devops.md` | [/posts/agent-dev-docker-devops.html](https://www.fastolf.com/posts/agent-dev-docker-devops.html) |
| 13 | `agent-dev-redis-message-queue.md` | [/posts/agent-dev-redis-message-queue.html](https://www.fastolf.com/posts/agent-dev-redis-message-queue.html) |
| 14 | `agent-dev-llm-evaluation-testing.md` | [/posts/agent-dev-llm-evaluation-testing.html](https://www.fastolf.com/posts/agent-dev-llm-evaluation-testing.html) |

---

## 编辑与发布

```bash
# 1. 编辑 docs/agent-dev/agent-dev-*.md
# 2. 构建
cd blog-source && ./deploy-to-root.sh
```

新增篇目：在 `docs/agent-dev/` 创建 `agent-dev-<topic>.md`（含 front matter），`sync_docs.py` 会自动 glob 发现。

同步更新：`agent-dev-learning-roadmap-index.md` 与本 README。

---

## 延伸阅读（已迁入 docs/agent-dev/）

| 主题 | 源文件 | 线上 |
|------|--------|------|
| LangGraph 生产指南 | `langgraph-production-agent-guide.md` | [/posts/langgraph-production-agent-guide.html](https://www.fastolf.com/posts/langgraph-production-agent-guide.html) |
| LLM Agent 架构全景 | `llm-agent-architecture-langchain-guide.md` | [/posts/llm-agent-architecture-langchain-guide.html](https://www.fastolf.com/posts/llm-agent-architecture-langchain-guide.html) |
