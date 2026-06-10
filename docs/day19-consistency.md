# Day 19 — Consistency Models

## Strong Consistency
System behaves as if not distributed at all. Every operation takes
effect atomically. All clients see the same data at the same time.
Cost: slower, harder to scale.

## Eventual Consistency
All nodes converge to the same value over time if writes stop.
Temporarily different nodes may return different values.
Cost: stale reads possible, but faster and more available.

## Why you can't always have strong consistency — CAP theorem
In a distributed system you can only guarantee 2 of 3:
Consistency, Availability, Partition tolerance.
Network partitions always happen — so you must choose between
consistency and availability. Strong consistency = slow.
Eventual consistency = fast but temporarily stale.

## LinkLite consistency map

| Data | Model | Reason |
|---|---|---|
| short_code uniqueness | Strong | Two users can't share a slug |
| Click counts | Eventual | Approximate counts are acceptable |
| Cache TTL expiry | Strong | Every node must respect same TTL |
| Link deletion | Eventual | In-flight redirects may succeed briefly |

## Key rule
Strong consistency where correctness is non-negotiable.
Eventual consistency where slight delays are acceptable.