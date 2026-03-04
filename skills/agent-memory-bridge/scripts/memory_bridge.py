#!/usr/bin/env python3
"""
Memory Bridge: Integrates Persistent Agent Memory with Agent Orchestrator

This script bridges the two systems, enabling:
1. Boot injection - Load context before spawning orchestrator agents
2. Write-back - Log results after agent completion
3. Cross-agent state sharing via shared brain
"""
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add parent paths for imports
sys.path.insert(0, os.path.expanduser("~/skills"))
sys.path.insert(0, os.path.expanduser("~/persistent-agent-memory/scripts"))

class MemoryBridge:
    """
    Bridge between Persistent Memory and Agent Orchestrator
    """
    
    def __init__(self, memory_base: str = "~/persistent-agent-memory"):
        self.memory_base = os.path.expanduser(memory_base)
        self.shared_brain_path = os.path.join(self.memory_base, "shared-brain")
        self.agent_memory_path = os.path.join(self.memory_base, "memory", "agents")
        
        # Ensure directories exist
        os.makedirs(self.shared_brain_path, exist_ok=True)
        os.makedirs(self.agent_memory_path, exist_ok=True)
    
    def boot_injection(self, agent_id: str, role: str = "coder") -> str:
        """
        Generate boot context for an agent.
        Called before spawning an agent to provide historical context.
        """
        context_parts = []
        
        # 1. Load agent identity
        context_parts.append(f"""
# Agent Boot Context
Agent ID: {agent_id}
Role: {role}
Boot Time: {datetime.now().isoformat()}
""")
        
        # 2. Load recent memory (last 2 days)
        memories = self._load_recent_memory(agent_id, days=2)
        if memories:
            context_parts.append("## Recent Activity\n" + "\n".join(memories))
        
        # 3. Load relevant shared brain files
        brain_files = self._get_brain_files_for_role(role)
        for bf in brain_files:
            data = self._read_shared_brain(bf)
            if data.get("entries"):
                context_parts.append(f"## {bf}\n")
                # Get last 5 entries
                entries = data["entries"][-5:]
                for entry in entries:
                    context_parts.append(f"- [{entry.get('timestamp', 'N/A')}] {entry.get('content', entry)}")
        
        # 4. Load pending handoffs
        handoffs = self._read_shared_brain("agent-handoffs.json")
        if handoffs.get("entries"):
            pending = [h for h in handoffs["entries"] if h.get("status") == "pending" and h.get("to") == agent_id]
            if pending:
                context_parts.append("## Pending Handoffs\n")
                for handoff in pending[-3:]:
                    context_parts.append(f"- From {handoff.get('from')}: {handoff.get('task')}")
        
        # 5. Add role-specific instructions
        context_parts.append(self._get_role_instructions(role))
        
        return "\n\n".join(context_parts)
    
    def write_back(self, agent_id: str, task: str, outcome: str, 
                   learnings: List[str] = None, handoffs: List[Dict] = None):
        """
        Write back results after task completion.
        Called after an agent finishes work.
        """
        learnings = learnings or []
        handoffs = handoffs or []
        
        # 1. Write to agent memory
        self._write_agent_memory(agent_id, task, outcome, learnings)
        
        # 2. Log knowledge
        for learning in learnings:
            self._log_knowledge(learning, agent_id)
        
        # 3. Update shared brain
        self._update_content_vault(task, outcome, agent_id)
        
        # 4. Process handoffs
        for handoff in handoffs:
            self._create_handoff(agent_id, handoff)
        
        # 5. Log agent run
        self._log_agent_run(agent_id, task, "completed")
    
    def spawn_orchestrated_agent(self, project: str, issue: str = None, 
                                  role: str = "coder", agent_type: str = "qwen-tentacle") -> str:
        """
        Spawn an orchestrator agent with memory boot injection.
        """
        agent_id = f"{project}-{role}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # 1. Generate boot context
        boot_context = self.boot_injection(agent_id, role)
        
        # 2. Write boot context to file
        boot_file = os.path.join(self.memory_base, "boot-contexts", f"{agent_id}.md")
        os.makedirs(os.path.dirname(boot_file), exist_ok=True)
        with open(boot_file, "w") as f:
            f.write(boot_context)
        
        # 3. Spawn orchestrator agent
        cmd = ["ao", "spawn", project]
        if issue:
            cmd.append(issue)
        
        # Set environment for agent
        env = os.environ.copy()
        env["AO_AGENT_ID"] = agent_id
        env["AO_TENTACLE_ROLE"] = role
        env["AO_BOOT_CONTEXT"] = boot_file
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            # Log the spawn
            self._write_agent_memory(
                agent_id,
                f"Spawned via orchestrator for {project}/{issue}",
                f"stdout: {result.stdout}\nstderr: {result.stderr}",
                ["orchestrator", "spawn"]
            )
            
            return agent_id
            
        except subprocess.TimeoutExpired:
            return f"Error: Spawn timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_swarm_plan(self, objective: str, project: str) -> List[Dict]:
        """
        Generate a plan for deploying a swarm of agents.
        Returns a list of agent configurations.
        """
        return [
            {
                "role": "planner",
                "task": f"Design architecture for: {objective}",
                "project": project,
                "depends_on": []
            },
            {
                "role": "analyzer",
                "task": f"Identify risks for: {objective}",
                "project": project,
                "depends_on": ["planner"]
            },
            {
                "role": "coder",
                "task": f"Implement solution for: {objective}",
                "project": project,
                "depends_on": ["planner", "analyzer"]
            },
            {
                "role": "reviewer",
                "task": f"Review implementation for: {objective}",
                "project": project,
                "depends_on": ["coder"]
            }
        ]
    
    def execute_swarm(self, objective: str, project: str) -> Dict[str, Any]:
        """
        Execute a swarm of agents for a complex objective.
        """
        plan = self.get_swarm_plan(objective, project)
        spawned_agents = {}
        results = {}
        
        # Execute in dependency order (simplified - would need proper DAG execution)
        for agent_config in plan:
            role = agent_config["role"]
            
            # Spawn agent
            agent_id = self.spawn_orchestrated_agent(
                project=agent_config["project"],
                role=role
            )
            
            spawned_agents[role] = agent_id
            
            # Log the handoff
            for dep in agent_config.get("depends_on", []):
                if dep in spawned_agents:
                    self._create_handoff(
                        from_agent=spawned_agents[dep],
                        to_agent=agent_id,
                        task=f"Continue work on: {objective}"
                    )
        
        return {
            "objective": objective,
            "spawned_agents": spawned_agents,
            "plan": plan
        }
    
    def recall_similar(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Recall similar past work from knowledge base.
        """
        # This would use the knowledge.db via SQLite
        # For now, search shared brain
        results = []
        
        for filename in os.listdir(self.shared_brain_path):
            if not filename.endswith(".json"):
                continue
                
            filepath = os.path.join(self.shared_brain_path, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    
                if "entries" in data:
                    for entry in data["entries"]:
                        content = json.dumps(entry)
                        if query.lower() in content.lower():
                            results.append({
                                "source": filename,
                                "entry": entry,
                                "timestamp": data.get("lastUpdatedAt")
                            })
            except:
                continue
        
        # Sort by timestamp, most recent first
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]
    
    # =========================================================================
    # Private Helpers
    # =========================================================================
    
    def _load_recent_memory(self, agent_id: str, days: int = 2) -> List[str]:
        """Load recent memory logs for an agent."""
        memories = []
        agent_dir = os.path.join(self.agent_memory_path, agent_id)
        
        if not os.path.exists(agent_dir):
            return memories
        
        for i in range(days):
            date = datetime.now()
            if i > 0:
                from datetime import timedelta
                date = date - timedelta(days=i)
            
            date_str = date.strftime("%Y-%m-%d")
            log_file = os.path.join(agent_dir, f"{date_str}.md")
            
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    memories.append(f.read())
        
        return memories
    
    def _write_agent_memory(self, agent_id: str, task: str, outcome: str, 
                           tags: List[str] = None):
        """Write to agent's daily memory log."""
        agent_dir = os.path.join(self.agent_memory_path, agent_id)
        os.makedirs(agent_dir, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M")
        log_file = os.path.join(agent_dir, f"{date_str}.md")
        
        tags_str = " ".join([f"#{tag}" for tag in (tags or [])])
        entry = f"""
## [{time_str}] {tags_str}
**Task:** {task}

**Outcome:**
{outcome}

---
"""
        with open(log_file, "a") as f:
            f.write(entry)
    
    def _read_shared_brain(self, filename: str) -> Dict:
        """Read a shared brain JSON file."""
        filepath = os.path.join(self.shared_brain_path, filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        return {"entries": [], "schemaVersion": "1.0"}
    
    def _update_content_vault(self, task: str, outcome: str, agent_id: str):
        """Update the content vault with work results."""
        vault = self._read_shared_brain("content-vault.json")
        
        vault["entries"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_id,
            "task": task[:100],
            "outcome_summary": outcome[:200],
            "type": "work_product"
        })
        
        vault["lastUpdatedAt"] = datetime.now().isoformat()
        vault["lastUpdatedBy"] = agent_id
        
        filepath = os.path.join(self.shared_brain_path, "content-vault.json")
        with open(filepath, "w") as f:
            json.dump(vault, f, indent=2)
    
    def _create_handoff(self, from_agent: str, to_agent: str, task: str):
        """Create a handoff between agents."""
        handoffs = self._read_shared_brain("agent-handoffs.json")
        
        handoffs["entries"].append({
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "task": task,
            "status": "pending",
            "context": ""
        })
        
        handoffs["lastUpdatedAt"] = datetime.now().isoformat()
        handoffs["lastUpdatedBy"] = from_agent
        
        filepath = os.path.join(self.shared_brain_path, "agent-handoffs.json")
        with open(filepath, "w") as f:
            json.dump(handoffs, f, indent=2)
    
    def _log_knowledge(self, fact: str, agent_id: str, category: str = "general"):
        """Log knowledge to the knowledge base."""
        # This would write to SQLite knowledge.db
        # For now, write to a JSON file
        knowledge_file = os.path.join(self.memory_base, "data", "knowledge_bridge.json")
        os.makedirs(os.path.dirname(knowledge_file), exist_ok=True)
        
        knowledge = {"facts": []}
        if os.path.exists(knowledge_file):
            with open(knowledge_file, "r") as f:
                knowledge = json.load(f)
        
        knowledge["facts"].append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_id,
            "fact": fact,
            "category": category
        })
        
        with open(knowledge_file, "w") as f:
            json.dump(knowledge, f, indent=2)
    
    def _log_agent_run(self, agent_id: str, task: str, status: str):
        """Log an agent run."""
        runs_file = os.path.join(self.memory_base, "data", "agent_runs_bridge.json")
        os.makedirs(os.path.dirname(runs_file), exist_ok=True)
        
        runs = {"runs": []}
        if os.path.exists(runs_file):
            with open(runs_file, "r") as f:
                runs = json.load(f)
        
        runs["runs"].append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "task": task,
            "status": status
        })
        
        with open(runs_file, "w") as f:
            json.dump(runs, f, indent=2)
    
    def _get_brain_files_for_role(self, role: str) -> List[str]:
        """Get relevant shared brain files for a role."""
        role_files = {
            "planner": ["intel-feed.json", "content-vault.json"],
            "analyzer": ["intel-feed.json", "content-vault.json"],
            "coder": ["agent-handoffs.json", "content-vault.json"],
            "reviewer": ["content-vault.json"],
            "explainer": ["intel-feed.json", "content-vault.json"],
        }
        return role_files.get(role, ["intel-feed.json"])
    
    def _get_role_instructions(self, role: str) -> str:
        """Get role-specific instructions."""
        instructions = {
            "planner": """
## Role Instructions: Planner
You are a system architect. Focus on:
- Clear component boundaries
- Scalability considerations
- Technology trade-offs
- Document decisions in shared brain
""",
            "analyzer": """
## Role Instructions: Analyzer
You are a code analyzer. Focus on:
- Security vulnerabilities
- Performance bottlenecks
- Edge cases
- Log findings to shared brain
""",
            "coder": """
## Role Instructions: Coder
You are an expert programmer. Focus on:
- Clean, idiomatic code
- Comprehensive error handling
- Type safety
- Write memory after completion
""",
            "reviewer": """
## Role Instructions: Reviewer
You are a code reviewer. Focus on:
- Correctness
- Maintainability
- Style consistency
- Constructive feedback
""",
            "explainer": """
## Role Instructions: Explainer
You are a technical writer. Focus on:
- Clear explanations
- Good examples
- Appropriate detail level
- Knowledge extraction
""",
        }
        return instructions.get(role, "")


