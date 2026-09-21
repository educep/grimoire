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

Corollaries, each paid for:

- **When you review a fix to a detector, plant the shape the FIXED detector's new boundary
  excludes** — not the shape that motivated the fix. Four generations of one detector were each
  defeated by the shape immediately outside their new edge.
- **A copy-aside and its restore are one operation and must be written in one language.** Path
  resolution differs between shells and runtimes on the same machine, and a restore that silently
  fails leaves the next measurement running against mutated code.
- **A green positive control is a claim about the CONTROL first and the guard second.** Before
  concluding a guard is inert, check that the thing you re-enabled is the thing the assertion
  actually reads. Restoring the *container* is the easier edit and the one that comes to mind, and
  it proves nothing about an assertion naming the *contained* thing — one control re-added a route
  prefix while the assertion fetched a specific path beneath it, so the mutation landed, was real,
  and changed nothing the test could see. "I re-added the route" and "I re-added the route the test
  fetches" are different acts with the same commit message.
- **Before calling a patch, stub or re-export a decoy, check the target's SHAPE.** A *traversal*
  target — walking to a shared object and setting an attribute on it — mutates one object for every
  caller everywhere, so no decoy is possible and retargeting it is readability, not correctness. A
  *name-binding* target — a module constant, an imported name, an attribute of one module's own
  namespace — rebinds only there, so the decoy is real and the claim owes a governance pair: the new
  target observably governs, the old one demonstrably does not, at least one direction red-proved by
  sabotage. When code has MOVED, the outcomes are not distinguishable by reading: some targets
  survive, some fail loudly at patch time, and one stays alive only because an unrelated import
  keeps the old name resolvable. That last is the dangerous one, and only running the sibling suites
  finds it.
- **A sentence claiming a guard FORBIDS something is a claim about the guard, and it wants a plant
  like any other.** Write the thing the sentence says is impossible, run it, and ship the plant
  beside the sentence. The worst instance on record sat one screen below the fix that was supposed
  to have made it true — written by that fix.

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
- **A new instance of a shared infrastructure primitive** — a cache, a queue, a connection pool, a
  storage alias — added beside an existing one. Diff the configuration, not just the new code: a
  component that depended on the default instance can be silently repointed at a per-process one,
  and the thing that breaks is usually a limiter or a lock whose whole value was being shared.
- **Prose crossing a service boundary where a flag belongs** — a message composed by the layer that
  does not know the reader, or a branch taken on whether a message *contains* some words. What
  crosses a boundary is a machine-readable signal; the sentence is written on the side that knows
  the user, and branching on copy breaks the day the copy is translated or reworded.
- **Claim truth**: a comment, docstring, disposition or count that asserts something the code does
  not do, or a citation that does not resolve. No gate catches this class.

______________________________________________________________________

## How to falsify a written claim

No gate catches a false sentence, so this is the reviewer's class alone. Five failure modes, each
measured, each cheap to check once you know its shape:

- **Verify the CAUSAL half, not the checkable half.** *"X, therefore Y"* is two claims and they are
  never equally cheap. The temptation is to confirm the half a search answers — the cited line is
  where it says it is — and treat the sentence as verified. One of the worst findings on record was
  exactly this: the cited gate existed at the cited line, and could not produce the effect claimed,
  because the state the claim assumed never occurs on that path. **Reachability is the usual shape:
  does control actually get there, in the state the claim assumes?**
- **A real mechanism is not necessarily THIS path's mechanism.** Corrected prose loves to name a
  genuine mechanism that is not the one reached here. Two questions, not one: *is the mechanism
  real?* — usually yes — and *is it the one this path executes?* One round produced six instances,
  every one passing the first question and failing the second.
- **A search can match your own correction and read it as the defect surviving.** A census over
  prose counts the errata note you just wrote, because correction-tracking documents are made of
  quotations. Open the hits and read their surroundings before counting them; a bare count cannot
  distinguish an occurrence from a quotation of one. The inverse bites too — a case-sensitive census
  that misses a differently-cased instance produces a false *absolute*.
- **Authority does not decide which of two disagreeing copies is stale; a re-measurement does.**
  The artifact that looks authoritative — the pin's documentation, the header, the reviewer's own
  instruction — is a copy like any other. One review found a figure stated three ways against a
  guard's documentation and prescribed taking the guard's number; three re-runs measured the other
  value, and following the instruction would have written a wrong number into four places under the
  guard's authority.
- **Check a claim that the law is SILENT before acting on it — hardest when the silence favours the
  claimant.** "The rule doesn't cover this" converts a deviation into a documentation task and skips
  the argument entirely. One proposal to fill such a gap would have destroyed the property it was
  written to serve — and the rule was not silent; it said the opposite, twice, in the file the
  proposer had open. Weight the check by who benefits. *Companion*: attribution is a claim too. A
  quotation reported as fabricated was verbatim and real, just misattributed to the wrong file —
  both readings cost work, so cite the file you actually read, and when a quotation "isn't there",
  consider that it may be somewhere else before calling it invented.
- **A document's SILENCE is not a measurement of the world.** An unticked box, a missing row, an
  absent entry records what somebody wrote down — not what exists — and reading it as absence
  converts a missing RECORD into a missing THING. *(Measured: a readiness audit filed "there is no
  production administrator account" as a launch blocker, citing a plan's unticked box; the account
  existed and two people had been signing in with it for weeks.)* A negative claim about the
  environment needs a query, a listing or an attempt — never a file's quiet. Where the environment
  genuinely cannot be measured from where you stand, the finding is written as *"unverified: the
  box is unticked"* and routed to its owner as a question, never filed as a blocker. It is the
  structural-graph rule one level up: **never evidence for a negative.** *Corollary for whoever
  writes such a document*: tick the box when the work lands, because the next reader will trust it.

**The cheap remedy is deletion, not hedging.** Measured over six passes at the same over-claim:
every pass that *rewrote* it with a supporting clause introduced a new false clause, because a hedge
attaches fresh evidence and each attachment is a new claim. The single pass that produced zero false
claims deleted the over-claim, added no citations, and ran net-negative on lines. **A deletion
cannot be false.**

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
measured false by the next pass. *Knowing this rule is not the same as having a step that enforces
it: put the re-read inside the disposition-writing step, not in the reviewer's memory.*

**A DEFERRAL is measured the way a fix is.** The sentence explaining why something was *not* done is
the only thing standing between the next reader and looking again, so it earns the same evidence a
fix earns. Two drafts of one deferral reason shipped wrong in a row — the first named a method the
class did not have, so its stated re-check trigger could never fire (worse than no trigger, because
it reads like a plan); the second asserted a refusal that a revert of the fix left green, because an
earlier gate produced the same message. **And a re-check trigger must name a condition that is
currently FALSE. Verify that it is.**

**An erratum carries a HIGHER evidence bar than the claim it corrects**, because it arrives after
the review scope has closed and nobody will check it. Two consecutive rounds posted corrections that
were themselves wrong, each written fast off one line of evidence while a reviewer was still
running; one would have replaced a true recorded measurement with a false one.
