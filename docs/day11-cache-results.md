# Day 11 — Cache Results

## Cache key format

link:{short_code}
example: link:aYgrfP

## TTL

3600 seconds (1 hour)

## Miss behavior

Query PostgreSQL → store result in Redis → redirect user

## Hit behavior

Return from Redis immediately → redirect user → DB never touched

## Invalidation rule

TTL expiry after 1 hour — next request will be a cache miss and refresh the cache

## Evidence

CACHE MISS: aYgrfP → first request hits DB
CACHE HIT: aYgrfP → second request served from Redis
