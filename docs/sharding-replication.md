# Sharding and Replication

## Sharding — solves size
One table too big for one server → split across multiple servers.

### Naive hash sharding problem
hash(short_code) % 10 → works for 10 servers
hash(short_code) % 11 → almost every row maps to wrong server
Must physically move data to match new formula. Expensive.

### Consistent hashing — the fix
Servers and keys placed on a ring.
Key belongs to next server clockwise.
Adding a server only moves data from its immediate neighbor.
Everything else stays put.

### Sharding key matters
Pick based on most common query pattern.
LinkLite queries by short_code → shard by short_code.
Cross-shard queries are expensive — avoid designs that require them.

### Hot shard problem
Viral link → one shard gets millions of hits.
Sharding solves storage size, not traffic hotspots.
Redis cache solves traffic hotspots.

---

## Replication — solves reliability and read scale

### Primary-Replica
One primary accepts all writes.
Replicas copy from primary and handle reads.
One replica as hot standby — promotes if primary dies.

### Replication lag
Replicas always slightly behind primary.
Milliseconds usually, seconds under heavy load.
Fix: route read-after-write to primary directly.

### Multi-Primary
Multiple servers accept writes simultaneously.
Harder — conflict resolution needed.
Use for global systems where users in different regions need
low-latency writes.

---

## When to use which

| Problem | Solution |
|---|---|
| Data too big for one server | Sharding |
| Server goes down | Replication |
| Too many reads | More replicas |
| Too many writes | More shards |
| Low latency globally | Replica per region |

## In practice — use both
Shard 1: Primary + 2 replicas
Shard 2: Primary + 2 replicas
Sharding handles size. Replication handles reliability.