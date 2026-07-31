---
name: mode-select
description: Choose how a piece of work should run — inline, a main-loop checklist, dispatched agents, or a background workflow — and re-choose as the work grows. Use before starting execution and again whenever the shape of the work changes.
---

# Select the mode — and keep selecting it

Four modes, one decision, revisited: **just-do-it inline** (one small change, main loop), a
**main-loop checklist** (sequential, human-confirmed steps), **dispatched agents** (`execute`:
parallel edit, sequential commit), or a **background workflow** (encoded pipeline with structured
returns and resume). Two rules pick between them; one rule keeps the pick honest.

## Rule 1 — authoring vs. applying (the safety axis)

*Authoring* — writing or changing files, plans, tests, docs, infra-as-code — may run in any mode,
parallel included. *Applying* — anything on the adapter's gated `apply` list: deploys, resource
deletes, production migrations, releases, DNS — **always** runs as a sequential, human-confirmed
checklist in the main loop, never inside a parallel or background run. The axis is not "code vs.
infra": a production migration is as irreversible as a `terraform apply`, and a `.tf` module edit is
as safe to parallelize as any refactor. Log every applied step's concrete outputs to the solutions
log so later sessions know the live state.

## Rule 2 — what a heavier mode actually buys

Background workflows do **not** buy more parallelism — the shared working tree and sequential commits
bound that identically in every mode. What they buy is: an encoded verify stage after every edit,
schema-validated returns, background execution with resume, and reproducibility. Dispatch buys
model-per-role economics: the orchestrator stops doing cheap mechanical work on an expensive model.
Pick the lightest mode that gives what the work needs — and remember the review-and-remediation loop
is main-loop-owned in every mode.

## Rule 3 — the decision goes stale; re-ask it

Choosing inline is often right for one small change, but the choice is about the work **as it is
now**, and it silently expires. Re-select the mode when any threshold is crossed: one slice becomes
several; a review returns more than a handful of findings; a second fix round starts; the touched
files spread across the codebase. **The tell is unmistakable: if you are hand-rolling what `execute`
describes — batching by hand, editing serially, commit after commit on the expensive model — the
mode decision is stale, and the answer is to switch, not to keep going.** This rule exists because a
real five-slice, five-review-round arc ran entirely by hand: the entry decision ("small one-off →
inline") was correct on day one and never re-asked.
