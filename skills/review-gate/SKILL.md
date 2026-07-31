---
name: review-gate
description: Run an independent adversarial review of finished work, triage its findings, and drive the fix loop until the work is genuinely clean. Use at every phase boundary and before any merge — especially on your own fixes.
---

# The review gate

An independent reviewer examines the work, returns machine-triagable findings on a severity scale,
and the main loop fixes or journals every one. This is the highest-value step in the whole pipeline:
across one real eleven-round arc it found a real defect **every single round**, and the worst
findings were never in the original work — they were in the previous round's fixes. The reviewer
persona, severity scale, and triage rules come from the adapter (`reviewer`); the loop below is the
method.

## Review the exact tree, and pin it

Before the fix round starts, **commit the reviewed state as a checkpoint** — verbatim, even if
imperfect — so the review's line references stay valid and the fixes land as a small readable diff
instead of dissolving into a blob. A review is a snapshot: its score describes the tree it examined,
never the tree after the fixes. There is no score for the current state until someone reviews the
current state.

## Execute, don't read

A finding verified by running it outranks ten reasoned from the diff. Render the page, run the
probe, decompile the artifact, race the two writers, redirect the output — *"I ran it rather than
inferring it"* is the sentence that separates the findings that survive from the plausible ones. The
recurring blind spot has a name: **verified at the layer below the one the user sees** — a green
test on the serializer while the page renders nothing, a model property no view can reach. A
user-facing change is only verified through the real entry point with the real data shape, and the
cheap way to settle a rendering question is to render the fragment three ways instead of arguing
about it. On re-review, **re-run your own previous probes** before trusting that a fix landed.

## The main event: the previous round's fixes

The recurring failure mode of fix rounds, in one sentence: *the author reasons about the state they
are designing, not the state they are creating.* So the reviewer's first targets are:

- **Each fix, adversarially** — does it hold on the state the system actually produces, not the
  state the fix was named after? A guard keyed on one field of a two-field invariant; a lock taken
  and then not used for the write it protects.
- **Interactions between fixes of the same round** — two individually-correct fixes whose
  combination is nobody's job. The score can go *up* after two correct fixes. This includes the
  smallest case: one fix making another unreachable in the same commit.
- **Claim vs. delivery** — documentation that overstates a guarantee is *worse than none*, because
  everyone downstream stops checking. A comment saying "the two writers serialize" when one branch
  does; a docstring calling a guard load-bearing for a load it cannot bear; a careful comment
  protecting code that can no longer execute. Where a hazard can be removed **by deletion**, prefer
  that to protecting it with prose.
- **Test honesty** — for every fix: delete the change mentally and name the test that goes red. Hunt
  assertions that cannot fail, guards no test reaches, substring checks on small integers, coverage
  silently lost in a file split, and fixtures that exercise a buggy path without ever asserting the
  end-state of the entities it touches.

## Triage — nothing is silently dropped

Every finding ends in exactly one of two states: **fixed** (pinned by a test where testable) or
**journaled by explicit decision** in the tech-debt file, with the why. The adapter's severity scale
sets the default: serious findings are always fixed; minor ones may be journaled unless they block
later work. Saying "no, and here is why, filed as #N" out loud is a valid resolution; quietly not
doing it is not. Cap the fix rounds; anything past the cap is journaled loudly.

## When a fix keeps failing at the same spot, change its shape

Six rounds of narrowing a predicate — another clause, another column, a lock around the read — and
each round the next reviewer found the state the narrower predicate hadn't considered. The round
that ended it didn't narrow anything: it **removed the ambiguity** (replaced the untrusted object
entirely), so the question "which version is this line reading?" stopped having two answers. When a
fix chain oscillates, stop patching the predicate and delete the thing that makes the predicate
necessary.

## Convergence, and what it does not mean

Falling scores from one reviewer mean *that method* is exhausted, not that the work is clean: after
seven converging rounds of static review, a fresh reviewer who executed its suspicions found a
catastrophe on the first pass. When scores converge, either ship or **rotate the perspective** — new
reviewer, different method (execution over reading), different layer — before declaring done. And
treat a decision-owner's answer that differs from the options offered as a **question, not an
answer**: freeze the rule and ask the one precise clarifying question with the object named.

## The lines that never move

- The review loop is **main-loop-owned** — a background run can't pause for a human, commit, or
  journal.
- The reviewer is **independent** (adapter `model-per-role.reviewer`, a judgment model) — never the
  author grading itself.
- Fixes re-enter this gate. A fix round that skipped review is where the next catastrophe comes
  from.
