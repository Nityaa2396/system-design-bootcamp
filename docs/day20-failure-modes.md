# Day 20 — Failure Modes and Resilience

## Failure 1 — Redis goes down
**What breaks:** Before fix — all redirects crash with 500.
**User impact:** Every short link stops working.
**Fix:** try/except around all Redis calls. Fall back to DB silently.
**Evidence:** Redis stopped → REDIS ERROR logged → DB fallback → 302 returned.
**Eventual consistency ok?** Yes — cache rebuilds automatically when Redis restarts.

## Failure 2 — PostgreSQL goes down
**What breaks:** Any redirect not in cache fails with 500.
**User impact:** Non-cached links fail. Cached links still work.
**Fix:** Not implemented yet. Would need circuit breaker or read replica.
**Mitigation for now:** Redis cache reduces DB dependency on hot links.

## Failure 3 — Background click task crashes
**What breaks:** Click event not recorded.
**User impact:** Nothing — redirect already happened before task runs.
**Fix:** try/except inside record_click. Log the error, move on.
**Eventual consistency ok?** Yes — losing one click is acceptable.

## Failure 4 — App server crashes
**What breaks:** All requests fail until server restarts.
**Fix:** Multiple app servers behind load balancer.
**Not implemented yet:** Single server for v1.

## Key resilience pattern learned
Wrap every external dependency in try/except.
Never let Redis or any cache layer crash your core user flow.
Degrade gracefully — slower is always better than broken.

## Failure drill results
Redis stopped → redirects fell back to DB → users unaffected ✅
Redis restarted → cache rebuilt automatically → back to full speed ✅