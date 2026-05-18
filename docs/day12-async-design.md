# Day 12 — Async Click Tracking

## Why async?

The redirect must be instant. Recording a click involves a DB write
which takes time. Doing it synchronously would slow down every redirect.
Background tasks let us redirect the user immediately and record the
click after the response is sent.

## What is the failure mode if the background task crashes?

The user still gets redirected successfully. The click just doesn't
get recorded. We lose that one data point silently.

## Is losing a click acceptable?

Yes — click counts are eventually consistent. Losing one click out
of thousands is acceptable. What's not acceptable is slowing down
the redirect to guarantee every click is recorded.
