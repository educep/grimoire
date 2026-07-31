---
name: execute
description: Run an approved plan of issues into committed work — parallel agents edit, the main loop commits, correctness is verified. Use after to-issues, when a plan is sliced and you need to build it safely with subagents.
---

# Execute the plan

Turn a sliced plan into committed work. Many agents **edit in parallel**; the **main loop commits
sequentially**; correctness is checked as each edit lands. Nothing here names a language, tool, or
command — every specific comes from the repo's adapter (`.claude/project-adapter.md`, see
`ADAPTER_CONTRACT.md`). Read the adapter first; it is law. If a repo has none, draft one from its
docs before running.

## First, decide this is even the right mode

If a step would run anything on the adapter's gated `apply` list — a deploy, a resource delete, a
production migration, a release — it does **not** belong here. Hand it to `mode-select`, which routes
live-state changes to a human-confirmed, sequential checklist. This engine only ever *authors*
(edits, tests, structured returns); it never *applies*.

## Notice when the work outgrows the main loop

Deciding to just do something inline is often right for one small change — but that
decision goes stale. Re-ask it as the work grows: when a slice becomes several, when a
review comes back with more than a handful of findings, when a second fix round starts, or
when the files touched spread across the codebase. **If you find yourself hand-rolling
what this skill describes — batching by hand, editing serially, commit after commit — that
is the signal to switch modes, not to keep going.** The cost of missing it is real: the
orchestrator becomes the bottleneck and does cheap mechanical work on an expensive model.

## Check your preconditions before dispatching

Confirm the things the run depends on are actually there, rather than finding out mid-flight: the
adapter's `verify` setup is up (a database container, a service), and — importantly — **every named
agent type or persona you intend to dispatch actually resolves, checked now, not assumed from
memory**. A name that fails to resolve does not fail loudly; it quietly degrades into a generic
agent, and you get a weaker review that reads like a real one. The failure has two causes, and the
subtler one is real: the name was never registered, or the definition file exists but has been
corrupted — e.g. a formatter mangling its frontmatter — so it no longer parses. If a name doesn't
resolve, say so and name the fallback you're using instead of silently substituting it.

## Batch the work

Group the plan's issues into batches, using the adapter's `module-topology`:

- **Feature-organized** → a vertical slice is already file-disjoint; keep it whole and run its issues
  in parallel.
- **Layer-organized** → vertical slices collide on shared files; split into **file-disjoint** groups
  so no two parallel agents touch the same file, and recombine at the PR boundary so the *phase*
  stays demoable even when a *batch* isn't.
- **Multi-repo** → each repo is its own scope; the cross-repo feature is the vertical, per-repo work
  its sub-slice.

The batch is the unit of parallelism. **Two issues share a batch only if their file sets are
disjoint** (and neither's output is the other's input). If they overlap, they are two batches. Order
smallest-first, but any batch whose dependencies are all done is fair to run — work the frontier.

## Run a batch

For each issue in the batch, launch one **implementer** agent (adapter `model-per-role.implementer`
— the cheap one) with a **self-contained** prompt: everything it needs, assuming it has read nothing
else. Each implementer:

- edits only its assigned, disjoint files; consults `docs-lookup` before non-trivial API use;
- **runs no git, and never writes a `shared-files` entry** — it surfaces that content in its return;
- ends in a `format`-clean state with `verify` passing on its slice — **but if `verify` runs against
  shared infrastructure (one test database, one service), parallel agents must not each run it: two
  concurrent full suites will wreck the shared state. Agents verify their subset at most; the main
  loop owns every full verification run**;
- returns a **structured contract** (validated against a schema, not free prose): the issue id, the
  exact files it touched, the intended commit message, a status, and notes for the human.

When correctness matters (money, tenancy, idempotency, anything the adapter's `constraints` flag),
make it a pipeline: **edit → verify**, the verify stage on the judgment model
(`model-per-role.domain-verify`), so each edit is checked the moment it lands instead of hoping
someone remembers to.

## Commit (main loop only)

**A dispatched agent's completion is not evidence.** Before committing anything from a batch, the
main loop inventories the working tree itself (what actually changed, versus what the contracts
claim) and **re-runs the gates itself** — `format`, `verify`, whatever the adapter's commit hooks
enforce — regardless of what any agent reported. Agents can die holding the field: a crashed agent's
diff is an **unreviewed draft**, not work in progress, even if it happens to be green. One real
implementer fixed 13 of 16 findings flawlessly and then died mid-task, leaving a 20-file diff its
author never linted, typed, or tested; the tree being green was luck, and the re-run is what turns
luck back into process.

Then the main loop commits **one issue at a time**, per `git-conventions`, from the returned
contract: stage exactly that issue's files, commit with its message. The other agents' uncommitted
edits stay in the tree, untouched, for the next commit. This sequential-commit-over-a-shared-tree is
the only race-free model — a stray checkout from a parallel agent would derail the others.

Then, as part of the same commit phase and not as an afterthought: apply any `shared-files` content
the agents surfaced, tick the plan's progress markers, and append what happened to the solutions log
— what shipped, what the work uncovered, what an operator must know, what is still open. These are
not paperwork; they are the only durable state a cold session can resume from, and they get written
reliably **only because the loop contains them**. Left as a habit at the end of a long day's work,
they are simply forgotten.

## Review, then remediate

At the phase boundary the main loop runs `review-gate` with the adapter's `reviewer` — the full
method lives in that skill: checkpoint-commit the reviewed tree first, prefer findings verified by
execution, attack the previous round's fixes and their interactions hardest, check every fix at the
layer the user sees, and end every finding either fixed or journaled by explicit decision. Fixes run
on the judgment model (`model-per-role.fixer`) as a normal batch — edit, no git — and the main loop
commits them **through the same gates as any batch**. Cap the re-review rounds; anything still
unfixed after the cap is journaled and flagged loudly, never silently dropped. Review, fix commits,
and journaling are **all main-loop-owned** — never buried inside a background run, which can't
pause, commit, or journal.

## When a batch won't land

Don't retry the same move blindly. Fixing a single failing task is the inner loop (bounded attempts
with the findings in hand). If a batch still won't land, hand the **remaining** plan to
`adaptive-replanning`: re-derive what to do next from the current state, carrying the failure's cause
as a lesson — reorder, split, insert a prerequisite, or stop and say why. Finished work is left
alone; the failure is a route now known to be blocked.

## Resume

Durable state is the **plan + progress markers + solutions log + git** (the adapter's
`artifact-paths`), never the tool. A fresh session reads those and continues from the first
unfinished item. Log concrete outputs so later sessions know the live state.

## The lines that never move

- The main loop owns **all git** and **all `shared-files`** writes. Agents edit and return; the main
  loop applies.
- Gated `apply` steps never run here — `mode-select` gates them.
- Structured schema returns only — commit correctness never depends on parsing prose.
- Cheap model for bulk edits; judgment model for review, fix, and domain-verify. Never one model for
  everything.
