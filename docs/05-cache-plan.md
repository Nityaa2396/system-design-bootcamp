# LinkLite Cache Plan

## What is cache-aside?

A reactive approach — the cache is only populated when data is
first requested. On a cache miss, the DB is queried, the result
is stored in cache, then returned to the caller.

**Step by step:**

1. Request comes in
2. Check cache first
3. Cache hit → return data immediately
4. Cache miss → query DB → store result in cache with TTL → return data

---

## What to cache

### 1. Short code lookup

**Cache key:** `link:{short_code}`
**TTL:** 1 hour
**Source of truth:** `links` table in PostgreSQL
**Fill strategy:** Cache-aside — populated on first redirect request
**Invalidation:** Delete from cache when link is updated or deleted

### 2. Hot stats summary

**Cache key:** `stats:{link_id}`
**TTL:** 5 minutes
**Source of truth:** `daily_link_stats` table in PostgreSQL
**Fill strategy:** Cache-aside — populated when analytics are first viewed
**Invalidation:** TTL expiry — slight delay in stats is acceptable

### 3. Rate limit counter

**Cache key:** `ratelimit:{user_id}`
**TTL:** End of day (midnight reset)
**Source of truth:** Redis is the source of truth here
**Fill strategy:** Set to 1 on first create request, increment on each
subsequent request
**Invalidation:** TTL expiry — auto resets every day

---

## Things I will NOT cache and why

| Data                | Reason                                                                                                     |
| ------------------- | ---------------------------------------------------------------------------------------------------------- |
| Raw click events    | Write-heavy, needs permanent storage in PostgreSQL. Redis is memory — if it restarts, data is gone forever |
| Newly created links | Cache on first request not upfront — nobody has clicked it yet                                             |
| Auth / user data    | Must always be accurate — stale auth data is a security risk                                               |

---

## Cache rule

Cache what gets read often and changes rarely.
Don't cache what gets written constantly or must always be accurate.
