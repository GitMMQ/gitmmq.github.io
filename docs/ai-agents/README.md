# AI Agent 文档索引 | AI Agent Documentation Index

本目录收录 **Agent Hermes** 与 **OpenClaw（龙虾）** 的完整中英文对照技术文档（**12 篇 + 知识地图**）。

完整知识点覆盖矩阵见 [knowledge-map.md](./knowledge-map.md)。

## 推荐阅读顺序 | Suggested Reading Order

总览 → 部署 → 工作区 → Gateway → 记忆 → 技能 → 工具 → 插件 → 多Agent → 自动化 → 模型 → 安全

## 文章目录 | Article Index

| # | 文档 | 博客链接 | 说明 |
|---|------|----------|------|
| 1 | [hermes-openclaw-overview.md](./hermes-openclaw-overview.md) | [/posts/3131a1c6.html](/posts/3131a1c6.html) | 总览：架构、应用、优缺点 |
| 2 | [deploy-migrate-operations.md](./deploy-migrate-operations.md) | [/posts/f10df97a.html](/posts/f10df97a.html) | 部署迁移与运维实战 |
| 3 | [workspace-context-prompt.md](./workspace-context-prompt.md) | [/posts/17b36b1c.html](/posts/17b36b1c.html) | 工作区文件与 Prompt 组装 |
| 4 | [gateway.md](./gateway.md) | [/posts/65592aa7.html](/posts/65592aa7.html) | Gateway 架构 |
| 5 | [memory-system.md](./memory-system.md) | [/posts/9fd79a5e.html](/posts/9fd79a5e.html) | 记忆系统 |
| 6 | [skills-learning-loop.md](./skills-learning-loop.md) | [/posts/13d06324.html](/posts/13d06324.html) | 技能系统与学习闭环 |
| 7 | [tools-execution-environments.md](./tools-execution-environments.md) | [/posts/83e13b7e.html](/posts/83e13b7e.html) | 工具链与执行环境 |
| 8 | [plugins-mcp-ecosystem.md](./plugins-mcp-ecosystem.md) | [/posts/44679524.html](/posts/44679524.html) | 插件体系与 MCP 生态 |
| 9 | [multi-agent-delegation.md](./multi-agent-delegation.md) | [/posts/91d18535.html](/posts/91d18535.html) | 多 Agent 路由与子代理 |
| 10 | [automation-cron-heartbeat.md](./automation-cron-heartbeat.md) | [/posts/65977e9c.html](/posts/65977e9c.html) | 自动化调度与主动巡检 |
| 11 | [model-provider-cost.md](./model-provider-cost.md) | [/posts/7df1e50a.html](/posts/7df1e50a.html) | 模型 Provider 与成本优化 |
| 12 | [security-model.md](./security-model.md) | [/posts/26215170.html](/posts/26215170.html) | 安全模型 |

## 发布 | Publishing

```bash
python3 scripts/publish_ai_agent_posts.py
```

将 `docs/ai-agents/*.md`（除 README、knowledge-map）转为 Hexo 静态 HTML 并幂等更新站点索引。

## 参考资源 | References

- OpenClaw 文档：https://docs.openclaw.ai/
- Hermes Agent 文档：https://hermes-agent.nousresearch.com/docs/
- Hermes GitHub：https://github.com/NousResearch/hermes-agent
- OpenClaw GitHub：https://github.com/openclaw/openclaw
- Agent Skills 开放标准：https://agentskills.io
