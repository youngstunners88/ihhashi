# Autonomous Agent Orchestration Skill

A comprehensive skill system that integrates **Composio Agent Orchestrator**, **Qwen 3.5 Tentacles**, and **Persistent Agent Memory** for fully autonomous, strategic AI operations.

## Overview

This skill system provides:

1. **Agent Orchestrator Integration** - Spawn parallel AI agents with git worktree isolation
2. **Qwen 3.5 Tentacles** - Multi-model specialized agents (analyzer, coder, reviewer, planner, explainer)
3. **Persistent Memory** - Cross-session learning via SQLite + Markdown logs + Shared Brain
4. **Strategic Autonomy** - Self-directed planning, execution, and learning

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGIC AUTONOMY LAYER                      │
│         (Self-directed planning, execution, learning)            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Qwen      │  │  Composio   │  │    Persistent Memory    │  │
│  │  Tentacles  │  │ Orchestrator│  │  (SQLite + Filesystem)  │  │
│  │             │  │             │  │                         │  │
│  │ • Analyzer  │  │ • Parallel  │  │ • Knowledge DB          │  │
│  │ • Coder     │  │   Agents    │  │ • Agent Logs            │  │
│  │ • Reviewer  │  │ • Worktrees │  │ • Shared Brain          │  │
│  │ • Planner   │  │ • CI/CD     │  │ • Cross-Agent State     │  │
│  │ • Explainer │  │ • Reactions │  │ • Boot Injection        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      EXECUTION MODES                             │
│  • Single Tentacle → One specialized task                        │
│  • Swarm Attack → Parallel comprehensive analysis                │
│  • Strategic Planning → Multi-phase waterfall execution          │
│  • Autonomous Coding → Full SDLC in one command                  │
│  • Orchestrated Fleet → Multiple agents on multiple repos        │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

```bash
# Node.js 20+ for Agent Orchestrator
# Python 3.10+ for skill system
# Git 2.25+
# tmux (default runtime)
# Ollama with Qwen models
```

### Setup

```bash
# 1. Clone/update the orchestrator (already done)
cd ~/composio-orchestrator

# 2. Build the orchestrator (when Node.js available)
# pnpm install && pnpm build

# 3. Initialize persistent memory
python3 ~/persistent-agent-memory/scripts/init_databases.py

# 4. Install this skill
cp -r skills/* ~/.kimi/skills/
```

## Quick Start

```python
from skills.integrated_autonomous_skill import get_integrated_skill

# Get the integrated skill
skill = get_integrated_skill()

# 1. Strategic Analysis
result = skill.strategic_analyze("Refactor authentication system")
print(result['synthesis'])
print(result['recommendations'])

# 2. Autonomous Coding
result = skill.autonomous_code_task(
    feature="Add OAuth2 login with Google",
    codebase="Current project uses FastAPI with JWT"
)
print(result.final_output)

# 3. Parallel Code Review
review = skill.parallel_code_review(your_code)
print(review['summary'])

# 4. Continue from Memory
result = skill.recall_and_continue("authentication work")
```

## Component APIs

### Qwen Tentacles

```python
from skills.qwen_tentacles import get_tentacles, TentacleRole

tentacles = get_tentacles()

# Single tentacle
result = tentacles.spawn_tentacle(
    role=TentacleRole.CODER,
    prompt="Write a Redis cache wrapper",
    context="Python 3.11, async/await, type hints"
)

# Swarm attack (all tentacles in parallel)
results = tentacles.swarm_attack("Design a rate limiter")

# Strategic planning (4-phase waterfall)
plan = tentacles.strategic_planning(
    objective="Build a webhook system",
    constraints=["< 100ms latency", "99.9% uptime"]
)

# Autonomous coding (full SDLC)
solution = tentacles.autonomous_coding("Add user roles system")
```

### Persistent Memory

```python
from skills.persistent_memory_skill import get_memory

memory = get_memory()

# Write agent memory
memory.write_agent_memory(
    agent_id="kimi-coder",
    entry="Fixed bug in auth module",
    tags=["bugfix", "auth"]
)

# Read recent memory
logs = memory.read_agent_memory("kimi-coder", days=2)

# Log knowledge
memory.log_knowledge(
    fact="FastAPI dependency injection uses async generators",
    category="frameworks",
    source="docs",
    agent_id="kimi-coder"
)

# Recall knowledge
facts = memory.recall_knowledge("FastAPI", category="frameworks", limit=5)

# Shared brain (cross-agent communication)
memory.update_shared_brain("intel-feed", {
    "entries": [{"type": "finding", "content": "New CVE in OpenSSL"}]
})
intel = memory.read_shared_brain("intel-feed")

# Boot context (load at startup)
context = memory.boot_context("kimi-coder")
```

### Agent Orchestrator

```python
from skills.orchestrator_skill import get_orchestrator

orch = get_orchestrator()

# Spawn agent for issue
task_id = orch.spawn_agent("my-project", issue="#123")

# Spawn multiple agents
task_ids = orch.spawn_parallel("my-project", ["#123", "#124", "#125"])

# Check status
status = orch.get_status()
```

## Usage Patterns

### Pattern 1: Research → Plan → Execute

```python
skill = get_integrated_skill()

# 1. Research with swarm
research = skill.strategic_analyze("How to implement CQRS pattern")

# 2. Plan based on research
plan = skill.strategic_plan_and_execute(
    objective="Implement CQRS for order system",
    constraints=[research['recommendations'][0]]
)

# 3. Execute with memory
result = skill.autonomous_code_task(
    feature="CQRS order commands and queries",
    codebase=plan.final_output
)
```

