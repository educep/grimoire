---
name: refactoring-discipline
description: Structural refactoring of oversized files — source or tests. Use when a file crosses the project's soft line threshold, BEFORE appending code to a file already near it, or when asked to refactor, split, or clean up a file. Diagnoses whether size is structural (multiple responsibilities → split by responsibility, interface-preserving, step-by-step) or cosmetic (one coherent thing that is just long → refuse to split). Never use it to satisfy a line count by chopping a file in half — it refuses that path.
---

# Refactoring discipline

> **Adapter first.** Read the project adapter's `refactoring` capability before acting. It
> supplies: the soft/hard line thresholds and what enforces them, the file-size census command,
> the test-layout rule (where relocated tests go), and the **interface surface** — the
> project/framework-specific list of things that are public interface even though they look
> internal. If the capability is absent, **say so before acting** — name it as an unconfirmed
> fallback rather than reporting a threshold as if the project had set it — and proceed on:
> soft threshold 500 lines, hard 700; tests mirror the source tree; interface surface =
> exported names and import paths. Replace each the moment the adapter states its own.

## Why this exists

A file crossing a line threshold is a symptom, not the problem. The problem is one of two
things, and they demand opposite responses:

1. **Multiple responsibilities in one file** — real problem; split along responsibility seams.
2. **One coherent responsibility that is just long** — not a problem; splitting it makes things
   worse.

Mechanically splitting to satisfy a number produces files that are individually smaller but
collectively harder to navigate: the next reader opens several files to reconstruct the one
thing they needed. The measured benefit of refactoring is that a typical future change **reads
and touches a smaller, correctly-scoped set of files**. If a split doesn't shrink that set, it
didn't help, whatever the line counts say.

The payoff is also not linear. Early steps (extracting duplication, naming things) often show
almost no visible improvement; the win arrives when a real seam has been carved and a
duplicate-free core emerges — often at the *last* step of a sequence. Don't declare victory
because counts look better; stop when file boundaries track responsibility boundaries.

## Triggering

- At or past the **soft threshold**: run Step 0 before adding anything to the file.
- **Proactively**: when about to append a function/method/test to a file already near the soft
  threshold — diagnose *first*, don't wait for the hard gate to fail a commit.
- On request ("refactor / split / clean up this file").
- Refuse the degenerate request: "make this file pass the line limit" without a responsibility
  diagnosis gets Step 0, not a chop.

## Step 0 — Diagnose before touching anything

Answer in writing before moving any code:

- **List the distinct responsibilities in this file.** Named, not vague ("request validation"
  and "export formatting", not "various helpers"). If you can only truthfully name one, this is
  case (2): **do not split.** Report "long but cohesive" with the responsibility named, and
  stop. A big enum match, an exhaustive parser, one legitimate test suite for one module —
  splitting these along no real seam is pure overhead: every step costs review and carries
  regression risk, and the halves must be re-read together anyway.
- **For test files**: is one file accumulating tests for multiple unrelated modules/concerns
  (real problem — split along the same seams as the production code), or one large, legitimate
  suite for one module (not automatically a problem)? Relocated tests go where the adapter's
  test-layout rule says — do not invent a new layout mid-refactor.
- **Pick the extraction that most shrinks what a typical future change must open.** Not the
  easiest extraction, not the biggest by line count. Sanity-check the choice against 2–3
  realistic upcoming changes (consult the tech-debt backlog and the active plan for what is
  actually coming).
- **Is this file worth refactoring right now?** Refactoring has real cost. A file that gets one
  more touch and then rests has a weak future-savings case; a file being extended in every phase
  is where the benefit compounds. But **a threshold crossing is a scheduling event, never a
  note**: "noted" crossings become blocked commits within the same run, so a crossing (or a file
  the plan is about to extend past the line) is scheduled as its own issue at the *front* of the
  phase that needs the room — gated before that phase, not bundled into its feature PR and not
  parked as a remark. Treat remaining headroom as a scheduling input: a file lines from its limit
  makes the *next* change the one that pays.
