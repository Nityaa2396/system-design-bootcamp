# LinkLite Scaling Basics

## Vertical vs horizontal scaling

| | Vertical | Horizontal |

| What | Bigger machine | More machines |
| Failure | Single point of failure | Resilient — others take over |
| Communication | Inter-process (same machine) | RPC over network |
| Consistency | Easy — one machine | Harder — data spread across servers |
| Limit | Hardware ceiling | Scales indefinitely |

## When does vertical stop being enough?

When you hit the hardware ceiling — no machine can grow infinitely.
Also when cost becomes prohibitive — one huge server costs more
than several smaller ones combined.

## What must be stateless before horizontal scaling works?

- No session data stored on the server itself
- Sessions stored in Redis instead — any server can read them
- No local file storage — use shared storage (S3 etc)
- No in-memory cache that's server-specific

## Where does the load balancer sit in LinkLite?

Client → Load Balancer → API servers → PostgreSQL + Redis

The load balancer is the single entry point. It distributes
requests across API servers using round-robin or least connections.

## Why are redirects easier to scale than analytics?

Redirects are stateless reads — check cache, return URL, done.
Analytics require aggregating millions of rows across time ranges.
Reads are easy to scale. Heavy computation is not.

## Load balancing algorithms

- Round robin — takes turns across servers
- Least connections — sends to least busy server
- IP hashing — same user always hits same server

## Sticky sessions

Not needed for LinkLite — app is stateless, sessions live
in Redis. Any server can handle any request.
