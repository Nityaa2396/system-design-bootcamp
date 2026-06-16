# Day 22 — Notification Service Design

## Problem statement
Internal services need to notify users via email, SMS, and in-app
without blocking their own operations. A dedicated notification
service handles all outbound communication.

## Functional requirements
1. Accept notification requests from other services
2. Send notifications via email, SMS, or in-app channel
3. Track delivery status of each notification

## Non-functional requirements
1. Low latency — notifications delivered within seconds
2. High availability — provider failover if primary goes down
3. At-least-once delivery — duplicates rare but acceptable, losses are not

## API design

### POST /v1/notifications
**Purpose:** Trigger a new notification
**Request:**
```json
{
  "user_id": "usr_123",
  "channel": "email",
  "event_type": "payment_received",
  "message": "Your payment of $50 was received"
}
```
**Response:** 201 Created with notification id
**Idempotent?** No — use idempotency key header

### GET /v1/notifications/{id}
**Purpose:** Check delivery status
**Response:**
```json
{
  "id": "notif_123",
  "status": "delivered",
  "sent_at": "2026-06-10T15:52:54Z"
}
```

## Schema

### notifications table
| Column | Type | Why |
|---|---|---|
| id | UUID | unique identifier |
| user_id | VARCHAR | who to notify |
| channel | VARCHAR | email/sms/in-app |
| event_type | VARCHAR | what triggered it |
| message | TEXT | the content |
| status | VARCHAR | pending/sent/delivered/failed |
| created_at | TIMESTAMP | when request came in |
| sent_at | TIMESTAMP | when actually sent |

### delivery_attempts table
| Column | Type | Why |
|---|---|---|
| id | UUID | unique identifier |
| notification_id | UUID | foreign key → notifications |
| attempted_at | TIMESTAMP | when attempt was made |
| status | VARCHAR | success/failed |
| error | TEXT | what went wrong |
| provider | VARCHAR | which provider was used |

## Queue design
Notifications processed asynchronously via background queue.
Triggering service fires and forgets — never waits for delivery.

## Provider failover
SendGrid fails → retry with Mailgun → retry with AWS SES →
all fail → move to dead letter queue → alert engineering team

## Retry strategy
Exponential backoff:
- Attempt 1 → fail → wait 1s
- Attempt 2 → fail → wait 2s
- Attempt 3 → fail → wait 4s
- All failed → dead letter queue

## User preferences
- Users can opt out of SMS but keep email
- Preferences stored in separate user_preferences table
- Notification service checks preferences before sending