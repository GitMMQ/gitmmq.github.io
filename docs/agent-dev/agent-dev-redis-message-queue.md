---
title: Agent 状态与任务队列：Redis 缓存与消息队列实战
date: 2026-06-05 18:00:00
categories:
  - framework
tags:
  - Redis
  - 消息队列
  - Agent
  - 会话管理
  - 缓存
---

> **English Title:** Agent State & Task Queues — Redis Caching & Message Queue Patterns

在 [Docker 与基础 DevOps](/posts/agent-dev-docker-devops.html) 里，你已经用 compose 把 Agent API、Redis 与向量库拉成同一拓扑。容器解决的是 **交付一致性**；真正扛住多用户并发、长对话与后台任务的，往往是 **Redis 作为会话缓存 + 消息队列中枢**。没有它，每个请求都把完整对话历史塞进 LLM 上下文，或把耗时 Tool 调用阻塞在 HTTP 线程里——延迟与成本会迅速失控。本文是系列第 13 篇，聚焦 Agent 场景下的 Redis 缓存模式、异步任务队列、Pub/Sub 协作，以及生产级持久化与 TTL 策略。

---

## 1. 为什么 Agent 离不开 Redis 与消息队列

Agent 运行时有三类「状态」需要跨请求、跨进程共享：

| 类型 | 典型内容 | 为何不能只放内存 |
| --- | --- | --- |
| **Session（会话）** | `thread_id`、最近 N 轮消息、用户偏好 | 多 Worker / 水平扩展后单进程内存不可见 |
| **Task（任务）** | 嵌入索引、批量 RAG、发邮件、调慢 API | LLM 与 Tool 耗时长，不能占满 HTTP 连接 |
| **Coordination（协作）** | 多 Agent 分工、人机审批闸门 | 需要广播「某步已完成」而非轮询 DB |

Redis 在 Agent 栈里常扮演三重角色：

1. **缓存（Cache）**：热会话、限流计数、短期 Tool 结果去重。
2. **队列（Queue）**：Celery / BullMQ / Redis Streams 承载异步 Job。
3. **Pub/Sub**：多 Agent 实例或「审批通过」事件的轻量通知。

与 Postgres / LangGraph Checkpointer 的分工：**Redis 管热路径与毫秒级读写**；关系库或专用 Checkpointer 管可审计、可回溯的长期状态。许多团队两者并存，而不是二选一。

常见反模式也要警惕：把 Redis 当「唯一真相源」却不做持久化，重启即丢全站会话；或把完整 RAG 检索结果（数万 token）塞进 String，导致 **big key** 阻塞单线程 Redis。正确做法是：**热小冷大**——热数据在 Redis，大块内容与审计日志在外部存储。

---

## 2. 会话状态缓存模式

### 2.1 Key 设计与 TTL

推荐按租户与会话隔离 Key，避免全局撞车：

```text
agent:session:{tenant_id}:{thread_id}  → Hash
agent:ratelimit:{user_id}              → String (INCR + EXPIRE)
```

**Hash 存会话字段** 示例：`messages`（JSON 数组或压缩 blob）、`last_model`、`tool_state`、`updated_at`。每次用户发消息时 `HSET` 更新，并 `EXPIRE` 滑动续期（如 24h 无活动则淘汰）。

### 2.2 只缓存「窗口」而非全量历史

LLM 上下文有 token 上限。缓存策略应是：

- Redis 存 **最近 K 轮** 或 **摘要 + 最近几轮**（摘要可由异步 Job 生成后写回 Hash 字段 `summary`）。
- 冷历史落库或对象存储；需要时再按 `thread_id` 拉取。

这样既控制 Redis 内存，也避免每次请求反序列化 megabytes 级 JSON。

### 2.3 与 Checkpointer 对齐

若使用 LangGraph，Checkpointer 可能写 Postgres；Redis 仍可作 **读加速层**：API 先读 Redis，miss 再读 DB 并回填。注意 **写顺序**：以 Checkpointer 为准，Redis 仅缓存，避免双写不一致。

### 2.4 限流与熔断

Agent 调用 LLM 按 token 计费，必须在 Redis 做 **租户级限流**：`INCR agent:rl:{tenant}:{minute}` 配合 `EXPIRE 60`，超限则返回 429 或降级到更小模型。Tool 调用外部 API 时，同样可对 `user_id + tool_name` 维度限流，防止模型陷入「疯狂重试」把下游打挂。

