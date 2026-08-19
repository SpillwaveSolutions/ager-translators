# ager-translators

**AGER translation layer** — compile a portable [OKF Agent Graph](https://github.com/SpillwaveSolutions/okf-agent-graph) (AGER v0.3) into runnable framework projects and host plugins.

AGER stays the source of truth. These packages are **emitters**.

## Family

| Package / repo | Emits |
| --- | --- |
| `ager-ir` (this repo) | Typed IR (load OKF/AGER → dataclasses) |
| [langgraph-ager](https://github.com/SpillwaveSolutions/langgraph-ager) | LangGraph `StateGraph` + Send fan-out + LoopPolicy breaks |
| [crewai-ager](https://github.com/SpillwaveSolutions/crewai-ager) | CrewAI hierarchical Crew (`manager_agent`, `max_iter`) |
| [claude-agent-sdk-ager](https://github.com/SpillwaveSolutions/claude-agent-sdk-ager) | Claude Agent SDK lead + subagents + tools |
| [claude-managed-agents-ager](https://github.com/SpillwaveSolutions/claude-managed-agents-ager) | Managed Agents YAML manifest |
| [langchain-deep-agents-ager](https://github.com/SpillwaveSolutions/langchain-deep-agents-ager) | Deep Agents + skills from AgentNodes |
| [claude-code-ager](https://github.com/SpillwaveSolutions/claude-code-ager) | Claude Code plugin (skills / agents / commands) |
| [grok-build-ager](https://github.com/SpillwaveSolutions/grok-build-ager) | Grok Build plugin (`.grok-plugin` + Claude layout) |
| [codex-ager](https://github.com/SpillwaveSolutions/codex-ager) | Codex plugin (`$ager-run`) |

Depends on [`okf-agent-graph`](https://github.com/SpillwaveSolutions/okf-agent-graph) (schema) and [`okf-plugin`](https://github.com/SpillwaveSolutions/okf-plugin) (graph validate / Mermaid).

## CLI

```bash
pip install -e .
ager-compile --target langgraph --bundle path/to/sample-ager --out ./generated/langgraph
ager-compile --target crewai --bundle path/to/sample-ager --out ./generated/crewai
ager-compile --list
```

Targets: `langgraph`, `crewai`, `claude-agent-sdk`, `claude-managed`, `deep-agents`, `claude-code`, `grok-build`, `codex`.

## Mapping (AGER → runtime)

| AGER | LangGraph | CrewAI | Claude | Deep Agents |
| --- | --- | --- | --- | --- |
| OrchestratorAgent | supervisor node | manager_agent | lead | system prompt |
| WorkerAgent | Send worker | Agent | subagent | skill |
| LoopControl | recursion + breaks | max_iter | max_turns | host recursion |
| ScratchPad | state keys | memory | artifacts | backend FS |
| ToolRule | pre-tool hook | tool wrap | permissions | skill policy |
| HumanGate | interrupt() | human input | review | interrupt |

## License

MIT
