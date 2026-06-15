# system-design-bootcamp

A 30-day hands-on system design bootcamp — documenting the learning journey week by week.

**Goal:** Go from knowing how to code to being able to design, document, and explain real backend systems.

**Capstone project:** LinkLite — a URL shortener built with real production design thinking.

**Stack:** FastAPI · PostgreSQL · Redis · RabbitMQ · Docker Compose · Mermaid

---

## Week 1 — Learning the Language of System Design

_Status: ✅ Completed_

No code this week. The focus was on thinking and writing like a system designer.
Every day produced a real design document for LinkLite.

---

### Day 1 — Requirements Thinking

**What I learned:** The difference between functional and non-functional requirements.
Functional = what a system does. Non-functional = how well it does it.

**Key insight:** Always state your assumptions before building anything.
A URL shortener with no rate limiting = one user can crash your entire database.

**Deliverable:** `docs/01-requirements.md`

- Problem statement, functional and non-functional requirements
- 5 PM questions before building (slug conflicts, abuse prevention, TTL, broken destinations, rate limits)
- 3 hidden constraints teams forget (click event storage cost, redirect uptime, predictable short codes = security risk)

---

### Day 2 — REST API Design

**What I learned:** REST is a specific style of API that uses HTTP methods,
URLs as resource names, and status codes as contracts.

**Key insight:** 301 vs 302 redirect — 301 caches in the browser forever so
you lose all analytics. 302 always checks the server first. Always use 302 for URL shorteners.

**Deliverable:** `docs/02-api-contract.md`

- 5 endpoints designed: POST /v1/links · GET /v1/links/{id} · GET /{slug} · GET /v1/links/{id}/stats · DELETE /v1/links/{id}
- Each endpoint has: purpose · request · response · status codes · idempotency · auth

---

### Day 3 — Data Modeling and Indexes

**What I learned:** Designing tables is not just about storing data —
it's about knowing how that data will be searched and fetched later.

**Key insight:** Indexes are not free. Every index slows down writes because
the DB updates the index on every insert/update. Only index columns you actually search by.

**Deliverable:** `docs/03-data-model.md`

- 3 tables: links · click_events · daily_link_stats
- Index decisions with reasoning for each
- Why raw IP addresses must be hashed (GDPR/privacy)

---

### Day 4 — Transactions and Correctness

**What I learned:** ACID properties map directly to real problems in LinkLite.
Not every problem needs a transaction — the right tool depends on the failure mode.

**Key insight:** Data splits into two buckets — must be exact (slug ownership,
link creation) and eventually consistent ok (click counts, deleted links).

**Deliverable:** `docs/04-correctness.md`

- 4 failure scenarios: duplicate slug · timeout after row created · 1000 simultaneous clicks · delete during redirect
- Solutions: unique constraint · idempotent retry · atomic SQL update · soft delete

---

### Day 5 — Caching Basics

**What I learned:** Cache-aside is a reactive approach — only populate the
cache when data is first requested. Never pre-load what nobody has asked for yet.

**Key insight:** Cache what gets read often and changes rarely.
Don't cache what gets written constantly or must always be accurate.

**Deliverable:** `docs/05-cache-plan.md`

- 3 things cached: short code lookup · hot stats summary · rate limit counters
- Each with: cache key · TTL · fill strategy · invalidation rule
- 3 things not cached with reasoning: raw click events · newly created links · auth data

---

### Day 6 — Scaling Basics

**What I learned:** Stateless doesn't mean the app has no state —
it means state lives in Redis, not on the server itself.
That's what makes horizontal scaling possible.

**Key insight:** Redirects are easy to scale (stateless cache reads).
Analytics are hard to scale (heavy aggregation across millions of rows).

**Deliverable:** `docs/06-scaling-basics.md`

- Vertical vs horizontal scaling tradeoffs
- Load balancing algorithms: round robin · least connections · IP hashing
- Mermaid architecture diagram: Client → LB → API servers → Postgres + Redis

---

### Day 7 — Diagramming Properly

**What I learned:** C4 model gives a standard way to diagram any system
at different levels of detail. Context = what's around the system.
Container = what's inside the system.

**Key insight:** Diagrams are a communication tool. The goal is for anyone
to understand the system without reading a single line of code.

**Deliverable:** `docs/07-diagrams.md`

- Context diagram — LinkLite + User + Google Safe Browsing
- Container diagram — API · PostgreSQL · Redis · Background Worker
- Sequence diagram — full redirect flow with cache hit and cache miss paths

---

## Week 1 Exit Checkpoint — Passed ✅

- [x] Functional vs non-functional requirements
- [x] Safe, idempotent, and neither
- [x] Why click_events needs its own table
- [x] Where transactions belong vs eventual consistency
- [x] Cache-aside pattern and what not to cache
- [x] Statelessness before horizontal scaling
- [x] Context diagram vs Container diagram

---

## Week 2 — Build the First Version

_Status: ✅ Completed_

This week went from paper designs to a real running backend.
Every concept from Week 1 became actual working code.

---

### Day 8 — Project Scaffold

**What I built:** FastAPI app skeleton with Docker Compose running
PostgreSQL and Redis locally. First working endpoint — GET /health.

**Key learning:** Docker Compose lets you spin up an entire backend
stack with one command. Postgres and Redis running as containers
means no local installation needed.

---

