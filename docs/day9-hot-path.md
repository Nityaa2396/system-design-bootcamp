# Day 9 — Hot Path Analysis

## What is the hottest path?

GET /{slug} — every single redirect hits this.
It's the core product — if this is slow, everything is slow.

## What query powers it?

SELECT \* FROM links WHERE short_code = ? AND is_deleted = false

## What makes it fast?

Unique index on short_code — Postgres uses B-tree to jump
directly to the right row instead of scanning the whole table.

## What would make it slow?

Without the index, every redirect would do a full table scan
across millions of rows. At scale that's seconds, not milliseconds.
