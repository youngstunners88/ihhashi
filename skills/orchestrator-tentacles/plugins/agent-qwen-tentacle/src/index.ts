/**
 * Agent Plugin: Qwen 3.5 Tentacles
 * 
 * Integrates Qwen models via Ollama as an agent for the orchestrator.
 * Supports multiple tentacle roles: analyzer, coder, reviewer, planner, explainer
 */
import {
  type Agent,
  type AgentLaunchConfig,
  type AgentSessionInfo,
  type ActivityDetection,
  type ActivityState,
  type PluginModule,
  type ProjectConfig,
  type RuntimeHandle,
  type Session,
  type WorkspaceHooksConfig,
  DEFAULT_READY_THRESHOLD_MS,
} from "@composio/ao-core";
import { execFile } from "node:child_process";
import { readFile, writeFile, mkdir, stat } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

// =============================================================================
// Plugin Manifest
// =============================================================================

export const manifest = {
  name: "qwen-tentacle",
  slot: "agent" as const,
  description: "Agent plugin: Qwen 3.5 Tentacles via Ollama with persistent memory",
  version: "1.0.0",
};

// =============================================================================
// Tentacle Configuration
// =============================================================================

type TentacleRole = "analyzer" | "coder" | "reviewer" | "planner" | "explainer";

interface TentacleConfig {
  model: string;
  systemPrompt: string;
  temperature?: number;
}

const TENTACLE_CONFIGS: Record<TentacleRole, TentacleConfig> = {
  analyzer: {
    model: "qwen2.5:14b",
    systemPrompt: `You are a code analyzer. Find bugs, security issues, and optimization opportunities.
Be thorough and specific. Provide concrete examples and line numbers when possible.
After completing your analysis, summarize findings for the memory log.`,
    temperature: 0.3,
  },
  coder: {
    model: "qwen2.5-coder:14b",
    systemPrompt: `You are an expert programmer. Write clean, efficient, well-documented code.
Follow best practices and include error handling. After writing code, explain your design decisions
for the memory log.`,
    temperature: 0.2,
  },
  reviewer: {
    model: "qwen2.5:14b",
    systemPrompt: `You are a code reviewer. Check for correctness, style, maintainability, and potential issues.
Be constructive and suggest improvements. After review, log your recommendations.`,
    temperature: 0.3,
  },
  planner: {
    model: "qwen2.5:32b",
    systemPrompt: `You are a system architect. Design scalable, maintainable solutions.
Consider trade-offs and provide clear rationale. Document your architectural decisions for future reference.`,
    temperature: 0.4,
  },
  explainer: {
    model: "qwen2.5:14b",
    systemPrompt: `You are a technical writer. Explain complex concepts clearly with examples.
After explaining, note key takeaways for the knowledge base.`,
    temperature: 0.5,
  },
};

// =============================================================================
// Memory Integration Helpers
// =============================================================================

interface MemoryConfig {
  memoryBasePath: string;
  agentId: string;
}

async function writeAgentMemory(config: MemoryConfig, entry: string): Promise<void> {
  const date = new Date().toISOString().split("T")[0];
  const time = new Date().toISOString().split("T")[1].split(".")[0];
  const agentDir = join(config.memoryBasePath, "memory", "agents", config.agentId);
  const logFile = join(agentDir, `${date}.md`);

  await mkdir(agentDir, { recursive: true });

  const logEntry = `\n## [${time}]\n${entry}\n`;
  await writeFile(logFile, logEntry, { flag: "a" });
}

async function bootContext(config: MemoryConfig): Promise<string> {
  const date = new Date().toISOString().split("T")[0];
  const agentDir = join(config.memoryBasePath, "memory", "agents", config.agentId);
  const todayFile = join(agentDir, `${date}.md`);
  const yesterdayDate = new Date(Date.now() - 86400000).toISOString().split("T")[0];
  const yesterdayFile = join(agentDir, `${yesterdayDate}.md`);

  let context = "";

  // Read recent memory
  for (const file of [todayFile, yesterdayFile]) {
    if (existsSync(file)) {
      try {
        const content = await readFile(file, "utf-8");
        context += `\n${content}`;
      } catch {
        // Ignore read errors
      }
    }
  }

  // Read shared brain
  const sharedBrainPath = join(config.memoryBasePath, "shared-brain");
  const brainFiles = ["intel-feed.json", "agent-handoffs.json", "content-vault.json"];

  for (const brainFile of brainFiles) {
    const filePath = join(sharedBrainPath, brainFile);
    if (existsSync(filePath)) {
      try {
        const content = await readFile(filePath, "utf-8");
        const data = JSON.parse(content);
        if (data.entries && Array.isArray(data.entries)) {
          context += `\n\n## ${brainFile}\n`;
          context += JSON.stringify(data.entries.slice(-3), null, 2);
        }
      } catch {
        // Ignore parse errors
      }
    }
  }

  return context;
}

