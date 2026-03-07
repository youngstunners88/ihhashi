# iHhashi Swarm - AI Development Orchestration

## Project Context
iHhashi is South Africa's #1 food delivery platform. This swarm directory contains the parallel AI development orchestration system that coordinates multiple specialized agents to build, maintain, and evolve the platform.

## Architecture
- **Backend**: FastAPI + MongoDB + Redis at `/backend/`
- **Frontend**: React 18 + Vite + TypeScript + Tailwind at `/frontend/`
- **AI**: Nduna chatbot (Groq LLM, 7 SA languages) at `backend/app/routes/nduna.py`
- **Real-time**: WebSocket tracking at `backend/app/routes/websocket.py`
- **Payments**: Paystack + Yoco at `backend/app/services/paystack.py`

## Swarm Components

### Paperclip (Governance Layer)
Located at `swarm/paperclip/`. Handles budget tracking, approval gates, audit logging, and heartbeat monitoring. NOT a decision-maker -- it wraps around agents as infrastructure.

### LangChain Skills (Toolkit)
Located at `swarm/skills/langchain-skills/`. Provides RAG, state graphs, memory, and orchestration capabilities that domain lead agents consume.

### Agency Agents (Personalities)
Located at `swarm/agents/`. 55+ base personalities from upstream plus 8 custom SA-specific agents. Activated on-demand (1-3 per task), not running simultaneously.

### Orchestrator (Unified Entry Point)
Located at `swarm/orchestrator/`. TypeScript CLI that routes tasks to agents, builds codebase context, and manages communication channels.

## SA-Specific Agents
These agents encode domain knowledge unique to South African delivery:
- **Localization Expert** - 11 official languages, cultural adaptation
- **POPIA/CPA Compliance Officer** - Data protection, consumer rights
- **Township Delivery Specialist** - Informal settlement navigation
- **Load-shedding Resilience Engineer** - Offline-first, power outage handling
- **Pricing Strategist** - ZAR pricing, surge during loadshedding
- **Community Moderator** - Driver reputation system
- **Nduna Conversation Architect** - Chatbot evolution
- **Route Intelligence Analyst** - Route memory quality

## Key Commands
```bash
bun swarm/orchestrator/index.ts task "Add Sepedi language support"
bun swarm/orchestrator/index.ts agents
bun swarm/orchestrator/index.ts budget
bun swarm/orchestrator/index.ts squad "Implement cash-on-delivery for townships"
```

## Budget Limits
- Daily: R500 ZAR
- Per-task: R50 ZAR
- Approval required for: payment changes, DB migrations, production deploys, user data model changes
