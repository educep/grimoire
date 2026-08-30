---
name: review
description: The review method — how to scope a review, how to rate what you find, how to report it, and how findings are disposed. Loaded by every caller that reviews: a dispatched reviewer agent, an in-session slash command, or an orchestrated review stage. Use when reviewing a diff, a file, or a branch. It does NOT decide where the report is written, and it does NOT hold the project's checklist.
---

# Review

> **Adapter first.** Read the adapter's `reviewer` capability before acting. It supplies the
> **project's checklist** (what to hunt for in *this* stack), the severity scale if the project
> overrides the default, the triage dispositions, and the fix-round cap. This skill supplies the
> method around that checklist. Defaults are given inline where the capability is silent.

This skill owns **how to review**. It deliberately owns neither of the two things that vary:

- **What to hunt for** is the adapter's, because a Django checklist is worthless in a Rust project.
- **Where the report goes** is the *caller's* — see below, which is the most important section here.

______________________________________________________________________

## The persistence contract — every caller declares it, even when the answer is "nowhere"

A review has three legitimate homes and they are not interchangeable:

| caller | who writes the report | where |
|---|---|---|
| a reviewer **agent**, dispatched programmatically | **nobody** — it *returns* the report | the caller decides |
| a **slash command** run by a human in-session | the command | a path the human gave, or printed |
| an **orchestrated review stage** | the **orchestrator**, from the returned findings | a phase-keyed artifact path |

**A caller that says nothing about persistence is a defect in that caller**, not a question to
resolve at runtime.

*Measured in the host project, 2026-08-29. The agent definition said nothing about files while the
workflow command told the orchestrator to save what the agent returned — and a note in the agent
claimed the two were "kept in sync". An executor dispatched the agent and then polled the reviews
directory **191 times** for a file it was itself responsible for writing. Each poll re-read the whole
conversation. Nothing terminated the loop; a human noticed it.*

Two rules follow, and they are cheap:

1. **If you are dispatched and told nothing about a file: return the report and write nothing.** Do
   not infer a path from convention. Do not poll for one.
2. **If you are waiting on a dispatched reviewer, await its RETURN VALUE.** A subagent's report
   reaches you as what it returns; writing a file is something a prompt can *ask* for, never
   something a dispatch *guarantees*. Running the same read-only command twice with no state change
   in between is the signal that you have made this mistake.

______________________________________________________________________

## Scope: you are told WHAT CHANGED, never WHAT TO LOOK FOR

Give the reviewer the diff range and the changed-file list, and stop. A prompted reviewer narrows to
its hunt list and **stops enumerating**; an unprompted one re-derives the whole surface. Run after
run, the most severe finding comes from the reviewer stepping *one door outside* the pointed scope.

If your prompt hands you a hunt list anyway, that prompt is defective — **enumerate the full
checklist regardless**.

On a re-review, the only legitimate prior context is the **already-resolved** findings, so settled
ground is not re-litigated. A list of suspicions is not legitimate context.

**Name the orchestrator's own commits as the least-trusted part of the diff.** The orchestrator is
usually the one actor whose output is neither schema-validated nor adversarially verified, and it
also writes the durable record.

______________________________________________________________________

## Rate by REACHABILITY, not by shape

A dangerous-looking construct no caller can reach is not a catastrophe — say what makes it
unreachable and rate it accordingly. A boring-looking line on a live door outranks an alarming one
behind a method-not-allowed.

State reachability explicitly for every high-severity finding. "Who can trigger this, and how?" is
the question that separates a finding from a shape.

**Latent is not harmless, and it is not zero.** Protection that is a property of the *caller* — an
`if request:`, a router that sends writes elsewhere, an override that happens to overwrite the value
— is one careless caller away from live, and no test notices the day it changes.

______________________________________________________________________

## Prefer a plant to an inspection

Where a claim can be tested by mutating the code and running the suite, **do that instead of
reasoning about it**. Plant the defect, watch the guard fail, restore, watch it pass. A mutation
beats an assertion, including the author's and including yours.

*In one four-phase sweep, four of the ten defects found in a guard were found by a one-line plant;
none was found by reading.*

Two corollaries the same sweep paid for:

- **When you review a fix to a detector, plant the shape the FIXED detector's new boundary
  excludes** — not the shape that motivated the fix. Four generations of one detector were each
  defeated by the shape immediately outside their new edge.
- **A copy-aside and its restore are one operation and must be written in one language.** Path
  resolution differs between shells and runtimes on the same machine, and a restore that silently
  fails leaves the next measurement running against mutated code.

______________________________________________________________________

## Severity scale (default — the adapter overrides)

| Level | Meaning |
|---|---|
| **CATASTROPHE** | Data loss, security breach, crashes in production |
| **DISGRACE** | Wrong behaviour, missing authorization, pathological queries |
| **EYESORE** | Code smell, missing types, style violation |
| **NITPICK** | Minor naming, missing docstring, dead code |

Projects commonly rename or decorate these; take the names from the adapter when it declares them.

______________________________________________________________________

## What to hunt for

**The project's checklist comes from the adapter's `reviewer` capability.** Apply every category it
declares; skip none.

These categories are stack-independent and apply *in addition*, because they are about the shape of
the code rather than the framework:

- **A guard that asserts member compliance instead of set equality** — it goes green the day it
  stops seeing things, which is indistinguishable from success.
- **A guard whose predicate is structural where the risk is behavioural** — "a filter exists"
  instead of "the filter excludes the attacker's row".
- **A population derived from a naming convention or a hand-maintained literal** rather than from
  what the thing *is*.
- **A fix that removes something from a guard's population without a replacement pin in the same
  commit** — the fix and the loss of coverage arrive together, and the suite gets *greener*.
- **An exemption keyed less specifically than the risk varies** — the entry grants more than its
  justification claims.
- **Claim truth**: a comment, docstring, disposition or count that asserts something the code does
  not do, or a citation that does not resolve. No gate catches this class.

______________________________________________________________________

## Output

Produce the prose report in whatever shape the adapter declares, **and always also return a
machine-triagable list** — `(severity, file, one-line summary)` per finding. A caller that has to
parse your narrative will parse it wrong.

Quote an exact `file:line` for every finding. Give a concrete fix, not a complaint. For every
high-severity finding, state its reachability.

______________________________________________________________________

## Triage dispositions (default — the adapter overrides)

- High severities → **always actionable**.
- Lowest severity, verified real and cheap → fold into the current fix round.
- Lowest severity, real but not worth doing now → **recorded**, marked *not scheduled*, with the
  reason.
- Refuted → rejected, with the refutation. Prefer refutation by execution.
- Genuinely deferred work → an entry in the project's backlog.

**Recording is total; the round cap gates the FIXING, never the recording.** A finding parked only
in a report nobody opens is indistinguishable from a finding that was dropped.

**A disposition is a claim about the tree.** Write "fixed" only after re-reading the file, never from
the intent that produced the edit — three dispositions written from intent in one review were all
measured false by the next pass.
