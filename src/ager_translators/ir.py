"""Minimal AGER IR. Sample loader matches okf-agent-graph sample-ager v0.3.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LoopControl:
    type: str
    id: str
    expression: str | None = None
    max: float | None = None
    max_ms: int | None = None


@dataclass
class Agent:
    id: str
    role: str
    title: str
    description: str
    instructions: str
    tools: list[str] = field(default_factory=list)
    max_workers: int = 5
    record_key: str = ""


@dataclass
class Tool:
    id: str
    title: str
    description: str
    cost_usd: float = 0.0
    rules: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Edge:
    source: str
    target: str
    rel: str


@dataclass
class AgerGraph:
    id: str
    title: str
    description: str
    ager_version: str
    entry: str
    agents: list[Agent]
    tools: list[Tool]
    edges: list[Edge]
    max_turns: int
    price_budget: float
    deadline_ms: int
    loop_priority: list[str]


def load_sample() -> AgerGraph:
    return AgerGraph(
        id="parallel-research",
        title="Parallel research graph",
        description="Orchestrator-workers research with judge and synthesizer.",
        ager_version="0.3.0",
        entry="lead-researcher",
        max_turns=6,
        price_budget=2.5,
        deadline_ms=600_000,
        loop_priority=["goal", "deadline", "price_budget", "max_turns", "no_progress"],
        agents=[
            Agent("lead-researcher", "orchestrator", "Lead researcher", "Plans facets and drives the outer loop.", "Decompose the query, spawn workers, judge, synthesize.", max_workers=5, record_key="orchestrator_plans"),
            Agent("worker", "worker", "Specialist worker", "Isolated doer.", "Return structured findings only.", tools=["web_search"], record_key="worker_outputs"),
            Agent("judge", "judge", "Quality judge", "Rubric scorer.", "Pass if score >= 0.78.", record_key="judgments"),
            Agent("synthesizer", "synthesizer", "Synthesizer", "Fan-in reduce.", "Merge findings into a final report.", record_key="final_report"),
        ],
        tools=[
            Tool("web_search", "Web search", "Budgeted search with duplicate block.", cost_usd=0.002, rules=[
                {"id": "block-if-budget", "action": "block", "when": "run.cost.usd >= run.budget.usd"},
                {"id": "block-dup", "action": "block", "when": "duplicate q in last 5"},
            ]),
        ],
        edges=[
            Edge("lead-researcher", "worker", "spawns"),
            Edge("lead-researcher", "judge", "routes_to"),
            Edge("worker", "web_search", "uses"),
            Edge("synthesizer", "worker", "aggregates_from"),
        ],
    )


def load_bundle(path: Path | None) -> AgerGraph:
    if path is None or not (path / "index.md").exists():
        return load_sample()
    return load_sample()
