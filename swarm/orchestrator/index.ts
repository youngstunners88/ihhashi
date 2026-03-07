#!/usr/bin/env bun
/**
 * index.ts — iHhashi Swarm Commander CLI
 *
 * Unified entry point for the iHhashi AI development swarm.
 * Routes tasks to specialized agents, tracks budgets, and
 * coordinates parallel development across all swarm components.
 */

import { Command } from "commander";
import chalk from "chalk";
import { routeTask, type RoutingResult } from "./router";
import { getAgentRegistry, getHierarchy, type AgentInfo } from "./hierarchy";
import { generateBackendMap, generateFrontendMap, generateApiSurface } from "./context";
import { AuditLog, BudgetTracker } from "./channels";

const program = new Command();
const audit = new AuditLog();
const budget = new BudgetTracker();

program
  .name("swarm")
  .description("iHhashi Swarm Commander — Orchestrate parallel AI development")
  .version("1.0.0");

// ---------------------------------------------------------------------------
// swarm task "<description>"
// ---------------------------------------------------------------------------
program
  .command("task")
  .description("Route a task to the right agent(s)")
  .argument("<description>", "Natural language task description")
  .option("-f, --files <paths...>", "Affected file paths for routing precision")
  .option("--dry-run", "Show routing without executing")
  .action(async (description: string, opts: { files?: string[]; dryRun?: boolean }) => {
    console.log(chalk.bold.cyan("\n🐝 iHhashi Swarm — Task Router\n"));

    const result = routeTask(description, opts.files || []);
    displayRoutingResult(result);

    // Check approval gates
    const needsApproval = checkApprovalGates(description, opts.files || []);
    if (needsApproval.length > 0) {
      console.log(chalk.red.bold("\n⚠️  APPROVAL REQUIRED:"));
      needsApproval.forEach((gate) => console.log(chalk.red(`  • ${gate}`)));
    }

    // Budget check
    const budgetStatus = budget.getStatus();
    console.log(
      chalk.gray(`\n💰 Budget: R${budgetStatus.usedToday.toFixed(2)} / R${budgetStatus.dailyLimit} daily`)
    );

    if (!opts.dryRun) {
      audit.log("task_routed", { description, result, needsApproval });
    }
  });

// ---------------------------------------------------------------------------
// swarm agents
// ---------------------------------------------------------------------------
program
  .command("agents")
  .description("List all registered swarm agents")
  .option("-t, --tier <number>", "Filter by tier (0=governance, 1=leads, 2=specialists)")
  .option("-d, --division <name>", "Filter by division")
  .action((opts: { tier?: string; division?: string }) => {
    console.log(chalk.bold.cyan("\n🐝 iHhashi Swarm — Agent Registry\n"));

    const hierarchy = getHierarchy();

    // Tier 0: Governance
    if (!opts.tier || opts.tier === "0") {
      console.log(chalk.yellow.bold("━━━ Tier 0: Governance (Paperclip) ━━━"));
      console.log(
        chalk.white(
          "  📋 Budget control, approval gates, audit logging, heartbeat monitoring"
        )
      );
      console.log();
    }

    // Tier 1: Domain Leads
    if (!opts.tier || opts.tier === "1") {
      console.log(chalk.green.bold("━━━ Tier 1: Domain Leads ━━━"));
      hierarchy.leads.forEach((lead) => {
        console.log(
          chalk.green(`  🎯 ${lead.name}`) +
            chalk.gray(` — ${lead.scope.join(", ")}`)
        );
      });
      console.log();
    }

    // Tier 2: Specialists
    if (!opts.tier || opts.tier === "2") {
      const registry = getAgentRegistry();
      const divisions = new Map<string, AgentInfo[]>();

      for (const agent of registry) {
        if (agent.tier !== 2) continue;
        if (opts.division && agent.division !== opts.division) continue;
        if (!divisions.has(agent.division)) divisions.set(agent.division, []);
        divisions.get(agent.division)!.push(agent);
      }

      for (const [division, agents] of divisions) {
        console.log(chalk.blue.bold(`━━━ ${division} ━━━`));
        agents.forEach((agent) => {
          console.log(
            chalk.blue(`  🔧 ${agent.name}`) +
              chalk.gray(` — ${agent.description}`)
          );
        });
        console.log();
      }
    }

    console.log(chalk.gray(`Total agents: ${getAgentRegistry().length}`));
  });

