---
name: roast
description: Stress-test a plan or design before any code is written. Use it to scope a feature, decide how to approach something, or pressure-test an existing plan or design.
---

# Roast the design

Interrogate the plan until you and the user genuinely agree on it. Walk every branch of the design, and settle the decisions that depend on each other one at a time. Ask one question per message and wait for the answer before the next one; never send a batch. For each question, say what you would recommend rather than leaving it open.

Explore before you ask. Anything you can find out for yourself, find out: read the code, the schemas, the API contracts, the git history, and the patterns the project already follows, and run several searches at once when that is faster. Save your questions for what looks wrong, what breaks from the existing pattern, or a call only the user can make.

Be a sparring partner, not a rubber stamp. Push on odd boundaries and data flows, drag unstated assumptions into the open, offer real alternatives, and go looking for the edge cases the idea has not handled yet: concurrency, partial failure, idempotency, going offline and reconnecting, event ordering and replay, pagination, migration and rollback. Think in vertical slices, the smallest end-to-end pieces that each deliver something a user can see, smallest first.

Three shapes deserve a standing challenge. **A predicate written as "not X" admits every future
value** — a negation that should be an allowlist will silently include whatever states get added
later, and converting it is a prerequisite, not a follow-up. **A premise about what callers do is
verified by enumerating the callers**, not by checking a property of the data — a column's
constraints bound what a row can hold, not what every caller does with it. **A constraint's blast
radius is priced across every environment**: enforcing an invariant at the storage layer validates
against all existing data everywhere, and "production holds no bad rows" is a statement about one
environment. And a guard that is wrong in both directions is refused up front, with the refusal
recorded — a wrong guard is not safer than no guard; it is false assurance at the exact point the
design is least certain.

Do not touch code or hand the work off until the design is approved. Once it is, write it up as a short spec where the adapter's `artifact-paths` says specs live (for example `<specs-dir>/YYYY-MM-DD-topic-design.md`) and **return it to whatever invoked you** — where a command or another agent called this skill, go back to that caller and continue there. Only when this skill is running as a step of the standalone skill pipeline does the spec pass onward to `to-plan`; if a caller invoked you, handing off instead of returning skips the rest of that caller's work.
