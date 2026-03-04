# Autonomous Agent Orchestration Skill System

A comprehensive skill system integrating **Composio Agent Orchestrator**, **Qwen 3.5 Tentacles**, and **Persistent Agent Memory** for fully autonomous AI operations.

## Quick Start

```bash
# Install the skill system
./install.sh

# Run the demo
python3 examples/demo.py

# Use the CLI
strategic-autonomy analyze -o "Design a caching system"
strategic-autonomy execute -o "Implement Redis caching" -c "Use FastAPI" -c "Support TTL"

# Memory bridge commands
memory-bridge spawn --project myapp --role coder
memory-bridge swarm --objective "Build auth system" --project myapp
memory-bridge recall --query "authentication"
```

## Structure

```
skills/
├── SKILL.md                           # Main documentation
├── README.md                          # This file
├── install.sh                         # Installation script
│
├── qwen_tentacles.py                  # Qwen 3.5 multi-model tentacles
├── persistent_memory_skill.py         # Persistent memory integration
├── orchestrator_skill.py              # Agent orchestrator integration
├── integrated_autonomous_skill.py     # Combined skill system
│
├── orchestrator-tentacles/            # Orchestrator plugin
│   └── plugins/
│       └── agent-qwen-tentacle/       # Qwen agent plugin
│           ├── src/index.ts           # Plugin implementation
│           ├── package.json
│           └── tsconfig.json
│
├── agent-memory-bridge/               # Memory-orchestrator bridge
│   └── scripts/
│       └── memory_bridge.py           # Bridge implementation
│
├── strategic-autonomy/                # Strategic autonomy skill
│   └── scripts/
│       └── strategic_autonomy.py      # Main autonomy CLI
│
└── examples/
    └── demo.py                        # Demo script
```

## Components

### 1. Qwen Tentacles (`qwen_tentacles.py`)
Multi-model AI system using Qwen 3.5 models:
- **Analyzer** (`qwen2.5:14b`) - Code analysis, bug detection
- **Coder** (`qwen2.5-coder:14b`) - Code generation
- **Reviewer** (`qwen2.5:14b`) - Code review
- **Planner** (`qwen2.5:32b`) - Architecture planning
- **Explainer** (`qwen2.5:14b`) - Documentation

Features:
- Single tentacle deployment
- Swarm attack (all tentacles in parallel)
- Strategic planning (4-phase waterfall)
- Autonomous coding (full SDLC)

### 2. Persistent Memory (`persistent_memory_skill.py`)
File-based persistent memory system:
- **SQLite databases** - Knowledge, CRM, analytics
- **Per-agent logs** - Daily markdown logs
- **Shared brain** - Cross-agent JSON state
- **Boot injection** - Context loading at startup

### 3. Agent Orchestrator (`orchestrator_skill.py`)
Parallel AI agent management:
- Spawn agents in isolated git worktrees
- Track session status
- Handle CI/CD reactions
- Manage PR lifecycle

### 4. Memory Bridge (`agent-memory-bridge/scripts/memory_bridge.py`)
Connects memory and orchestrator:
- Boot injection for orchestrator agents
- Write-back after task completion
- Swarm deployment
- Cross-agent handoffs

### 5. Strategic Autonomy (`strategic-autonomy/scripts/strategic_autonomy.py`)
Self-directed autonomous operations:
- Strategic analysis (quick/standard/comprehensive)
- Autonomous execution (plan → execute → verify → learn)
- Recall and improve (learn from past work)
- Continuous learning (feedback integration)

### 6. Qwen Tentacle Plugin (`orchestrator-tentacles/plugins/agent-qwen-tentacle/`)
Orchestrator agent plugin for Qwen models:
- TypeScript implementation
- Memory integration hooks
- Tentacle role selection
- Session tracking

## Usage Examples

### Python API

```python
from integrated_autonomous_skill import get_integrated_skill

skill = get_integrated_skill()

# Strategic analysis
result = skill.strategic_analyze("Design auth system")
print(result['recommendations'])

# Autonomous coding
result = skill.autonomous_code_task("Add OAuth2 login")
print(result.final_output)

# Code review
review = skill.parallel_code_review(your_code)
print(review['summary'])
```

### CLI

```bash
# Analysis
strategic-autonomy analyze -o "Design microservices" -d comprehensive

# Execution
strategic-autonomy execute -o "Build API gateway" \
    -c "Use Kong" -c "Rate limit 1000/min"

# Improvement
strategic-autonomy improve -p "authentication system"

# Learning
strategic-autonomy learn -f "API was too slow" -t "performance"
```

### Memory Bridge

```bash
# Boot context
memory-bridge boot --agent-id myagent --role coder

# Spawn agent
memory-bridge spawn --project myapp --issue "#123" --role planner

# Deploy swarm
memory-bridge swarm --objective "Refactor codebase" --project myapp

# Recall similar
memory-bridge recall --query "payment processing"
```

## Configuration

### Orchestrator Config (`~/agent-orchestrator.yaml`)

```yaml
port: 3000

defaults:
  runtime: tmux
  agent: qwen-tentacle
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

### Model Mapping

Edit `qwen_tentacles.py`:

```python
ROLE_MODELS = {
    TentacleRole.ANALYZER: "qwen2.5:14b",
    TentacleRole.CODER: "qwen2.5-coder:14b",
    TentacleRole.REVIEWER: "qwen2.5:14b",
    TentacleRole.PLANNER: "qwen2.5:32b",
    TentacleRole.EXPLAINER: "qwen2.5:14b",
}
```

## Installation Requirements

- Python 3.10+
- Git 2.25+
- Node.js 20+ (for orchestrator)
- tmux (default runtime)
- Ollama with Qwen models

## See Also

- [SKILL.md](SKILL.md) - Full documentation
- [Composio Agent Orchestrator](https://github.com/ComposioHQ/agent-orchestrator)
- [Persistent Agent Memory](https://github.com/jacklevin74/persistent-agent-memory)
- [Qwen 3.5 Models](https://huggingface.co/collections/Qwen/qwen35)

## License

MIT
