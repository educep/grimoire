---
name: review-gate
description: Run an independent adversarial review of finished work, triage its findings, and drive the fix loop until the work is genuinely clean. Use at every phase boundary and before any merge — especially on your own fixes.
---

# The review gate

An independent reviewer examines the work, returns machine-triagable findings on a severity scale,
and the main loop fixes or journals every one. This is the highest-value step in the whole pipeline:
across one real eleven-round arc it found a real defect **every single round**, and the worst
findings were never in the original work — they were in the previous round's fixes. The reviewer
**method** — scoping, reachability rating, plant-over-inspection, output shape, triage — is the
[`review`](../review/SKILL.md) skill; the project's **checklist**, severity names and fix-round cap
come from the adapter (`reviewer`); the loop below is how the rounds are sequenced.

> **This skill is an ORCHESTRATED CALLER, so it declares its persistence contract**: the reviewer
> **returns** findings and **the main loop writes the report file**, to the adapter's
> `artifact-paths`. Never wait for the reviewer to write it — awaiting a file a subagent was never
> told to create is how one run burned 191 polls on a file nobody was going to write.

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
test on the response-building function while the page renders nothing, a data-model property no
view can reach. A
user-facing change is only verified through the real entry point with the real data shape, and the
cheap way to settle a rendering question is to render the fragment three ways instead of arguing
about it. On re-review, **re-run your own previous probes** before trusting that a fix landed.

## Scope with WHAT CHANGED, never WHAT TO LOOK FOR

Give the reviewer the diff and the changed-file list — never a hunt list. A hunt list narrows; an
unprompted reviewer **enumerates**, and enumeration is the reliable severity-finder: run after run,
the most severe finding has come from the reviewer stepping *one door outside* the pointed scope —
a counterparty no list would have named, a sibling endpoint, a writable field beside the guarded
one. On re-review, supply only the previous round's findings marked resolved; nothing else.

Coverage is itself a claim, held to the same standard as any other:

- **A commit declared in scope but touched by no finding is effectively unexamined.** "It was in
  the diff" is the same hollow coverage claim reviews keep finding in tests.
- **A review publishes what it did NOT examine** — migrations never run, translations never opened,
  concurrency argued rather than raced. The gaps live visibly in the report, not in silence.
- **Convergence is not corroboration.** Multiple reviewers "agreeing" can mean they all read the
  same wrong sentence. Agreement counts only when the derivations were independent.
- **Findings carry an evidence grade** — measured, verified directly, source-census-only, or
  hypothesis-not-reproduced — and a pass that may not edit the tree says which load-bearing numbers
  remain asserted rather than reproduced.

Gate on the **actionable set**, never the score. The score's *direction* is diagnostic (a rise
after fixes is the fix-interaction signature); the number itself never decides anything.

## Mutation is the method

A finding either survives mutation or it is an opinion. The working set:

- **Break the source at least three ways** and name, *before running*, the test expected to go red
  for each. A mutation that survives is a finding in itself — sometimes the best one of the round.
- **Positive control**: neutralize the fix in place, reproduce the original failure, restore. A
  control that does not fail is more often **a mutation that never landed** than a broken guard —
  prove the mutation landed (diff or hash the mutated file, compare predicted vs. observed reds)
  before crediting a clean control.
- **Restore from an aside copy taken now and verified by hash — never from version control**, which
  restores to the last commit and destroys uncommitted work sitting in the same file. Aside copies
  have a lifetime: delete each one the moment it is consumed, or a stale copy silently reverts a
  later fix.
- **Independence for layered guards**: prove each layer with the others neutralized, or you have
  proven the stack once and each layer zero times.
- **Assert the persisted end-state, re-read after the call — never the call sequence.** The
  decorative-fix class: every call-level check passes while a later line overwrites the result.

## A guard must be observable — and so must its scope

