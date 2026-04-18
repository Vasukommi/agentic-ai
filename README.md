# Agentic AI

Embedded AI action layer for SaaS products.

The product goal is to let a SaaS company embed an agent inside its own UI so its end users can complete real product tasks through natural language. The agent should translate intent into typed, validated actions and workflows, not just answer documentation questions.

Project direction and agent working rules live in [AGENTS.md](./AGENTS.md).

## Repo Layout

```text
apps/
  api/        FastAPI runtime and action execution API
  web/        Future admin/control-plane UI
docs/         Architecture notes and product decisions
packages/
  sdk-js/     Future framework-agnostic browser SDK
  react/      Future React components/hooks
```

## Backend Quick Start

```sh
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Then open:

- API: `http://127.0.0.1:8000`
- Docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

By default the API uses local SQLite at `apps/api/agentic_ai.db` so the foundation can run without Docker. Production should use Postgres through `AGENTIC_DATABASE_URL`.

```sh
cd apps/api
alembic -c alembic.ini upgrade head
```

## First Runtime Endpoints

- `GET /v1/actions` lists available action contracts.
- `POST /v1/actions` creates a persisted action contract.
- `GET /v1/actions/{action_id}` returns one action contract.
- `POST /v1/sessions` creates a short-lived bearer token for an embedded end user.
- `POST /v1/runs` validates an action request and returns either missing fields, confirmation needed, or a mocked completion.
- `GET /v1/runs` lists persisted run records.

The current runtime persists organizations, apps, actions, runs, and audit events. Tenant auth, real connector execution, and durable workflows come next.

`POST /v1/runs` and `GET /v1/runs` require `Authorization: Bearer <session_token>` from `POST /v1/sessions`.

If `AGENTIC_SESSION_SIGNING_SECRET` is configured, `POST /v1/sessions` also requires:

- `X-Agentic-Timestamp: <unix-seconds>`
- `X-Agentic-Signature: sha256=<hmac>`

The signature payload is `<timestamp>.<raw-request-body>` using HMAC-SHA256.
