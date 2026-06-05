# Agent 开发学习路线 — 博客系列规划

> 将五层能力模型拆分为 14 篇独立技术博客，由 subagent 逐篇展开写作，统一发布到 Hexo 博客。

## 系列结构

| # | 层级 | 技术点 | 文件名 slug | 优先级 |
|---|------|--------|-------------|--------|
| 01 | 第一层：编程基础 | Python 3.10+ Agent 开发基础 | `agent-dev-python-foundation` | 必修 |
| 02 | 第一层：编程基础 | TypeScript/Node.js 全栈 Agent 开发 | `agent-dev-typescript-nodejs` | 必修 |
| 03 | 第二层：大模型基础 | Prompt Engineering 系统性设计 | `agent-dev-prompt-engineering` | 必修 |
| 04 | 第二层：大模型基础 | 主流模型 API 调用实战 | `agent-dev-llm-api-guide` | 必修 |
| 05 | 第二层：大模型基础 | Embedding 与向量检索 | `agent-dev-embedding-vector-search` | 必修 |
| 06 | 第三层：Agent 框架 | LangChain / LangGraph 核心 | `agent-dev-langchain-langgraph` | 核心 |
| 07 | 第三层：Agent 框架 | OpenAI Agents SDK | `agent-dev-openai-agents-sdk` | 核心 |
| 08 | 第三层：Agent 框架 | CrewAI / AutoGen 多 Agent 协作 | `agent-dev-crewai-autogen` | 核心 |
| 09 | 第四层：工具与集成 | MCP 协议与 Server 开发 | `agent-dev-mcp-protocol` | 关键 |
| 10 | 第四层：工具与集成 | Function Calling / Tool Use | `agent-dev-function-calling` | 关键 |
| 11 | 第四层：工具与集成 | API 集成（REST/OAuth/Webhook） | `agent-dev-api-integration` | 关键 |
| 12 | 第五层：工程化 | Docker 与基础 DevOps | `agent-dev-docker-devops` | 必修 |
| 13 | 第五层：工程化 | Redis 与消息队列 | `agent-dev-redis-message-queue` | 必修 |
| 14 | 第五层：工程化 | Agent 评估与测试 | `agent-dev-llm-evaluation-testing` | 必修 |

## 每篇博客统一规范

- **路径**: `blog-source/source/_posts/<slug>.md`
- **Front Matter**:
  - `title`: 中文标题 + 可选英文副标题
  - `date`: 2026-06-05，按序号递增分钟（16:00 + index * 5min）
  - `categories`: `framework`（框架类）或 `python`/`node`（语言类）
  - `tags`: 与主题相关的 3-5 个标签
- **结构**:
  1. 引言（为什么学、在 Agent 开发中的位置）
  2. 核心概念（中英文对照关键术语）
  3. 代码示例（可运行的最小示例）
  4. 实战要点 / 常见陷阱
  5. 与 Agent 开发的关联
  6. 延伸阅读（系列内上下篇链接）
- **篇幅**: 1500-2500 字，技术博客风格，非教程流水账
- **语言**: 中文为主，关键术语附英文

## 发布流程

```bash
cd blog-source
npm ci
./deploy-to-root.sh
git add -A && git commit && git push
```

## 系列索引文（可选）

完成后可写一篇 `agent-dev-learning-roadmap-index.md` 作为系列目录页。