- **But a deferral that makes a correctness fix unaffordable is a wrong deferral.** One split was
  correctly deferred by the rule above — and the deferral turned out to be the only thing blocking
  restoration of a deleted runtime detector, because the five lines would not fit under the size
  limit. The reviewer's formulation is the reusable test: *if the limit makes those five lines
  unaffordable, that is the deferred entry arguing its own case.* Re-open the deferral. The rule
  against bundling is about **review legibility**, and a separate commit on the same branch
  satisfies it — the thing to avoid is a split smuggled into a feature diff, not a split at all.
- **A file at exactly its limit is a trap for the next author, not a success.** Meeting a size limit
  by tightening the documentation you just wrote is a losing game: it buys one commit and pushes the
  cost onto whoever comes next, in a file whose culture may be the very thing worth keeping. Record
  it as debt with the seam named, and do not treat a grandfathering mechanism as a hatch for new
  growth.

## Step 0b — The seam is dictated by guards, not by taste

Before settling on a seam, **grep the test tree for source-scanning constructs** — file-globbing,
AST parsing, runtime path introspection, raw source reads — and check whether any hit names this file or its
symbols; report "none" explicitly if that is the answer. A guard that pins members to *this file*
makes some moves fail **by construction**, whatever the responsibility diagnosis says: one recorded
seam hypothesis grouped a method by how it *reads* while the guard measured what it *writes*, and
the planned split was impossible. The shipped rule becomes "what the censuses pin stays; everything
else moves." When a guard's scope must widen to cover a new file, do not widen a hand-maintained
literal — pin the scope to something **derived at runtime** (the class list, the resolved
inheritance order), because the scope of a guard is itself a census and a literal goes stale
silently, scoring green over files the scanner never opens.

The size limit has a failure mode of its own worth naming: **the cap starts editing the prose
rather than the code.** On a file at its limit, a needed comment costs a commit, so what gets cut
is documentation — in exactly the files where writing things down catches defects. When the cap is
doing that, the split is due now, and "stop and report" beats shaving explanation to fit. **A
PROSE-ONLY correctness fix counts as a correctness fix**: correcting a comment, a docstring or a
citation that currently states something false ships no executable line and is still a fix, and *"it
is only prose"* is precisely the argument that gets it compressed away instead of made. One file at
its cap was compressed twice to stay there, and a journaled defect's two-line record could not be
written into it at all. At the cap, a prose correction is a split trigger like any other.

**Where the work's own nature is to grow files, budget the split at PLANNING time** from the
measured headroom, rather than reacting to the limit mid-round. One round took three structural
splits as reactions to the cap — while its declared subject was adding measured explanation to two
files that were already near it.

## Step 1 — Order of operations

In this sequence, every time:

1. **Extract duplication first** (repeated inline patterns → functions/constants). Splitting
   files before de-duplicating scatters the duplicates across files — strictly worse, and the
   single most common way this goes wrong. If you're tempted to jump to "make 3 files out of 1",
   stop and check this step is actually done.
2. **Extract functions/classes for coherent sub-responsibilities within the same file.** This is
   where the real seams get discovered — and where you find out a seam you assumed doesn't
   exist.
3. **Only then move code to new files/modules** along the seams steps 1–2 exposed.
4. **Split/relocate the tests along the same seams in the same pass**, not as an afterthought —
   this is usually the test-file bloat fix.

## Step 2 — Non-negotiable execution rules

- **Interface preservation is the definition of refactoring.** If any public signature, return
  type, or externally observable behavior changes, it is a rewrite, not a refactor — flag it as
  carrying different risk; never fold it silently into "refactoring".
- **Check the adapter's interface surface item by item.** Frameworks hide public interface in
  things that look internal — module paths that are also task names, registration that rides on
  import order, string references from templates or config. After moving code, grep every
  import/reference site; keep a re-export at the old path where anything external (including
  migrations or queued jobs) references it. **The interface surface includes config files**: a
  lint or type-checker suppression naming the old module path flips a gate red (or silently
  un-suppresses) in a way neither the diff nor the test suite shows.
- **Prove the move, don't assert it.** Three techniques, each cheap: (a) an **AST identity diff**
  — unparse every moved member, normalized, and show missing = 0 / added = 0 / differing = 0;
  (b) the **inverted positive control** — a refactor's control proves the moved code is *reached*
  (raise inside it, watch the callers redden with the new module in the traceback), not that a bug
  reproduces; (c) **no test file touched by the extraction commit** — that is what makes the
  no-behaviour-change claim checkable from the diff alone.
