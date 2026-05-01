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