### Pattern 2: Recall → Continue → Learn

```python
skill = get_integrated_skill()

# Recall similar work
past = skill.recall_and_continue("payment processing")

if past:
    # Continue from where we left off
    result = skill.strategic_analyze(
        "Continue payment work",
        context=past['synthesis']
    )
else:
    # Start fresh
    result = skill.strategic_analyze("Design payment system")

# Always learn from results
skill.memory.log_knowledge(
    fact=f"Payment approach: {result['recommendations'][0]}",
    category="payments",
    agent_id=skill.agent_id
)
```

### Pattern 3: Parallel Review → Fix → Verify

```python
skill = get_integrated_skill()

# Review code from multiple angles
review = skill.parallel_code_review(
    code=new_code,
    criteria=["security", "performance", "maintainability"]
)

if not review['approved']:
    # Fix issues
    fix = skill.autonomous_code_task(
        feature=f"Fix issues: {review['issues_found']}",
        codebase=new_code
    )
    
    # Re-verify
    re_review = skill.parallel_code_review(fix.final_output)
```

## Configuration

### Agent Orchestrator Config

Create `~/agent-orchestrator.yaml`:

```yaml
port: 3000

defaults:
  runtime: tmux
  agent: qwen-tentacle  # Our custom agent plugin
  workspace: worktree
  notifiers: [desktop]

projects:
  my-app:
    repo: owner/my-app
    path: ~/my-app
    defaultBranch: main
    sessionPrefix: app

reactions:
  ci-failed:
    auto: true
    action: send-to-agent
    retries: 2
```

### Tentacle Model Mapping

Edit `skills/qwen_tentacles.py`:

```python
ROLE_MODELS = {
    TentacleRole.ANALYZER: "qwen2.5:14b",
    TentacleRole.CODER: "qwen2.5-coder:14b",
    TentacleRole.REVIEWER: "qwen2.5:14b",
    TentacleRole.PLANNER: "qwen2.5:32b",
    TentacleRole.EXPLAINER: "qwen2.5:14b",
}
```

## Agent Orchestrator Plugin: Qwen Tentacle

The Qwen Tentacle agent plugin allows the orchestrator to use Qwen models as agents.

```typescript
// packages/plugins/agent-qwen-tentacle/src/index.ts
export const manifest = {
  name: "qwen-tentacle",
  slot: "agent" as const,
  description: "Agent plugin: Qwen 3.5 Tentacles via Ollama",
  version: "1.0.0",
};
```

Features:
- Multi-model selection based on task type
- Persistent memory boot injection
- Automatic memory write-back
- Tentacle role assignment per task

## Persistent Memory Protocol

### Write Protocol (After Every Task)

```python
# 1. Log to agent memory
memory.write_agent_memory(
    agent_id="kimi",
    entry="Did X, found Y, decided Z"
)

# 2. Update shared brain if cross-agent relevant
memory.update_shared_brain("intel-feed", {"entries": [...]})

# 3. Log knowledge for future recall
memory.log_knowledge(fact="...", category="...")
```

### Read Protocol (Before Every Task)

```python
# Boot injection loads context automatically
context = memory.boot_context("kimi")

# Or manually check recent work
logs = memory.read_agent_memory("kimi", days=2)
handoffs = memory.read_shared_brain("agent-handoffs")
```

## Command Reference

### CLI Commands

```bash
# Orchestrator
ao start https://github.com/user/repo        # Start with repo
ao spawn my-project 123                      # Spawn agent for issue
ao status                                    # Check all sessions
ao kill session-1                            # Kill session

# Persistent Memory
python3 scripts/boot_agent.py --agent-id kimi
python3 scripts/write_agent_memory.py --agent-id kimi --entry "Did X"
python3 scripts/db_status.py

# Skill System
python3 -m skills.strategic-autonomy --task "Analyze codebase"
```

### Python API

```python
# Convenience functions
from skills.integrated_autonomous_skill import auto_code, swarm_analyze, review_code

# One-liners
code = auto_code("Add API endpoint")
analysis = swarm_analyze("Security audit")
review = review_code(your_code)
```

## Best Practices

1. **Always boot before tasks**: Load context from persistent memory
2. **Always write after tasks**: Log outcomes for future learning
3. **Use swarm for complex analysis**: Multiple perspectives yield better results
4. **Use strategic planning for large tasks**: Break into phases
5. **Check memory before starting**: Avoid duplicating work
6. **Update shared brain**: Help other agents learn from your work

## Troubleshooting

### Ollama Connection Failed

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Pull models
ollama pull qwen2.5:14b
ollama pull qwen2.5-coder:latest
```

### Agent Orchestrator Not Found

```bash
# Build from source
cd composio-orchestrator
pnpm install && pnpm build

# Link CLI
npm link
```

### Memory Database Locked

```bash
# Check for zombie processes
ps aux | grep sqlite

# Reset if needed (loses data!)
rm -rf ~/persistent-agent-memory/data/*.db
python3 scripts/init_databases.py
```

## License

MIT

---

**Note**: This skill system combines multiple external projects:
- [Composio Agent Orchestrator](https://github.com/ComposioHQ/agent-orchestrator)
- [Persistent Agent Memory](https://github.com/jacklevin74/persistent-agent-memory)
- [Qwen 3.5 Models](https://huggingface.co/collections/Qwen/qwen35)