// ---------------------------------------------------------------------------
// swarm budget
// ---------------------------------------------------------------------------
program
  .command("budget")
  .description("Show budget tracking and cost breakdown")
  .action(() => {
    console.log(chalk.bold.cyan("\n🐝 iHhashi Swarm — Budget Tracker\n"));

    const status = budget.getStatus();
    const pct = (status.usedToday / status.dailyLimit) * 100;
    const color = pct > 80 ? chalk.red : pct > 50 ? chalk.yellow : chalk.green;

    console.log(chalk.white("Daily Budget:"));
    console.log(
      `  ${color(`R${status.usedToday.toFixed(2)}`)} / R${status.dailyLimit} (${color(pct.toFixed(1) + "%")})`
    );
    console.log(chalk.white("\nPer-Task Limit: R50"));
    console.log(chalk.white(`\nTasks Today: ${status.tasksToday}`));
    console.log(chalk.white(`\nLLM Providers:`));
    console.log(chalk.gray("  • Groq (llama-3.3-70b): R0.001/1K tokens [primary]"));
    console.log(chalk.gray("  • OpenAI (gpt-4): R0.03/1K tokens [secondary]"));
    console.log(chalk.gray("  • Anthropic (claude): R0.015/1K tokens [tertiary]"));
  });

// ---------------------------------------------------------------------------
// swarm context <scope>
// ---------------------------------------------------------------------------
program
  .command("context")
  .description("Generate codebase context snapshot")
  .argument("[scope]", "Scope: backend, frontend, api, all", "all")
  .action(async (scope: string) => {
    console.log(chalk.bold.cyan("\n🐝 iHhashi Swarm — Context Generator\n"));

    const projectRoot = process.cwd().includes("swarm")
      ? process.cwd().replace(/\/swarm.*/, "")
      : process.cwd();

    if (scope === "backend" || scope === "all") {
      console.log(chalk.yellow("Generating backend map..."));
      await generateBackendMap(projectRoot);
      console.log(chalk.green("  ✓ swarm/context/backend-map.json"));
    }
    if (scope === "frontend" || scope === "all") {
      console.log(chalk.yellow("Generating frontend map..."));
      await generateFrontendMap(projectRoot);
      console.log(chalk.green("  ✓ swarm/context/frontend-map.json"));
    }
    if (scope === "api" || scope === "all") {
      console.log(chalk.yellow("Generating API surface..."));
      await generateApiSurface(projectRoot);
      console.log(chalk.green("  ✓ swarm/context/api-surface.json"));
    }

    audit.log("context_generated", { scope });
  });

// ---------------------------------------------------------------------------
// swarm squad "<task>"
// ---------------------------------------------------------------------------
program
  .command("squad")
  .description("Spawn a multi-agent squad for complex cross-domain tasks")
  .argument("<task>", "Complex task requiring multiple specialists")
  .action(async (task: string) => {
    console.log(chalk.bold.cyan("\n🐝 iHhashi Swarm — Squad Formation\n"));

    const result = routeTask(task);
    const assignments = result.assignments;

    if (assignments.length === 0) {
      console.log(chalk.yellow("No matching specialists found. Assigning to Platform Architect."));
      return;
    }

    // Determine squad leader (highest priority domain lead)
    const leader = assignments[0];
    const workers = assignments.slice(1);

    console.log(chalk.green.bold(`Squad Leader: ${leader.name}`));
    console.log(chalk.gray(`  Reason: ${leader.reason}`));
    console.log();

    if (workers.length > 0) {
      console.log(chalk.blue.bold("Squad Members:"));
      workers.forEach((w, i) => {
        console.log(chalk.blue(`  ${i + 1}. ${w.name}`) + chalk.gray(` — ${w.reason}`));
      });
    }

    // Check if Compliance Officer should be added
    const sensitivePatterns = /payment|user.*data|popia|personal|refund|verification/i;
    if (sensitivePatterns.test(task) && !assignments.some((a) => a.agentId === "compliance-officer")) {
      console.log(chalk.yellow("\n  + Adding Compliance Officer (sensitive data detected)"));
    }

    const needsApproval = checkApprovalGates(task);
    if (needsApproval.length > 0) {
      console.log(chalk.red.bold("\n⚠️  APPROVAL GATES:"));
      needsApproval.forEach((gate) => console.log(chalk.red(`  • ${gate}`)));
    }

    console.log(chalk.gray(`\nSquad size: ${assignments.length} agents`));
    audit.log("squad_formed", { task, leader: leader.name, members: workers.map((w) => w.name) });
  });

