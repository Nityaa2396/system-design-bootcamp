# TikTok — System Design Case Study

## What it is
A short-form video platform with 1 billion daily active users.
Core product: an endless personalized feed of videos that starts
playing instantly and gets smarter the more you watch.

---

## Functional requirements
1. Upload video — creator uploads, video processed and published
2. Watch and interact — play, like, comment, share, follow
3. Recommendations — personalized feed based on watch behavior
4. Content moderation — detect and remove violating content

## Non-functional requirements
1. Low latency — video starts in under 2 seconds on any network
2. Scalability — millions of simultaneous uploads and streams
3. Privacy — watch history and user data protected
4. Eventual consistency — view counts and likes sync globally

---

## Scale estimates
| Metric | Estimate |
|---|---|
| Daily active users | 1 billion |
| Videos uploaded per day | 10 million |
| Average video size | 50MB |
| Daily upload storage (raw) | 500 TB |
| Daily storage after transcoding | ~2.5 petabytes |
| Video views per day | 1 billion+ |
| Recommendation decisions per second | ~11,600 |

---

## The 4 pipelines

### Pipeline 1 — Upload
Creator uploads video
↓
Raw file stored in S3 (object storage)
↓
Background job triggered (async — same pattern as LinkLite clicks)
↓
Transcoding service converts to 5 formats:
1080p, 720p, 480p, 360p, 240p
↓
Each format stored in S3
↓
Metadata saved to database (title, creator, tags, duration)
↓
Video indexed for search
↓
Content moderation runs (ML model checks for violations)
↓
Video published to feed

### Pipeline 2 — Serving (watching a video)
User opens TikTok
↓
Request hits CDN edge server (nearest location globally)
↓
CDN cache hit → stream video instantly
CDN cache miss → fetch from S3 → cache at edge → stream
↓
Video streams in chunks (not downloaded fully before playing)
↓
While watching — pre-fetch service downloads next 3 videos
↓
Swipe up → next video already on device → instant play

### Pipeline 3 — Recommendation
User opens app
↓
Stage 1 — Candidate generation (fast, approximate)
Fetch user profile: watch history, likes, follows
Pull 1000 candidate videos from pool of billions
Filter by: language, location, trending, followed creators
↓
Stage 2 — Ranking (slow, accurate)
ML ranking model scores all 1000 candidates
Signals used: completion rate, likes, shares, comments,
rewatch rate, time of day, device type
↓
Top 10 returned to feed
↓
User watches → completion rate recorded
↓
Profile updated → next recommendation better

### Pipeline 4 — Analytics

Every interaction → event fired (same async pattern)
↓
Kafka topic: "video-events"
↓
3 consumer groups read simultaneously:
1. View counter service → increments view count
2. User profile service → updates watch history
3. Recommendation trainer → feeds ML model
↓
Aggregated stats stored in time-series database
↓
Creator sees analytics dashboard

---

## The recommendation engine — TikTok's secret weapon

### Why TikTok learns faster than YouTube
- TikTok videos: 15–60 seconds → hundreds of signals per hour
- YouTube videos: 10–20 minutes → 5–10 signals per hour
- More signals = faster learning = better recommendations

### The key signal — completion rate
| Action | Signal strength |
|---|---|
| Watched 100% | Strong positive |
| Rewatched | Very strong positive |
| Watched 80% | Positive |
| Scrolled after 2 seconds | Strong negative |
| Liked/commented | Positive but weaker than completion |

You don't need to like a video. Just watching it fully is enough.

### Cold start problem
New user — no watch history — what to show?
1. Show trending videos globally
2. Ask for 3 interests on signup
3. After 5 videos — enough signal to personalize
4. After 20 videos — feed feels personal

---

## Pre-fetching — why TikTok feels instant

While you watch video 1:
- Recommendation picks videos 2, 3, 4
- Pre-fetch service downloads them to your device
- Swipe → instant play, no spinner

Tradeoff: wastes mobile data. Videos downloaded that you never watch.
Why TikTok uses more data than any other app — intentional.

---

## Key components

### CDN (Content Delivery Network)
Videos cached at edge servers globally — nearest server serves you.
User in Mumbai gets video from Mumbai CDN, not US servers.
Reduces latency from seconds to milliseconds.

### Transcoding service
Every uploaded video converted to 5 resolutions.
On slow network → 240p served. On 5G → 1080p served.
Adaptive bitrate streaming adjusts quality mid-video.

### Feature store
Stores pre-computed user features — watch history, preferences.
Updated in real time as you watch.
Recommendation engine reads from here — not from raw database.
Makes recommendation fast — features already computed.

### Vector database
Videos represented as embedding vectors.
Similar videos are close together in vector space.
Candidate generation finds nearest videos to your taste vector.
Same concept as PolicyCopilot's Qdrant — just at billion scale.

---

## Data model

### videos
| Column | Type | Notes |
|---|---|---|
| id | UUID | unique video ID |
| creator_id | UUID | who uploaded |
| title | TEXT | video title |
| s3_url_1080p | TEXT | highest quality |
| s3_url_480p | TEXT | medium quality |
| s3_url_240p | TEXT | lowest quality |
| duration_seconds | INTEGER | video length |
| status | VARCHAR | processing/published/removed |
| created_at | TIMESTAMP | upload time |

### video_events
| Column | Type | Notes |
|---|---|---|
| id | UUID | event ID |
| user_id | UUID | who watched |
| video_id | UUID | what they watched |
| watch_seconds | INTEGER | how long they watched |
| completion_rate | FLOAT | percentage watched |
| event_type | VARCHAR | watch/like/share/comment |
| created_at | TIMESTAMP | when it happened |

### user_profiles
| Column | Type | Notes |
|---|---|---|
| user_id | UUID | primary key |
| interest_vector | BLOB | ML embedding of preferences |
| watch_history | JSON | last 1000 videos watched |
| updated_at | TIMESTAMP | last profile update |

---

## Failure modes

| Failure | User impact | Mitigation |
|---|---|---|
| CDN goes down | Videos don't load | Multiple CDN providers, failover |
| Recommendation engine slow | Feed loads slowly | Cache last known feed, serve stale |
| Transcoding fails | Video stuck processing | Retry queue, alert creator |
| Kafka consumer lag | View counts delayed | Acceptable — eventual consistency |
| Pre-fetch wrong video | Wrong video pre-loaded | Small waste, re-fetch on swipe |

---

## How TikTok differs from LinkLite and WhatsApp

| Aspect | LinkLite | WhatsApp | TikTok |
|---|---|---|---|
| Core data | URLs | Messages | Videos |
| Hardest problem | Cache redirects | Real-time delivery | Personalization at scale |
| Protocol | HTTP | WebSocket | HTTP + CDN + pre-fetch |
| Storage | PostgreSQL | Sharded DB | S3 + CDN + vector DB |
| ML involved | None | None | Core to the product |
| Scale | Thousands | 2 billion users | 1 billion DAU |