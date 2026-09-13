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
>
> **EVERY round writes its own file, and that includes the relay and any closure review** — one per
> round, written before the round is reported done. *(Measured on two consecutive phases: the first
> ran its relay and left no report, caught only because the next reviewer noticed a plan tick citing
> a report that existed nowhere; the second lost both of its review rounds — twenty-six findings —
> recoverable only because the reviewer agents were still resumable. "Journal-only" names where a
> finding may not GO, not permission to keep it out of a file.)* **A finding that exists only in a
> summary's count is already lost**: a count cannot be triaged, cited or reopened. Never
> reconstruct one from memory — ask the reviewer for it verbatim with re-review forbidden, and if it
> cannot be recovered, record the gap as a gap.

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

**Text search proves what a file CONTAINS; it never proves what the file EMITS.** An artifact is
not verified until it has been executed or rendered and its output inspected. One run's eleven
scripted edits shipped a structurally broken output past 122 source-level assertions, a
six-thousand-test suite, and a formatter that tidied the wreckage on its way through — every one of
which was reading the source, and none of which was reading the product.

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
- **The plant is repeated once per SPELLING and once per POSITION the claim covers.** A guard
  whose documentation called it undefeatable died to a one-line counterexample a reviewer wrote in
  minutes; elsewhere a single plant passed while six other positions of the same violation went
  unseen. One plant proves one cell of the table.
- **Positive control**: neutralize the fix in place, reproduce the original failure, restore. A
  control that does not fail is more often **a mutation that never landed** than a broken guard —
  prove the mutation landed **by comparing the file's bytes, never by consulting the version-control
  index** (one harness checked "did it land?" against an index diff and declared two landed plants
  vacuous), and compare predicted vs. observed reds before crediting a clean control. A plant must
  also be **reachable in the state the assertion is about**; an unreachable plant is a green control
  with a different cause.
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

**And derive the population from the project's own LABEL for the thing, never from the module tree
you expect to find it in.** A directory boundary is a *guess about where a label was applied*; the
label — the decorator, the mixin, the section constant, the permission class — is the answer. One
phase built two halves of one gate: the half derived from the routing table caught an endpoint
mounted outside the expected tree that no walk of the UI could see; the half derived from the
module tree missed five live doors the project's own label covered. Same phase, same author; the
only difference was the source of the population.

## Guard design: the five ways a guard turns out to measure nothing

These are the defeats that recur. Each was found by a plant, none by reading.

- **A proxy replaced by another proxy is not a fix, and a proxy is replaced at the UNIT the risk
  lives in.** "A filter exists" is not "the filter excludes the attacker's row" — build the foreign
  input and assert exclusion. One detector went through four generations inside a single review
  loop, each a *different* structural stand-in, each feeling like progress: a validator exists → the
  mixin is applied → the query carries a condition → (defeated by a condition that excludes nothing).
  When you do replace a proxy, **name the unit the guard's own subject is counted in and assert at
  that unit** — two successive replacements measured residual occurrences and then characters, while
  the subject was occurrences; a proxy in a unit the risk does not live in cannot be strengthened,
  only replaced. The tell: you cannot state the replacement's failure mode in one sentence using the
  noun the guard's own name uses.
  *A structural proxy is still worth shipping as a ratchet when the class you defend against is the
  ACCIDENTAL form — but only if you measured which form that is and said so in the guard.*
- **Ask what the NEW predicate cannot see, and write each answer down as a named bucket — then
  assert the bucket set.** Replacing one predicate with a better one immediately produced six
  further blind shapes, every one found where somebody asked that question and every defeat where
  nobody did. A predicate with no bucket census is a proxy in better clothes. **Corollary for the
  reviewer**: on a detector fix your first question is not "is the new predicate correct?" but
  "what is the enumerated set of shapes it cannot see, and is that set asserted?"
- **A guard's documentation explaining WHY its detection is sound is a specification for the next
  evasion.** Four of one round's five defeats came from a boundary the fixer had announced in prose
  — the comment was literally the recipe. Write the documentation, then plant against every boundary
  it names before shipping.
- **A guard whose verdict depends on reaching a later step must assert the earlier step was
  reached.** One harness judged a second execution and reported a finding only on a specific failure
  there; four of its thirty-one members could not even compile, so the second execution died with a
  different message and every planted defect in them passed. The guard was green over 87% of a
  population it claimed to execute in full, and its anti-vacuity companion (a minimum member count,
  non-empty bodies) was satisfied by the broken members like any other. **Execute the member the way
  the runtime would see it, or pin BY SET EQUALITY which members you could not**, so a member that
  starts being skipped is an event and not a silent shrink of the executed set. This is the
  set-equality question asked one level down: the population is pinned — is its EXECUTION pinned, or
  only its size?
- **A claim about a population is only as strong as the STEP THAT SELECTS the population.** A
  containment test standing in for identity, an unexamined selector, a filter applied upstream of
  the assertion — each leaves a claim that is true of nothing. One filter written to make a new
  family of files measurable removed that family's own idiom before a single assertion saw it.