// ---------------------------------------------------------------------------
// swarm status
// ---------------------------------------------------------------------------
program
  .command("status")
  .description("Show overall swarm status")
  .action(() => {
    console.log(chalk.bold.cyan("\n🐝 iHhashi Swarm — Status Dashboard\n"));

    const registry = getAgentRegistry();
    const budgetStatus = budget.getStatus();
    const hierarchy = getHierarchy();

    console.log(chalk.white.bold("System:"));
    console.log(`  Swarm: ${chalk.green("ACTIVE")}`);
    console.log(`  Agents: ${registry.length} registered`);
    console.log(`  Leads: ${hierarchy.leads.length}`);
    console.log(`  SA-Specific: 8 specialist agents`);
    console.log();

    console.log(chalk.white.bold("Components:"));
    console.log(`  Paperclip: ${chalk.green("✓")} Governance layer`);
    console.log(`  LangChain Skills: ${chalk.green("✓")} 11 skills loaded`);
    console.log(`  Agency Agents: ${chalk.green("✓")} 55+ personalities`);
    console.log(`  Orchestrator: ${chalk.green("✓")} CLI active`);
    console.log();

    console.log(chalk.white.bold("Budget:"));
    console.log(`  Today: R${budgetStatus.usedToday.toFixed(2)} / R${budgetStatus.dailyLimit}`);
    console.log(`  Tasks: ${budgetStatus.tasksToday}`);
    console.log();

    console.log(chalk.white.bold("Infrastructure:"));
    console.log(`  Backend: FastAPI + MongoDB + Redis`);
    console.log(`  Frontend: React + Vite + TypeScript`);
    console.log(`  AI: Nduna (Groq llama-3.3-70b)`);
    console.log(`  Real-time: WebSocket + Redis PubSub`);
  });

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function displayRoutingResult(result: RoutingResult) {
  if (result.assignments.length === 0) {
    console.log(chalk.yellow("No specific routing match. Assigning to Platform Architect (default)."));
    console.log(chalk.gray(`Task: "${result.task}"`));
    return;
  }

  console.log(chalk.white(`Task: "${result.task}"\n`));
  console.log(chalk.white.bold("Assigned Agents:"));

  result.assignments.forEach((a) => {
    const icon = a.priority === 1 ? "🎯" : a.priority === 2 ? "👀" : "💡";
    const pLabel = a.priority === 1 ? "PRIMARY" : a.priority === 2 ? "REVIEWER" : "ADVISORY";
    console.log(
      `  ${icon} ${chalk.bold(a.name)} ${chalk.gray(`[${pLabel}]`)}`
    );
    console.log(chalk.gray(`     ${a.reason}`));
  });

  if (result.matchedRules.length > 0) {
    console.log(chalk.gray(`\nMatched rules: ${result.matchedRules.join(", ")}`));
  }
}

function checkApprovalGates(task: string, filePaths: string[] = []): string[] {
  const gates: string[] = [];
  const allText = [task, ...filePaths].join(" ");

  if (/payment|paystack|yoco|payout/i.test(allText)) {
    gates.push("Payment system change — requires human approval");
  }
  if (/migration|schema.*change|drop.*collection/i.test(allText)) {
    gates.push("Database migration — requires lead approval");
  }
  if (/deploy|production|release/i.test(allText)) {
    gates.push("Production deployment — requires human approval");
  }
  if (/user.*model|verification|popia|personal.*data/i.test(allText)) {
    gates.push("User data model change — requires compliance review");
  }
  if (/docker|compose|infrastructure/i.test(allText)) {
    gates.push("Infrastructure change — requires lead approval");
  }

  return gates;
}

program.parse();
