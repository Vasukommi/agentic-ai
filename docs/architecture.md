# Architecture Notes

## Product Shape

This is a hosted embedded-agent platform for SaaS companies.

- SaaS owners log into our control plane to configure actions, policies, credentials, and analytics.
- Their end users interact with the agent inside the SaaS product.
- The embedded UI is only one surface. The core product is safe task execution: guidance, actions, diagnostics, and escalation.

## Runtime Flow

1. Host SaaS embeds our SDK or mounts our React component.
2. Host backend creates a signed end-user session with tenant, user, and role context.
3. End user asks for a task in natural language.
4. Runtime maps intent to a typed action or workflow.
5. Runtime collects missing fields.
6. Runtime validates the payload against the action schema.
7. Runtime asks for confirmation when policy requires it.
8. Runtime executes the connector or workflow.
9. Runtime stores trace, audit events, and result status.

## Product Modes

- `Guide mode`: answer how-to questions and explain manual steps.
- `Action mode`: collect fields, validate payloads, confirm risky changes, and execute typed actions.
- `Diagnostic mode`: investigate a failed user task with scoped logs, traces, run history, and known issues.
- `Escalation mode`: create a high-quality support or engineering ticket with an internal evidence pack.

## Core Primitives

- `Action`: a single typed operation, usually mapped to one API call.
- `Workflow`: a multi-step process with branching, retries, and possible human approval.
- `Context fetcher`: a safe read operation used to load current user/account/product state.
- `Policy`: rules that decide visibility, permission, confirmation, and risk level.
- `Run`: one execution attempt with inputs, steps, tool calls, status, and audit trail.
- `DiagnosticRun`: one read-only investigation into a user-reported issue or failed action.
- `EvidencePack`: curated logs, trace IDs, errors, recent actions, metadata, and summaries for support/dev teams.
- `Ticket`: an external support or engineering issue created from a diagnostic run.

## UI Principle

The embedded agent must be host-controlled by default.

We should not repeat the common support-widget problem where a fixed iframe with an extreme z-index blocks save buttons, drawers, modals, or sticky action bars. The SDK should support:

- Floating widget with configurable position, offset, and z-index.
- Inline mounting into a host-provided container.
- Drawer/panel mode controlled by the host app.
- Headless mode for customers who want their own UI.
- Runtime controls like `show`, `hide`, `open`, `close`, `setOffset`, and `setZIndex`.

The host SaaS owns visual priority. Our widget should adapt to its layout, not fight it.

## Diagnostic Direction

Many SaaS issues today follow a slow path:

1. User reports that something failed.
2. Support asks questions and tries to reproduce.
3. Support escalates to engineering.
4. Engineering asks for logs, trace IDs, user ID, tenant ID, and exact steps.
5. The ticket goes back and forth before real debugging starts.

Our product should compress this flow. When a user reports a failure, the agent should be able to inspect scoped context and produce a support-ready summary.

The first version should stay read-only:

- pull related run status and error metadata
- identify user, tenant, environment, timestamp, and action
- attach trace IDs and job IDs when available
- summarize likely cause in user-safe language
- ask before creating a ticket
- attach raw logs only to the internal evidence pack, not the end-user chat

Long term, diagnostics can connect to systems like OpenSearch, Elastic, Grafana/Loki, Sentry, Jira, Zendesk, Slack, email, and databases. These should be connector-backed capabilities with strict scoping and audit logs, not unrestricted agent access.
