"""Emitters. Each target returns {relative_path: content}."""

from __future__ import annotations

from .ir import AgerGraph


def emit_langgraph(g: AgerGraph) -> dict[str, str]:
    lead = next(a for a in g.agents if a.role == "orchestrator")
    graph_py = (
        f"# Generated from AGER {g.ager_version}: {g.title}\n"
        "from langgraph.graph import END, START, StateGraph\n"
        "from langgraph.types import Send\n\n"
        "def lead(state):\n"
        f"    facets = [f\"facet:{'{'}state['query']{'}'}\"][:{lead.max_workers}]\n"
        "    return {**state, 'plan': facets, 'outer_iteration': state.get('outer_iteration', 0) + 1}\n\n"
        "def fanout(state):\n"
        "    return [Send('worker', {**state, 'task': f}) for f in state.get('plan', [])]\n\n"
        "def worker(state):\n"
        "    outs = list(state.get('worker_outputs', [])) + [{'task': state.get('task')}]\n"
        "    return {**state, 'worker_outputs': outs}\n\n"
        "def judge(state):\n"
        "    score = min(1.0, 0.4 + 0.1 * len(state.get('worker_outputs', [])))\n"
        "    return {**state, 'judgment': {'pass': score >= 0.78, 'score': score}}\n\n"
        "def synth(state):\n"
        "    return {**state, 'final_report': str(state.get('worker_outputs'))}\n\n"
        "def loop_or_end(state):\n"
        "    if state.get('judgment', {}).get('pass'):\n"
        "        return 'synth'\n"
        f"    if state.get('outer_iteration', 0) >= {g.max_turns}:\n"
        "        return 'synth'\n"
        "    return 'lead'\n\n"
        "def build_graph():\n"
        "    gr = StateGraph(dict)\n"
        "    gr.add_node('lead', lead)\n"
        "    gr.add_node('worker', worker)\n"
        "    gr.add_node('judge', judge)\n"
        "    gr.add_node('synth', synth)\n"
        "    gr.add_edge(START, 'lead')\n"
        "    gr.add_conditional_edges('lead', fanout, ['worker'])\n"
        "    gr.add_edge('worker', 'judge')\n"
        "    gr.add_conditional_edges('judge', loop_or_end, {'lead': 'lead', 'synth': 'synth'})\n"
        "    gr.add_edge('synth', END)\n"
        "    return gr.compile()\n"
    )
    return {
        "pyproject.toml": f"[project]\nname = \"{g.id}-langgraph\"\nversion = \"0.1.0\"\nrequires-python = \">=3.11\"\ndependencies = [\"langgraph>=0.2\"]\n",
        "research_graph/graph.py": graph_py,
        "README.md": f"# {g.title} — LangGraph\n\nmax_turns={g.max_turns} price=${g.price_budget}\n",
    }


def emit_crewai(g: AgerGraph) -> dict[str, str]:
    agents = "\n".join(
        f"{a.id.replace('-', '_')} = Agent(role={a.title!r}, goal={a.description!r}, backstory={a.instructions!r}, allow_delegation={a.role == 'orchestrator'})"
        for a in g.agents
    )
    names = ", ".join(a.id.replace("-", "_") for a in g.agents)
    lead = next(a for a in g.agents if a.role == "orchestrator").id.replace("-", "_")
    return {
        "crew.py": (
            f"# Generated from AGER {g.ager_version}: {g.title}\n"
            "from crewai import Agent, Crew, Process, Task\n\n"
            f"{agents}\n\n"
            f"crew = Crew(agents=[{names}], process=Process.hierarchical, manager_agent={lead}, max_iter={g.max_turns}, memory=True)\n"
        ),
        "README.md": f"# {g.title} — CrewAI\n\nmax_iter={g.max_turns}\n",
    }


def emit_claude_sdk(g: AgerGraph) -> dict[str, str]:
    lead = next(a for a in g.agents if a.role == "orchestrator")
    subs = {
        a.id: {"description": a.description, "prompt": a.instructions, "tools": a.tools}
        for a in g.agents
        if a.id != lead.id
    }
    return {
        "agent.py": (
            f"# Generated from AGER {g.ager_version}\n"
            "from claude_agent_sdk import ClaudeAgentOptions, query\n\n"
            f"OPTIONS = ClaudeAgentOptions(system_prompt={lead.instructions!r}, max_turns={g.max_turns}, agents={subs!r})\n"
        ),
        "README.md": f"# {g.title} — Claude Agent SDK\n",
    }


def emit_claude_managed(g: AgerGraph) -> dict[str, str]:
    lines = [
        "apiVersion: anthropic.com/managed-agents/v1",
        "kind: AgentGraph",
        "spec:",
        f"  entry: {g.entry}",
        "  loop:",
        f"    max_turns: {g.max_turns}",
        f"    price_budget_usd: {g.price_budget}",
        "  agents:",
    ]
    for a in g.agents:
        lines += [f"    - id: {a.id}", f"      type: {a.role}", f"      name: {a.title!r}"]
    return {"managed-graph.yaml": "\n".join(lines) + "\n", "README.md": f"# {g.title} — Claude Managed Agents\n"}


def emit_deep_agents(g: AgerGraph) -> dict[str, str]:
    files = {
        "agent.py": (
            "from deepagents import create_deep_agent\n"
            "from deepagents.backends import FilesystemBackend\n"
            'agent = create_deep_agent(model="anthropic:claude-sonnet-4-5", backend=FilesystemBackend(root_dir=".", virtual_mode=True), skills=["./skills/"])\n'
        ),
        "README.md": f"# {g.title} — Deep Agents\n",
    }
    for a in g.agents:
        files[f"skills/{a.id}/SKILL.md"] = f"---\nname: {a.id}\ndescription: {a.description}\n---\n\n# {a.title}\n\n{a.instructions}\n"
    return files


def _plugin(g: AgerGraph, name: str, extra: str) -> dict[str, str]:
    return {
        extra: f'{{\n  "name": "{name}",\n  "version": "0.1.0",\n  "ager_version": "{g.ager_version}"\n}}\n',
        "skills/ager-run/SKILL.md": f"---\nname: ager-run\ndescription: Run {g.title}\n---\n\n# {g.title}\n\nEntry `{g.entry}`. max_turns={g.max_turns}.\n",
        "README.md": f"# {name}\n\nCompiled plugin for **{g.title}**.\n",
    }


def emit_claude_code(g: AgerGraph) -> dict[str, str]:
    return _plugin(g, "claude-code-ager", ".claude-plugin/plugin.json")


def emit_grok_build(g: AgerGraph) -> dict[str, str]:
    files = _plugin(g, "grok-build-ager", ".grok-plugin/marketplace.json")
    files[".claude-plugin/plugin.json"] = files[".grok-plugin/marketplace.json"]
    return files


def emit_codex(g: AgerGraph) -> dict[str, str]:
    return _plugin(g, "codex-ager", ".codex-plugin/plugin.json")


EMITTERS = {
    "langgraph": emit_langgraph,
    "crewai": emit_crewai,
    "claude-agent-sdk": emit_claude_sdk,
    "claude-managed": emit_claude_managed,
    "deep-agents": emit_deep_agents,
    "claude-code": emit_claude_code,
    "grok-build": emit_grok_build,
    "codex": emit_codex,
}

TARGETS = list(EMITTERS)
