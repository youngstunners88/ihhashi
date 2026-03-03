#!/usr/bin/env python3
"""
iHhashi Agent Orchestrator Skill
Wraps ComposioHQ/agent-orchestrator for autonomous parallel agent management.

Usage:
    python orchestrate.py init          # Initialize for current project
    python orchestrate.py spawn <issue> # Spawn agent on an issue
    python orchestrate.py status        # List all active sessions
    python orchestrate.py send <session> <message>  # Send instruction
    python orchestrate.py kill <session> # Kill a session
    python orchestrate.py auto <issues...>  # Auto-assign multiple issues
"""

import subprocess
import sys
import os
import json
import yaml
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[3]
AO_PATH = REPO_ROOT / "plugins" / "agent-orchestrator"
PAM_PATH = REPO_ROOT / "plugins" / "persistent-agent-memory"
CONFIG_PATH = REPO_ROOT / "ao-config.yaml"
MEMORY_SCRIPT = PAM_PATH / "scripts" / "write_agent_memory.py"

DEFAULT_CONFIG = {
    "port": 3000,
    "defaults": {
        "runtime": "tmux",
        "agent": "claude-code",
        "workspace": "worktree",
        "notifiers": ["desktop"],
    },
    "projects": {
        "ihhashi": {
            "repo": "youngstunners88/ihhashi",
            "path": str(REPO_ROOT),
            "defaultBranch": "master",
        }
    },
    "reactions": {
        "ci-failed": {"auto": True, "action": "send-to-agent", "retries": 2},
        "changes-requested": {"auto": True, "action": "send-to-agent"},
        "approved-and-green": {"auto": False, "action": "notify"},
    },
}


def log_memory(agent_id: str, entry: str):
    """Log an action to persistent agent memory."""
    try:
        subprocess.run(
            [
                sys.executable,
                str(MEMORY_SCRIPT),
                "--agent-id", agent_id,
                "--entry", entry,
            ],
            cwd=str(PAM_PATH),
            capture_output=True,
            timeout=10,
        )
    except Exception:
        pass  # Memory logging is best-effort


def run_ao(args: list[str], capture=False):
    """Run an agent-orchestrator CLI command."""
    ao_cli = AO_PATH / "packages" / "cli" / "dist" / "index.js"
    cmd = ["node", str(ao_cli)] + args
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        return result.stdout
    else:
        subprocess.run(cmd, cwd=str(REPO_ROOT))


def init():
    """Initialize agent-orchestrator for the iHhashi project."""
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False)
        print(f"Created config at {CONFIG_PATH}")
    else:
        print(f"Config already exists at {CONFIG_PATH}")

    log_memory("orchestrator", "Initialized agent-orchestrator for iHhashi project")
    print("Agent orchestrator initialized for iHhashi.")
    print(f"  Runtime: {DEFAULT_CONFIG['defaults']['runtime']}")
    print(f"  Agent: {DEFAULT_CONFIG['defaults']['agent']}")
    print(f"  Max parallel: 5")


def spawn(issue: str):
    """Spawn a new agent on an issue."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_memory("orchestrator", f"Spawning agent for issue #{issue}")
    run_ao(["spawn", "ihhashi", issue])
    print(f"Agent spawned for issue #{issue}")


def status():
    """Show status of all active agents."""
    output = run_ao(["session", "ls"], capture=True)
    if output:
        print(output)
    else:
        print("No active agent sessions.")
    log_memory("orchestrator", "Checked agent status")


def send(session: str, message: str):
    """Send instructions to a running agent."""
    run_ao(["send", session, message])
    log_memory("orchestrator", f"Sent message to session {session}: {message[:80]}")


def kill(session: str):
    """Kill a running agent session."""
    run_ao(["session", "kill", session])
    log_memory("orchestrator", f"Killed session {session}")


def auto_assign(issues: list[str]):
    """Auto-assign multiple issues to parallel agents."""
    print(f"Auto-assigning {len(issues)} issues to parallel agents...")
    log_memory("orchestrator", f"Auto-assigning {len(issues)} issues: {', '.join(issues)}")
    for issue in issues:
        spawn(issue)
    print(f"All {len(issues)} agents spawned.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        init()
    elif command == "spawn":
        if len(sys.argv) < 3:
            print("Usage: orchestrate.py spawn <issue-number>")
            sys.exit(1)
        spawn(sys.argv[2])
    elif command == "status":
        status()
    elif command == "send":
        if len(sys.argv) < 4:
            print("Usage: orchestrate.py send <session> <message>")
            sys.exit(1)
        send(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "kill":
        if len(sys.argv) < 3:
            print("Usage: orchestrate.py kill <session>")
            sys.exit(1)
        kill(sys.argv[2])
    elif command == "auto":
        if len(sys.argv) < 3:
            print("Usage: orchestrate.py auto <issue1> <issue2> ...")
            sys.exit(1)
        auto_assign(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
