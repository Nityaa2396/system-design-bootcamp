started day 1 of system design bootcamp - had no idea what a url shortener
even was before today. watched the bytebyteGo video and it clicked pretty fast.
learned the difference between functional and non-functional requirements -
basically what a system does vs how well it does it. figured out that redirects
need to be fast because high read traffic can break user experience at scale.
also learned that no rate limiting = one user can crash your whole db.
small things that teams forget but actually matter a lot.

day 2 - learned what a REST api is - REST is a specific style of api
that uses http methods like GET POST DELETE, urls as resource names,
and status codes as responses. its the most common style used in web backends.biggest thing that clicked today was
status codes - they are not random numbers, every range means something.
2xx worked, 3xx go somewhere else, 4xx you messed up, 5xx server broke.

also learned why 302 and not 301 for redirects - 301 caches in the browser
forever so you lose every click from analytics. 302 always checks the server
first so you stay in control.

pagination was new - never return all rows at once, always break it into
pages otherwise the server breaks under load.

designed 5 endpoints for linklite today - create, read, redirect, stats, delete.
starting to see how each design decision has a reason behind it.

day 3 - data modeling and indexes. learned that designing tables is not
just about storing data - its about knowing how that data will be searched
and fetched later.

biggest thing that clicked today - indexes are not free. every index you
add slows down writes because the db has to update the index every time
you insert or update a row. so you only index columns you actually search by.

learned why click_events will become the heaviest table in linklite -
every single click adds a row. billions of rows over time. thats why
daily_link_stats exists - pre-calculate once, read instantly.

also learned that storing raw ip addresses is a privacy violation -
you hash it first so you can detect duplicate clicks without identifying
the actual person.

three tables designed today - links, click_events, daily_link_stats.
starting to see how each table serves a specific purpose and how they
connect to each other through foreign keys.

![alt text](image.png) - Day-4

day 4 - transactions and correctness. learned that ACID is not just a
concept - it directly maps to real problems in linklite.

biggest thing that clicked today - not every problem needs a transaction.
slug conflicts are handled by a unique constraint, click counts are handled
by atomic sql updates. transactions are for when partial writes would leave
the database in a broken state.

learned three new terms that sound scary but aren't - race condition is just
two things editing the same data at the same time and one change getting lost.
orphan row is data that got created but the user never knew it succeeded.
soft delete is setting is_deleted = true instead of actually removing the row.

also learned that eventual consistency is okay for some data - click counts
being slightly off is fine. but slug ownership and link creation must be exact

- user needs to know for sure if their link exists or not.

starting to think about data in two buckets - what must be correct instantly
and what can be slightly delayed.

Day- 5
![alt text](image-1.png)

day 5 - caching basics. learned that cache-aside is a reactive approach

- you don't pre-load the cache, you populate it on the first request and
  serve everyone else from there.

biggest thing that clicked today - cache is not free storage. redis keeps
everything in memory so it's fast but expensive and not permanent. if redis
restarts without a db backup, your data is gone. that's why raw click events
stay in postgresql and only summaries go into cache.

learned what ttl is - a timer on every cached item. without ttl, stale data
lives forever. a deleted link could still redirect users to the wrong place
for days.

designed 3 cache entries for linklite - short code lookup, hot stats summary,
and rate limit counters. each one has a clear key, ttl, and invalidation rule.

rule that stuck: cache what gets read often and changes rarely.
don't cache what gets written constantly or must always be exact.

Day - 6 ![alt text](image-2.png)

day 6 - scaling basics. learned the difference between vertical and
horizontal scaling. vertical means bigger machine - easy but has a
hardware ceiling and one point of failure. horizontal means more machines

- resilient, scales indefinitely, but requires the app to be stateless first.

biggest thing that clicked today - stateless doesn't mean the app has no
state. it means state lives somewhere shared like redis, not on the server
itself. that's what makes it possible for any server to handle any request.

learned 3 load balancing algorithms - round robin takes turns, least
connections picks the least busy server, ip hashing sends the same user
to the same server every time.

sticky sessions are unnecessary for linklite because the app is stateless.
sessions live in redis so it doesn't matter which server you hit.

redirects are easy to scale - stateless cache reads. analytics are hard
to scale - heavy aggregation across millions of rows. that difference matters
when designing for growth.

day 7 - diagramming with c4 model. learned that diagrams have levels -
you don't draw everything at once. context level shows your system and
what's around it. container level zooms in and shows what's inside.

drew three diagrams for linklite today - context, container, and the
redirect sequence flow. the sequence diagram made the cache-aside pattern
click visually - cache hit means db never gets touched, cache miss means
db gets queried and result gets stored for next time.

biggest takeaway - diagrams are a communication tool. the goal is for
anyone to look at it and understand the system without reading a single
line of code.

don't need to memorize mermaid syntax - need to know what to draw
and why. syntax is always a lookup away.

Week 1 — LinkLite Design Journey

![alt text](image-3.png)

day 13 - rate limiting. learned that without a limit one user can create
millions of links and crash the database. the fix is simple - store a
counter in redis with a daily ttl and reject requests once the limit is hit.

redis makes this cheap - incrementing a counter is one operation,
reads are instant. no db involved at all.

tested it by firing 11 requests in a loop - first 10 succeeded,
11th got 429 rate limit exceeded. exactly what we designed on day 1
when we said "no rate limit = one user crashes your db".

the limit is set to 10 for testing. in production this would be
higher - maybe 100 or 1000 per day depending on the use case.

starting to see how everything from week 1 docs is becoming real code now.
requirements → api design → data model → cache → rate limiting.
its all connected.
