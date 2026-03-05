# iHhashi Swarm Commander Skill

## Description
Dynamic orchestration skill that leads and coordinates the iHhashi Swarm - a parallel AI development force for South Africa's #1 delivery platform.

## When to Use
- User asks to "deploy the swarm", "use the swarm", or "swarm task"
- Multi-agent coordination is needed for complex features
- Task spans multiple domains (backend + frontend + mobile)
- SA-specific expertise is required (township delivery, loadshedding, POPIA)

## Swarm Hierarchy

### Tier 0: Governance (Paperclip)
Budget control, approval gates, audit logging. Config at `swarm/paperclip/`.

### Tier 1: Domain Leads
| Lead | Scope | LangChain Skill |
|------|-------|-----------------|
| Platform Architect | System design, Docker, CI/CD | Deep Architecture |
| AI/ML Lead | Nduna chatbot, route intelligence | RAG + Middleware |
| Delivery Ops Lead | Routes, matching, multi-modal | LangGraph State |
| Growth Lead | Referrals, Hashi Coins, marketing | Fundamentals |

### Tier 2: Specialists (22+ agents)
See `swarm/agents/` for full roster including 8 SA-specific agents.

## Task Routing Rules

When receiving a task, route based on:

### File Pattern Matching
- `backend/app/routes/nduna*` → AI/ML Lead + Nduna Architect
- `backend/app/routes/payments*` → Payments Engineer + Compliance Officer (APPROVAL REQUIRED)
- `backend/app/services/route_optimizer*` → Logistics Engineer + Route Intelligence
- `backend/app/models/user*` → Backend Engineer + Compliance Officer
- `frontend/src/**` → Frontend Engineer
- `backend/app/i18n/*` → Localization Expert

### Keyword Matching
- township, spaza, informal, cash → Township Delivery Specialist
- loadshedding, offline, power, reconnect → Loadshedding Resilience Engineer
- language, translate, zulu, xhosa, sotho → Localization Expert + Nduna Architect
- price, surge, fee, delivery cost → Pricing Strategist
- reputation, badge, trust, community → Community Moderator
- security, popia, compliance, audit → Compliance Officer
- test, qa, coverage, playwright → QA Engineer

### Approval Gates (require human confirmation)
- Any change to `backend/app/routes/payments*` or `backend/app/services/paystack*`
- Any change to `backend/app/models/user.py` or verification models
- Database migration scripts
- Docker/deployment configuration changes
- Production environment changes

## Squad Formation
For complex cross-domain tasks, form a temporary squad:
1. Identify primary domain → assign Domain Lead as squad leader
2. Identify secondary domains → assign specialist workers
3. If touches payments/user data → add Compliance Officer to squad
4. If touches i18n → add Localization Expert to squad
5. Each squad member works on their scope in parallel
6. Squad leader reviews and integrates

## Context Loading
Before executing, load relevant context from:
- `swarm/context/backend-map.json` - API endpoint registry
- `swarm/context/frontend-map.json` - Component hierarchy
- `swarm/context/model-schema.json` - MongoDB model schemas
- `swarm/context/api-surface.json` - Full API surface

## Budget Tracking
- Daily limit: R500 ZAR
- Per-task limit: R50 ZAR
- Track token usage per agent per task
- Alert at 80% budget threshold
- Log all costs to `swarm/state/budget.json`

## Example Workflows

### Simple Task: "Fix Nduna Zulu greeting"
→ Route: Nduna Architect (primary) + Localization Expert (review)
→ Context: nduna.py, i18n/locales/
→ Gate: None
→ Budget: Standard

### Complex Task: "Add cash-on-delivery for township areas"
→ Squad: Delivery Ops Lead (leader)
  - Township Delivery Specialist (primary)
  - Payments Engineer (payment logic)
  - Compliance Officer (CPA review)
  - Frontend Engineer (checkout UI)
  - Mobile Engineer (offline payment flow)
→ Context: payments.py, delivery.py, order.py, route_optimizer.py
→ Gate: APPROVAL REQUIRED (payment system change)
→ Budget: Elevated

### System Task: "Prepare for Stage 6 loadshedding"
→ Squad: Platform Architect (leader)
  - Loadshedding Resilience Engineer (primary)
  - Backend Engineer (Redis durability)
  - Frontend Engineer (offline UI)
  - Mobile Engineer (battery awareness)
→ Context: websocket.py, redis_client.py, frontend service workers
→ Gate: None (defensive measure)
→ Budget: Standard
