# LinkLite Data Model

## Table 1: links

| Column         | Data Type   | Constraints      | Why                                   |
| -------------- | ----------- | ---------------- | ------------------------------------- |
| `id`           | UUID        | Primary Key      | Random, secure, unguessable           |
| `short_code`   | VARCHAR(10) | Unique, Not Null | Each slug must point to one link only |
| `original_url` | TEXT        | Not Null         | URLs can be very long                 |
| `created_at`   | TIMESTAMP   | Not Null         | When the link was created             |
| `expires_at`   | TIMESTAMP   | Nullable         | Optional expiry                       |
| `is_deleted`   | BOOLEAN     | Default false    | Soft delete — don't remove from DB    |

**Indexes:**

- `id` → Primary Key index
- `short_code` → Unique index — every redirect searches by this

---

## Table 2: click_events

| Column       | Data Type | Constraints            | Why                       |
| ------------ | --------- | ---------------------- | ------------------------- |
| `id`         | UUID      | Primary Key            | Every row needs unique ID |
| `link_id`    | UUID      | Foreign Key → links.id | Which link was clicked    |
| `clicked_at` | TIMESTAMP | Not Null               | Exact time of click       |
| `ip_hash`    | VARCHAR   | Nullable               | Hashed IP — privacy safe  |
| `user_agent` | TEXT      | Nullable               | Browser/device info       |
| `referer`    | TEXT      | Nullable               | Where the click came from |

**Indexes:**

- `id` → Primary Key index
- `link_id` → every stats query filters by this
- `clicked_at` → queries like "clicks today" filter by date

---

## Table 3: daily_link_stats

| Column    | Data Type | Constraints            | Why                         |
| --------- | --------- | ---------------------- | --------------------------- |
| `link_id` | UUID      | Foreign Key → links.id | Which link                  |
| `day`     | DATE      | Not Null               | Which day the stats are for |
| `clicks`  | INTEGER   | Default 0              | Total clicks that day       |

**Indexes:**

- `link_id` + `day` → composite index — every stats query filters by both

---

## Index decisions summary

| Table            | Column        | Index type  | Reason                       |
| ---------------- | ------------- | ----------- | ---------------------------- |
| links            | id            | Primary Key | Default lookup               |
| links            | short_code    | Unique      | Every redirect hits this     |
| click_events     | id            | Primary Key | Default lookup               |
| click_events     | link_id       | Regular     | Stats queries filter by link |
| click_events     | clicked_at    | Regular     | Date range queries           |
| daily_link_stats | link_id + day | Composite   | Pre-aggregated stats lookup  |

---

## Key questions

**Why must short_code be unique?**
Each short code must point to exactly one link. If two links shared
the same short code, the server wouldn't know which URL to redirect to.

**Why will click_events become huge over time?**
Every single click on every single link adds one row. At scale that's
billions of rows over months. Needs an archiving strategy.

**Why is counting clicks from raw click_events bad?**
Performance. Counting 100 million rows every time someone views analytics
is too slow. daily_link_stats pre-calculates the count once per day —
reading one number is instant.
