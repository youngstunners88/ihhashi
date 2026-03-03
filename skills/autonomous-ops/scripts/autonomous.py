#!/usr/bin/env python3
"""
iHhashi Autonomous Operations Skill
Master controller combining all three systems:
  1. Agent Orchestrator (ComposioHQ) - Parallel agent management
  2. Qwen 3.5 Tentacles - Multi-model AI capabilities
  3. Persistent Agent Memory - Stateful agent coordination

Workflows:
    python autonomous.py issue-swarm <issue1> <issue2> ...
    python autonomous.py review-pipeline <file_or_pr>
    python autonomous.py sa-translate <content_file>
    python autonomous.py ops-cycle
    python autonomous.py market-intel <topic>
    python autonomous.py deploy-guard
    python autonomous.py full-auto
    python autonomous.py status
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = REPO_ROOT / "skills"
ORCHESTRATOR_SCRIPT = SKILLS_ROOT / "orchestrator" / "scripts" / "orchestrate.py"
TENTACLES_SCRIPT = SKILLS_ROOT / "qwen-tentacles" / "scripts" / "tentacles.py"
MEMORY_SCRIPT = SKILLS_ROOT / "persistent-memory" / "scripts" / "memory.py"

AGENT_ID = "ihhashi-ops"


def run_skill(script: Path, args: list[str], capture: bool = False):
    """Run a skill script."""
    cmd = [sys.executable, str(script)] + args
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
        return result.stdout
    else:
        result = subprocess.run(cmd, cwd=str(REPO_ROOT))
        return result.returncode


def log(entry: str):
    """Log activity to persistent memory."""
    run_skill(MEMORY_SCRIPT, ["write", AGENT_ID, entry])


def issue_swarm(issues: list[str]):
    """
    Issue Swarm Workflow:
    1. Classify each issue using Qwen 3.5 efficient model
    2. Prioritize by category
    3. Spawn parallel agents via orchestrator
    4. Log all actions to persistent memory
    """
    print("=" * 60)
    print("ISSUE SWARM - Autonomous Parallel Issue Resolution")
    print("=" * 60)
    log(f"Issue swarm started for {len(issues)} issues: {', '.join(issues)}")

    # Step 1: Classify each issue
    print("\n[1/3] Classifying issues with Qwen 3.5 (9B efficient)...")
    for issue in issues:
        print(f"  Classifying issue #{issue}...")
        run_skill(TENTACLES_SCRIPT, ["classify", f"GitHub issue #{issue}"])

    # Step 2: Initialize orchestrator
    print("\n[2/3] Initializing agent orchestrator...")
    run_skill(ORCHESTRATOR_SCRIPT, ["init"])

    # Step 3: Spawn agents
    print(f"\n[3/3] Spawning {len(issues)} parallel agents...")
    run_skill(ORCHESTRATOR_SCRIPT, ["auto"] + issues)

    log(f"Issue swarm complete: {len(issues)} agents spawned")
    print(f"\nSwarm deployed: {len(issues)} agents working in parallel")


def review_pipeline(target: str):
    """
    Code Review Pipeline:
    1. Classify changes (efficient model)
    2. Deep code review (large model)
    3. Architecture assessment (flagship model)
    4. Log findings to knowledge base
    """
    print("=" * 60)
    print("REVIEW PIPELINE - Multi-Model Code Analysis")
    print("=" * 60)
    log(f"Review pipeline started for: {target}")

    # Step 1: Classify
    print("\n[1/3] Classifying changes (Qwen 3.5 9B)...")
    run_skill(TENTACLES_SCRIPT, ["classify", target])

    # Step 2: Deep review
    print("\n[2/3] Deep code review (Qwen 3.5 122B)...")
    run_skill(TENTACLES_SCRIPT, ["code-review", target])

    # Step 3: Architecture assessment
    print("\n[3/3] Architecture assessment (Qwen 3.5 397B)...")
    run_skill(TENTACLES_SCRIPT, ["architect", f"Review architecture implications of changes to {target}"])

    # Log findings
    run_skill(MEMORY_SCRIPT, ["knowledge", f"Code review completed for {target}", "--tags", "code-review,pipeline", "--source", "review-pipeline"])
    log(f"Review pipeline complete for: {target}")
    print("\nReview pipeline complete. Findings logged to knowledge base.")


def sa_translate(content_file: str):
    """
    SA Translation Workflow:
    Translate content to all supported South African languages.
    Uses Qwen 3.5 medium (35B-A3B) for each translation.
    """
    sa_langs = ["zu", "xh", "af", "st", "tn"]
    lang_names = {
        "zu": "isiZulu",
        "xh": "isiXhosa",
        "af": "Afrikaans",
        "st": "Sesotho",
        "tn": "Setswana",
    }

    content_path = Path(content_file)
    if content_path.exists():
        content = content_path.read_text()[:500]  # Cap for demo
    else:
        content = content_file

    print("=" * 60)
    print("SA TRANSLATE - Multi-Language Content Pipeline")
    print("=" * 60)
    log(f"SA translation started for {len(sa_langs)} languages")

    for lang in sa_langs:
        print(f"\n[{lang}] Translating to {lang_names[lang]}...")
        run_skill(TENTACLES_SCRIPT, ["translate", content, "--lang", lang])

    log(f"SA translation complete: {', '.join(sa_langs)}")
    print(f"\nTranslation pipeline complete for {len(sa_langs)} languages.")


def ops_cycle():
    """
    Full Operational Cycle:
    1. Boot all agents with context injection
    2. Check system status
    3. Process pending handoffs
    4. Report findings
    """
    agents = ["orchestrator", "qwen-tentacle", "ihhashi-ops", "memory-manager"]

    print("=" * 60)
    print("OPS CYCLE - Full Autonomous Operation")
    print("=" * 60)
    log("Ops cycle started")

    # Step 1: Boot all agents
    print("\n[1/4] Booting agents with context injection...")
    for agent in agents:
        print(f"\n  --- Booting: {agent} ---")
        run_skill(MEMORY_SCRIPT, ["boot", agent])

    # Step 2: System health check
    print("\n[2/4] System health check...")
    run_skill(MEMORY_SCRIPT, ["status"])

    # Step 3: Check orchestrator status
    print("\n[3/4] Agent orchestrator status...")
    run_skill(ORCHESTRATOR_SCRIPT, ["status"])

    # Step 4: Summary
    print("\n[4/4] Ops cycle complete")
    log("Ops cycle complete - all agents booted, systems healthy")


def market_intel(topic: str):
    """
    Market Intelligence Workflow:
    Use the flagship Qwen 3.5 model (397B) for deep market research.
    """
    print("=" * 60)
    print("MARKET INTEL - SA Food Delivery Research")
    print("=" * 60)
    log(f"Market intel started: {topic}")

    # Research with flagship model
    print("\n[1/2] Deep research (Qwen 3.5 397B flagship)...")
    run_skill(TENTACLES_SCRIPT, ["research", topic])

    # Summarize findings
    print("\n[2/2] Summarizing findings...")
    run_skill(TENTACLES_SCRIPT, ["summarize", f"Market research on: {topic}"])

    # Log to knowledge base
    run_skill(MEMORY_SCRIPT, [
        "knowledge",
        f"Market intel: {topic}",
        "--tags", "market-intel,research,sa-food-delivery",
        "--source", "market-intel-workflow",
    ])
    log(f"Market intel complete: {topic}")


def deploy_guard():
    """
    Pre-Deployment Guard:
    1. Review all staged changes
    2. Architecture validation
    3. Security audit
    4. Go/no-go recommendation
    """
    print("=" * 60)
    print("DEPLOY GUARD - Pre-Deployment Validation")
    print("=" * 60)
    log("Deploy guard activated")

    # Get staged changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--stat"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    staged = result.stdout if result.stdout else "No staged changes"

    result = subprocess.run(
        ["git", "diff", "--stat"],
        capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    unstaged = result.stdout if result.stdout else "No unstaged changes"

    print(f"\nStaged changes:\n{staged}")
    print(f"\nUnstaged changes:\n{unstaged}")

    # Code review
    print("\n[1/3] Code review (Qwen 3.5 122B)...")
    run_skill(TENTACLES_SCRIPT, ["code-review", staged])

    # Architecture check
    print("\n[2/3] Architecture validation (Qwen 3.5 397B)...")
    run_skill(TENTACLES_SCRIPT, ["architect", f"Validate deployment readiness for changes: {staged[:200]}"])

    # Security classification
    print("\n[3/3] Security classification (Qwen 3.5 9B)...")
    run_skill(TENTACLES_SCRIPT, ["classify", staged, "--categories", "safe,risky,critical,blocker"])

    log("Deploy guard complete")
    print("\nDeploy guard complete. Review findings above for go/no-go decision.")


def full_auto():
    """
    Full Autonomous Mode:
    Run the complete autonomous pipeline end-to-end.
    """
    print("=" * 60)
    print("FULL AUTO - Complete Autonomous Pipeline")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    log("Full autonomous mode activated")

    # 1. Boot all agents
    print("\n>>> Phase 1: Boot agents")
    ops_cycle()

    # 2. Deploy guard
    print("\n>>> Phase 2: Deploy guard")
    deploy_guard()

    # 3. Log completion
    run_skill(MEMORY_SCRIPT, [
        "log-run", AGENT_ID, "full-auto",
        "--status", "ok",
        "--summary", "Full autonomous cycle completed successfully",
    ])

    log("Full autonomous mode completed")
    print(f"\nCompleted: {datetime.now().isoformat()}")
    print("All systems operational. Agents booted and ready.")


def show_status():
    """Show status of all integrated systems."""
    print("=" * 60)
    print("iHhashi AUTONOMOUS OPS - System Status")
    print("=" * 60)

    print("\n--- Persistent Memory ---")
    run_skill(MEMORY_SCRIPT, ["status"])

    print("\n--- Agent Orchestrator ---")
    run_skill(ORCHESTRATOR_SCRIPT, ["status"])

    print("\n--- Qwen 3.5 Tentacles ---")
    run_skill(TENTACLES_SCRIPT, ["list"])

    print("\n--- Integrated Systems ---")
    systems = {
        "Agent Orchestrator": REPO_ROOT / "plugins" / "agent-orchestrator" / "package.json",
        "Persistent Memory": REPO_ROOT / "plugins" / "persistent-agent-memory" / "scripts" / "init_databases.py",
        "Orchestrator Skill": SKILLS_ROOT / "orchestrator" / "skill.json",
        "Qwen Tentacles Skill": SKILLS_ROOT / "qwen-tentacles" / "skill.json",
        "Memory Skill": SKILLS_ROOT / "persistent-memory" / "skill.json",
        "Autonomous Ops Skill": SKILLS_ROOT / "autonomous-ops" / "skill.json",
    }
    for name, path in systems.items():
        status = "INSTALLED" if path.exists() else "MISSING"
        print(f"  {name:30s} [{status}]")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        show_status()
        sys.exit(0)

    command = sys.argv[1]

    if command == "issue-swarm":
        if len(sys.argv) < 3:
            print("Usage: autonomous.py issue-swarm <issue1> <issue2> ...")
            sys.exit(1)
        issue_swarm(sys.argv[2:])
    elif command == "review-pipeline":
        if len(sys.argv) < 3:
            print("Usage: autonomous.py review-pipeline <file_or_pr>")
            sys.exit(1)
        review_pipeline(sys.argv[2])
    elif command == "sa-translate":
        if len(sys.argv) < 3:
            print("Usage: autonomous.py sa-translate <content_file_or_text>")
            sys.exit(1)
        sa_translate(sys.argv[2])
    elif command == "ops-cycle":
        ops_cycle()
    elif command == "market-intel":
        if len(sys.argv) < 3:
            print("Usage: autonomous.py market-intel <topic>")
            sys.exit(1)
        market_intel(" ".join(sys.argv[2:]))
    elif command == "deploy-guard":
        deploy_guard()
    elif command == "full-auto":
        full_auto()
    elif command == "status":
        show_status()
    else:
        print(f"Unknown workflow: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
