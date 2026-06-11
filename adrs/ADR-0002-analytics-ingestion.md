# ADR-0002: Analytics Ingestion Strategy

## Status
Accepted

## Context
Every redirect needs to record a click event in PostgreSQL.
This write operation adds latency to the redirect path.
The redirect must feel instant — analytics can be delayed.

## Decision
Use FastAPI background tasks to record click events asynchronously.
Redirect happens immediately. Click is recorded after response is sent.

## Alternatives considered
- **Synchronous write** — click recorded before redirect returned.
  Guarantees every click is recorded but adds DB write latency to
  every redirect. Unacceptable for the hottest path in the system.
- **RabbitMQ queue** — publish click event to queue, worker consumes.
  More reliable than background tasks but adds operational complexity.
  Deferred to v2.

## Consequences

### Positive
- Redirect latency unaffected by analytics write
- Simple implementation — no external queue needed for v1
- User experience is never impacted by analytics failures

### Negative
- Click events can be lost if background task crashes
- No retry mechanism — failed clicks are gone permanently
- Eventually consistent — counts may lag slightly

## When to revisit
- If click loss rate becomes unacceptable
- When scaling to multiple app servers — background tasks
  don't share state across servers, RabbitMQ becomes necessary