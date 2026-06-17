# Day 24 — Notification Service SLOs + Abuse Controls

## SLOs

### SLO 1 — Delivery Success Rate
**SLI:** Percentage of notifications delivered successfully
**Target:** 99.5% delivered within 30 seconds
**Alert or dashboard?** 3am alert if drops below 99%

### SLO 2 — Delivery Latency
**SLI:** p95 time from request received to notification sent
**Target:** p95 under 30 seconds
**Alert or dashboard?** Dashboard — page if exceeds 5 minutes

### SLO 3 — Dead Letter Queue Size
**SLI:** Number of messages in dead letter queue
**Target:** Under 100 messages at any time
**Alert or dashboard?** Dashboard — page if exceeds 1000

## Abuse controls

### Per-user send limit
Max 10 notifications per user per hour per channel.
Redis counter per user per channel with 1hr TTL.
Exceeding limit returns 429 Too Many Requests.

### Per-service budget limit
Each calling service has a daily notification budget.
Payment service: 100k/day. Marketing service: 50k/day.
Prevents one service from monopolizing the system.

### Provider circuit breaker
If provider fails 5 times in 60 seconds → circuit trips.
Requests automatically routed to backup provider.
After 30 second cooldown → circuit resets → try primary again.

## 5 security risks + mitigations

| Risk | Mitigation |
|---|---|
| Service sends unlimited notifications | Per-service rate limit |
| User spammed across all channels | Per-user send limit per channel |
| Provider credentials exposed | Store in secrets manager not .env |
| Message content not validated | Sanitize input, max message length |
| Dead letter queue grows indefinitely | Alert at 1000 messages, auto-archive at 10000 |