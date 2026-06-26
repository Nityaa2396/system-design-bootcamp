---

## Key components

### Audio ingestion service
Captures the real-time audio stream from the meeting.
Splits it into small chunks (every 1-2 seconds) and sends
to the STT model for processing.

### Speech-to-Text (STT) model
Converts audio chunks to text. Uses models like OpenAI Whisper
or a custom-trained model. Runs on GPU for speed.
Outputs: text + confidence score + timestamp per word.

### Speaker diarization
Identifies who is speaking at any given moment.
Separates overlapping voices and assigns speaker labels.
One of the hardest problems in the system.

### WebSocket service
Keeps a persistent open connection to each user's browser.
Pushes new transcript text the moment STT produces it.
Why not polling? — polling asks every second, wastes resources,
adds latency. WebSockets push instantly, one connection per user.

### LLM summarization
After meeting ends, full transcript is sent to an LLM
with a prompt: "summarize this meeting, extract action items,
identify key decisions."
Runs async — user doesn't wait during the meeting.

### Search (Elasticsearch)
Indexes every transcript line after the meeting.
Allows full text search across all past meetings.
Why not PostgreSQL? — Postgres text search is slow at scale.
Elasticsearch is built specifically for fast full-text search.

---

## Data model

### meetings
| Column | Type | Notes |
|---|---|---|
| id | UUID | primary key |
| title | VARCHAR | meeting name |
| status | VARCHAR | recording/processing/completed |
| duration | INTEGER | seconds |
| created_at | TIMESTAMP | when meeting started |
| user_id | UUID | who owns the meeting |

### transcript_lines
| Column | Type | Notes |
|---|---|---|
| id | UUID | primary key |
| meeting_id | UUID | foreign key → meetings |
| speaker_id | UUID | who said it |
| content | TEXT | what was said |
| timestamp | TIMESTAMP | when it was said |
| sequence_number | INTEGER | order of lines |

### summaries
| Column | Type | Notes |
|---|---|---|
| id | UUID | primary key |
| meeting_id | UUID | foreign key → meetings |
| summary_text | TEXT | LLM generated summary |
| action_items | TEXT | extracted action items |
| created_at | TIMESTAMP | when summary was generated |

### users
| Column | Type | Notes |
|---|---|---|
| id | UUID | primary key |
| email | VARCHAR | unique |
| name | VARCHAR | display name |
| created_at | TIMESTAMP | when account created |

### meeting_participants
| Column | Type | Notes |
|---|---|---|
| meeting_id | UUID | foreign key → meetings |
| user_id | UUID | foreign key → users |
| role | VARCHAR | host/participant |

---

## Hardest problems

### 1. Speaker diarization
Separating overlapping voices and correctly attributing each
line of transcript to the right speaker in real time.
Hard because: accents, background noise, multiple people
talking at once, new speakers joining mid-meeting.

### 2. Real-time latency
Audio chunk → STT → WebSocket push → browser render
must happen in under 2 seconds. Every step adds latency.
STT model inference on GPU is the biggest bottleneck.

### 3. Scale
10,000 simultaneous meetings = 10,000 audio streams being
processed at the same time. Each needs its own STT pipeline,
WebSocket connection, and storage writes.
Solution: horizontal scaling of audio ingestion and STT services.

---

## Failure modes

| Failure | User impact | Mitigation |
|---|---|---|
| STT model goes down | Transcription stops | Fallback to backup STT provider |
| WebSocket drops | User stops seeing live transcript | Auto-reconnect, replay missed lines |
| LLM unavailable | No summary generated | Queue the request, retry when available |
| Storage goes down | Transcript lost | Write to multiple replicas |

---

## Key design decisions

| Decision | Why |
|---|---|
| WebSockets not polling | Polling wastes resources, adds latency |
| Async LLM summarization | User doesn't wait during meeting |
| Elasticsearch for search | PostgreSQL text search too slow at scale |
| Chunked audio processing | Can't wait for full meeting to end before transcribing |
| GPU for STT | CPU inference too slow for real-time requirements |

---

## How this differs from LinkLite

| Aspect | LinkLite | Otter.ai |
|---|---|---|
| Data type | URLs | Audio + text |
| Real-time | No | Yes — WebSockets |
| AI component | None | STT model + LLM |
| Storage | PostgreSQL + Redis | PostgreSQL + object storage + Elasticsearch |
| Hardest problem | Scale redirects cheaply | Speaker diarization at scale |