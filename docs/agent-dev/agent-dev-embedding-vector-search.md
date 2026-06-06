---
title: Agent 记忆系统：Embedding 与向量检索实战（Chroma / Milvus / Qdrant）
date: 2026-06-05 17:20:00
categories:
  - framework
tags:
  - Embedding
  - 向量检索
  - RAG
  - Agent
  - Chroma
---

> **English Title:** Agent Memory with Embeddings & Vector Search — Chroma, Milvus & Qdrant

掌握[大模型 API 调用](/posts/agent-dev-llm-api-guide.html)之后，Agent 仍面临一个硬约束：**上下文窗口有限，而业务记忆无限**。对话历史、用户偏好、文档知识库、工具执行日志——若全部塞进 Prompt，成本与延迟会迅速失控。Embedding 将文本映射为稠密向量，再配合向量数据库做相似度检索，是构建 Agent **长期记忆** 与 **RAG 知识注入** 的标准解法。它与 Prompt、Tool 调用并列，构成现代 Agent 栈的「数据面」。本文从原理到选型，再到可运行的 Python 流水线，帮你把「能对话」升级为「能记住、能查证」。

---

## 1. 为什么 Agent 需要向量记忆？

传统 Agent 只依赖滑动窗口内的 messages，会带来三类问题：

| 问题 | 表现 | 向量记忆如何解决 |
| --- | --- | --- |
| **遗忘** | 多轮后早期决策丢失 | 将关键片段写入向量库，按语义召回 |
| **幻觉** | 模型编造未见过的事实 | RAG 注入检索到的原文作为 grounding |
| **成本** | 全量历史 token 线性增长 | 只检索 Top-K 相关块，压缩有效上下文 |

Agent 记忆可粗分为：**短期**（当前 thread 的 messages）、**长期**（跨会话的用户画像与摘要）、**外部知识**（PDF、Wiki、工单）。Embedding + 向量检索主要服务后两者；短期记忆仍建议配合 Redis 或数据库存原文，向量层负责「按意思找片段」。例如用户说「还是按上次那样配环境」，系统无需扫描全部历史，只需用当前意图检索「上次环境配置」相关块即可。这种**语义索引**比关键词匹配更抗表述变化，是 Agent 体验从「健忘」到「贴心」的关键跃迁。

---

## 2. 文本 Embedding 模型选型

Embedding 模型的任务是把语义相近的句子映射到向量空间中彼此靠近的位置。主流选择：

| 模型 | 特点 | 适用场景 |
| --- | --- | --- |
| **OpenAI `text-embedding-3-small/large`** | 质量稳定、维度可调、与生态集成好 | 英文为主、愿付 API 费用 |
| **BGE（`BAAI/bge-m3` 等）** | 开源可私有化、中文表现优秀 | 内网部署、成本敏感 |
| **多语言（`multilingual-e5`、`bge-m3`）** | 中英混合、跨语言检索 | 全球化产品、混合语料 |

**选型原则：** 同一索引内**必须使用同一模型**；换模型需全量重嵌入。维度越高不一定越好——在召回率与存储/延迟之间权衡。中文 Agent 若走 API，可优先 `text-embedding-3-small`；若自建，BGE-M3 是常见默认。本地推理可用 `sentence-transformers` 加载 BGE，避免每次检索都走外网；注意 GPU 批处理能显著降低入库阶段的耗时。无论哪种模型，都应在离线集上做一次 **MTEB 或自建问答对** 的抽检，确认你的领域语料（工单、代码注释、产品手册）召回达标后再上线。

---

## 3. 相似度检索原理

向量检索的核心是比较查询向量 **q** 与库中向量 **d** 的相似度：

- **余弦相似度（Cosine）**：衡量方向一致性，对向量长度不敏感，文本场景最常用
- **点积（Dot Product）**：若向量已 L2 归一化，等价于余弦；未归一化时大范数向量会占优
- **欧氏距离（L2）**：几何距离，部分库默认支持

百万级以上规模时，全量暴力扫描不可行，需 **近似最近邻（ANN）** 索引。**HNSW**（分层可导航小世界图）是工业界主流：构建时建多层图，查询时从顶层贪心下降，在 **召回率 vs 延迟** 间通过 `ef_search`、`M` 等参数调节。理解这一点有助于调参：召回偏低时先增大 `ef`，而非盲目加 chunk。另有 IVF、PQ 等索引适合超大规模与内存受限场景，但 Agent 记忆库往往在百万条以内，HNSW 通常足够。检索返回的是「相似」而非「相同」——务必在 Prompt 中要求模型**仅依据检索片段回答**，并在无相关结果时明确说「知识库中未找到」，降低胡编风险。

---

## 4. 向量数据库对比：Chroma vs Milvus vs Qdrant

