---
title: Agent 评估与测试：LLM-as-Judge 与回归测试策略
date: 2026-06-05 18:05:00
categories:
  - framework
tags:
  - 评估
  - 测试
  - Agent
  - LLM-as-Judge
  - 质量
---

> **English Title:** Agent Evaluation & Testing — LLM-as-Judge and Regression Strategies

完成 [Redis 与消息队列](/posts/agent-dev-redis-message-queue.html) 后，你的 Agent 已经能在容器里跑起来、用 Redis 扛会话与任务队列。但「能跑」不等于「敢上线」：同一条用户问题，换模型版本或改一句 System Prompt，回答可能从正确工单分类变成幻觉引用。传统单元测试断言 `assert result == 42` 在 LLM 场景往往失效——你需要一套 **面向分布的评测体系**：可重复的 Golden Dataset、自动回归、以及用更强模型当裁判的 LLM-as-Judge。本文是系列第 14 篇（收官篇），把评估从「人肉点踩」推进到可 CI 集成的工程流程。

---

## 1. 为什么 Agent 测试特别难？

Agent 链路比单次 Chat Completion 更长：**规划 → 多轮 Tool 调用 → 记忆/RAG 注入 → 最终回复**。难点集中在以下几类：

| 难点 | 表现 | 对测试的启示 |
| --- | --- | --- |
| **非确定性（Non-determinism）** | 同输入多次运行，措辞、工具顺序可能不同 | 测「约束与结果类」而非逐字匹配 |
| **多步副作用** | 写库、发邮件、调支付 API | 用 Mock/Sandbox + 轨迹（trace）断言 |
| **上下文敏感** | 检索块变化导致答案漂移 | 固定检索快照或录制 replay |
| **评判主观** | 「回答是否有帮助」难以写 assert | 引入 Rubric + LLM-as-Judge 或人工抽检 |

因此 Agent 测试通常是 **分层组合**：底层 Tool 与解析器仍用确定性单测；中层用 **轨迹断言**（调了哪些工具、参数是否合法）；顶层用 **端到端评测集** 衡量任务完成率与安全合规。切忌只测「模型有没有返回字符串」——那会放过工具选错、参数幻觉等生产事故主因。

---

## 2. 评估维度：准确率、安全、延迟、成本

上线前建议把指标写进 Dashboard，并与业务 SLA 对齐：

| 维度 | 典型指标 | Agent 场景注意点 |
| --- | --- | --- |
| **准确率 / 任务完成率** | Exact Match、F1、人工 Pass@1 | 多步任务用「最终状态是否达标」（如工单是否创建） |
| **安全（Safety）** | 越狱成功率、PII 泄露、越权工具调用 | 单独红队集，与功能集分开跑 |
| **延迟（Latency）** | P50/P95 端到端、首 token 时间 | 含 Tool RTT；长链路看「步数上限」 |
| **成本（Cost）** | 每次会话 Token、$/1k 会话 | 换小模型做路由时对比「质量-成本」前沿 |

**工程习惯：** 每次 Prompt / 模型变更跑同一套 Golden Set，记录四维指标的 **delta**，避免「准确率升 2%、成本涨 40%」未被看见。安全维度建议 **失败即阻断合并**（fail closed），功能维度可用阈值 + 人工复核。

---

## 3. LLM-as-Judge 方法论

当参考答案无法逐字对比时，用 **更强的 Judge 模型**（或专用评测模型）按 Rubric 打分，是 2026 年 Agent 团队的主流做法。

**基本流程：**

1. 定义 **评分准则（Rubric）**：如「事实正确 0–2」「工具使用合理 0–2」「格式合规 0–1」。
2. Judge 输入：`用户问题 + Agent 最终回答 +（可选）参考要点 + 工具轨迹摘要`。
3. Judge 输出：**结构化 JSON**（分数 + 一句理由），便于聚合与回归对比。
4. **校准**：抽 50–100 条让人类标注，计算 Judge 与人类的 Cohen's κ；κ 过低则改 Rubric 或换 Judge 模型。

**常见陷阱：**

- **位置偏见（Position Bias）**：比较 A/B 两条回答时，Judge 偏爱先出现的；应随机交换顺序或分两次单评。
- **自我偏好**：用与被测相同的模型当 Judge 会偏宽松；尽量用 **更强或不同家族** 的模型。
- **长度偏见**：更长不等于更好；Rubric 里写明「简洁不扣分」。

Judge 适合评 **主观质量**；涉及数学、代码执行结果，仍应以 **可执行验证**（`pytest`、SQL 查询、API 回读）为准。

---

## 4. Golden Dataset 与回归测试

**Golden Dataset（黄金集）** 是一组经人工审核的 `(input, expected_behavior, optional_reference)`，覆盖主路径与已知边界（空输入、歧义、对抗、多语言等）。

构建原则：

- **版本化**：`datasets/support_v3.jsonl`，与 Prompt `v3`、模型 `gpt-4.1-mini` 绑定。
- **稳定输入**：RAG 场景可 **冻结检索结果**（recorded chunks），避免索引更新导致回归噪声。
- **行为断言优先于全文**：例如 `assert "create_ticket" in trace.tools` 或 `assert json.loads(output)["status"] == "ok"`。

**回归测试（Regression Testing）** 在 CI 中每次 PR 触发：对 Golden Set 跑 Agent → 聚合指标 → 与 **main 分支基线** 对比。若任务完成率下降超过阈值（如 3%）或安全用例失败，则阻断合并。样本量较小时可用 **统计检验** 或「连续两次 nightly 下降」再告警，降低抖动误报。

