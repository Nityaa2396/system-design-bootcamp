# Day 23 — Notification Delivery Guarantees

## Delivery semantics

| Guarantee | Means | Risk |
|---|---|---|
| At-most-once | Send once, never retry | Messages lost |
| At-least-once | Retry until confirmed | Duplicates possible |
| Exactly-once | Delivered exactly once | Very hard, expensive |

## Chosen strategy
At-least-once delivery. Losing a notification is worse than
a duplicate. Duplicates handled via dedupe key.

## What happens if provider times out?
Provider accepts message but confirmation never arrives.
System retries — user may receive duplicate notification.
Fix: dedupe key stored in Redis. Provider checks key before
sending — if already sent, skip.

## What happens if worker retries after success?
Same as above — duplicate delivered. Dedupe key prevents this.
Key format: `notif:{notification_id}:{channel}`
TTL: 24 hours

## Dead letter queue
After 3 failed attempts — message moves to dead letter queue.
Engineering team alerted. Manual review and replay possible.
Nothing is lost — just delayed.

## At-least-once vs at-most-once by channel
| Channel | Strategy | Why |
|---|---|---|
| Email — transactional | At-least-once | Losing receipt is unacceptable |
| Email — marketing | At-most-once | Duplicate spam damages trust |
| SMS | At-least-once | Losing OTP blocks user |
| In-app | At-most-once | Duplicate badges are annoying |