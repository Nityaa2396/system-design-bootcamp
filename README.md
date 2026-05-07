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

## Week 2 — Coming Next

FastAPI · PostgreSQL · Docker Compose · Building LinkLite for real

_Week 2 will be updated once completed._
