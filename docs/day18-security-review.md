# Day 18 — API Security Review

## Risk 1 — Broken Object Level Authorization
**Problem:** Anyone can access any link by changing the ID in the URL.
No check that the link belongs to the requesting user.
**Mitigation:** Add authentication + ownership check before returning
link details. Known gap — LinkLite has no auth in v1.

## Risk 2 — Broken Authentication
**Problem:** Zero authentication on any endpoint. Anyone can create,
delete, or view any link.
**Mitigation:** Add API key authentication on create/delete endpoints.
Every request must include Authorization: Bearer <key> header.
Return 401 if missing or invalid.

## Risk 3 — Unrestricted Resource Consumption
**Problem:** Stats endpoint has no rate limit. Someone can call
GET /v1/links/{id}/stats millions of times and slow down the DB.
**Mitigation:** Apply same Redis rate limiting already built for
create endpoint. Enforce pagination — never return unlimited rows.

## Risk 4 — Security Misconfiguration
**Problem:** .env file contains DB credentials and Redis URL.
If committed to GitHub anyone can access the database.
FastAPI auto-generates /docs endpoint exposing entire API publicly.
**Mitigation:** .env added to .gitignore today. Disable /docs
in production by setting docs_url=None in FastAPI config.

## Risk 5 — Improper Inventory Management
**Problem:** Test or debug endpoints left running in production
are accessible to attackers who scan for common paths.
**Mitigation:** Keep inventory of all active endpoints. Remove
test endpoints before deploying. Never expose admin endpoints
without authentication.

## Summary
Most critical right now: Risk 4 — fixed today with .gitignore.
Next priority: Risk 2 — add API key auth before any public deployment.