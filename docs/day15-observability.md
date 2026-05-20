# Day 15 — Observability

## What logs are for

Recording what happened on each individual request.
Useful for debugging a specific failure after it happens.

## What metrics are for

Measuring patterns over time — request count, error rate, latency.
Useful for spotting trends before they become incidents.

## What traces are for

Following one request through the entire system end to end.
Useful for finding where time is being spent across services.

## What our logs now capture

- request_id — unique ID per request for tracing
- method — GET/POST/DELETE
- path — which endpoint was hit
- status — response code
- duration_ms — how long it took

## Evidence from LinkLite

Cache miss redirect: 25.5ms — hits PostgreSQL
Cache hit redirect: 3.69ms — hits Redis only
Cache is 7x faster than DB on the redirect path.

## Questions our telemetry can now answer

- How long is each request taking?
- Which endpoints are slow?
- Are we getting more errors over time?
- Is the cache actually helping?
