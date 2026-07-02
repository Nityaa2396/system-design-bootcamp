# WhatsApp — System Design Case Study

## What it is
A real-time messaging app used by 2 billion people globally.
Core product: send and receive messages instantly across any network.

---

## Functional requirements
1. Send and receive messages — text, images, videos, voice notes
2. Voice and video calls — real-time audio/video between users
3. Group messaging — create groups, add/remove members, group calls
4. Search — find messages, contacts, media across chat history
5. Privacy controls — last seen, read receipts, profile visibility

## Non-functional requirements
1. Low latency — message delivered under 100ms on good network
2. Reliability — 99.99% uptime, 2 billion people depend on it
3. Storage — undelivered messages held 30 days, media on device
4. End-to-end encryption — WhatsApp servers never see message content

---

## Scale estimates
| Metric | Estimate |
|---|---|
| Daily active users | 1 billion |
| Messages per day | 100 billion |
| Messages per second | ~1.15 million |
| Average message size | ~1KB |
| Daily text storage | ~100TB |
| Daily storage with media | ~1 petabyte |

---

## The 3 core flows

### Flow 1 — Online messaging (both users online)
Sender phone
↓
WebSocket connection → Message server
↓
Check if recipient is online → YES
↓
Push to recipient's WebSocket connection
↓
Recipient phone receives message
↓
ACK sent back → double tick on sender's phone
↓
Recipient opens message → blue tick

### Flow 2 — Offline messaging (recipient offline)
Sender phone → WebSocket → Message server
↓
Check if recipient is online → NO
↓
Store in offline queue (database)
↓
Recipient comes back online → WebSocket reconnects
↓
Server checks offline queue
↓
Delivers all queued messages in order
↓
ACK sent → double tick appears on sender's phone

### Flow 3 — Media sending
Sender selects photo
↓
Photo encrypted on device
↓
Uploaded directly to media server (S3-like storage)
↓
Media server returns URL + encryption key
↓
URL sent as text message through normal message flow
↓
Recipient phone receives URL
↓
Downloads photo directly from media server
↓
Decrypts using key → photo appears in chat

---

## Key components

### WebSocket service
Keeps persistent connection between each phone and server.
Why not HTTP polling? Polling drains battery, adds latency.
WebSocket stays open — server pushes messages instantly.

### Message server
Receives messages, checks recipient status, routes or queues.
Does NOT store messages long-term — only undelivered ones.
Handles 1.15 million messages per second across many servers.

### Offline queue (database)
Holds messages for offline users — max 30 days.
Messages deleted after delivery ACK received.
Ordered by timestamp — messages delivered in correct order.

### Media server (object storage)
Stores encrypted photos, videos, voice notes.
Never sees unencrypted content — encryption happens on device.
CDN in front for fast downloads globally.

### Presence service
Tracks who is online/offline in real time.
Powers "last seen" and online indicators.
Checked by message server before routing vs queuing.

---

## The tick system — how it works
| Tick | Meaning | Triggered by |
|---|---|---|
| Single grey tick | Delivered to server | Server ACK |
| Double grey tick | Delivered to device | Recipient device ACK |
| Double blue tick | Read by recipient | Recipient opened chat |

Each tick is a separate ACK message flowing back through the system.

---

## End-to-end encryption
WhatsApp uses the Signal protocol.
Keys generated on your device — WhatsApp never has them.
Messages encrypted before leaving your phone.
Server routes encrypted blobs — cannot read content.
Recipient's device decrypts using their private key.

---

## Sharding strategy
2 billion users — can't fit on one server.
Shard by user_id using consistent hashing.
Each user mapped to a specific message server.
When you send a message — routed to recipient's assigned server.
Adding new servers only moves a small slice of users.

---

## Data model

### messages
| Column | Type | Notes |
|---|---|---|
| id | UUID | unique per message |
| sender_id | UUID | who sent it |
| recipient_id | UUID | who receives it |
| content | BLOB | encrypted — server can't read |
| status | VARCHAR | sent/delivered/read |
| created_at | TIMESTAMP | when sent |
| delivered_at | TIMESTAMP | when delivered |

### offline_queue
| Column | Type | Notes |
|---|---|---|
| id | UUID | queue entry ID |
| recipient_id | UUID | who to deliver to |
| message_id | UUID | foreign key → messages |
| queued_at | TIMESTAMP | when queued |
| expires_at | TIMESTAMP | 30 days after queued |

### media
| Column | Type | Notes |
|---|---|---|
| id | UUID | media ID |
| uploader_id | UUID | who uploaded |
| url | TEXT | location in object storage |
| size_bytes | INTEGER | file size |
| mime_type | VARCHAR | image/video/audio |
| expires_at | TIMESTAMP | when deleted from server |

---

## Failure modes

| Failure | User impact | Mitigation |
|---|---|---|
| Message server crashes | Messages lost or delayed | Offline queue persists in DB |
| WebSocket drops | App reconnects automatically | Client retry with exponential backoff |
| Media server down | Images don't load | CDN caches recently accessed media |
| Offline queue full | Message delivery fails after 30 days | User notified, message dropped |

---

## How WhatsApp differs from LinkLite

| Aspect | LinkLite | WhatsApp |
|---|---|---|
| Protocol | HTTP REST | WebSocket (persistent) |
| State | Stateless servers | Stateful — user assigned to server |
| Storage | PostgreSQL | Sharded DB + object storage |
| Scale | Thousands of users | 2 billion users |
| Encryption | None (v1) | End-to-end (Signal protocol) |
| Hardest problem | Cache redirects cheaply | Real-time delivery at 1.15M msg/sec |