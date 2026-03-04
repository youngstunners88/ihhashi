#!/usr/bin/env python3
"""
Integrated Autonomous Skill
Combines Orchestrator + Qwen Tentacles + Persistent Memory
for fully autonomous agent operations
"""
import json
import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Import component skills
sys.path.insert(0, os.path.dirname(__file__))
from qwen_tentacles import get_tentacles, TentacleRole
from persistent_memory_skill import get_memory

@dataclass
class AutonomousResult:
    task_id: str
    objective: str
    strategy: str
    tentacle_results: Dict
    memory_logged: bool
    orchestrator_spawned: bool
    final_output: str
    timestamp: str

class IntegratedAutonomousSkill:
    """
    Strategic autonomous agent that orchestrates multiple systems:
    - Qwen Tentacles for parallel analysis and execution
    - Persistent Memory for learning and continuity
    - Composio Orchestrator for parallel agent spawning (when available)
    """
    
    def __init__(self):
        self.tentacles = get_tentacles()
        self.memory = get_memory()
        self.agent_id = "kimi-integrated"
        
    def _log_action(self, action: str, outcome: str, context: Dict = None):
        """Log action to persistent memory"""
        self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"{action}\nOutcome: {outcome}",
            tags=["autonomous", "action"]
        )
        
        if context:
            self.memory.log_knowledge(
                fact=f"{action}: {outcome}",
                category="autonomous_actions",
                source="integrated_skill",
                agent_id=self.agent_id
            )
    
    def strategic_analyze(self, objective: str, context: str = "") -> Dict:
        """
        Strategic analysis using all tentacles
        """
        # Boot context from memory
        boot_ctx = self.memory.boot_context(self.agent_id)
        full_context = f"{boot_ctx}\n\n{context}" if boot_ctx else context
        
        # Deploy swarm for comprehensive analysis
        results = self.tentacles.swarm_attack(objective, full_context)
        
        # Log the analysis
        self._log_action(
            f"Strategic analysis: {objective}",
            f"Completed with {len(results)} tentacles",
            {"objective": objective, "tentacles_used": list(results.keys())}
        )
        
        # Synthesize findings
        synthesis = self._synthesize_findings(results)
        
        return {
            "findings": results,
            "synthesis": synthesis,
            "recommendations": self._extract_recommendations(results),
            "confidence": self._calculate_confidence(results)
        }
    
    def _synthesize_findings(self, results: Dict) -> str:
        """Synthesize findings from all tentacles"""
        parts = []
        for role, result in results.items():
            parts.append(f"\n### {role.value.upper()}\n{result.response[:500]}...")
        return "\n".join(parts)
    
    def _extract_recommendations(self, results: Dict) -> List[str]:
        """Extract actionable recommendations"""
        recommendations = []
        for role, result in results.items():
            # Look for action items in responses
            lines = result.response.split('\n')
            for line in lines:
                if any(marker in line.lower() for marker in ['recommend', 'should', 'must', 'action']):
                    recommendations.append(f"[{role.value}] {line.strip()}")
        return recommendations[:10]  # Top 10
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calculate overall confidence score"""
        if not results:
            return 0.0
        
        # Simple heuristic: more comprehensive responses = higher confidence
        total_tokens = sum(r.tokens_used for r in results.values())
        avg_tokens = total_tokens / len(results)
        
        # Normalize to 0-1 scale (assuming 1000 tokens is good)
        confidence = min(avg_tokens / 1000, 1.0)
        return confidence
    
    def autonomous_code_task(self, feature: str, codebase: str = "") -> AutonomousResult:
        """
        Fully autonomous coding workflow
        """
        task_id = f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Step 1: Strategic Analysis
        analysis = self.strategic_analyze(
            f"Code this feature: {feature}",
            codebase
        )
        
        # Step 2: Generate solution using tentacles
        solution = self.tentacles.autonomous_coding(feature, codebase)
        
        # Step 3: Log to memory
        memory_logged = self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"Autonomous coding: {feature}\nApproved: {solution['approved']}",
            tags=["coding", "autonomous", feature[:20]]
        )
        
        # Step 4: Update shared brain
        self.memory.update_shared_brain(
            "content-vault",
            {
                "lastFeature": feature,
                "implementation": solution['implementation'].response[:500],
                "approved": solution['approved']
            }
        )
        
        # Build final output
        final_output = f"""
# Autonomous Implementation: {feature}

