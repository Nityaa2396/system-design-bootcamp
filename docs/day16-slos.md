# LinkLite SLOs

## SLO 1 — Redirect Success Rate

**SLI:** Percentage of GET /{slug} requests returning 302
**Target:** 99.9% of redirects must succeed
**Why it matters:** Redirect is the core product. If this breaks,
every short link using LinkLite is broken for every user.
**Alert or dashboard?** 3am alert — users are broken right now

## SLO 2 — Redirect Latency

**SLI:** p95 latency of GET /{slug} in milliseconds
**Target:** p95 under 50ms (cache hit baseline: 3.69ms)
**Why it matters:** Slow redirects feel like broken links to users.
At scale a 2 second redirect is unacceptable.
**Alert or dashboard?** Dashboard — degraded but not broken.
Page a human if p95 exceeds 500ms consistently.

## SLO 3 — Create Link Success Rate

**SLI:** Percentage of POST /v1/links returning 201
**Target:** 99.5% of create requests must succeed
**Why it matters:** Users can't create links. Lower target than
redirects because creating is less frequent than clicking.
**Alert or dashboard?** Dashboard unless it drops below 95%
then it becomes a 3am alert.

## What pages a human at 3am

- Redirect success rate drops below 99%
- Redirect p95 latency exceeds 500ms for 5 min straight
- App returns 500 errors on any endpoint

## What shows on dashboard only

- Cache hit rate dropping
- Create link success rate between 99% and 99.5%
- Redirect latency between 50ms and 500ms

## What gets ignored

- Single one-off errors
- Latency spikes under 10 seconds
- Rate limit 429s — those are working as intended
