#!/usr/bin/env python3
"""
Demo script for Autonomous Agent Orchestration Skill System

This script demonstrates the key capabilities of the integrated system:
1. Strategic Analysis with Qwen Tentacles
2. Persistent Memory operations
3. Autonomous execution workflows
"""
import os
import sys

# Add skills to path
sys.path.insert(0, os.path.expanduser("~/skills"))

from integrated_autonomous_skill import get_integrated_skill
from strategic_autonomy.scripts.strategic_autonomy import StrategicAutonomy

def demo_strategic_analysis():
    """Demo: Strategic Analysis"""
    print("=" * 60)
    print("DEMO 1: Strategic Analysis")
    print("=" * 60)
    
    skill = get_integrated_skill()
    
    objective = "Design a rate limiting system for a REST API"
    print(f"\nObjective: {objective}")
    print("Deploying all tentacles for comprehensive analysis...\n")
    
    result = skill.strategic_analyze(objective)
    
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"\nKey Recommendations:")
    for rec in result['recommendations'][:5]:
        print(f"  • {rec}")
    
    print(f"\nSynthesis (truncated):")
    print(result['synthesis'][:1000] + "...")
    
    return result

def demo_persistent_memory():
    """Demo: Persistent Memory"""
    print("\n" + "=" * 60)
    print("DEMO 2: Persistent Memory")
    print("=" * 60)
    
    skill = get_integrated_skill()
    
    # Write memory
    print("\nWriting to agent memory...")
    skill.memory.write_agent_memory(
        agent_id="demo-agent",
        entry="Completed rate limiter design analysis",
        tags=["demo", "rate-limiting"]
    )
    print("✓ Memory written")
    
    # Log knowledge
    print("\nLogging knowledge...")
    skill.memory.log_knowledge(
        fact="Token bucket algorithm is best for burst tolerance",
        category="system_design",
        agent_id="demo-agent"
    )
    print("✓ Knowledge logged")
    
    # Recall
    print("\nRecalling similar work...")
    similar = skill.memory.recall_knowledge("rate limit", limit=3)
    print(f"✓ Found {len(similar)} related facts")
    
    # Boot context
    print("\nLoading boot context...")
    context = skill.memory.boot_context("demo-agent")
    print(f"✓ Loaded {len(context)} characters of context")
    
    return context

def demo_autonomous_coding():
    """Demo: Autonomous Coding"""
    print("\n" + "=" * 60)
    print("DEMO 3: Autonomous Coding Workflow")
    print("=" * 60)
    
    skill = get_integrated_skill()
    
    feature = "Add Redis caching layer to API"
    print(f"\nFeature: {feature}")
    print("Running full autonomous workflow...\n")
    
    result = skill.autonomous_code_task(
        feature=feature,
        codebase="FastAPI application with MongoDB"
    )
    
    print(f"Task ID: {result.task_id}")
    print(f"Strategy: {result.strategy}")
    print(f"Memory Logged: {result.memory_logged}")
    print(f"\nFinal Output (truncated):")
    print(result.final_output[:1500] + "...")
    
    return result

def demo_strategic_autonomy():
    """Demo: Strategic Autonomy"""
    print("\n" + "=" * 60)
    print("DEMO 4: Strategic Autonomy")
    print("=" * 60)
    
    autonomy = StrategicAutonomy(agent_id="demo-strategic")
    
    # Boot
    print("\nBooting strategic autonomy...")
    context = autonomy.boot()
    print(f"✓ Booted with {len(context)} chars of context")
    
    # Strategic analysis
    print("\nRunning strategic analysis...")
    result = autonomy.strategic_analyze(
        "Evaluate microservices vs monolith for a startup",
        depth="standard"
    )
    
    print(f"✓ Analysis complete")
    print(f"  Strategy: {result.strategy_used}")
    print(f"  Phases: {result.phases_completed}/{result.total_phases}")
    print(f"  Findings: {len(result.key_findings)}")
    print(f"  Recommendations: {len(result.recommendations)}")
    
    return result

def demo_recall_and_improve():
    """Demo: Recall and Improve"""
    print("\n" + "=" * 60)
    print("DEMO 5: Recall and Improve")
    print("=" * 60)
    
    autonomy = StrategicAutonomy(agent_id="demo-improve")
    
    pattern = "authentication system"
    print(f"\nPattern: {pattern}")
    print("Searching memory for similar work...")
    
    result = autonomy.recall_and_improve(pattern)
    
    print(f"✓ Found {result.metadata.get('past_tasks_count', 0)} similar tasks")
    print(f"✓ Identified {result.metadata.get('improvements_found', 0)} improvement opportunities")
    print(f"\nFinal Output:")
    print(result.final_output[:1000] + "...")
    
    return result

def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("AUTONOMOUS AGENT ORCHESTRATION SKILL SYSTEM")
    print("Demo Suite")
    print("=" * 60)
    
    try:
        # Run demos
        demo_strategic_analysis()
        demo_persistent_memory()
        demo_autonomous_coding()
        demo_strategic_autonomy()
        demo_recall_and_improve()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
