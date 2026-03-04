#!/usr/bin/env python3
"""
Strategic Autonomy Skill

The main entry point for autonomous agent operations.
Combines Orchestrator + Qwen Tentacles + Persistent Memory
into a unified strategic system.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Add paths for imports
sys.path.insert(0, os.path.expanduser("~/skills"))

from qwen_tentacles import get_tentacles, TentacleRole
from persistent_memory_skill import get_memory

@dataclass
class StrategicResult:
    """Result of a strategic operation"""
    task_id: str
    objective: str
    strategy_used: str
    success: bool
    phases_completed: int
    total_phases: int
    key_findings: List[str]
    recommendations: List[str]
    final_output: str
    memory_logged: bool
    timestamp: str
    metadata: Dict[str, Any]

class StrategicAutonomy:
    """
    Strategic Autonomous Agent System
    
    Capabilities:
    - Self-directed planning using multiple tentacles
    - Persistent memory across sessions
    - Parallel agent orchestration
    - Continuous learning and improvement
    """
    
    def __init__(self, agent_id: str = "strategic-core"):
        self.agent_id = agent_id
        self.tentacles = get_tentacles()
        self.memory = get_memory()
        
    def _log(self, action: str, details: str, tags: List[str] = None):
        """Log action to memory"""
        tags = tags or ["strategic", "autonomy"]
        self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"{action}: {details}",
            tags=tags
        )
    
    def boot(self) -> str:
        """
        Boot the strategic agent with context from memory.
        Call this before any strategic operation.
        """
        context = self.memory.boot_context(self.agent_id)
        
        # Log the boot
        self._log("Boot", f"Loaded context from memory")
        
        # Update shared brain
        self.memory.update_shared_brain("intel-feed", {
            "entries": [{
                "timestamp": datetime.now().isoformat(),
                "type": "boot",
                "agent": self.agent_id,
                "context_length": len(context)
            }]
        })
        
        return context
    
    def strategic_analyze(self, objective: str, depth: str = "comprehensive") -> StrategicResult:
        """
        Comprehensive strategic analysis using all tentacles.
        
        Args:
            objective: What to analyze
            depth: "quick" (1 tentacle) | "standard" (3 tentacles) | "comprehensive" (all 5)
        """
        task_id = f"analyze-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Boot with context
        context = self.boot()
        full_context = f"{context}\n\nObjective: {objective}"
        
        self._log("Strategic Analysis", f"Starting {depth} analysis: {objective}")
        
        # Deploy tentacles based on depth
        if depth == "quick":
            results = {
                TentacleRole.ANALYZER: self.tentacles.spawn_tentacle(
                    TentacleRole.ANALYZER, objective, context
                )
            }
        elif depth == "standard":
            results = {
                TentacleRole.PLANNER: self.tentacles.spawn_tentacle(
                    TentacleRole.PLANNER, objective, context
                ),
                TentacleRole.ANALYZER: self.tentacles.spawn_tentacle(
                    TentacleRole.ANALYZER, objective, context
                ),
                TentacleRole.REVIEWER: self.tentacles.spawn_tentacle(
                    TentacleRole.REVIEWER, objective, context
                ),
            }
        else:  # comprehensive
            results = self.tentacles.swarm_attack(objective, full_context)
        
        # Extract findings
        key_findings = []
        recommendations = []
        
        for role, result in results.items():
            lines = result.response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    if any(marker in line.lower() for marker in ['finding', 'issue', 'problem', 'observation']):
                        key_findings.append(f"[{role.value}] {line[2:]}")
                    elif any(marker in line.lower() for marker in ['recommend', 'suggest', 'should', 'consider']):
                        recommendations.append(f"[{role.value}] {line[2:]}")
        
        # Synthesize final output
        synthesis = self._synthesize_results(results, objective)
        
        # Log to memory
        memory_logged = self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"Strategic analysis complete: {objective}\nFindings: {len(key_findings)}\nRecommendations: {len(recommendations)}",
            tags=["analysis", depth]
        )
        
        # Log knowledge
        for finding in key_findings[:3]:
            self.memory.log_knowledge(
                fact=finding,
                category="analysis_findings",
                agent_id=self.agent_id
            )
        
        return StrategicResult(
            task_id=task_id,
            objective=objective,
            strategy_used=f"strategic_analysis_{depth}",
            success=True,
            phases_completed=len(results),
            total_phases=len(results),
            key_findings=key_findings[:10],
            recommendations=recommendations[:10],
            final_output=synthesis,
            memory_logged=memory_logged,
            timestamp=datetime.now().isoformat(),
            metadata={
                "depth": depth,
                "tentacles_used": [r.value for r in results.keys()],
                "total_tokens": sum(r.tokens_used for r in results.values()),
                "total_latency_ms": sum(r.latency_ms for r in results.values())
            }
        )
    
    def autonomous_execute(self, objective: str, 
                          constraints: List[str] = None,
                          max_iterations: int = 5) -> StrategicResult:
        """
        Fully autonomous execution: plan → execute → verify → learn
        """
        task_id = f"execute-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        constraints = constraints or []
        
        self._log("Autonomous Execution", f"Starting: {objective}")
        
        # Phase 1: Strategic Planning
        self._log("Phase 1", "Strategic Planning")
        plan_result = self.tentacles.strategic_planning(objective, constraints)
        
        # Phase 2: Risk Analysis (if complex)
        if len(constraints) > 2 or "complex" in objective.lower():
            self._log("Phase 2", "Risk Analysis")
            analyzer = self.tentacles.spawn_tentacle(
                TentacleRole.ANALYZER,
                f"Identify risks in this plan:\n{plan_result['phases'][0]['result'].response}",
                objective
            )
            risks = analyzer.response
        else:
            risks = "No additional risks identified"
        
        # Phase 3: Implementation
        self._log("Phase 3", "Implementation")
        impl_phase = plan_result['phases'][2] if len(plan_result['phases']) > 2 else plan_result['phases'][-1]
        implementation = impl_phase['result'].response
        
        # Phase 4: Self-Review
        self._log("Phase 4", "Self-Review")
        review_result = self.tentacles.spawn_tentacle(
            TentacleRole.REVIEWER,
            f"Review this implementation:\n{implementation}",
            f"Objective: {objective}"
        )
        
        approved = "LGTM" in review_result.response or "looks good" in review_result.response.lower()
        
        # Phase 5: Learning
        self._log("Phase 5", "Learning and Logging")
        learnings = [
            f"Plan approach: {plan_result['phases'][0]['result'].response[:200]}",
            f"Implementation strategy: {implementation[:200]}",
            f"Review outcome: {'Approved' if approved else 'Needs work'}"
        ]
        
        # Write to memory
        memory_logged = self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"Autonomous execution: {objective}\nApproved: {approved}\nIterations: {max_iterations}",
            tags=["execution", "autonomous"]
        )
        
        # Update shared brain
        self.memory.update_shared_brain("content-vault", {
            "last_execution": {
                "timestamp": datetime.now().isoformat(),
                "objective": objective,
                "approved": approved,
                "output": implementation[:500]
            }
        })
        
        # Build final output
        final_output = f"""