def main():
    parser = argparse.ArgumentParser(description="Memory Bridge for Agent Orchestrator")
    parser.add_argument("command", choices=["boot", "writeback", "spawn", "swarm", "recall"])
    parser.add_argument("--agent-id", help="Agent identifier")
    parser.add_argument("--role", default="coder", help="Tentacle role")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--issue", help="Issue identifier")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--outcome", help="Task outcome")
    parser.add_argument("--objective", help="Swarm objective")
    parser.add_argument("--query", help="Recall query")
    
    args = parser.parse_args()
    
    bridge = MemoryBridge()
    
    if args.command == "boot":
        context = bridge.boot_injection(args.agent_id, args.role)
        print(context)
    
    elif args.command == "writeback":
        bridge.write_back(args.agent_id, args.task, args.outcome)
        print(f"Writeback complete for {args.agent_id}")
    
    elif args.command == "spawn":
        agent_id = bridge.spawn_orchestrated_agent(
            project=args.project,
            issue=args.issue,
            role=args.role
        )
        print(f"Spawned agent: {agent_id}")
    
    elif args.command == "swarm":
        result = bridge.execute_swarm(args.objective, args.project)
        print(json.dumps(result, indent=2))
    
    elif args.command == "recall":
        results = bridge.recall_similar(args.query)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
