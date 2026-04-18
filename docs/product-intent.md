# Product Intent

This document captures product direction that should influence architecture decisions even before the features are built.

## Core Belief

Modern SaaS products are powerful but operationally complex. Users struggle in three ways:

- They do not know how to complete a task manually.
- They know what they want, but do not want to navigate forms and workflows.
- Something failed, and they do not know what happened or how to report it usefully.

Our product should support all three.

## Product Modes

### Guide Mode

The user asks how to do something manually.

Example:

```text
How do I invite a user?
```

The agent should answer with product-specific steps and offer to do it if an action exists.

### Action Mode

The user asks the agent to perform a task.

Example:

```text
Invite john@example.com as an admin.
```

The agent should map the request to a typed action, collect missing fields, validate inputs, ask for confirmation when required, execute safely, and store an audit trail.

### Diagnostic Mode

The user reports that something failed.

Example:

```text
My report export failed.
```

The agent should inspect allowed diagnostic context, identify related runs/logs/traces, summarize the issue, and ask whether to create a support ticket.

### Escalation Mode

The agent cannot fix the issue directly or the issue appears genuine.

It should create a high-quality support or engineering ticket with:

- user-safe summary
- internal technical summary
- user ID and tenant/workspace ID
- timestamp and environment
- failed action or feature
- run ID, trace ID, job ID, request ID where available
- relevant redacted logs
- recent user steps
- linked conversation

The user should not see raw logs or sensitive internals.

## Setup Philosophy

Customer setup must feel closer to:

```text
Connect systems. Review detected capabilities. Enable safe actions. Embed agent.
```

It must not feel like:

```text
Manually build an entire agent platform from scratch inside our dashboard.
```

To support this, the product should eventually include:

- OpenAPI import for customer SaaS APIs
- connector marketplace for common systems
- docs/help-center ingestion
- guided action review
- sandbox test mode
- generated action suggestions
- policy and approval templates

## Connector Direction

The connector layer should be MCP-like in spirit: systems expose typed capabilities that the runtime can safely use.

Potential connector categories:

- customer REST/OpenAPI API
- Slack
- Jira
- Zendesk
- email
- docs/help centers
- Postgres/MySQL read-only
- OpenSearch/Elastic
- Grafana/Loki
- Sentry

Connectors should expose capabilities. Admins should enable actions. The agent should only see what policies allow.

## Diagnostic Product Wedge

A strong early wedge may be:

```text
Embedded AI support engineer for SaaS apps.
```

The immediate value is not replacing developers. The value is creating developer-ready bug reports automatically.

Current painful flow:

```text
User reports issue -> support asks questions -> support escalates -> developer asks for logs -> debugging starts late.
```

Target flow:

```text
User reports issue -> agent gathers context -> agent creates evidence-backed ticket -> support/dev starts with useful data.
```

This wedge is concrete, valuable, and aligned with the broader action-agent platform.

## Long-Term Direction

The future product can move from:

1. guide the user
2. execute approved actions
3. diagnose failures
4. create evidence-backed tickets
5. suggest fixes
6. automate safe remediations

Do not start at step 6. Build the runtime and trust layer first.
