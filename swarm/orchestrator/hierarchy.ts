/**
 * hierarchy.ts — Team Hierarchy & Agent Registry for iHhashi Swarm
 *
 * Defines the three-tier swarm structure:
 *   Tier 0: Governance (Paperclip) — budget, approvals, auditing
 *   Tier 1: Domain Leads — strategic ownership of major domains
 *   Tier 2: Specialists — execution across engineering, SA-specific, quality
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  tier: 0 | 1 | 2;
  division: string;
  personalityFile: string;
  scope: string[];
  skills?: string[];
  reportsTo?: string;
}

export interface LeadInfo {
  id: string;
  name: string;
  scope: string[];
  skills: string[];
  specialists: string[];
}

export interface SwarmHierarchy {
  governance: { name: string; responsibilities: string[] };
  leads: LeadInfo[];
  specialists: AgentInfo[];
}

// ---------------------------------------------------------------------------
// Agent Registry
// ---------------------------------------------------------------------------

const AGENT_REGISTRY: AgentInfo[] = [
  // Tier 1: Domain Leads
  {
    id: "platform-architect",
    name: "Platform Architect",
    description: "System design, infrastructure, technical standards",
    tier: 1,
    division: "Leadership",
    personalityFile: "swarm/agents/operations/platform-architect.md",
    scope: ["backend/app/main.py", "docker-compose.yml", ".github/", "backend/app/config.py"],
    skills: ["deep-architecture", "memory", "orchestration"],
  },
  {
    id: "ai-ml-lead",
    name: "AI/ML Lead",
    description: "AI systems, Nduna chatbot, route intelligence, pricing ML",
    tier: 1,
    division: "Leadership",
    personalityFile: "swarm/agents/operations/ai-ml-lead.md",
    scope: ["backend/app/routes/nduna*.py", "backend/app/routes/pricing_intelligence.py"],
    skills: ["rag", "middleware", "memory"],
  },
  {
    id: "delivery-ops-lead",
    name: "Delivery Operations Lead",
    description: "Route memory, driver matching, multi-modal delivery, community",
    tier: 1,
    division: "Leadership",
    personalityFile: "swarm/agents/operations/delivery-ops-lead.md",
    scope: ["backend/app/routes/trips.py", "backend/app/routes/community.py", "backend/app/services/matching.py"],
    skills: ["langgraph-state-graphs", "persistence"],
  },
  {
    id: "growth-lead",
    name: "Growth Lead",
    description: "User acquisition, referrals, Hashi Coins, marketing",
    tier: 1,
    division: "Leadership",
    personalityFile: "swarm/agents/product/growth-lead.md",
    scope: ["backend/app/routes/referrals.py", "backend/app/routes/customer_rewards.py", "marketing/"],
    skills: ["langchain-fundamentals"],
  },

  // Tier 2: Engineering Division
  {
    id: "backend-engineer",
    name: "Backend Engineer",
    description: "FastAPI routes, MongoDB models, Pydantic schemas",
    tier: 2,
    division: "Engineering",
    personalityFile: "swarm/agents/engineering/engineering-backend-architect.md",
    scope: ["backend/"],
    reportsTo: "platform-architect",
  },
  {
    id: "frontend-engineer",
    name: "Frontend Engineer",
    description: "React components, Zustand stores, TypeScript, Tailwind",
    tier: 2,
    division: "Engineering",
    personalityFile: "swarm/agents/engineering/engineering-frontend-developer.md",
    scope: ["frontend/src/"],
    reportsTo: "platform-architect",
  },
  {
    id: "mobile-engineer",
    name: "Mobile Engineer",
    description: "Capacitor/Android, PWA, offline-first patterns",
    tier: 2,
    division: "Engineering",
    personalityFile: "swarm/agents/engineering/engineering-mobile-app-builder.md",
    scope: ["frontend/android/", "frontend/capacitor.config.ts"],
    reportsTo: "platform-architect",
  },
  {
    id: "logistics-engineer",
    name: "Logistics Engineer",
    description: "OR-Tools optimization, delivery fees, driver matching",
    tier: 2,
    division: "Engineering",
    personalityFile: "swarm/agents/engineering/logistics-engineer.md",
    scope: ["backend/app/services/route_optimizer.py", "backend/app/services/matching.py", "backend/app/services/delivery_fee.py"],
    reportsTo: "delivery-ops-lead",
  },
  {
    id: "payments-engineer",
    name: "Payments Engineer",
    description: "Paystack/Yoco integration, payouts, Hashi Coins ledger",
    tier: 2,
    division: "Engineering",
    personalityFile: "swarm/agents/engineering/payments-engineer.md",
    scope: ["backend/app/services/paystack.py", "backend/app/routes/payments.py", "backend/app/routes/refunds.py"],
    reportsTo: "platform-architect",
  },
  {
    id: "devops-engineer",
    name: "DevOps Engineer",
    description: "Docker, CI/CD, deployment, monitoring",
    tier: 2,
    division: "Engineering",
    personalityFile: "swarm/agents/engineering/engineering-devops-automator.md",
    scope: ["docker-compose.yml", ".github/workflows/", "render.yaml", "netlify.toml"],
    reportsTo: "platform-architect",
  },

  // Tier 2: SA-Specific Division
  {
    id: "localization-expert",
    name: "Localization Expert",
    description: "11 SA languages, cultural validation, i18n management",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/localization-expert.md",
    scope: ["backend/app/i18n/", "frontend/src/lib/"],
    reportsTo: "ai-ml-lead",
  },
  {
    id: "compliance-officer",
    name: "POPIA/CPA Compliance Officer",
    description: "Data protection, consumer rights, legal review",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/compliance-officer.md",
    scope: ["backend/app/models/user.py", "backend/app/models/verification.py", "legal/"],
    reportsTo: "platform-architect",
  },
  {
    id: "township-delivery-specialist",
    name: "Township Delivery Specialist",
    description: "Informal settlement navigation, spaza shops, cash-on-delivery",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/township-delivery.md",
    scope: ["backend/app/services/route_optimizer.py", "backend/app/models/delivery.py"],
    reportsTo: "delivery-ops-lead",
  },
  {
    id: "loadshedding-resilience-engineer",
    name: "Load-shedding Resilience Engineer",
    description: "Offline-first, WebSocket reconnection, state recovery",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/loadshedding-resilience.md",
    scope: ["backend/app/routes/websocket.py", "backend/app/core/redis_client.py"],
    reportsTo: "platform-architect",
  },
  {
    id: "pricing-strategist",
    name: "Pricing Strategist",
    description: "Dynamic pricing, surge during loadshedding, fee optimization",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/pricing-strategist.md",
    scope: ["backend/app/routes/pricing_intelligence.py", "backend/app/services/delivery_fee.py"],
    reportsTo: "ai-ml-lead",
  },
  {
    id: "community-moderator",
    name: "Community Moderator",
    description: "Driver reputation, insight validation, anti-fraud",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/community-moderator.md",
    scope: ["backend/app/routes/community.py", "backend/app/models/community.py"],
    reportsTo: "delivery-ops-lead",
  },
  {
    id: "nduna-architect",
    name: "Nduna Conversation Architect",
    description: "Chatbot evolution, multilingual prompts, function calling",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/nduna-architect.md",
    scope: ["backend/app/routes/nduna.py", "backend/app/routes/nduna_intelligence.py"],
    reportsTo: "ai-ml-lead",
  },
  {
    id: "route-intelligence",
    name: "Route Intelligence Analyst",
    description: "Route memory pipeline, ETA accuracy, community validation",
    tier: 2,
    division: "SA-Specific",
    personalityFile: "swarm/agents/sa-specific/route-intelligence.md",
    scope: ["backend/app/models/route_memory.py", "backend/app/routes/route_memory.py"],
    reportsTo: "delivery-ops-lead",
  },

  // Tier 2: Quality Division
  {
    id: "qa-engineer",
    name: "QA Engineer",
    description: "Testing, coverage, Playwright E2E, Vitest",
    tier: 2,
    division: "Quality",
    personalityFile: "swarm/agents/quality/qa-engineer.md",
    scope: ["backend/tests/", "frontend/src/__tests__/", "frontend/e2e/"],
    reportsTo: "platform-architect",
  },
  {
    id: "security-auditor",
    name: "Security Auditor",
    description: "Auth flows, JWT, rate limiting, POPIA security",
    tier: 2,
    division: "Quality",
    personalityFile: "swarm/agents/quality/security-auditor.md",
    scope: ["backend/app/routes/auth.py", "backend/app/config.py"],
    reportsTo: "platform-architect",
  },
];

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function getAgentRegistry(): AgentInfo[] {
  return AGENT_REGISTRY;
}

export function getAgent(id: string): AgentInfo | undefined {
  return AGENT_REGISTRY.find((a) => a.id === id);
}

export function getHierarchy(): SwarmHierarchy {
  const leads = AGENT_REGISTRY.filter((a) => a.tier === 1);
  const specialists = AGENT_REGISTRY.filter((a) => a.tier === 2);

  return {
    governance: {
      name: "Paperclip Governor",
      responsibilities: [
        "Budget tracking (R500/day, R50/task)",
        "Approval gates for sensitive operations",
        "Audit logging for POPIA compliance",
        "Heartbeat monitoring (5-minute intervals)",
        "LLM cost tracking across Groq/OpenAI/Anthropic",
      ],
    },
    leads: leads.map((l) => ({
      id: l.id,
      name: l.name,
      scope: l.scope,
      skills: l.skills || [],
      specialists: specialists
        .filter((s) => s.reportsTo === l.id)
        .map((s) => s.id),
    })),
    specialists,
  };
}

export function getLeadFor(agentId: string): AgentInfo | undefined {
  const agent = getAgent(agentId);
  if (!agent?.reportsTo) return undefined;
  return getAgent(agent.reportsTo);
}

export function getEscalationPath(agentId: string): AgentInfo[] {
  const path: AgentInfo[] = [];
  let current = getAgent(agentId);
  while (current?.reportsTo) {
    const lead = getAgent(current.reportsTo);
    if (lead) path.push(lead);
    current = lead;
  }
  return path;
}

export function getAgentsByDivision(division: string): AgentInfo[] {
  return AGENT_REGISTRY.filter((a) => a.division === division);
}

export function getAgentsForScope(filePath: string): AgentInfo[] {
  return AGENT_REGISTRY.filter((a) =>
    a.scope.some((s) => filePath.includes(s.replace("*", "")))
  );
}