For every guard, **name the input on which guarded and unguarded outputs differ, and make that
input a fixture**. Structurally-minimal fixtures (one line, one item) cannot observe accumulation
guards; boundary values can make a guard invisible (a multiplier of zero pins nothing). A corpus
with only one polarity cannot test both directions — eight rejection cases prove the validator is
not too permissive and say nothing about too strict; a corpus that cannot distinguish the two
implementations proves nothing at all. A guard whose own documentation asserts its
untestability ("no outcome test can fail here") is how a defect stays broken forever — treat
it as a finding, not a fence.

When example-based rounds keep closing one gap at a time on the same defect, stop adding fixtures
and **assert the invariant over generated inputs** — one run of randomized interleavings ended a
four-round convergence and found a money bug every example-based round had walked past.

A guard's own scope is a census: it asserts **set equality over its domain, derived from reality**
(the class list, the registry, the resolved inheritance order), never member compliance
against a hand-maintained literal that goes stale silently. And "reality" means the **runtime
registry, not the repo's declarations** — one door census widened three times (declared classes → registration sites →
what the framework actually mounts) and the final widening found the worst hole of its run in a
door no repo file contains, supplied by the framework itself. Framework-supplied doors are doors. An exemption is keyed at the granularity of the thing exempted — a
coarser key grants the exemption to neighbours nobody meant to exempt. And a guard's own
documentation records what it is **measured** to catch, including what is structurally
invisible to it.

## Read the comments as claims

A comment saying "no path does X" is a census; "this is unreachable" is a measurement; "the only
writer is Y" is a sibling sweep; "A always equals B" is an invariant. Reviews that tried to
**falsify the checkable sentences** produced some of their sharpest findings. Comment-truth is
swept by *reading*, not grepping — a class sweep is only as wide as its vocabulary, and a false
comment need contain none of your grep terms. This matters doubly where agents act on prose: a
false comment does not merely mislead, it steers every reader that opens the file, with the full
authority of the codebase.

Claims are settled by execution **regardless of rank**: a verifier may refute the reviewer by
mutation, a fix agent may overrule the orchestrator's "I verified this", and an executor may
retract an instruction of the plan itself by derivation — each has happened, correctly. This is the
property to protect above any single rule; nothing outranks a measurement.

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

## Who reviews the orchestrator?

The pipeline distrusts everything except the thing driving it. A dispatched agent gets a written
brief, a schema-validated contract, an adversarial verifier, and a gate. **The main loop gets none of
that** — the verify stage verifies *the implementer*. Everything the orchestrator does between "the
agent returned" and "this is merged" — resolving handoff steps, tightening a comment to fit a size
limit, rewriting a test, writing the debt entry — has no reviewer at all unless someone points one at
it. Measured on one run: the orchestrator's own commits were about half the diff and produced **every
catastrophe in it**.

Two countermeasures, and the second is the one that does the work:

- Scope the review to the **whole branch diff**, never the agent's reported file list. Often already
  true — check before claiming it as the fix.
- **Name the orchestrator's commits as the least-trusted part** in the reviewer's prompt. That is the
  novel half. Its first deliberate use returned two severe findings immediately.

Two structural traps come with it:

- **The author of an acceptance criterion must not be the party who declares it met.** One criterion
  was arithmetically unsatisfiable and nobody noticed, because the same party wrote it and graded it.
  Make criteria **runnable checks**, not sentences.
- **Whatever the prompt demands, the orchestrator owes.** A run whose every batch script required
  three mutations with the redden predicted in advance shipped an orchestrator fix with zero — and
  that fix reintroduced the exact defect class the run existed to close.

## Every gate runs on code; the orchestrator writes prose

Tests, linters, type checkers, formatters and size limits all read source. Debt entries, archive
notes, decision logs, changelogs and commit messages pass through untouched — and orchestrator output
is *disproportionately* prose. Where a project's knowledge lives in those records this inverts the
usual risk: a false comment in code dies when the code changes; **a false sentence in an archived
entry is permanent and authoritative.**