# Autonomous Execution: {objective}

## Execution Plan
{plan_result['phases'][0]['result'].response[:1000]}

## Risks Identified
{risks[:500]}

## Implementation
{implementation[:2000]}

## Review
{review_result.response[:1000]}

## Status
{'✅ Approved' if approved else '⚠️ Needs Revision'}

## Learnings
{chr(10).join(f"- {l}" for l in learnings)}
"""
        
        return StrategicResult(
            task_id=task_id,
            objective=objective,
            strategy_used="autonomous_execute",
            success=approved,
            phases_completed=5,
            total_phases=5,
            key_findings=[risks[:200]],
            recommendations=[review_result.response[:200]],
            final_output=final_output,
            memory_logged=memory_logged,
            timestamp=datetime.now().isoformat(),
            metadata={
                "approved": approved,
                "total_tokens": plan_result['total_tokens'],
                "total_latency_ms": plan_result['total_latency_ms'],
                "learnings": learnings
            }
        )
    
    def recall_and_improve(self, pattern: str) -> StrategicResult:
        """
        Recall similar past work and improve upon it.
        """
        task_id = f"improve-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Recall similar work
        past_work = self.memory.recall_knowledge(
            query=pattern,
            category="autonomous_actions",
            limit=5
        )
        
        if not past_work:
            # No past work, start fresh
            return self.strategic_analyze(f"Analyze and improve: {pattern}")
        
        # Build context from past work
        past_context = "Previous similar work:\n"
        for work in past_work:
            past_context += f"- {work.get('fact', '')}\n"
        
        self._log("Recall and Improve", f"Found {len(past_work)} similar tasks")
        
        # Analyze past work for improvement opportunities
        improvement_prompt = f"""
Based on this past work:
{past_context}

How can we improve the approach for: {pattern}

Focus on:
1. What worked well
2. What could be improved
3. New approaches to consider
4. Lessons learned
"""
        
        # Get improvement suggestions from all tentacles
        results = self.tentacles.swarm_attack(improvement_prompt, past_context)
        
        # Synthesize improvements
        improvements = []
        for role, result in results.items():
            if "improve" in result.response.lower() or "better" in result.response.lower():
                improvements.append(f"[{role.value}] {result.response[:300]}")
        
        # Create improved plan
        planner_result = self.tentacles.spawn_tentacle(
            TentacleRole.PLANNER,
            f"Create an improved plan for: {pattern}",
            "\n".join(improvements[:3])
        )
        
        # Log the improvement
        memory_logged = self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"Improved approach for: {pattern}\nBased on {len(past_work)} past tasks",
            tags=["improvement", pattern[:20]]
        )
        
        final_output = f"""
# Recall and Improve: {pattern}

## Past Work Found
{len(past_work)} similar tasks identified

