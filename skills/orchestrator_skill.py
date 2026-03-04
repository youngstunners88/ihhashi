#!/usr/bin/env python3
"""
Composio Orchestrator Skill
Integrates agent-orchestrator for parallel AI agent management
"""
import subprocess
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentTask:
    task_id: str
    repo: str
    issue: Optional[str]
    branch: str
    status: str
    created_at: str

class OrchestratorSkill:
    """
    Skill for managing parallel AI agents via Composio Orchestrator
    """
    
    def __init__(self, config_path: str = "~/composio-orchestrator"):
        self.config_path = os.path.expanduser(config_path)
        self.active_agents: Dict[str, AgentTask] = {}
        
    def spawn_agent(self, repo: str, issue: Optional[str] = None, 
                   agent_type: str = "claude-code") -> str:
        """Spawn a new AI agent for a specific task"""
        task_id = f"agent-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        try:
            cmd = ["ao", "spawn", repo]
            if issue:
                cmd.append(issue)
            
            subprocess.Popen(
                cmd,
                cwd=self.config_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.active_agents[task_id] = AgentTask(
                task_id=task_id,
                repo=repo,
                issue=issue,
                branch=f"agent-{task_id}",
                status="running",
                created_at=datetime.now().isoformat()
            )
            
            return task_id
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_status(self) -> Dict:
        """Get status of all active agents"""
        try:
            result = subprocess.run(
                ["ao", "status"],
                capture_output=True,
                text=True,
                cwd=self.config_path
            )
            return {
                "raw_output": result.stdout,
                "active_count": len(self.active_agents),
                "agents": {k: v.__dict__ for k, v in self.active_agents.items()}
            }
        except Exception as e:
            return {"error": str(e)}
    
    def spawn_parallel(self, repo: str, issues: List[str]) -> List[str]:
        """Spawn multiple agents in parallel for different issues"""
        task_ids = []
        for issue in issues:
            task_id = self.spawn_agent(repo, issue)
            task_ids.append(task_id)
        return task_ids

# Global instance
_orchestrator = None

def get_orchestrator() -> OrchestratorSkill:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorSkill()
    return _orchestrator