- **A factual claim carries the command that produced it.** Not "verified in the database" but the
  command and its output. Writing the command is what forces running it.
- **Verify closure by counting, not by asserting.** One item was declared closed in three places
  while its entry sat open for four more commits; it surfaced only when someone counted entries
  before and after.
- **Beware the claim the harness structurally cannot check.** "Verified physically" against a test
  runner configured to skip the very mechanism under test proves the thing beside it. If no gate can
  see the assertion, it is a hypothesis wearing a result's clothes.

## Claims expire, and an adopted claim is still a claim

- **A latency or safety claim names the commit it was measured against.** One was correct when
  written and false hours later, because a sibling commit in the same phase made the harm reachable.
  The analysis was right about the code it ran against and silent about which code that was.
- **A deferral that makes a correctness fix unaffordable is a wrong deferral.** Reusable test: *if
  the constraint makes those five lines unaffordable, the deferred item is arguing its own case.*
- **A reviewer's suggested wording is a claim — and so is your paraphrase of it.** One adopted
  suggestion shipped two errors: one inherited verbatim, one introduced by the orchestrator editing
  the reviewer's sentence. The record then attributed **both** to the reviewer, which is how a lesson
  about distrusting a trusted source came to rest on evidence that quietly moved the author's own
  error onto that source. Verification does not transfer with authorship — including when the author
  is you, editing someone else's sentence.

## Triage — gate the FIXING, never the RECORDING

Two decisions that must stay separate:

- **What you record is total.** Every finding is journaled — the ones not worth acting marked
  *not scheduled*, with the why. "Record-only in the report" fails in practice because intake reads
  the journal, not the report: a finding parked in a file nothing opens is a finding forgotten
  (measured: a relay's eleven findings became eight in the rollup, the smallest lost by
  summarising, not by decision). Suppressing a finding to protect a shrinking count is accounting
  fraud against your own backlog — the count is not the metric; **better code is**, and a round
  that discovers debt should say up front that the count will move less than the work did. The
  honest way to shrink the number is to fix things. When several small findings share a theme,
  one rollup entry beats a flurry — and **archiving what got fixed is a numbered step**, not a
  habit, or the journal silently fills with stale-open entries.
- **What you fix in a round is bounded — by severity, with the round cap as a ceiling, never a
  target.** Serious findings are fixed; the rest are recorded. Gating on "the reviewer went quiet"
  never terminates, because reviewers descend in severity indefinitely. A **round is any response
  to findings — dispatched or main-loop**; hand-fixing between reviews still counts against the
  cap. Two exits are different and must be told apart: cap-expiry with a *falling* score and only
  minor residue is the design working — journal and ship; cap-expiry with a falling score and
  **real findings still live is a stop-and-ask**, because the cap exists for diminishing returns
  and that case is the opposite.

Saying "no, and here is why, filed as #N" out loud is a valid resolution; quietly not doing it is
not. When the same *shape* keeps recurring across rounds, a further general round manufactures a
further instance — switch to **bounded-list closure**: enumerate the instances, close each, and
verify each closure by re-running that finding's own mutation. And when a fix touches a rule with
several call sites, scope it as a **table** — sites × surfaces — never a list: a list cannot
express "correct one way, stale the other", and the misses hide in the empty cells.

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

When a finding does need the owner, **the escalation carries a draft**. An escalation that only
asks repeats every round the answer does not arrive — one two-sentence item was declined at three
consecutive intakes for the identical reason, escalated, and raised again, five opportunities all
spent asking, when the missing move was never a decision but a *draft*. A reversible, cheap-to-redo
call ships as "this is what we did — overturn it if you disagree"; a third decline is evidence the
item was misfiled as work-needing-input when it was really a one-line authoring task.

## The lines that never move

- The review loop is **main-loop-owned** — a background run can't pause for a human, commit, or
  journal.
- The reviewer is **independent** (adapter `model-per-role.reviewer`, a judgment model) — never the
  author grading itself. **That includes the orchestrator**, which is the author most likely to be
  exempted by accident.
