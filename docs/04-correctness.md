# LinkLite Correctness and Transactions

## Scenario 1: Duplicate custom slug

**Failure mode:** Two users create the same slug simultaneously —
without a constraint, both succeed and one overwrites the other
**Transaction needed?** No — unique constraint on short_code handles it
**Retry safe?** Yes — second user gets 409, can pick a different slug
**Eventual consistency ok?** No — slug ownership must be exact, not approximate

## Scenario 2: Timeout after row created

**Failure mode:** Row saved in DB but server crashes before response
is sent — user sees an error but the row already exists (orphan row)
**Transaction needed?** Yes — wrap create in a transaction so partial
writes get rolled back
**Retry safe?** Yes — system detects row already exists and returns it
**Eventual consistency ok?** No — user must know if their link was
created or not

## Scenario 3: 1000 simultaneous clicks

**Failure mode:** Race condition — two clicks read count as 500,
both write 501, one increment is lost
**Transaction needed?** No — atomic SQL update handles it:
UPDATE links SET click_count = click_count + 1 WHERE id = ?
**Retry safe?** Yes
**Eventual consistency ok?** Yes — click count being slightly
delayed or approximate is acceptable

## Scenario 4: Delete during redirect

**Failure mode:** Link deleted while redirect traffic still arriving —
server tries to fetch a row that no longer exists and crashes
**Transaction needed?** No
**Retry safe?** Yes
**Eventual consistency ok?** Yes — soft delete sets is_deleted = true,
redirect returns 410 Gone cleanly

## Conclusion

**Data that must be exact:** slug uniqueness, link ownership
**Data that can be approximate:** click counts, analytics stats
