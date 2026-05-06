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

![alt text](image.png)

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