- **A reader that decides reachability, ownership or counts PARSES its input; it does not match
  text over it — and it counts the thing, not the line that mentions it.** A substring scan over
  source treated a file named only in a comment as live; the naive comment-stripper written to fix
  that then blanked real code after a comment marker inside a string.
- **A coupling guard is keyed on what the CONSUMER consumes, not on what the producer contains.**
  Read the consumer's code to the end of its own filter and key the guard on the population that
  SURVIVES that filter. One guard was re-keyed three times — "the source contains the marker", then
  "this page's include graph emits the marker", then finally "an element the consumer would actually
  act on" — and only the third could redden. Then **plant the smallest real change that breaks the
  consumer**, not the reviewer's counterexample: a plant that sweeps more than the real change
  proves less than it looks like it proves.

Three finishing moves, each cheap and each having caught a guard that measured nothing:

- **Neuter the MECHANISM the check names and confirm the check notices.** Not the fix — the
  mechanism. Two cells of one table passed with the component they exist to cover disconnected,
  because an unrelated cascade happened to supply the same outcome; whatever stays green with its
  named mechanism disconnected is asserting something else's work.
- **An exemption's KEY and its SUBTRACTION are two separate claims.** Re-keying an exemption from
  the file to the thing exempted fixes the first and leaves the second: where the exempt thing and
  the forbidden thing can be the same string, subtracting *by value* masks every further instance
  of that string. Assert what the subtraction retires, by member and count, in both directions.
- **A control expires when the condition it rode on changes.** A discriminating control pointed at
  the last unprocessed region of a sweep; once that region was processed, the control's plant
  supplied its own evidence and held over an empty source. Any control whose proof depends on the
  work being *unfinished* must be re-derived at the end of the work — and an emptied population read
  by a set-equality check needs an anti-vacuity assertion beside it.

**A declaration is EXECUTED on the axis it names, and a census carries one table per axis.** A table
asserting *"two callers differing only in X get the same answer"* is satisfied by a door that refuses
both of them — agreement recorded, nothing measured. When rows turn out to belong to a *different*
axis, they cannot be parked in the only table that exists: the opposite claim (*"they differ, in this
direction"*) is self-controlling in a way the agreement claim is not, because a blind probe satisfies
"both answer the same" trivially and cannot satisfy "this one is admitted and that one is refused".
So: **one table per axis, asserted disjoint, probed as a union** — the two tables make opposite
claims about a row, so no row can sit in both, and walking the union means a row MOVED between them
keeps the assertion it had and gains the new one. The same trap in miniature: a measurement is
bounded by whether its fixture reaches the path at all — three probes intended to vary one axis once
short-circuited to the same branch and rendered one answer three times, which read as agreement.

**A narrowing is diffed against the space the guard must SEE, never against the population it must
KEEP.** Keeping the right members is necessary and proves nothing: one fix round re-admitted the
exact spelling the reviewer's plant used, verified the retired members stayed retired, and left two
whole shapes invisible. And **a narrowing's lower bound needs a plant on the sibling you did NOT
name** — narrowing a catch-all to a specific error class shipped with the excluded *subclass* pinned
and the excluded *sibling* unpinned, so a different failure of the same subsystem would have crashed
every page the guard protected. Name the parent, parametrise the plant over a subclass **and** a
sibling, and grep the tree for the same construct before shipping.

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
are designing, not the state they are creating.* **A fix round is the single most dangerous place in
the work to write new code or a new claim** — measured across many phases, the round that repairs a
defect reintroduces its shape, and the third occurrence of a class is repeatedly *inside the
artifact written to prevent the second*. So the fix diff gets everything the original got: the same
plants, the same re-derivation of the population, the same re-reading of the rule being widened. The
reviewer's first targets are:

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

**A project's adapter may extend the relay with a bounded CLOSURE ROUND** — check the adapter's
`reviewer` capability before treating journal-only as absolute; where the two disagree, the adapter
wins. The shape that works: after the relay, residue that is *low-severity, cheap, and in files the
phase already opened* is fixed in ONE bounded round, then a **scoped verification-only review of
that closure diff alone** runs and ITS findings are journal-only. The loop ends there, guaranteed.
The point, in one owner's words, is *more fixes in-phase, so the phase generates less backlog and
fewer loops.*

**The closure review SUSPENDS the class-sweep obligation.** The sweep rule says an instance of the
class you are already fixing, in a file you have already opened, is in scope — and at the closure
review that would reopen the very loop the closure round exists to end. **A terminal gate a sweep
can reopen is not terminal**, so the closure guarantee wins: its findings are journaled and filed,
never fixed, however cheap and however clearly in-class. (Measured where both rules fired on the
same three findings: filing them produced the better outcome, because the entry attacked the class
by construction instead of the three instances.)

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