- **A refactor has TWO proof obligations, and the second is the one that fails.** Identity proofs
  say the code is the same. They are not merely silent about the sentences that became false by
  changing address — **they are the mechanism that produces them**, because identity guarantees the
  prose was carried over unchanged, and unchanged prose is exactly what goes false when its address
  moves. Three interface-preserving splits produced fourteen false sentences between them ("lives in
  the sibling module", "the seam left open", a line count, a citation), every one relocated verbatim
  by a commit whose header said nothing had been re-worded. So a split ships with *the code is
  identical* **and** *every deictic sentence still resolves at its new address* — as a citation check
  that RUNS, not a re-read. And a "split" that leaves both copies in place is not a move at all; say
  which one you did.
- **An allowlist or exemption keyed on a FILE PATH is RE-PATHED when code moves, never extended.**
  A move that GROWS such a list has silently widened whatever the list grants — the path half of the
  key is load-bearing, because it is what stops a copy-paste of a safe pattern into a new module.
  Verify by planting the real violation in the NEW module and watching the census redden.
- **When the rule you need already exists in the tree, using it is mandatory and re-deriving it is
  the defect.** A second copy inherits none of the widenings the original has earned. One hand-rolled
  scanner was written one attribute short of the correct shared one, under documentation claiming
  the shared module's rules were imported rather than restated.
- **Every step independently verified.** Run the affected module's test suite plus the project's
  format/lint/type gates after *each* step, not once at the end. A step that can't be verified
  in isolation is too big — break it down. Refactor only on green (see the tdd skill): never
  start a step with failing tests.
- **One step, one commit.** Never bundle "extract duplication" and "move to new file" into one
  untested change. This also keeps each step revertable alone.
- **Track the largest single file, not total LOC.** Module-wide LOC can stay flat while the file
  every change must open shrinks — that's the metric that predicts future savings.

## Step 3 — Blind spots to actively check

- **A first-pass plan finds the shallowest move, not the structural one** — extract-one-function
  instead of extract-the-responsibility. Before executing, re-examine the plan once, explicitly
  asking: *is there a whole class/module hiding here that I'm about to extract piecemeal?*
- **"Smaller files" is not "fewer files per change."** After splitting, trace 2–3 realistic
  future changes through the new structure: does each touch fewer files, or the same content
  spread across more places? If the latter, the split was cosmetic — say so and reconsider.
- **Never trim tests to hit a number.** Test files balloon from poor placement, not "too much
  testing". Relocate along seams; deleting or condensing test content to satisfy a threshold is
  a red line — ask first, always.
- **Scripted rewrites lie.** sed/grep-based moves silently mangle indentation and
  whitespace-sensitive syntax. Diff the actual output; never trust that a mechanical
  find-replace did what it was told.
- **Don't manufacture seams.** A long-but-cohesive file is not a bug. Inventing responsibility
  boundaries to produce files under the threshold is the failure mode this skill exists to stop.
- **Delete a dead artifact on a REACHABILITY argument — nothing can ever execute it — never on a
  usage argument.** "Nobody calls it today" deletes things that are one configuration change from
  live. Two dead artifacts in one section got opposite and correct dispositions only because
  somebody made that distinction explicit.

## Done checklist

- [ ] Distinct responsibilities were named in writing before any code moved
- [ ] Duplication extracted before any file split
- [ ] Every step verified independently (module tests + format/lint/type gates), one commit each
- [ ] No public interface or observable behavior changed (adapter interface surface checked
      item by item; reference sites grepped)
- [ ] Largest-file trend improved — not just threshold compliance
- [ ] Tests relocated along the same seams, none trimmed
- [ ] 2–3 realistic future changes traced through the new structure and each touches fewer or
      more-focused files than before

Relationship to neighbors: line-level quality cleanup inside a file belongs to a simplify-style
pass; this skill owns structure across files. `tdd` governs the green-only rule during steps.
`mode-select` decides how a big split runs (a multi-file, multi-step split is checklist- or
dispatch-shaped work, not an inline afterthought).
