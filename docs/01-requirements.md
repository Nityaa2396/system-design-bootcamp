# LinkLite Requirements

## Problem statement

Users should be able to create short URLs and share them.

## Functional requirements

- Create short URL from long URL
- Redirect from short URL to original URL
- Support custom slug (optional)
- Track click counts
- Show basic analytics per short link

## Non-functional requirements

- Redirect should be fast
- Reads will be much higher than writes
- Analytics can be delayed
- Service should tolerate retries safely

## Constraints / assumptions

- Single region for v1
- Internal/private demo only
- 1k DAU assumed
- 95% of traffic is redirects

## Out of scope

- Auth / social login
- Billing
- Multi-region HA
- Advanced dashboards

## Success metrics

- Create short link works reliably
- Redirect latency feels fast locally
- Basic click counts visible

## 5 questions I'd ask a PM before building this for real

1. What happens when two users request the same custom slug simultaneously — first wins, or error to both?
2. Do we scan destination URLs for malicious content before accepting them?
3. Do short links expire? Is TTL configurable per link or global?
4. What should users see if the destination URL is down — redirect anyway or show an error?
5. Is there a rate limit on how many links one user can create to prevent abuse?

## 3 hidden constraints teams usually forget

1. Cost — storing click_events for every redirect at scale becomes the
   most expensive part, not the links themselves. Need an archiving
   strategy before launch, not after.

2. Reliability — the redirect is the core product. If the DB or cache
   serving short_code → original_url goes down, every short link in
   the world that uses LinkLite breaks. This one path needs the highest
   uptime guarantee.

3. Security — sequential or predictable short codes let attackers
   enumerate all links (guess abc123, try abc124, abc125...).
   Short codes must be randomly generated, not sequential.
