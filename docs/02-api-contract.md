# LinkLite API Contract

## Endpoints

### 1. POST /v1/links

**Purpose:** Create a new short link
**Request:**

```json
{
  "original_url": "https://google.com",
  "custom_slug": "my-link"
}
```

**Response:** Returns the created link object
**Status codes:**

- 201 Created → link created successfully
- 400 Bad Request → invalid URL sent
- 409 Conflict → slug already taken
  **Idempotent?** No
  **Auth required?** Yes

---

### 2. GET /v1/links/{id}

**Purpose:** Retrieve details of a specific short link
**Request:** No body. {id} in the URL is the link's unique ID
**Response:** Returns link details on success
**Status codes:**

- 200 OK → link found and returned
- 404 Not Found → link doesn't exist
- 401 Unauthorized → not authenticated
  **Idempotent?** Yes
  **Auth required?** Yes

---

### 3. GET /{slug}

**Purpose:** Redirect user to the original URL
**Request:** No body. slug is the short code in the URL
**Response:** No body — just redirects
**Status codes:**

- 302 Found → redirect to original URL
- 404 Not Found → slug doesn't exist
- 410 Gone → link existed but has expired
  **Idempotent?** Yes
  **Auth required?** No

---

### 4. GET /v1/links/{id}/stats

**Purpose:** Return click analytics for a link — total clicks,
clicks per day, referrer sources
**Request:** No body. {id} in URL. Pagination via query params:
?page=1&limit=20 (default limit: 20)
**Response:** Paginated list of click stats
**Status codes:**

- 200 OK → stats returned successfully
- 404 Not Found → link doesn't exist
- 410 Gone → link existed but has been deleted
- 401 Unauthorized → not authenticated
  **Idempotent?** Yes
  **Auth required?** Yes

---

### 5. DELETE /v1/links/{id}

**Purpose:** Delete an existing short link
**Request:** No body. {id} in the URL is the link's unique ID
**Response:** Empty body on success
**Status codes:**

- 204 No Content → deleted successfully
- 404 Not Found → link doesn't exist
- 401 Unauthorized → not your link
  **Idempotent?** Yes
  **Auth required?** Yes

---

## Key design decisions

- Redirect status code: 302 — browser always checks server first,
  analytics captured every click
- API versioning: /v1/ prefix — old clients won't break when we release v2
- Pagination: applied on /stats endpoint, default limit 20 rows
