# ADR-0001: Slug Generation Strategy

## Status

Accepted

## Context

LinkLite needs short, unique, URL-safe identifiers for every link.
The slug is the core of the product — it appears in every short URL
and is looked up on every redirect.

## Decision

Use random base62 (a-z, A-Z, 0-9) with 6 characters.
Auto-retry up to 5 times on collision before failing.

## Alternatives considered

- **Sequential IDs + encoding** — predictable, attackers can enumerate all links
- **UUID-derived** — too long, not human friendly
- **User-supplied only** — puts burden on user, no fallback

## Consequences

### Positive

- 56 billion possible combinations — collision probability is very low
- Not sequential — harder to enumerate other users
