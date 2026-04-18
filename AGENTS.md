# Agentic AI Development Guide

## Mission

Build an embedded AI action layer for SaaS products.

The buyer is the SaaS company. The user is their customer inside their product. Our agent helps that end user complete real product tasks through natural language while respecting the host SaaS permissions, policies, and UI.

This is not a generic chatbot, support inbox, or documentation-only RAG bot. The core product is safe, typed, auditable task execution across actions, guidance, and diagnostics.

## Product North Star

Let a SaaS company add an in-product agent that can:

- understand an end user's intent
- load relevant user, tenant, and product context
- collect missing information
- map the task to a typed action or workflow
- validate every payload before execution
- require approval for risky changes
- call the SaaS owner's APIs safely
- investigate failed tasks with scoped diagnostic context
- escalate issues with evidence when automation cannot solve them
- show progress and results inside the host UI
- leave a complete audit trail

If a feature does not improve this loop, defer it.

## Non-Goals

- Do not build a Chatwoot clone.
- Do not build a generic customer-support helpdesk.
- Do not make RAG the center of the product.
- Do not let the LLM invent arbitrary API calls or payloads.
- Do not rely on leaked, proprietary, or copied agent prompts/code as source material.
- Do not ship a widget that assumes bottom-right placement and maximum z-index are always acceptable.

## Stack Direction

- Backend/runtime: FastAPI
- Contracts and validation: Pydantic
- Database: Postgres
- ORM: SQLAlchemy 2.0 or SQLModel
- Cache/queue: Redis
- Agent/workflow layer: LangGraph or OpenAI Agents SDK Python behind our own abstraction
- Durable workflows later: Temporal if long-running workflows and approvals demand it
- Admin UI: Next.js
- Embedded SDK: TypeScript browser SDK plus React package

Keep the backend agent/runtime in Python. Keep UI and embed packages in TypeScript.

## Core Architecture

Use these primitives consistently:

- `Action`: one typed operation, usually mapped to one external API call.
- `Workflow`: a multi-step process with branching, retries, and possible approval pauses.
- `ContextFetcher`: a safe read operation that loads user/account/product state.
- `Policy`: rules for visibility, permission, risk, confirmation, and execution.
- `Run`: one execution attempt with inputs, steps, status, result, and audit trail.
- `Connector`: customer-specific API integration and credential boundary.
- `DiagnosticRun`: a read-only investigation of a failed user task or reported issue.
- `EvidencePack`: scoped logs, traces, run data, errors, and metadata attached to an escalation.

The action contract is the source of truth. Prompts can help translate intent, but schemas, policies, and runtime checks decide what can execute.

## Execution Loop

For every meaningful feature, think through this loop before coding:

1. Who is the actor: SaaS admin, end user, or our operator?
2. What tenant/workspace context is required?
3. What action or workflow is being enabled?
4. What fields are required, optional, sensitive, or constrained?
5. What permissions and approvals are required?
6. What should be logged for audit and debugging?
7. How does the host SaaS control the UI placement and behavior?
8. If this fails, what diagnostic context would support or engineering need?

Then implement the smallest happy-path version that validates the architecture.

## Quality Bar

- Prefer clear contracts over clever prompts.
- Prefer typed data over freeform strings.
- Prefer explicit policies over hidden assumptions.
- Prefer small vertical slices over broad abstractions.
- Keep execution auditable from day one.
- Make failure states understandable to the end user and the SaaS admin.
- Capture enough structured context to create useful support tickets without exposing raw logs to end users.
- Avoid unnecessary defensive programming, but never skip security and authorization checks.

## Embedded UI Rules

The host SaaS owns layout priority. Our SDK must adapt.

Required integration modes:

- `floating`: configurable position, offset, and z-index
- `inline`: render into a host-provided container
- `drawer`: controlled by the host app
- `headless`: customer builds their own UI on our APIs

Do not hardcode an extreme z-index. Do not assume bottom-right is safe. Provide runtime controls like `show`, `hide`, `open`, `close`, `setOffset`, and `setZIndex`.

## Security Rules

- Never execute writes without validating against an action schema.
- Never trust browser-provided identity or permissions directly.
- Use short-lived signed sessions from the host backend for end-user context.
- Store customer credentials server-side only.
- Keep destructive and billing-related actions approval-gated by default.
- Record every external action attempt with inputs, actor, status, and result.
- Keep diagnostic access read-only by default.
- Scope logs, traces, and database reads by tenant/user/session whenever possible.
- Redact secrets and sensitive data before storing or attaching evidence.

## Planning Discipline

Before large changes, write a short plan that states:

- current goal
- files/modules involved
- smallest useful outcome
- verification command or smoke test

During implementation:

- inspect existing code before changing it
- keep changes focused
- avoid speculative abstractions
- update docs when a decision changes the product direction

After implementation:

- run the narrowest useful verification
- summarize what changed and what remains risky

## Current Milestones

1. Establish FastAPI runtime with action contracts and mocked runs.
2. Add persistence for organizations, apps, actions, runs, and audit events.
3. Add signed end-user sessions from host SaaS backends.
4. Add connector execution for one mocked external SaaS API.
5. Add basic embedded SDK with host-controlled placement.
6. Add admin UI for configuring actions and viewing runs.
7. Add workflow/approval support.
8. Add diagnostic runs and evidence packs for failed actions.
9. Add ticket/escalation connectors such as Jira, Zendesk, or Slack.
10. Add agent intent mapping once action execution and diagnostics are reliable.

Build in this order. The agent should not become the foundation until the action runtime is safe.