| 维度 | **Chroma** | **Milvus** | **Qdrant** |
| --- | --- | --- | --- |
| 定位 | 嵌入式 / 轻量原型 | 分布式、超大规模 | 生产级、过滤能力强 |
| 部署 | `pip install` 即可本地跑 | 需 K8s / 集群组件 | Docker 单节点即可起步 |
| 元数据过滤 | 基础 | 丰富 | **Payload 过滤** 体验好 |
| 规模 | 百万级内舒适 | 十亿级向量 | 千万～亿级 |
| Agent 场景 | 本地开发、MVP | 企业知识库、多租户 | 带权限的多用户记忆 |

**务实建议：** 学习与 PoC 用 **Chroma**；需要复杂 `where` 过滤（`user_id`、`session_id`）且要上生产，看 **Qdrant**；数据量与 SLA 要求极高、已有运维体系，选 **Milvus**。三者 Python SDK 心智模型相近：`collection` → `upsert` → `query`。

---

## 5. Agent 场景的 RAG 流水线

典型 RAG（Retrieval-Augmented Generation）在 Agent 中的位置：

```
文档/对话 → 分块(Chunk) → Embedding → 写入向量库
用户提问 → Query Embedding → Top-K 检索 → 拼入 Prompt → LLM 生成
```

与纯问答 RAG 不同，Agent 还需：**写入时机**（工具结果、用户确认的事实何时入库）、**检索时机**（Planner 决策前 vs 回答前）、**引用格式**（要求模型标注 `[1][2]` 便于审计）。记忆写入建议附带 `metadata`：`user_id`、`source`、`timestamp`、`importance`，便于过滤与过期清理。进阶做法是把检索封装为独立 **Tool**（如 `search_memory(query)`），由 LLM 决定何时查记忆，而不是每轮固定注入 Top-K——这在多跳任务中更省 token，也更接近人类「想起来再查」的行为。下一篇 [LangChain / LangGraph](/posts/agent-dev-langchain-langgraph.html) 将把此类节点编排进状态图。

---

## 6. Python 示例：嵌入、存储、检索

以下用 **Chroma** 演示最小闭环（需 `pip install chromadb openai`）：

```python
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.PersistentClient(path="./agent_memory")
collection = chroma.get_or_create_collection("memories")

def embed(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [d.embedding for d in resp.data]

# 写入记忆
docs = [
    "用户偏好：接口文档用 OpenAPI 3.1",
    "上次部署失败原因：Redis 连接超时",
]
ids = ["mem-1", "mem-2"]
collection.add(
    ids=ids,
    documents=docs,
    embeddings=embed(docs),
    metadatas=[{"user_id": "u42"}, {"user_id": "u42"}],
)

# 检索
query = "部署出过什么问题？"
q_emb = embed([query])[0]
hits = collection.query(
    query_embeddings=[q_emb],
    n_results=2,
    where={"user_id": "u42"},
)
for doc, dist in zip(hits["documents"][0], hits["distances"][0]):
    print(doc, dist)
```

将 `hits["documents"]` 拼入 system 或 user message 即可驱动 Agent 回答。生产环境把 `PersistentClient` 换成 Qdrant/Milvus 对应客户端，**接口模式不变**。

---

## 7. 常见陷阱

| 陷阱 | 后果 | 对策 |
| --- | --- | --- |
| **Chunk 过大/过小** | 过大噪声多；过小语义碎裂 | 512～1024 token，按段落或标题切分，适当 overlap |
| **无元数据过滤** | 召回他人记忆，严重越权 | 强制 `user_id` / `tenant_id` 过滤 |
| **混用 Embedding 模型** | 相似度失真 | 版本化索引，迁移时全量重嵌 |
| **只检索不校验** | 陈旧记忆误导模型 | 结合时间戳衰减 + LLM 判断「是否与问题相关」 |
| **忽略重排序** | Top-K 含噪声 | 可用 Cross-Encoder 或 LLM rerank 二次精选 |

另外：**不要把密钥写进向量库**；敏感内容入库前脱敏。评测时用固定「黄金问题集」测 Recall@K，而非凭感觉调 chunk。

---

## 8. 小结

Embedding 与向量检索是 Agent **记忆层** 的基建：它不负责推理，却决定 Agent 能否在有限上下文中「想起」正确信息。建议路径：Chroma 本地跑通 RAG → 加上 metadata 过滤 → 按规模迁移 Qdrant/Milvus → 与 LangGraph 的 checkpointer 分工（状态机管流程，向量库管语义记忆）。监控指标建议关注：**检索延迟 P99**、**Recall@5**、**注入 token 占比** 与 **「未找到仍作答」率**，四者联动才能判断记忆系统是否真的在帮 Agent，而不是增加噪声。掌握本文后，即可进入框架层，把检索节点编排进多步 Agent。

---

**系列导航 Series Navigation：**

- 上一篇：[主流模型 API 调用实战](/posts/agent-dev-llm-api-guide.html)
- 下一篇：[LangChain / LangGraph 核心](/posts/agent-dev-langchain-langgraph.html)
