# Day 17 — Idempotency and Retries

## What retry problems exist in LinkLite
POST /v1/links is not safe to retry without idempotency.
If a request times out after the DB row is created but before
the response is sent — a retry creates a duplicate link.

## Chosen strategy
Idempotency key via request header — `Idempotency-Key: <unique-value>`.
Client generates a unique key per request and sends it every time.
Server stores the result in Redis for 24 hours.
On retry with same key — server returns stored result, no new row created.

## How duplicate requests behave
Same Idempotency-Key = same response returned.
No second DB write. No duplicate short code. Safe to retry infinitely.

## How it works
1. Client sends Idempotency-Key header
2. Server checks Redis for that key
3. Key exists → return cached response immediately
4. Key missing → create link → store response in Redis with 24hr TTL

## When to revisit
If keys need to persist longer than 24 hours.
If we add user auth — keys should be scoped per user not globally.