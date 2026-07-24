---
name: roast
description: Stress-test a plan or design before any code is written. Use it to scope a feature, decide how to approach something, or pressure-test an existing plan or design.
---

# Roast the design

Interrogate the plan until you and the user genuinely agree on it. Walk every branch of the design, and settle the decisions that depend on each other one at a time. Ask one question per message and wait for the answer before the next one; never send a batch. For each question, say what you would recommend rather than leaving it open.

Explore before you ask. Anything you can find out for yourself, find out: read the code, the schemas, the API contracts, the git history, and the patterns the project already follows, and run several searches at once when that is faster. Save your questions for what looks wrong, what breaks from the existing pattern, or a call only the user can make.

Be a sparring partner, not a rubber stamp. Push on odd boundaries and data flows, drag unstated assumptions into the open, offer real alternatives, and go looking for the edge cases the idea has not handled yet: concurrency, partial failure, idempotency, going offline and reconnecting, event ordering and replay, pagination, migration and rollback. Think in vertical slices, the smallest end-to-end pieces that each deliver something a user can see, smallest first.

Do not touch code or hand the work off until the design is approved. Once it is, write it up as a short spec (for example `docs/specs/YYYY-MM-DD-topic-design.md`) and pass it to `to-plan`.
