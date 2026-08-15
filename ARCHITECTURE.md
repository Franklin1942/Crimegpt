# CrimeGPT Architecture

## Overview

CrimeGPT is a two-tier application: a FastAPI backend exposing a JSON API under `/api`, and a
Next.js (App Router) frontend that consumes it from the browser with a bearer token.

```
Browser ──JWT──▶ Next.js (3000) ──fetch──▶ FastAPI (8000) ──SQLAlchemy──▶ PostgreSQL
                                              │
                                              ├── AI engine (OpenAI ▸ rule-based fallback)
                                              ├── Document text extraction (pypdf/docx/OCR)
                                              └── ReportLab charge-sheet PDF
```

## Backend

| Layer | Location | Responsibility |
|-------|----------|----------------|
| API routers | `backend/app/api/` | HTTP surface, validation, RBAC dependencies |
| Schemas | `backend/app/schemas/` | Pydantic request/response contracts |
| Models | `backend/app/models/` | SQLAlchemy 2.0 ORM entities |
| Services | `backend/app/services/` | AI analysis, legal intelligence, copilot, PDF reports, text extraction |
| Core | `backend/app/core/` | Settings, JWT/password hashing, dependencies, audit helper |
| DB | `backend/app/db/` | Engine, session factory, `init_db()` |

### Authentication & RBAC

`POST /api/auth/login` returns a JWT (`sub` = username, `role` = user role). `get_current_user`
resolves the token to a `User`; `require_roles(...)` restricts endpoints:

- `administrator` — user management, case deletion, audit log
- `investigating_officer` — case create/update, uploads, analysis
- `cyber_analyst` — read access, analysis, copilot

### AI engine

`services/ai_service.analyze_text` calls OpenAI when `OPENAI_API_KEY` is set and falls back to a
deterministic rule-based pipeline on any error:

1. keyword-scored crime classification,
2. regex entity extraction (emails, mobiles, IPs, URLs, accounts, UPI IDs, amounts),
3. sentence/date timeline building,
4. entity-driven investigation recommendations,
5. BNS / IT Act section mapping from `services/legal_service`.

The same fallback pattern backs the Investigator Copilot (`services/chat_service`), which serves
offline procedural playbooks (fund freeze, CDR, seizure, charge sheet).

### Data model

`users 1─* cases 1─* documents 1─1 document_analyses`, plus `chat_sessions 1─* chat_messages`,
`notifications` and `audit_logs`. Cascade deletes flow from a case to its documents and analyses.
`database/schema.sql` mirrors these tables for a managed PostgreSQL deployment; `init_db()`
creates them automatically otherwise.

## Frontend

- `src/app/login` — public login page with demo accounts.
- `src/app/(app)/*` — authenticated route group; its layout redirects to `/login` when no session.
- `src/contexts/AuthContext.tsx` — token persistence in `localStorage`, `/auth/me` bootstrap.
- `src/lib/api.ts` — typed fetch wrapper that attaches the bearer token and normalises errors.
- Pages: dashboard (Recharts analytics), cases list/create, case detail (uploads, AI findings,
  evidence checklist, charge-sheet download), copilot, audit log.

## Deployment

`docker-compose.yml` runs PostgreSQL, the backend image (uvicorn) and the frontend image
(Next.js standalone output). Uploads are stored on a named volume; secrets come from the
environment (`SECRET_KEY`, `OPENAI_API_KEY`).