## Analysis
{analysis['synthesis'][:1000]}

## Implementation
{solution['implementation'].response[:2000]}

## Review
{solution['review'].response[:1000]}

## Tests
{solution['tests'].response[:1000]}

---
Status: {'✅ Approved' if solution['approved'] else '⚠️ Needs Review'}
Confidence: {analysis['confidence']:.0%}
        """
        
        return AutonomousResult(
            task_id=task_id,
            objective=feature,
            strategy="autonomous_coding",
            tentacle_results=solution,
            memory_logged=memory_logged,
            orchestrator_spawned=False,
            final_output=final_output,
            timestamp=datetime.now().isoformat()
        )
    
    def parallel_code_review(self, code: str, criteria: List[str] = None) -> Dict:
        """
        Parallel code review using multiple tentacles
        """
        criteria = criteria or ["correctness", "security", "performance", "maintainability"]
        
        results = {}
        for criterion in criteria:
            result = self.tentacles.spawn_tentacle(
                TentacleRole.REVIEWER,
                f"Review this code for {criterion}:\n{code}",
                f"Focus on: {criterion}"
            )
            results[criterion] = result
        
        # Summarize findings
        issues_found = []
        for criterion, result in results.items():
            if any(word in result.response.lower() for word in ['issue', 'bug', 'problem', 'error', 'warning']):
                issues_found.append(criterion)
        
        # Log to memory
        self.memory.log_knowledge(
            fact=f"Code review found issues in: {', '.join(issues_found) if issues_found else 'None'}",
            category="code_reviews",
            agent_id=self.agent_id
        )
        
        return {
            "reviews": results,
            "issues_found": issues_found,
            "approved": len(issues_found) == 0,
            "summary": f"Issues found in: {', '.join(issues_found)}" if issues_found else "All checks passed"
        }
    
    def strategic_plan_and_execute(self, objective: str, 
                                   constraints: List[str] = None) -> AutonomousResult:
        """
        Full strategic planning and execution
        """
        task_id = f"strategic-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Strategic planning with tentacles
        plan = self.tentacles.strategic_planning(objective, constraints)
        
        # Log plan to memory
        self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"Strategic plan for: {objective}\nPhases: {len(plan['phases'])}",
            tags=["planning", "strategic"]
        )
        
        # Build output
        final_output = f"""
# Strategic Plan: {objective}

## Phase Results
"""
        for phase in plan['phases']:
            final_output += f"\n### {phase['name']}\n{phase['result'].response[:500]}...\n"
        
        final_output += f"""

## Summary
Total Tokens: {plan['total_tokens']:,}
Total Latency: {plan['total_latency_ms']:.0f}ms
        """
        
        return AutonomousResult(
            task_id=task_id,
            objective=objective,
            strategy="strategic_planning",
            tentacle_results=plan,
            memory_logged=True,
            orchestrator_spawned=False,
            final_output=final_output,
            timestamp=datetime.now().isoformat()
        )
    
    def recall_and_continue(self, task_pattern: str) -> Optional[AutonomousResult]:
        """
        Recall similar past tasks and continue from there
        """
        # Search memory for similar tasks
        past_tasks = self.memory.recall_knowledge(
            query=task_pattern,
            category="autonomous_actions",
            limit=5
        )
        
        if not past_tasks:
            return None
        
        # Build context from past tasks
        context = "Previous similar tasks:\n"
        for task in past_tasks:
            context += f"- {task.get('fact', '')}\n"
        
        # Continue with new analysis incorporating past learnings
        result = self.strategic_analyze(
            f"Continue work on: {task_pattern}",
            context
        )
        
        return result

# Global instance
_integrated = None

def get_integrated_skill() -> IntegratedAutonomousSkill:
    global _integrated
    if _integrated is None:
        _integrated = IntegratedAutonomousSkill()
    return _integrated

# Convenience functions for direct use
def auto_code(feature: str, codebase: str = "") -> str:
    """Quick autonomous coding"""
    skill = get_integrated_skill()
    result = skill.autonomous_code_task(feature, codebase)
    return result.final_output

def swarm_analyze(objective: str) -> Dict:
    """Quick swarm analysis"""
    skill = get_integrated_skill()
    return skill.strategic_analyze(objective)

def review_code(code: str) -> Dict:
    """Quick code review"""
    skill = get_integrated_skill()
    return skill.parallel_code_review(code)