- Fixes re-enter this gate. A fix round that skipped review is where the next catastrophe comes
  from.
- **The last act of a phase is a review, never a fix** — see the relay below. A fix round that ships
  its final diff unreviewed has simply moved the unreviewed commit one round later.

## The relay: a phase ends on a review

Cap the fix rounds and the last round still ships unreviewed. Raising the cap moves that problem, it
does not solve it. The relay does: **the final fix diff gets its own scoped, verification-only
review** — its scope is exactly the commits that shipped *after* the last review of their phase and
have therefore never been read by any reviewer — and its findings are **journaled, never fixed
in-phase** — otherwise the loop recurses forever.

That rule has exactly one legal departure, and it is narrow: **an introduced-here, user-facing
regression** — created by this phase's own fix rounds — may be cleared with a minimal diff and a
mutation proof in the commit, under an explicit departure note; the phase then ends with a **second
scoped relay on that diff** (this terminates: the diff shrinks). Cosmetic findings never ride the
departure commit — a departure that silently widens turns the record false. Relay findings authored
by this phase's own remediation are the same case: clearing them is defensible and owes the second
relay, because "journal, don't fix" exists to stop churn on *other people's* findings, not to let
remediation launder its own damage into the backlog. The departure exists for phase-END only — when
a re-relay runs at the start of the *next* phase, its findings route through that phase's normal
gates.

The relay is also the **recovery vehicle for a pipeline breach**: when a change ships outside the
gates (a decided fix hand-implemented before any verify or review ran), the remediation is a
journaled breach note plus a **mandated retroactive scope** on the bypassed diff in the next
relay — verification-only, findings journaled like any relay's. Exercised once: the retroactive
pass proved the bypassed fix four independent ways, reproduced the original defect under a
revert, and still surfaced residue the hand-fix had not considered. It converts unreviewed work
back into reviewed work; it never converts the bypass into an accepted route.

It asks a different question from a review round. A review round asks *is the code right?* The relay
asks *did fixing it break something?* — aimed squarely at the remediation, because **remediation
damages what it touches**. That second question is about the method, not the code, which makes the
relay the natural feeder for whatever ledger of lessons the project keeps. A run that skips it does
not merely skip a gate; it starves that ledger and rediscovers the same failures by accident, later.

Each finding carries a **provenance line** — phase, round, and exit state (`clean`, `cap-spent`, or
`needs-human` with the reason). `needs-human` means the **agent halted itself on a stop predicate**
— a product decision, a gated apply, a trajectory stop; an external interruption is not an exit
state at all (killed ≠ stopped — the loop resumes and journals nothing because of it). The next
phase **opens** by triaging that residue, provenance first: residue after a clean exit is ready
first-slice material; a finding journaled at a round-1 `needs-human` exit is an under-triaged
unknown with a question still attached. Same journal, opposite handling — without the line they are
indistinguishable. This also makes the debt entry, already measured and triaged, the inter-phase
handoff medium instead of raw review reports.

Two rules about severity crossing the phase boundary:

- **The ask never replaces the record.** An out-of-scope catastrophe keeps its severity, is never
  fixed in-phase, and is journaled **immediately, with `needs-human` provenance, in the same commit
  as the relay entries — before any chat report**. One run's highest-severity discovery existed
  nowhere but a conversation while lesser findings were dutifully journaled around it. Asking may
  accompany the journal entry, never substitute for it.
- **Taking a deferred item early inherits its stated conditions.** A reviewer's "not this PR — file
  it, with a test that X" names the price of doing it now. One hunk took the fix early without the
  test and without the entry: three departures in one hunk, each invisible alone.

An **empty relay after a clean exit is a real outcome**, not a failure to look harder. The relay
**deliberately manufactures entries**, and that is not the same failure as filing work you should
have done. Relay entries are journaled *because fixing them in-phase is forbidden*; pair it with
outflow discipline so the ledger still shrinks.
