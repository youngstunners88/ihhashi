/**
 * channels.ts — Communication Channels for iHhashi Swarm
 *
 * Defines how agents communicate, track costs, and log actions.
 * Uses Redis DB 1 for task queues (separate from app cache on DB 0).
 */

import { readFile, writeFile, appendFile, mkdir } from "fs/promises";
import { join } from "path";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AgentMessage {
  from: string;
  to: string;
  type: "task" | "result" | "escalation" | "broadcast" | "approval_request";
  payload: Record<string, unknown>;
  timestamp: string;
}

export interface TaskQueueItem {
  id: string;
  task: string;
  assignedTo: string[];
  status: "pending" | "in_progress" | "completed" | "blocked";
  priority: "low" | "medium" | "high" | "critical";
  createdAt: string;
  updatedAt: string;
}

export interface BudgetEntry {
  taskId: string;
  agentId: string;
  provider: string;
  tokensUsed: number;
  costZar: number;
  timestamp: string;
}

export interface BudgetStatus {
  dailyLimit: number;
  usedToday: number;
  tasksToday: number;
  entries: BudgetEntry[];
}

// ---------------------------------------------------------------------------
// Audit Log
// ---------------------------------------------------------------------------

export class AuditLog {
  private logDir: string;

  constructor(baseDir: string = process.cwd()) {
    const projectRoot = baseDir.includes("swarm")
      ? baseDir.replace(/\/swarm.*/, "")
      : baseDir;
    this.logDir = join(projectRoot, "swarm/state");
  }

  async log(event: string, data: Record<string, unknown>): Promise<void> {
    await mkdir(this.logDir, { recursive: true });

    const entry = {
      event,
      data,
      timestamp: new Date().toISOString(),
      sessionId: process.env.SWARM_SESSION_ID || "local",
    };

    const logFile = join(this.logDir, "audit.log");
    await appendFile(logFile, JSON.stringify(entry) + "\n");
  }

  async getRecentLogs(limit: number = 50): Promise<object[]> {
    const logFile = join(this.logDir, "audit.log");
    try {
      const content = await readFile(logFile, "utf-8");
      const lines = content.trim().split("\n").filter(Boolean);
      return lines
        .slice(-limit)
        .map((l) => JSON.parse(l))
        .reverse();
    } catch {
      return [];
    }
  }
}

// ---------------------------------------------------------------------------
// Budget Tracker
// ---------------------------------------------------------------------------

const LLM_COSTS_PER_1K_TOKENS: Record<string, number> = {
  groq: 0.001,       // R0.001 per 1K tokens
  openai: 0.03,      // R0.03 per 1K tokens
  anthropic: 0.015,  // R0.015 per 1K tokens
};

export class BudgetTracker {
  private budgetFile: string;
  private dailyLimit: number = 500; // R500 ZAR
  private perTaskLimit: number = 50; // R50 ZAR

  constructor(baseDir: string = process.cwd()) {
    const projectRoot = baseDir.includes("swarm")
      ? baseDir.replace(/\/swarm.*/, "")
      : baseDir;
    this.budgetFile = join(projectRoot, "swarm/state/budget.json");
  }

  getStatus(): BudgetStatus {
    try {
      const content = require("fs").readFileSync(this.budgetFile, "utf-8");
      const data = JSON.parse(content) as BudgetStatus;

      // Reset if it's a new day
      const today = new Date().toISOString().split("T")[0];
      const lastEntry = data.entries[data.entries.length - 1];
      if (lastEntry && !lastEntry.timestamp.startsWith(today)) {
        return {
          dailyLimit: this.dailyLimit,
          usedToday: 0,
          tasksToday: 0,
          entries: [],
        };
      }
      return data;
    } catch {
      return {
        dailyLimit: this.dailyLimit,
        usedToday: 0,
        tasksToday: 0,
        entries: [],
      };
    }
  }

  async recordUsage(entry: Omit<BudgetEntry, "timestamp">): Promise<void> {
    await mkdir(join(this.budgetFile, ".."), { recursive: true });

    const status = this.getStatus();
    const newEntry: BudgetEntry = {
      ...entry,
      timestamp: new Date().toISOString(),
    };

    status.entries.push(newEntry);
    status.usedToday += entry.costZar;
    status.tasksToday += 1;

    await writeFile(this.budgetFile, JSON.stringify(status, null, 2));

    // Alert if approaching limit
    const pct = status.usedToday / status.dailyLimit;
    if (pct >= 0.8) {
      console.warn(`⚠️ Budget alert: ${(pct * 100).toFixed(1)}% of daily limit used`);
    }
  }

  calculateCost(provider: string, tokensUsed: number): number {
    const rate = LLM_COSTS_PER_1K_TOKENS[provider] || 0.01;
    return (tokensUsed / 1000) * rate;
  }

  isWithinBudget(estimatedCostZar: number): boolean {
    const status = this.getStatus();
    return status.usedToday + estimatedCostZar <= status.dailyLimit;
  }

  isWithinTaskLimit(estimatedCostZar: number): boolean {
    return estimatedCostZar <= this.perTaskLimit;
  }
}

// ---------------------------------------------------------------------------
// Broadcast Channel
// ---------------------------------------------------------------------------

export class BroadcastChannel {
  private subscribers: Map<string, ((msg: AgentMessage) => void)[]> = new Map();

  subscribe(event: string, handler: (msg: AgentMessage) => void): void {
    if (!this.subscribers.has(event)) {
      this.subscribers.set(event, []);
    }
    this.subscribers.get(event)!.push(handler);
  }

  emit(event: string, message: AgentMessage): void {
    const handlers = this.subscribers.get(event) || [];
    handlers.forEach((handler) => handler(message));

    // Also emit to wildcard subscribers
    const wildcardHandlers = this.subscribers.get("*") || [];
    wildcardHandlers.forEach((handler) => handler(message));
  }

  /**
   * System-wide alerts (e.g., load-shedding detected)
   */
  systemAlert(alert: string, data: Record<string, unknown> = {}): void {
    this.emit("system_alert", {
      from: "swarm-commander",
      to: "*",
      type: "broadcast",
      payload: { alert, ...data },
      timestamp: new Date().toISOString(),
    });
  }
}