### Day 9 — Create Link + Redirect Path

**What I built:** POST /v1/links saves a link to PostgreSQL.
GET /{slug} reads from DB and returns a 302 redirect.

**Key learning:** The redirect is the hottest path in the entire system.
Every click hits it. The unique index on short_code is what makes
it fast — without it, every redirect would scan millions of rows.

---

### Day 10 — Slug Generation + ADR-0001

**What I built:** Improved slug generation with auto-retry on collision.
Wrote first Architecture Decision Record documenting why base62 random
slugs were chosen over sequential IDs or UUIDs.

**Key learning:** ID generation is a design decision not a coding detail.
Sequential slugs are predictable — attackers can enumerate all links.
Random base62 gives 56 billion combinations and is not guessable.

---

### Day 11 — Redis Cache on Redirect Path

**What I built:** Cache-aside pattern on GET /{slug}. First request
is a cache miss — hits DB and stores in Redis with 1hr TTL.
Every subsequent request is a cache hit — DB never touched.

**Key learning:** Saw CACHE MISS and CACHE HIT in logs in real time.
The thing designed on paper in Day 5 is now working in production code.

---

### Day 12 — Async Click Tracking

**What I built:** Background task fires after every redirect to record
click events in PostgreSQL. User gets redirected instantly — DB write
happens after the response is sent.

**Key learning:** Never slow down the user-facing path for analytics.
Losing one click is acceptable. Making every redirect wait for a DB
write is not.

---

### Day 13 — Rate Limiting

**What I built:** Redis counter per IP address with daily TTL.
After 10 links created, next request returns 429 Too Many Requests.
Counter resets automatically at TTL expiry.

**Key learning:** Tested with a loop of 11 requests — first 10 succeeded,
11th got rate limited. Exactly what was designed in the requirements doc
on Day 1.

---

### Day 14 — Week 2 Review

**What I tested:** All 5 endpoints end to end. Health check, create link,
redirect, cache hit, click events in DB — all working.

**Week 2 exit checkpoint — passed:**

- [x] App starts cleanly with docker compose up
- [x] Redis goes down — redirect still works via DB fallback
- [x] Cache hit and miss visible in logs
- [x] Slug generation retries on collision automatically
- [x] ADR documents why base62 was chosen
- [x] Click events recorded async without slowing redirect

---

## Week 3 — Think Like a Production Engineer
*Status: ✅ Completed*

This week shifted from "does it work?" to "how do you know it's working 
and what happens when it breaks?"

---

### Day 15 — Observability
**What I built:** Structured logging middleware on every request.
Every request now logs request_id, method, path, status code, and 
duration in milliseconds.

**Key insight:** Saw cache miss vs cache hit latency in real numbers.
Cache miss = 25.5ms hitting Postgres. Cache hit = 3.69ms hitting Redis.
Cache is 7x faster — not theory, measured from the actual system.

---

### Day 16 — SLOs and Alerts
**What I built:** Defined 3 SLOs for LinkLite. Redirect success rate 
≥ 99.9% — 3am alert if missed. Redirect p95 latency under 50ms — 
dashboard only. Create link success rate ≥ 99.5%.

**Key insight:** Not everything needs to wake you up at 3am. Be 
deliberate about what's a real emergency vs what can wait until morning.

---

### Day 17 — Idempotency
**What I built:** Idempotency key support on POST /v1/links. Same key 
returns same response — no duplicate link created on retry.
Stored in Redis with 24hr TTL.

**Key insight:** POST requests are not safe to retry by default.
Idempotency keys make them safe. Stripe uses this for payments —
same problem, higher stakes.

---

### Day 18 — API Security
**What I built:** Security review of LinkLite against OWASP API Top 10.
Fixed the most critical gap immediately — added .gitignore so .env 
credentials never get pushed to GitHub.

**Key insight:** Security isn't a feature you add at the end. Every 
endpoint without authentication or rate limiting is a gap. Looked at 
LinkLite like an attacker for the first time.

---

### Day 19 — Consistency Models
**What I built:** Mapped every piece of LinkLite data to the right 
consistency model. Slug uniqueness = strong. Click counts = eventual.

**Key insight:** CAP theorem — in a distributed system you can only 
guarantee 2 of 3: consistency, availability, partition tolerance.
Strong consistency = correct but slow. Eventual = fast but temporarily stale.

---

### Day 20 — Failure Modes + Failure Drill
**What I built:** Redis failure handling with graceful fallback to 
PostgreSQL. Wrapped all Redis calls in try/except.

**Key insight:** Actually stopped Redis while the app was running and 
watched it crash with 500. Fixed it. Restarted Redis and watched it 
recover automatically. Slower is always better than broken.

---

### Day 21 — Week 3 Review + ADR-0002
**What I wrote:** ADR-0002 documenting async analytics ingestion decision.
Why background tasks over synchronous writes. Tradeoffs — speed vs 
guaranteed delivery.

**Week 3 exit checkpoint — passed:**
- [x] 3 pillars of observability
- [x] SLO vs SLA difference
- [x] Redis failure handled gracefully
- [x] Idempotency key implemented and tested
- [x] 2 security risks identified
- [x] Consistency models mapped to LinkLite data

---

## Week 4 — Coming Next
Final design doc · Diagrams update · Architecture review · Demo · Postmortem

*Week 4 will be updated once completed.*
