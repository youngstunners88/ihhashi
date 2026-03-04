#!/usr/bin/env python3
"""
Qwen 3.5 Tentacles Skill
Multi-model orchestration using Qwen models as specialized agents
"""
import subprocess
import json
import os
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

class TentacleRole(Enum):
    ANALYZER = "analyzer"      # Code analysis, bug detection
    CODER = "coder"            # Code generation
    REVIEWER = "reviewer"      # Code review
    PLANNER = "planner"        # Architecture planning
    EXPLAINER = "explainer"    # Documentation/explanation

@dataclass
class TentacleResult:
    role: TentacleRole
    model: str
    prompt: str
    response: str
    latency_ms: float
    tokens_used: int

class QwenTentacles:
    """
    Strategic multi-tentacle AI system using Qwen models
    """
    
    # Model mapping for different roles
    ROLE_MODELS = {
        TentacleRole.ANALYZER: "qwen2.5:14b",      # Deep analysis
        TentacleRole.CODER: "qwen2.5-coder:latest", # Code generation
        TentacleRole.REVIEWER: "qwen2.5:14b",       # Code review
        TentacleRole.PLANNER: "qwen2.5:14b",        # Architecture
        TentacleRole.EXPLAINER: "llama3:latest",    # Explanations
    }
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.executor = ThreadPoolExecutor(max_workers=5)
        
    def _call_ollama(self, model: str, prompt: str, system: str = "") -> Dict:
        """Call Ollama API"""
        import requests
        
        url = f"{self.ollama_host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=300)
            return response.json()
        except Exception as e:
            return {"error": str(e), "response": ""}
    
    def spawn_tentacle(self, role: TentacleRole, prompt: str, 
                      context: str = "") -> TentacleResult:
        """
        Deploy a single tentacle (specialized agent)
        
        Args:
            role: The specialization role
            prompt: Task description
            context: Additional context
        """
        import time
        
        model = self.ROLE_MODELS.get(role, "qwen2.5:14b")
        
        # Role-specific system prompts
        system_prompts = {
            TentacleRole.ANALYZER: "You are a code analyzer. Find bugs, security issues, and optimization opportunities. Be thorough and specific.",
            TentacleRole.CODER: "You are an expert programmer. Write clean, efficient, well-documented code. Follow best practices.",
            TentacleRole.REVIEWER: "You are a code reviewer. Check for correctness, style, maintainability, and potential issues. Be constructive.",
            TentacleRole.PLANNER: "You are a system architect. Design scalable, maintainable solutions. Consider trade-offs.",
            TentacleRole.EXPLAINER: "You are a technical writer. Explain complex concepts clearly. Use examples.",
        }
        
        system = system_prompts.get(role, "You are a helpful AI assistant.")
        full_prompt = f"{context}\n\nTask: {prompt}" if context else prompt
        
        start_time = time.time()
        result = self._call_ollama(model, full_prompt, system)
        latency = (time.time() - start_time) * 1000
        
        return TentacleResult(
            role=role,
            model=model,
            prompt=prompt,
            response=result.get("response", ""),
            latency_ms=latency,
            tokens_used=result.get("eval_count", 0)
        )
    
    def swarm_attack(self, task: str, context: str = "") -> Dict[TentacleRole, TentacleResult]:
        """
        Deploy all tentacles in parallel for comprehensive analysis
        
        Args:
            task: The main task
            context: Additional context
            
        Returns:
            Dictionary mapping roles to their results
        """
        futures = {}
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all tentacles
            for role in TentacleRole:
                future = executor.submit(
                    self.spawn_tentacle,
                    role,
                    task,
                    context
                )
                futures[future] = role
            
            # Collect results as they complete
            for future in as_completed(futures):
                role = futures[future]
                try:
                    results[role] = future.result()
                except Exception as e:
                    results[role] = TentacleResult(
                        role=role,
                        model="error",
                        prompt=task,
                        response=f"Error: {str(e)}",
                        latency_ms=0,
                        tokens_used=0
                    )
        
        return results
    
    def strategic_planning(self, objective: str, constraints: List[str] = None) -> Dict:
        """
        Multi-phase strategic planning using tentacles
        
        Phase 1: Planner analyzes requirements
        Phase 2: Analyzer identifies risks  
        Phase 3: Coder generates implementation
        Phase 4: Reviewer validates approach
        """
        constraints = constraints or []
        constraint_text = "\n".join(f"- {c}" for c in constraints)
        
        # Phase 1: Planning
        planner = self.spawn_tentacle(
            TentacleRole.PLANNER,
            f"Create a detailed plan for: {objective}",
            f"Constraints:\n{constraint_text}"
        )
        
        # Phase 2: Risk Analysis
        analyzer = self.spawn_tentacle(
            TentacleRole.ANALYZER,
            f"Identify risks and issues in this plan:\n{planner.response}",
            f"Objective: {objective}"
        )
        
        # Phase 3: Implementation
        coder = self.spawn_tentacle(
            TentacleRole.CODER,
            f"Implement the plan, addressing these risks:\n{analyzer.response}",
            f"Plan:\n{planner.response}"
        )
        
        # Phase 4: Review
        reviewer = self.spawn_tentacle(
            TentacleRole.REVIEWER,
            f"Review this implementation:\n{coder.response}",
            f"Original objective: {objective}"
        )
        
        return {
            "phases": [
                {"name": "planning", "result": planner},
                {"name": "risk_analysis", "result": analyzer},
                {"name": "implementation", "result": coder},
                {"name": "review", "result": reviewer},
            ],
            "final_output": reviewer.response,
            "total_tokens": sum([
                planner.tokens_used,
                analyzer.tokens_used,
                coder.tokens_used,
                reviewer.tokens_used
            ]),
            "total_latency_ms": sum([
                planner.latency_ms,
                analyzer.latency_ms,
                coder.latency_ms,
                reviewer.latency_ms
            ])
        }
    
    def autonomous_coding(self, feature_request: str, codebase_context: str = "") -> Dict:
        """
        Fully autonomous coding workflow
        
        1. Analyze requirements
        2. Design solution
        3. Generate code
        4. Self-review
        5. Generate tests
        """
        # Step 1: Understand requirements
        explainer = self.spawn_tentacle(
            TentacleRole.EXPLAINER,
            f"Clarify this feature request and identify key requirements:\n{feature_request}",
            codebase_context
        )
        
        # Step 2: Plan architecture
        planner = self.spawn_tentacle(
            TentacleRole.PLANNER,
            f"Design the architecture for:\n{explainer.response}",
            codebase_context
        )
        
        # Step 3: Generate implementation
        coder = self.spawn_tentacle(
            TentacleRole.CODER,
            f"Implement this design:\n{planner.response}",
            f"Requirements:\n{explainer.response}\n\n{codebase_context}"
        )
        
        # Step 4: Self-review
        reviewer = self.spawn_tentacle(
            TentacleRole.REVIEWER,
            f"Review this code:\n{coder.response}",
            f"Feature: {feature_request}"
        )
        
        # Step 5: Generate tests
        test_coder = self.spawn_tentacle(
            TentacleRole.CODER,
            f"Generate comprehensive tests for:\n{coder.response}",
            "Include unit tests, edge cases, and integration tests."
        )
        
        return {
            "requirements": explainer,
            "architecture": planner,
            "implementation": coder,
            "review": reviewer,
            "tests": test_coder,
            "approved": "LGTM" in reviewer.response or "looks good" in reviewer.response.lower(),
        }

# Global instance
_tentacles = None

def get_tentacles() -> QwenTentacles:
    global _tentacles
    if _tentacles is None:
        _tentacles = QwenTentacles()
    return _tentacles