## Improvement Opportunities
{chr(10).join(improvements[:5])}

## Improved Plan
{planner_result.response[:2000]}

## Key Improvements
1. Leveraged past learnings
2. Incorporated feedback
3. Optimized approach
"""
        
        return StrategicResult(
            task_id=task_id,
            objective=f"Improve: {pattern}",
            strategy_used="recall_and_improve",
            success=True,
            phases_completed=2,
            total_phases=2,
            key_findings=[f"Found {len(past_work)} similar tasks"],
            recommendations=improvements[:5],
            final_output=final_output,
            memory_logged=memory_logged,
            timestamp=datetime.now().isoformat(),
            metadata={
                "past_tasks_count": len(past_work),
                "improvements_found": len(improvements)
            }
        )
    
    def continuous_learn(self, feedback: str, task_type: str):
        """
        Learn from feedback and update knowledge base.
        """
        # Log the feedback
        self.memory.write_agent_memory(
            agent_id=self.agent_id,
            entry=f"Feedback received: {feedback}",
            tags=["feedback", task_type]
        )
        
        # Extract learnings using explainer tentacle
        explainer = self.tentacles.spawn_tentacle(
            TentacleRole.EXPLAINER,
            f"Extract key learnings from this feedback:\n{feedback}",
            f"Task type: {task_type}"
        )
        
        # Log knowledge
        self.memory.log_knowledge(
            fact=f"Learning from {task_type}: {explainer.response[:500]}",
            category="learnings",
            agent_id=self.agent_id
        )
        
        # Update shared brain
        self.memory.update_shared_brain("intel-feed", {
            "entries": [{
                "timestamp": datetime.now().isoformat(),
                "type": "learning",
                "task_type": task_type,
                "feedback_summary": feedback[:200]
            }]
        })
    
    def _synthesize_results(self, results: Dict, objective: str) -> str:
        """Synthesize results from multiple tentacles"""
        parts = [f"# Strategic Analysis: {objective}\n"]
        
        for role, result in results.items():
            parts.append(f"\n## {role.value.upper()} Perspective\n")
            parts.append(result.response[:1000])
            parts.append(f"\n*Tokens: {result.tokens_used}, Latency: {result.latency_ms:.0f}ms*\n")
        
        parts.append("\n---\n\n## Summary\n")
        parts.append(f"Analysis completed using {len(results)} specialized tentacles.")
        parts.append(f"\nTotal tokens: {sum(r.tokens_used for r in results.values())}")
        
        return "\n".join(parts)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Strategic Autonomy - Autonomous Agent Operations"
    )
    parser.add_argument(
        "command",
        choices=["analyze", "execute", "improve", "learn", "boot"],
        help="Command to execute"
    )
    parser.add_argument("--objective", "-o", help="Main objective or task")
    parser.add_argument("--depth", "-d", default="comprehensive",
                       choices=["quick", "standard", "comprehensive"],
                       help="Analysis depth")
    parser.add_argument("--constraint", "-c", action="append",
                       help="Constraints (can be used multiple times)")
    parser.add_argument("--pattern", "-p", help="Pattern to recall and improve")
    parser.add_argument("--feedback", "-f", help="Feedback for learning")
    parser.add_argument("--task-type", "-t", help="Type of task for learning")
    parser.add_argument("--output", "-O", help="Output file (default: stdout)")
    parser.add_argument("--json", "-j", action="store_true",
                       help="Output as JSON")
    
    args = parser.parse_args()
    
    # Initialize strategic autonomy
    autonomy = StrategicAutonomy(agent_id="strategic-cli")
    
    # Execute command
    if args.command == "boot":
        context = autonomy.boot()
        result = {"context_length": len(context), "booted": True}
    
    elif args.command == "analyze":
        if not args.objective:
            print("Error: --objective required for analyze")
            return 1
        result = autonomy.strategic_analyze(args.objective, args.depth)
        result = asdict(result)
    
    elif args.command == "execute":
        if not args.objective:
            print("Error: --objective required for execute")
            return 1
        result = autonomy.autonomous_execute(
            args.objective,
            args.constraint or []
        )
        result = asdict(result)
    
    elif args.command == "improve":
        if not args.pattern:
            print("Error: --pattern required for improve")
            return 1
        result = autonomy.recall_and_improve(args.pattern)
        result = asdict(result)
    
    elif args.command == "learn":
        if not args.feedback or not args.task_type:
            print("Error: --feedback and --task-type required for learn")
            return 1
        autonomy.continuous_learn(args.feedback, args.task_type)
        result = {"status": "learned", "feedback_logged": True}
    
    else:
        print(f"Unknown command: {args.command}")
        return 1
    
    # Output result
    if args.json:
        output = json.dumps(result, indent=2, default=str)
    else:
        if isinstance(result, dict) and "final_output" in result:
            output = result["final_output"]
        elif isinstance(result, dict) and "context_length" in result:
            output = f"Booted with {result['context_length']} characters of context"
        else:
            output = json.dumps(result, indent=2, default=str)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
