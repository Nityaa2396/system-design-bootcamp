# LinkLite — Full Design Document

## 1. Problem statement
Users need a way to shorten long URLs and share them easily.
Every click on a short link must redirect instantly to the original URL.
Click analytics must be tracked without slowing down the redirect.

## 2. Requirements

### Functional
- Create a short link from a long URL
- Redirect short link to original URL
- Support custom slugs
- Track clicks per link
- Show basic analytics

### Non-functional
- Redirect latency p95 under 50ms
- Redirect success rate 99.9%
- Create link success rate 99.5%
- System degrades gracefully if cache goes down
- No single point of failure in the redirect path

## 3. Assumptions and scale
- 1,000 DAU for v1
- Read:write ratio approximately 100:1
- 95% of traffic is redirects
- Single region deployment
- No authentication in v1

## 4. API design

| Endpoint | Method | Purpose |
|---|---|---|
| /v1/links | POST | Create short link |
| /v1/links/{id} | GET | Get link details |
| /{slug} | GET | Redirect to original URL |
| /v1/links/{id}/stats | GET | Get click analytics |
| /v1/links/{id} | DELETE | Soft delete link |

Key decisions:
- 302 not 301 — browser never caches, analytics always captured
- /v1/ prefix — versioning so old clients don't break on API changes
- Idempotency-Key header on POST — safe to retry without duplicates

## 5. Data model

### links
| Column | Type | Notes |
|---|---|---|
| id | UUID | primary key |
| short_code | VARCHAR(10) | unique index — hottest lookup |
| original_url | TEXT | destination |
| created_at | TIMESTAMP | creation time |
| expires_at | TIMESTAMP | optional TTL |
| is_deleted | BOOLEAN | soft delete |

### click_events
| Column | Type | Notes |
|---|---|---|
| id | UUID | primary key |
| link_id | UUID | foreign key → links |
| clicked_at | TIMESTAMP | indexed for date queries |
| ip_hash | VARCHAR | hashed — privacy safe |
| user_agent | TEXT | browser/device info |
| referer | TEXT | traffic source |

### daily_link_stats
| Column | Type | Notes |
|---|---|---|
| link_id | UUID | composite index with day |
| day | DATE | which day |
| clicks | INTEGER | pre-aggregated count |

## 6. High-level architecture
Client → Load Balancer → API Servers (stateless)

↓           ↓

Redis      PostgreSQL

(cache)    (source of truth)

↓

Background Worker

↓

click_events table

## 7. Read path — redirect flow
1. Request hits API server
2. Check Redis for `link:{slug}`
3. Cache hit → return 302 immediately (3–5ms)
4. Cache miss → query PostgreSQL → store in Redis → return 302 (20–30ms)
5. Redis down → skip cache → query PostgreSQL → return 302 (20–30ms)
6. Background task fires to record click

## 8. Write path — create link flow
1. Check idempotency key in Redis — return cached response if exists
2. Check rate limit — return 429 if exceeded
3. Generate unique base62 slug — retry up to 5 times on collision
4. Insert into PostgreSQL links table
5. Store idempotency key in Redis with 24hr TTL
6. Increment rate limit counter
7. Return 201 Created

## 9. Cache strategy
Pattern: cache-aside (reactive, not pre-loaded)

| Key | Value | TTL | Purpose |
|---|---|---|---|
| link:{slug} | original_url | 1hr | Redirect lookup |
| ratelimit:{ip} | count | 24hr | Rate limiting |
| idempotency:{key} | response | 24hr | Duplicate prevention |
| stats:{link_id} | click summary | 5min | Analytics |

## 10. Background processing
Click events recorded asynchronously after redirect response sent.
User never waits for analytics write.
Failure mode: click lost silently — acceptable (eventual consistency).
Trade-off: speed over guaranteed delivery.

## 11. Reliability and failure modes

| Failure | User impact | Mitigation |
|---|---|---|
| Redis down | Redirects slower, no cache | try/except → fallback to DB |
| PostgreSQL down | Non-cached redirects fail | Redis cache absorbs hot traffic |
| Background task fails | Click not recorded | Log error, accept data loss |
| App server crashes | Requests fail until restart | Multiple servers behind LB |

## 12. Security and abuse prevention
- Rate limiting: 10 creates per IP per day via Redis counter
- Idempotency keys: prevent duplicate link creation on retry
- Soft delete: is_deleted flag — rows never removed from DB
- IP hashing: raw IPs never stored — privacy compliant
- .gitignore: credentials never committed to GitHub
- Known gap: no authentication in v1

## 13. Observability
Structured logging on every request:
request_id={id} method={GET} path=/{slug} status=302 duration_ms=3.69

Cache hit/miss logged on every redirect.
Evidence: cache miss = 25.5ms, cache hit = 3.69ms — 7x difference.

## 14. SLOs

| SLO | Target | Alert |
|---|---|---|
| Redirect success rate | ≥ 99.9% | 3am alert |
| Redirect p95 latency | < 50ms | Dashboard |
| Create success rate | ≥ 99.5% | Dashboard |

## 15. Tradeoffs and alternatives considered

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Redirect code | 302 | 301 | 301 caches forever, breaks analytics |
| Slug generation | Random base62 | Sequential ID | Sequential is enumerable — security risk |
| Click tracking | Async background task | Synchronous write | Sync adds latency to every redirect |
| Queue | FastAPI BackgroundTasks | RabbitMQ | Simpler for v1, no retry mechanism |
| Cache pattern | Cache-aside | Write-through | Only cache what's actually requested |
| Delete strategy | Soft delete | Hard delete | Hard delete breaks in-flight redirects |

## 16. Future improvements
- Add authentication — API keys per user
- Add RabbitMQ for reliable click ingestion with retries
- Add rate limiting to stats endpoint
- Add multi-region deployment for lower global latency
- Add link expiry enforcement via background job
- Add Google Safe Browsing URL validation
- Move from background tasks to proper worker queue

## Scaling beyond v1

### Sharding
When links table exceeds ~100M rows, shard by short_code
using consistent hashing.

- Sharding key: short_code — every redirect already looks up by this
- Strategy: consistent hashing — adding servers only moves a small
  slice of data, not everything
- Add routing layer between API and database shards
- Tradeoff: cross-shard queries (global analytics) become expensive
  — need a separate aggregation pipeline

### Replication
Add primary-replica replication immediately — not just at scale.
This is a reliability decision, not a scale decision.

- All writes → primary (creates, deletes — 5% of traffic)
- All reads → replicas (redirects, stats — 95% of traffic)
- One replica as hot standby — auto-promotes if primary dies
- Tradeoff: replication lag — newly created link may not be visible
  on replica for a few milliseconds
- Fix: route read-after-write directly to primary

### Combined at scale
Shard 1: Primary + 2 replicas
Shard 2: Primary + 2 replicas
Shard 3: Primary + 2 replicas
Sharding handles size. Replication handles reliability.