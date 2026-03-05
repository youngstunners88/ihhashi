/**
 * router.ts — Task Routing Engine for iHhashi Swarm
 *
 * Takes a task description (and optional file paths) and determines which
 * agent(s) should handle it. Uses a two-pass strategy:
 *   1. File-pattern matching (highest specificity wins)
 *   2. Keyword matching against the task description
 *
 * Returns a ranked list of AgentAssignment objects.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AgentAssignment {
  /** Agent identifier matching the registry in swarm.config.yaml */
  agentId: string;
  /** Human-readable agent name */
  name: string;
  /** Why this agent was selected */
  reason: string;
  /** 1 = primary, 2 = secondary reviewer, 3 = advisory */
  priority: 1 | 2 | 3;
}

export interface RoutingResult {
  /** Original task description */
  task: string;
  /** Agents assigned, ordered by priority */
  assignments: AgentAssignment[];
  /** ISO timestamp */
  routedAt: string;
  /** Which routing rules fired */
  matchedRules: string[];
}

// ---------------------------------------------------------------------------
// File-pattern routing rules
// ---------------------------------------------------------------------------

interface FilePatternRule {
  id: string;
  /** Glob-style pattern to match against affected file paths */
  pattern: RegExp;
  agents: Omit<AgentAssignment, "reason">[];
}

const FILE_PATTERN_RULES: FilePatternRule[] = [
  {
    id: "nduna-routes",
    pattern: /backend\/app\/routes\/nduna/i,
    agents: [
      { agentId: "ai-ml-lead", name: "AI/ML Lead", priority: 1 },
      { agentId: "nduna-architect", name: "Nduna Architect", priority: 2 },
    ],
  },
  {
    id: "payments-routes",
    pattern: /backend\/app\/routes\/payments/i,
    agents: [
      { agentId: "payments-engineer", name: "Payments Engineer", priority: 1 },
      { agentId: "compliance-officer", name: "Compliance Officer", priority: 2 },
    ],
  },
  {
    id: "frontend-src",
    pattern: /frontend\/src\//i,
    agents: [
      { agentId: "frontend-engineer", name: "Frontend Engineer", priority: 1 },
    ],
  },
  {
    id: "route-optimizer",
    pattern: /backend\/app\/services\/route_optimizer/i,
    agents: [
      { agentId: "logistics-engineer", name: "Logistics Engineer", priority: 1 },
      { agentId: "route-intelligence", name: "Route Intelligence", priority: 2 },
    ],
  },
];

// ---------------------------------------------------------------------------
// Keyword routing rules
// ---------------------------------------------------------------------------

interface KeywordRule {
  id: string;
  /** Pattern tested against the task description */
  pattern: RegExp;
  agents: Omit<AgentAssignment, "reason">[];
}

const KEYWORD_RULES: KeywordRule[] = [
  {
    id: "township-delivery",
    pattern: /\b(township|spaza|cash)\b/i,
    agents: [
      { agentId: "township-delivery-specialist", name: "Township Delivery Specialist", priority: 1 },
    ],
  },
  {
    id: "loadshedding",
    pattern: /\b(loadshedding|load[\s-]?shedding|offline|power)\b/i,
    agents: [
      { agentId: "loadshedding-resilience-engineer", name: "Loadshedding Resilience Engineer", priority: 1 },
    ],
  },
  {
    id: "localization",
    pattern: /\b(language|translate|i18n|zulu|xhosa)\b/i,
    agents: [
      { agentId: "localization-expert", name: "Localization Expert", priority: 1 },
    ],
  },
  {
    id: "pricing",
    pattern: /\b(price|surge|fee|cost)\b/i,
    agents: [
      { agentId: "pricing-strategist", name: "Pricing Strategist", priority: 1 },
    ],
  },
  {
    id: "community",
    pattern: /\b(reputation|badge|trust|community)\b/i,
    agents: [
      { agentId: "community-moderator", name: "Community Moderator", priority: 1 },
    ],
  },
];

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Route a task to the appropriate agent(s).
 *
 * @param task        - Natural-language task description
 * @param filePaths   - Optional list of affected file paths for pattern matching
 * @returns           - RoutingResult with ranked agent assignments
 */
export function routeTask(task: string, filePaths: string[] = []): RoutingResult {
  const assignments: AgentAssignment[] = [];
  const matchedRules: string[] = [];
  const seen = new Set<string>(); // deduplicate agent assignments

  // Pass 1: file-pattern matching
  for (const rule of FILE_PATTERN_RULES) {
    const matchingFiles = filePaths.filter((fp) => rule.pattern.test(fp));
    if (matchingFiles.length > 0) {
      matchedRules.push(`file:${rule.id}`);
      for (const agent of rule.agents) {
        if (!seen.has(agent.agentId)) {
          seen.add(agent.agentId);
          assignments.push({
            ...agent,
            reason: `File pattern matched: ${matchingFiles[0]}`,
          });
        }
      }
    }
  }

  // Also check file patterns against the task description itself
  // (users often mention paths inline)
  for (const rule of FILE_PATTERN_RULES) {
    if (rule.pattern.test(task)) {
      matchedRules.push(`file-in-task:${rule.id}`);
      for (const agent of rule.agents) {
        if (!seen.has(agent.agentId)) {
          seen.add(agent.agentId);
          assignments.push({
            ...agent,
            reason: `File path mentioned in task description`,
          });
        }
      }
    }
  }

  // Pass 2: keyword matching
  for (const rule of KEYWORD_RULES) {
    const match = task.match(rule.pattern);
    if (match) {
      matchedRules.push(`keyword:${rule.id}`);
      for (const agent of rule.agents) {
        if (!seen.has(agent.agentId)) {
          seen.add(agent.agentId);
          assignments.push({
            ...agent,
            reason: `Keyword matched: "${match[0]}"`,
          });
        }
      }
    }
  }

  // Sort: primary first, then secondary, then advisory
  assignments.sort((a, b) => a.priority - b.priority);

  return {
    task,
    assignments,
    routedAt: new Date().toISOString(),
    matchedRules,
  };
}

/**
 * Convenience: check if a task has any routing matches at all.
 */
export function hasRouting(task: string, filePaths: string[] = []): boolean {
  return routeTask(task, filePaths).assignments.length > 0;
}
