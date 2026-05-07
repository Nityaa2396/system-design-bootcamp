# LinkLite Diagrams

## 1. Context Diagram

```mermaid

  title System Context — LinkLite

  Person(user, "User", "Creates short links and shares them")

  System(linklite, "LinkLite", "URL shortening service")

  System_Ext(safebrowsing, "Google Safe Browsing", "Scans URLs for malicious content")

  Rel(user, linklite, "Creates and clicks short links")
  Rel(linklite, safebrowsing, "Validates URLs before storing")
```

## 2. Container Diagram

```mermaid
C4Container
  title Container Diagram — LinkLite

  Person(user, "User", "Creates and clicks short links")

  System_Boundary(linklite, "LinkLite") {
    Container(api, "API Server", "FastAPI", "Handles all requests")
    Container(db, "PostgreSQL", "Database", "Stores links and click events")
    Container(cache, "Redis", "Cache", "Caches short code lookups and rate limits")
    Container(worker, "Background Worker", "Python", "Processes click events async")
  }

  System_Ext(safebrowsing, "Google Safe Browsing", "Scans URLs")

  Rel(user, api, "Makes requests", "HTTPS")
  Rel(api, db, "Reads and writes", "SQL")
  Rel(api, cache, "Cache reads and writes", "Redis protocol")
  Rel(api, safebrowsing, "Validates URLs", "HTTPS")
  Rel(worker, db, "Writes click stats", "SQL")
```

## 3. Sequence Diagram — Redirect Flow

```mermaid
sequenceDiagram
  actor User
  participant LB as Load Balancer
  participant API as API Server
  participant Redis
  participant DB as PostgreSQL

  User->>LB: GET /abc123
  LB->>API: Forward request
  API->>Redis: GET link:abc123
  alt Cache hit
    Redis-->>API: Return original URL
  else Cache miss
    Redis-->>API: nil
    API->>DB: SELECT original_url WHERE short_code = abc123
    DB-->>API: Return original URL
    API->>Redis: SET link:abc123 TTL 1hr
  end
  API-->>LB: 302 redirect to original URL
  LB-->>User: 302 redirect
```