---

## 3. 异步任务队列：Celery、BullMQ 与 Redis Streams

Agent 中适合入队的操作：文档切块嵌入、向量库 upsert、发送通知、重试失败的 Webhook、长耗时 Tool（生成报告 PDF 等）。

| 方案 | 生态 | 特点 |
| --- | --- | --- |
| **Celery + Redis broker** | Python | 成熟、生态丰富；需单独 Worker 进程 |
| **BullMQ** | Node.js | 延迟任务、重试、优先级队列开箱即用 |
| **Redis Streams + Consumer Group** | 语言无关 | 轻量、可回溯；需自己处理 ACK 与死信 |

**选型建议：** Python 全栈 Agent 优先 Celery；Node 服务用 BullMQ；若已有统一 Redis 且团队愿维护消费逻辑，Streams 可减少中间件种类。

任务载荷应包含：`job_id`、`thread_id`、`tenant_id`、`trace_id`（对接 OpenTelemetry），便于日志串联。幂等键写入 Redis `SET job:done:{id} NX EX 3600`，防止 Worker 重试导致重复副作用。

**与 HTTP 请求的衔接：** API 收到用户消息后，先写会话 Hash，再 `delay()` / `add()` 入队；立即返回 `202 Accepted` 与 `job_id`，前端轮询或 SSE 订阅进度字段 `status`（`queued` → `running` → `done`）。这样用户不必盯着 30 秒的 Tool 调用，体验与 [API 集成](/posts/agent-dev-api-integration.html) 里的 Webhook 异步模式一致。

Celery 配置要点：`task_acks_late=True` 保证 Worker 崩溃时任务可重投；`task_time_limit` 防止嵌入死循环；`result_backend` 可仍用 Redis，但 **不要把超大结果塞进 backend**——结果写对象存储，Redis 只存 URL。

---

## 4. Pub/Sub 与多 Agent 协调

Redis 经典 Pub/Sub **不持久化**：订阅者离线则消息丢失，适合「提示性」事件，不适合资金类事务。

典型 Agent 场景：

- **Human-in-the-loop**：审批服务 `PUBLISH agent:approval:{thread_id} '{"approved":true}'`，阻塞中的 Agent Worker `SUBSCRIBE` 后恢复图执行。
- **多 Agent 广播**：Planner 完成分解后 `PUBLISH agent:plan:ready`，Executor 实例各自订阅（或按 channel 分片）。

需要 **至少一次投递** 时，改用 **Redis Streams** 或独立 MQ（RabbitMQ、Kafka），不要用裸 Pub/Sub。

[CrewAI / AutoGen 多 Agent](/posts/agent-dev-crewai-autogen.html) 场景下，可用 channel 区分角色：`agent:role:planner`、`agent:role:critic`。Planner 发布子任务描述，多个 Executor 竞争消费 Stream，避免单点 Worker 成为瓶颈——这与消费者组（Consumer Group）模型天然契合。

---

## 5. Agent 场景下的 Redis 数据结构

| 结构 | Agent 用途 | 常用命令 |
| --- | --- | --- |
| **String** | 限流、分布式锁、简单 KV 缓存 | `INCR`, `SET NX EX` |
| **Hash** | 会话字段、Tool 中间状态 | `HSET`, `HGETALL` |
| **List** | 简单 FIFO 任务（轻量场景） | `LPUSH`, `BRPOP` |
| **Stream** | 可回溯任务流、事件溯源 | `XADD`, `XREADGROUP` |
| **Set** | 去重 job_id、在线 Worker 注册 | `SADD`, `SMEMBERS` |
| **Sorted Set** | 延迟队列（score = 执行时间戳） | `ZADD`, `ZRANGEBYSCORE` |

**List vs Stream：** List 实现简单，但无 Consumer Group、难追溯；生产更推荐 Stream 或 Celery/BullMQ。

---

## 6. Python 示例（redis-py）

安装：`pip install redis`。

