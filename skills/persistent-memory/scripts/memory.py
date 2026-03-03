#!/usr/bin/env python3
"""
iHhashi Persistent Agent Memory Skill
Wraps jacklevin74/persistent-agent-memory for agent state management.

Usage:
    python memory.py boot <agent-id>          # Boot agent with context
    python memory.py write <agent-id> <entry> # Write memory entry
    python memory.py knowledge <content> --tags <t1,t2> --source <src>
    python memory.py status                   # Database health check
    python memory.py handoff <from> <to> <task>  # Cross-agent handoff
    python memory.py query --tags <tag1,tag2>    # Query knowledge base
    python memory.py log-run <agent-id> <job> --status <ok|error> --summary <text>
"""

import subprocess
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

REPO_ROOT = Path(__file__).resolve().parents[3]
PAM_PATH = REPO_ROOT / "plugins" / "persistent-agent-memory"
SCRIPTS_PATH = PAM_PATH / "scripts"
DATA_PATH = PAM_PATH / "data"
MEMORY_PATH = PAM_PATH / "memory" / "agents"
SHARED_BRAIN = PAM_PATH / "shared-brain"


def run_pam_script(script: str, args: list[str]):
    """Run a persistent-agent-memory script."""
    script_path = SCRIPTS_PATH / script
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PAM_PATH))
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def boot(agent_id: str):
    """Boot an agent with proactive context injection."""
    print(f"Booting agent: {agent_id}")
    print("=" * 60)

    # Load last 2 days of agent logs
    agent_dir = MEMORY_PATH / agent_id
    if agent_dir.exists():
        today = datetime.now()
        for days_ago in range(2, -1, -1):
            date = today - timedelta(days=days_ago)
            log_file = agent_dir / f"{date.strftime('%Y-%m-%d')}.md"
            if log_file.exists():
                print(f"\n--- Agent Log: {log_file.name} ---")
                print(log_file.read_text())
    else:
        agent_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Created memory directory: {agent_dir}")

    # Load relevant shared brain files
    brain_map = {
        "orchestrator": ["agent-handoffs.json", "intel-feed.json"],
        "qwen-tentacle": ["intel-feed.json", "content-vault.json"],
        "ihhashi-ops": ["agent-handoffs.json", "content-vault.json", "outreach-log.json"],
        "memory-manager": ["agent-handoffs.json"],
    }

    relevant_files = brain_map.get(agent_id, ["agent-handoffs.json"])
    for fname in relevant_files:
        fpath = SHARED_BRAIN / fname
        if fpath.exists():
            try:
                data = json.loads(fpath.read_text())
                print(f"\n--- Shared Brain: {fname} ---")
                print(json.dumps(data, indent=2)[:2000])  # Cap output
            except json.JSONDecodeError:
                print(f"  {fname}: empty or invalid")

    print(f"\nAgent {agent_id} booted successfully.")
    return 0


def write_memory(agent_id: str, entry: str):
    """Write a memory entry for an agent."""
    return run_pam_script("write_agent_memory.py", [
        "--agent-id", agent_id,
        "--entry", entry,
    ])


def log_knowledge(content: str, tags: str = "", source: str = "manual"):
    """Log a knowledge chunk to the knowledge database."""
    args = ["--content", content, "--source", source, "--agent-id", "ihhashi-ops"]
    if tags:
        args.extend(["--tags", tags])
    return run_pam_script("log_knowledge.py", args)


def db_status():
    """Check health of all databases."""
    return run_pam_script("db_status.py", [])


