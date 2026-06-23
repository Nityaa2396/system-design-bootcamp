# Day 29 — Fresh Design Drill: Pastebin

## What I got right
- 3 functional requirements — create, read, expire
- 3 non-functional requirements — latency, scalability, privacy
- API endpoints — POST/GET/DELETE /v1/pastes
- Schema — UUID, TEXT content, short_code, timestamps, is_private
- Cache key format — paste:{short_code} with 1hr TTL
- Async view count increment — same pattern as LinkLite clicks
- Redis down → fallback to PostgreSQL

## What I missed or got wrong
- Used int instead of UUID for id — guessable IDs are a security risk
- Forgot max content size limit — no size cap = storage abuse risk
- Expiry cleanup needs a background job — doesn't happen automatically
- Called the table "links" initially — carried over LinkLite terminology

## What still feels shaky
- Background job scheduling — how do you run a job every hour in production?
- Privacy implementation — how does "unlisted" actually work technically?

## Key insight
The same framework transfers. Requirements → API → schema → cache → 
async → failure modes. Different system, same thinking process.
Pastebin is simpler than LinkLite because there's no redirect — 
just store and retrieve text. The hard part is content size limits 
and expiry management.