```python
import json
import redis
from datetime import timedelta

r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)

SESSION_TTL = int(timedelta(hours=24).total_seconds())

def session_key(tenant_id: str, thread_id: str) -> str:
    return f"agent:session:{tenant_id}:{thread_id}"

def append_message(tenant_id: str, thread_id: str, role: str, content: str) -> None:
    key = session_key(tenant_id, thread_id)
    raw = r.hget(key, "messages") or "[]"
    messages = json.loads(raw)
    messages.append({"role": role, "content": content})
    # 只保留最近 20 条，控制体积
    messages = messages[-20:]
    pipe = r.pipeline()
    pipe.hset(key, mapping={"messages": json.dumps(messages, ensure_ascii=False)})
    pipe.expire(key, SESSION_TTL)
    pipe.execute()

def enqueue_embedding_job(job_id: str, doc_id: str, payload: dict) -> None:
    r.xadd(
        "agent:jobs:embed",
        {"job_id": job_id, "doc_id": doc_id, "payload": json.dumps(payload)},
        maxlen=10000,  # 近似裁剪，防止 Stream 无限增长
    )

def consume_embed_group(consumer_name: str):
    group = "embed_workers"
    stream = "agent:jobs:embed"
    try:
        r.xgroup_create(stream, group, id="0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    while True:
        resp = r.xreadgroup(group, consumer_name, {stream: ">"}, count=1, block=5000)
        if not resp:
            continue
        for _stream, entries in resp:
            for msg_id, fields in entries:
                # ... 执行嵌入，写向量库 ...
                r.xack(stream, group, msg_id)
```

Celery 侧只需将 broker 设为 `redis://...`，任务函数内复用上述 `append_message` 更新会话进度即可。

---

## 7. 生产环境：持久化、集群与 TTL

### 7.1 持久化

- **RDB**：定时快照，恢复快，可能丢最近几分钟数据。
- **AOF**：追加写日志，可配置 `everysec`，会话与队列数据更安全。

Agent 会话若可重建，可接受适度丢失；**任务队列与 Stream** 建议开启 AOF，并监控 `appendfsync` 延迟。

### 7.2 高可用

- **Redis Sentinel**：主从自动故障转移，适合中小规模。
- **Redis Cluster**：数据分片，注意 **多 key 事务与 Lua** 受 slot 限制；会话 Key 用 hash tag：`agent:session:{tenant}:{thread}` 保证同 slot。

### 7.3 TTL 与内存

- 所有会话 Key **必须 EXPIRE**，防止僵尸 thread 吃光内存。
- 配置 `maxmemory-policy volatile-lru`（或 `allkeys-lru`），并为 Stream 设置 `MAXLEN ~`。
- 大 payload 不要进 Redis：存 S3/MinIO，Redis 只存指针 `s3://bucket/key`。

### 7.4 安全

生产禁用 `FLUSHALL` 权限；TLS 连接；密码与 ACL 按服务拆分（API 只读写 session 前缀，Worker 只访问 queue 前缀）。

### 7.5 可观测性

在 [Docker 部署](/posts/agent-dev-docker-devops.html) 之上，为 Redis 增加指标：`used_memory`、`connected_clients`、`instantaneous_ops_per_sec`、Stream 的 `lag`（待消费条数）。Agent 侧自定义 metric：`session_cache_hit_ratio`、`queue_wait_seconds`、`tool_retry_count`。告警阈值示例：内存使用率 > 80%、某 Stream lag 连续 5 分钟 > 1000。

---

## 8. 小结

Redis 让 Agent 服务具备 **可共享的会话热数据、可扩展的异步任务、可协作的轻量事件通道**。实践路径：先用 Hash + TTL 管会话窗口 → 将慢 Tool 与嵌入迁到 Celery/Streams → 仅在需要广播时用 Pub/Sub，可靠投递用 Stream 或专业 MQ → 最后补齐持久化、集群与监控（内存、连接数、Stream lag）。完成本篇后，建议继续 [Agent 评估与测试](/posts/agent-dev-llm-evaluation-testing.html)，用可重复的评测集验证「队列里的 Agent」是否仍然答得准、走得稳。

---

**系列导航 Series Navigation：**

- 上一篇：[Docker 与基础 DevOps](/posts/agent-dev-docker-devops.html)
- 下一篇：[Agent 评估与测试](/posts/agent-dev-llm-evaluation-testing.html)