def create_handoff(from_agent: str, to_agent: str, task: str):
    """Create a cross-agent handoff via shared brain."""
    handoff_file = SHARED_BRAIN / "agent-handoffs.json"

    try:
        if handoff_file.exists():
            data = json.loads(handoff_file.read_text())
        else:
            data = {"handoffs": [], "lastUpdatedBy": "", "lastUpdatedAt": "", "schemaVersion": 1}
    except json.JSONDecodeError:
        data = {"handoffs": [], "lastUpdatedBy": "", "lastUpdatedAt": "", "schemaVersion": 1}

    handoff = {
        "from": from_agent,
        "to": to_agent,
        "task": task,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    data["handoffs"].append(handoff)
    data["lastUpdatedBy"] = from_agent
    data["lastUpdatedAt"] = datetime.now().isoformat()

    handoff_file.write_text(json.dumps(data, indent=2))
    print(f"Handoff created: {from_agent} -> {to_agent}")
    print(f"Task: {task}")

    # Also log to memory
    write_memory(from_agent, f"Created handoff to {to_agent}: {task}")
    return 0


def query_knowledge(tags: str):
    """Query the knowledge database by tags."""
    db_path = DATA_PATH / "knowledge.db"
    if not db_path.exists():
        print("Knowledge database not found. Run init first.")
        return 1

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    tag_list = [t.strip() for t in tags.split(",")]
    placeholders = ",".join(["?" for _ in tag_list])

    try:
        # Try querying chunks table with tag matching
        cursor = conn.execute(
            f"SELECT * FROM chunks WHERE tags LIKE ? ORDER BY created_at DESC LIMIT 20",
            (f"%{tag_list[0]}%",)
        )
        rows = cursor.fetchall()

        if rows:
            print(f"Found {len(rows)} knowledge chunks matching '{tags}':")
            for row in rows:
                row_dict = dict(row)
                print(f"  [{row_dict.get('created_at', 'N/A')}] {row_dict.get('content', '')[:120]}")
        else:
            print(f"No knowledge chunks found matching '{tags}'")

    except sqlite3.OperationalError as e:
        print(f"Query error: {e}")
        # List available tables
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Available tables: {', '.join(tables)}")
    finally:
        conn.close()

    return 0


def log_run(agent_id: str, job: str, status: str = "ok", summary: str = ""):
    """Log an agent run to the execution history database."""
    args = ["--oneshot", "--agent-id", agent_id, "--job", job, "--status", status]
    if summary:
        args.extend(["--summary", summary])
    return run_pam_script("log_agent_run.py", args)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "boot":
        if len(sys.argv) < 3:
            print("Usage: memory.py boot <agent-id>")
            sys.exit(1)
        boot(sys.argv[2])
    elif command == "write":
        if len(sys.argv) < 4:
            print("Usage: memory.py write <agent-id> <entry>")
            sys.exit(1)
        write_memory(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "knowledge":
        if len(sys.argv) < 3:
            print("Usage: memory.py knowledge <content> --tags <t1,t2> --source <src>")
            sys.exit(1)
        content = sys.argv[2]
        tags = ""
        source = "manual"
        if "--tags" in sys.argv:
            idx = sys.argv.index("--tags") + 1
            if idx < len(sys.argv):
                tags = sys.argv[idx]
        if "--source" in sys.argv:
            idx = sys.argv.index("--source") + 1
            if idx < len(sys.argv):
                source = sys.argv[idx]
        log_knowledge(content, tags, source)
    elif command == "status":
        db_status()
    elif command == "handoff":
        if len(sys.argv) < 5:
            print("Usage: memory.py handoff <from> <to> <task>")
            sys.exit(1)
        create_handoff(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    elif command == "query":
        if "--tags" not in sys.argv:
            print("Usage: memory.py query --tags <tag1,tag2>")
            sys.exit(1)
        idx = sys.argv.index("--tags") + 1
        query_knowledge(sys.argv[idx])
    elif command == "log-run":
        if len(sys.argv) < 4:
            print("Usage: memory.py log-run <agent-id> <job> --status <ok|error> --summary <text>")
            sys.exit(1)
        agent_id = sys.argv[2]
        job = sys.argv[3]
        status = "ok"
        summary = ""
        if "--status" in sys.argv:
            idx = sys.argv.index("--status") + 1
            if idx < len(sys.argv):
                status = sys.argv[idx]
        if "--summary" in sys.argv:
            idx = sys.argv.index("--summary") + 1
            if idx < len(sys.argv):
                summary = " ".join(sys.argv[idx:])
        log_run(agent_id, job, status, summary)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