维护 Golden Set 时，建议为每条用例打上 **标签**（`billing`、`refund`、`rag_miss`），回归报告按标签出 breakdown——避免「总体准确率不变，但退款场景全面劣化」被平均值掩盖。对 flaky 用例（偶发网络超时），标记 `quarantine` 并单独追踪，不要与 Prompt 回归混在同一门禁里。

---

## 5. LangSmith 与自建 Eval Pipeline

**LangSmith**（及同类：Weights & Biases Weave、Braintrust、Arize Phoenix）提供：Trace 采集、数据集管理、在线/离线评测、Prompt 版本对比。适合已使用 LangChain/LangGraph 的团队——`run_on_dataset` 一类 API 能把「跑一遍集合并打分」标准化。

**自建 Pipeline** 适合深度定制或数据不出境的场景，最小架构：

```
Golden JSONL → Runner(Agent) → Traces(JSON) → Scorers(规则 + LLM Judge) → Report(HTML/PR Comment)
```

要点：Runner 与生产共用同一 **Tool Gateway 配置**（可指向 Mock）；Scorers 插件化（`exact_match`、`json_schema`、`llm_judge`）；结果写入 Postgres 或 S3，供历史曲线查询。无论 LangSmith 还是自建，都应把 **trace_id** 写进日志，方便从失败样本反查完整多步轨迹。

离线评测通过后，仍建议保留 **影子流量（Shadow）**：生产请求复制一份到评测环境，只记录不调真实副作用，用于发现「评测集未覆盖的长尾问法」。影子模式对 Redis 队列与 Worker 容量有要求——可与系列前文中的异步拓扑结合，避免拖慢主链路。

---

## 6. A/B 测试 Prompt 与模型

Prompt 与模型迭代应走 **实验框架**，而非直接全量切换：

| 阶段 | 做法 |
| --- | --- |
| 离线 | 同一 Golden Set 上对比 `prompt_v2` vs `prompt_v3`、模型 A vs B |
| 小流量在线 | 5%–10% 流量分流，看完成率、转人工率、平均成本 |
| 全量 | 胜出版本打 tag，基线写入回归配置 |

实验变量 **一次只改一类**（只改 System 或只换模型），否则无法归因。记录 `experiment_id` 到 trace metadata，便于 SQL 聚合。注意 **新奇效应**：新模型短期指标可能虚高，至少观察 1–2 个完整业务周期。

---

## 7. Python 评测示例

以下示例展示：**规则打分 + LLM-as-Judge + 简单回归门控**（伪代码级，便于迁入 pytest）。

```python
# eval/scorers.py
import json
from dataclasses import dataclass

@dataclass
class EvalCase:
    user_input: str
    must_call_tools: list[str]  # 例如 ["search_kb", "create_ticket"]
    reference_points: list[str]  # Judge 对照要点

def score_tools(trace: dict, case: EvalCase) -> float:
    called = {t["name"] for t in trace.get("tool_calls", [])}
    if not set(case.must_call_tools).issubset(called):
        return 0.0
    return 1.0

def llm_judge(client, case: EvalCase, answer: str) -> dict:
    rubric = (
        "按 0-5 打分：事实正确、工具合理、用户问题是否解决。"
        "只输出 JSON：{\"score\": int, \"reason\": str}"
    )
    resp = client.chat.completions.create(
        model="gpt-4.1",  # Judge 强于被测模型
        messages=[
            {"role": "system", "content": rubric},
            {"role": "user", "content": json.dumps({
                "question": case.user_input,
                "reference_points": case.reference_points,
                "answer": answer,
            }, ensure_ascii=False)},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)

# eval/run_regression.py
def run_suite(agent_run, cases: list[EvalCase], baseline: float = 0.85) -> None:
    scores = []
    for case in cases:
        trace, answer = agent_run(case.user_input)
        t = score_tools(trace, case)
        j = llm_judge(judge_client, case, answer)["score"] / 5.0
        scores.append(0.4 * t + 0.6 * j)  # 可按业务调权
    mean = sum(scores) / len(scores)
    assert mean >= baseline, f"regression: {mean:.3f} < {baseline}"
```

结合 **LangSmith** 时，可将 `agent_run` 换为 `client.run_on_dataset(dataset_name="support_golden_v3")`，自定义 `Evaluator` 封装上述 `llm_judge`。本地开发则用 `pytest -k eval` 只跑快速子集（10 条），nightly 跑全量 200+ 条。

---

## 8. 小结与系列导航

Agent 测试没有银弹，但有清晰路径：**确定性层测 Tool 与解析，分布层用 Golden Set + 回归，主观层用 LLM-as-Judge（需人工校准），上线用 A/B 验证业务指标**。把评测接进 CI 后，Prompt 迭代从「凭感觉」变为「有证据的发布」——这与本系列强调的 Prompt 版本化、Docker 交付、Redis 异步拓扑一起，构成可运维 Agent 产品的最后一块拼图。

**系列导航 Series Navigation：**

- 上一篇：[Redis 与消息队列](/posts/agent-dev-redis-message-queue.html)
- **系列目录（全 14 篇）**：[Agent 开发学习路线索引](/posts/agent-dev-learning-roadmap-index.html)（规划见仓库 `docs/agent-learning-series-plan.md`）
- 系列起点：[Python 3.10+ Agent 开发基础](/posts/agent-dev-python-foundation.html)

若你从零跟完本系列，建议用一篇 **roadmap 复盘文** 串起五层能力模型，并在团队内落地：Golden Dataset 仓库、每周回归报告、Judge κ 季度复核——让 Agent 质量成为可度量的工程资产，而非上线后的救火现场。