// =============================================================================
// Ollama Integration
// =============================================================================

interface OllamaResponse {
  response: string;
  done: boolean;
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  eval_count?: number;
}

async function callOllama(
  model: string,
  prompt: string,
  system: string,
  temperature: number = 0.3,
  host: string = "http://localhost:11434"
): Promise<OllamaResponse> {
  const url = `${host}/api/generate`;
  
  const payload = {
    model,
    prompt,
    system,
    options: { temperature },
    stream: false,
  };

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`Ollama error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<OllamaResponse>;
}

// =============================================================================
// Session Tracking
// =============================================================================

interface QwenSession {
  sessionId: string;
  role: TentacleRole;
  model: string;
  startTime: Date;
  lastActivity: Date;
  promptCount: number;
  totalTokens: number;
}

const activeSessions = new Map<string, QwenSession>();

async function findSessionFile(workspacePath: string): Promise<string | null> {
  const qwenDir = join(workspacePath, ".qwen-tentacle");
  const sessionFile = join(qwenDir, "session.json");
  
  if (existsSync(sessionFile)) {
    return sessionFile;
  }
  return null;
}

async function readSessionFile(sessionFile: string): Promise<QwenSession | null> {
  try {
    const content = await readFile(sessionFile, "utf-8");
    const data = JSON.parse(content);
    return {
      ...data,
      startTime: new Date(data.startTime),
      lastActivity: new Date(data.lastActivity),
    };
  } catch {
    return null;
  }
}

async function writeSessionFile(sessionFile: string, session: QwenSession): Promise<void> {
  await mkdir(join(sessionFile, ".."), { recursive: true });
  await writeFile(sessionFile, JSON.stringify(session, null, 2));
}

// =============================================================================
// Agent Implementation
// =============================================================================

function createQwenTentacleAgent(): Agent {
  return {
    name: "qwen-tentacle",
    processName: "ollama",
    promptDelivery: "inline",

    getLaunchCommand(config: AgentLaunchConfig): string {
      // The actual execution happens via our wrapper script
      const role = (config.model as TentacleRole) || "coder";
      const tentacleConfig = TENTACLE_CONFIGS[role];
      
      // Build command that will be executed
      const escapedPrompt = config.prompt?.replace(/'/g, "'\\''") || "";
      const parts = [
        "python3",
        "-c",
        `'import sys; sys.path.insert(0, "skills"); from qwen_tentacles import get_tentacles, TentacleRole; t = get_tentacles(); r = t.spawn_tentacle(TentacleRole.${role.toUpper()}, "${escapedPrompt}"); print(r.response)'`,
      ];

      return parts.join(" ");
    },

    getEnvironment(config: AgentLaunchConfig): Record<string, string> {
      const env: Record<string, string> = {};
      
      // Set agent identification
      env["AO_AGENT_ID"] = config.sessionId;
      env["AO_TENTACLE_ROLE"] = config.model || "coder";
      
      // Memory configuration
      env["AO_MEMORY_BASE"] = "~/persistent-agent-memory";
      
      // Ollama configuration
      env["OLLAMA_HOST"] = "http://localhost:11434";
      
      if (config.issueId) {
        env["AO_ISSUE_ID"] = config.issueId;
      }

      return env;
    },

    detectActivity(terminalOutput: string): ActivityState {
      const lines = terminalOutput.trim().split("\n");
      const lastLine = lines[lines.length - 1]?.trim() ?? "";

      // Check for completion markers
      if (lastLine.includes("Task completed") || lastLine.includes("Done.")) {
        return "ready";
      }

      // Check for waiting markers
      if (lastLine.includes("Waiting for input") || lastLine.includes("?")) {
        return "waiting_input";
      }

      // Check for error markers
      if (lastLine.includes("Error:") || lastLine.includes("Failed:")) {
        return "blocked";
      }

      // Default to active if output is recent and substantial
      if (lines.length > 5) {
        return "active";
      }

      return "idle";
    },

    async isProcessRunning(handle: RuntimeHandle): Promise<boolean> {
      // For Qwen tentacle, we check if there's an active session
      const session = activeSessions.get(handle.id);
      if (!session) return false;

      // Check if session has been inactive for too long
      const inactiveMs = Date.now() - session.lastActivity.getTime();
      const maxInactiveMs = 30 * 60 * 1000; // 30 minutes

      return inactiveMs < maxInactiveMs;
    },

    async getActivityState(
      session: Session,
      readyThresholdMs?: number
    ): Promise<ActivityDetection | null> {
      const threshold = readyThresholdMs ?? DEFAULT_READY_THRESHOLD_MS;
      const qwenSession = activeSessions.get(session.id);

      if (!qwenSession) {
        return { state: "exited", timestamp: new Date() };
      }

      const inactiveMs = Date.now() - qwenSession.lastActivity.getTime();

      if (inactiveMs > threshold * 2) {
        return { state: "idle", timestamp: qwenSession.lastActivity };
      }

      if (inactiveMs > threshold) {
        return { state: "ready", timestamp: qwenSession.lastActivity };
      }

      return { state: "active", timestamp: qwenSession.lastActivity };
    },

    async getSessionInfo(session: Session): Promise<AgentSessionInfo | null> {
      const qwenSession = activeSessions.get(session.id);
      if (!qwenSession) return null;

      return {
        summary: `Qwen ${qwenSession.role} tentacle - ${qwenSession.promptCount} prompts, ${qwenSession.totalTokens} tokens`,
        agentSessionId: session.id,
        cost: {
          inputTokens: Math.floor(qwenSession.totalTokens * 0.7),
          outputTokens: Math.floor(qwenSession.totalTokens * 0.3),
          estimatedCostUsd: qwenSession.totalTokens * 0.00001, // Rough estimate
        },
      };
    },

    async setupWorkspaceHooks(workspacePath: string, config: WorkspaceHooksConfig): Promise<void> {
      // Create .qwen-tentacle directory
      const qwenDir = join(workspacePath, ".qwen-tentacle");
      await mkdir(qwenDir, { recursive: true });

      // Create config file
      const configPath = join(qwenDir, "config.json");
      const configData = {
        memoryBase: config.dataDir,
        hooks: {
          postTask: true,
          logKnowledge: true,
        },
      };
      await writeFile(configPath, JSON.stringify(configData, null, 2));

      // Create memory writer script
      const hookScript = `#!/usr/bin/env python3
"""Post-task hook for Qwen Tentacle agent"""
import sys
import os
from datetime import datetime

# Add skills path
sys.path.insert(0, os.path.expanduser("skills"))
from persistent_memory_skill import get_memory

memory = get_memory()
agent_id = os.environ.get("AO_AGENT_ID", "qwen-tentacle")

# Read task output from stdin
task_output = sys.stdin.read()

# Write to agent memory
memory.write_agent_memory(
    agent_id=agent_id,
    entry=f"Task completed:\\n{task_output[:500]}...",
    tags=["qwen-tentacle", "task"]
)

# Log any knowledge extracted
if "knowledge:" in task_output.lower():
    lines = task_output.split("\\n")
    for i, line in enumerate(lines):
        if "knowledge:" in line.lower():
            fact = "\\n".join(lines[i:i+3])
            memory.log_knowledge(
                fact=fact,
                category="extracted",
                source="qwen-tentacle",
                agent_id=agent_id
            )

print("Memory updated")
`;

      const hookPath = join(qwenDir, "post-task-hook.py");
      await writeFile(hookPath, hookScript);
    },

    async postLaunchSetup(session: Session): Promise<void> {
      if (!session.workspacePath) return;

      // Initialize session tracking
      const role = (session.metadata?.role as TentacleRole) || "coder";
      const qwenSession: QwenSession = {
        sessionId: session.id,
        role,
        model: TENTACLE_CONFIGS[role].model,
        startTime: new Date(),
        lastActivity: new Date(),
        promptCount: 0,
        totalTokens: 0,
      };

      activeSessions.set(session.id, qwenSession);

      // Write session file
      const sessionFile = join(session.workspacePath, ".qwen-tentacle", "session.json");
      await writeSessionFile(sessionFile, qwenSession);

      // Load boot context from memory
      const memoryConfig: MemoryConfig = {
        memoryBasePath: "~/persistent-agent-memory",
        agentId: session.id,
      };

      const context = await bootContext(memoryConfig);
      if (context) {
        // Write context to file for agent to read
        const contextFile = join(session.workspacePath, ".qwen-tentacle", "boot-context.md");
        await writeFile(contextFile, context);
      }
    },
  };
}

// =============================================================================
// Plugin Export
// =============================================================================

export function create(): Agent {
  return createQwenTentacleAgent();
}

export default { manifest, create } satisfies PluginModule<Agent>;
