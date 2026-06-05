#!/usr/bin/env python3
"""Import docs/ai-agents markdown into Hexo source posts."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "ai-agents"
OUTPUT = Path(__file__).resolve().parent / "source" / "_posts"
TZ = timezone(timedelta(hours=8))
BASE_DATE_BATCH1 = datetime(2026, 6, 5, 11, 0, 0, tzinfo=TZ)
BASE_DATE_BATCH2 = datetime(2026, 6, 6, 10, 0, 0, tzinfo=TZ)

POSTS = [
    {
        "md": "hermes-openclaw-overview.md",
        "title": "Agent Hermes 与 OpenClaw（龙虾）：架构、应用与对比",
        "tags": ["AI Agent", "Hermes", "OpenClaw"],
        "batch": 1,
        "hour_offset": 0,
    },
    {
        "md": "memory-system.md",
        "title": "Agent Hermes 与 OpenClaw 记忆系统深度解析",
        "tags": ["AI Agent", "Memory", "Hermes", "OpenClaw"],
        "batch": 1,
        "hour_offset": 1,
    },
    {
        "md": "gateway.md",
        "title": "Agent Hermes 与 OpenClaw Gateway 架构深度解析",
        "tags": ["AI Agent", "Gateway", "Hermes", "OpenClaw"],
        "batch": 1,
        "hour_offset": 2,
    },
    {
        "md": "security-model.md",
        "title": "Agent Hermes 与 OpenClaw 安全模型深度解析",
        "tags": ["AI Agent", "Security", "Hermes", "OpenClaw"],
        "batch": 1,
        "hour_offset": 3,
    },
    {
        "md": "skills-learning-loop.md",
        "title": "Agent Hermes 与 OpenClaw 技能系统与学习闭环全解析",
        "tags": ["AI Agent", "Skills", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 0,
    },
    {
        "md": "tools-execution-environments.md",
        "title": "Agent Hermes 与 OpenClaw 工具链与执行环境全解析",
        "tags": ["AI Agent", "Tools", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 1,
    },
    {
        "md": "workspace-context-prompt.md",
        "title": "Agent Hermes 与 OpenClaw 工作区文件与 Prompt 组装全解析",
        "tags": ["AI Agent", "Prompt", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 2,
    },
    {
        "md": "automation-cron-heartbeat.md",
        "title": "Agent Hermes 与 OpenClaw 自动化调度与主动巡检全解析",
        "tags": ["AI Agent", "Cron", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 3,
    },
    {
        "md": "model-provider-cost.md",
        "title": "Agent Hermes 与 OpenClaw 模型 Provider 与 Token 成本优化全解析",
        "tags": ["AI Agent", "Model", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 4,
    },
    {
        "md": "multi-agent-delegation.md",
        "title": "Agent Hermes 与 OpenClaw 多 Agent 路由与子代理委派全解析",
        "tags": ["AI Agent", "Multi-Agent", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 5,
    },
    {
        "md": "plugins-mcp-ecosystem.md",
        "title": "Agent Hermes 与 OpenClaw 插件体系与 MCP 生态全解析",
        "tags": ["AI Agent", "MCP", "Plugins", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 6,
    },
    {
        "md": "deploy-migrate-operations.md",
        "title": "Agent Hermes 与 OpenClaw 部署迁移与运维实战指南",
        "tags": ["AI Agent", "Deploy", "Hermes", "OpenClaw"],
        "batch": 2,
        "hour_offset": 7,
    },
]


def post_id(slug: str) -> str:
    return hashlib.md5(slug.encode()).hexdigest()[:8]


def publish_date(meta: dict) -> datetime:
    base = BASE_DATE_BATCH1 if meta["batch"] == 1 else BASE_DATE_BATCH2
    return base + timedelta(hours=meta["hour_offset"])


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    created = 0

    for meta in POSTS:
        md_path = DOCS / meta["md"]
        if not md_path.exists():
            raise FileNotFoundError(md_path)

        body = md_path.read_text(encoding="utf-8").strip()
        date = publish_date(meta).strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{post_id(meta['md'])}.md"

        front_matter = [
            "---",
            f"title: {yaml_quote(meta['title'])}",
            f"date: {date}",
            "categories:",
            '  - "mechine"',
            "tags:",
        ]
        front_matter.extend(f'  - {yaml_quote(tag)}' for tag in meta["tags"])
        front_matter.append("---")

        (OUTPUT / filename).write_text("\n".join(front_matter) + "\n\n" + body + "\n", encoding="utf-8")
        created += 1

    print(json.dumps({"created": created, "output": str(OUTPUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
