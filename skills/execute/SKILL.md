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

**Edit-disjoint is not verify-disjoint.** Mutation-based verify stages are *writers*: they mutate
production files in place for positive controls, and they *traverse* files they never edit
(rendering through them). Conflict analysis unions each issue's edit set with the files its verify
stage mutates **or traverses**; overlapping verify sets serialize, and check the disjointness by
grep rather than assuming it. One verifier reading another's un-restored positive control raises a
correct alarm about a state that never existed.

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

**Anything the loop must not get wrong lives in the schema or a numbered step, never in prose.**
Batch returns partition their own outcome (committable / pending-handoff / held — a designed
handoff is not a failed fix, and a held issue feeds a fix round, not the human); verify verdicts
carry the commands run, the mutations with their reddens predicted in advance, and any main-loop
steps owed. This was measured head-to-head: the same rule, moved from prose into a schema field,
immediately held an issue that the prose version had waved through — anything the gate must not
miss goes in the **schema**, not the prompt.

Two rules about the prompts themselves. **Certifications are forbidden**: a prompt says what to
CHECK, never what is "already verified" — a criterion asserting an outcome unconditionally once
made an agent write a test blessing the defect, and a mandated test is a spec too (agents must
check the test CAN fail and say so when it cannot). And **every number the plan states — counts,
sites, seams, censuses — is a hypothesis the executor re-derives before acting**; the stated
census has been wrong in both directions often enough that following it is the error. When a spec
contradicts itself, the STEPS are authoritative and the gap is journaled, never silently absorbed.

When correctness matters (money, tenancy, idempotency, anything the adapter's `constraints` flag),
make it a pipeline: **edit → verify**, the verify stage on the judgment model
(`model-per-role.domain-verify`), so each edit is checked the moment it lands instead of hoping
someone remembers to. Correctness-criticality overrides the lightest-mode instinct — one small
money issue still gets the pipeline, slower on purpose — and the verify stage is **ring-fenced
from budget trimming**: it is the only thing between a cheap model's mistakes and the review gate.
A mechanical sweep is not exempt: its transform is valid only under a per-site precondition, so
verify the precondition per site, or the sweep manufactures the mirror of the bug it kills. And a
fix prompted by one instance **sweeps the class, not the pointed instance** — fixing only what was
pointed at leaves the identical defect one file over, where it becomes the next round's worst
finding.

## Commit (main loop only)

**A dispatched agent's completion is not evidence — and a validated contract proves shape, not
truth.** One agent did its work correctly and returned a placeholder contract (a fake file list,
a stub summary); the real file set had to be derived from the tree and the verifier's account.
Schema validation guarantees the return parses, never that it is honest — the tree inventory is
the control, and garbage in the contract is not a reason to discard sound work: derive the
contract from the tree. So before committing anything from a batch, the main loop inventories
the working tree itself (what actually changed, versus what the contracts claim) and **re-runs
the gates itself** — `format`, `verify`, whatever the adapter's commit hooks enforce —
regardless of what any agent reported. Agents can die holding the field: a crashed agent's
diff is an **unreviewed draft**, not work in progress, even if it happens to be green. One real
implementer fixed 13 of 16 findings flawlessly and then died mid-task, leaving a 20-file diff its
author never linted, typed, or tested; the tree being green was luck, and the re-run is what turns
luck back into process.

Then the main loop commits **one issue at a time**, per `git-conventions`, from the returned
contract: stage exactly that issue's files, commit with its message. The other agents' uncommitted
edits stay in the tree, untouched, for the next commit. This sequential-commit-over-a-shared-tree is
the only race-free model — a stray checkout from a parallel agent would derail the others.

Three rules guard this step:

- **A gate is only a gate if it runs first.** The commit does not happen until the verify verdict
  exists and has been read — one implementer committed against its prompt's explicit bar and the
  work landed before its verdict did. A prompt prohibition is friction; the commit step checking
  for the verdict is the control.
- **Verify the branch before every commit, not just before branch creation.** A clean tree says
  nothing about which branch you are on, and in a shared checkout the branch can move *between two
  of your own tool calls* — the human owns the same checkout and has no reason to announce a
  switch. The check is one command and belongs before staging.
- **One actor per checkout — including sibling worktrees**, which share the object database, refs
  and hooks. And another actor's in-flight state is not residue: before cleaning "abandoned"
  mutations or scratch files, verify their owner is actually done — one cleanup destroyed a running
  verifier's positive control.

Then, as part of the same commit phase and not as an afterthought: apply any `shared-files` content
the agents surfaced, tick the plan's progress markers, and append what happened to the solutions log
— what shipped, what the work uncovered, what an operator must know, what is still open. These are
not paperwork; they are the only durable state a cold session can resume from, and they get written
reliably **only because the loop contains them**. Left as a habit at the end of a long day's work,
they are simply forgotten.

## A phase OPENS with debt intake, and CLOSES on a review

**Opening.** The previous phase's relay journaled findings it was forbidden to fix. Triage them
first, provenance-first (see `review-gate`): residue after a clean exit is first-slice material;
anything journaled at a `needs-human` exit still carries an unanswered question. Cheap, in-scope and
file-disjoint items become the phase's opening slice. This is what makes the debt entry — measured,
triaged, already invested — the handoff medium between phases.

**While running: fix in-phase, don't file for later.** If an item is caused by this work, or lives in
a file this work touches, and needs no owner decision — fix it here. Filing is for items that need a
ruling, or whose fix lands in a surface a later phase rewrites. Getting this wrong compounds fast:
one run closed two entries while filing five, all small and squarely inside files it had already
opened. Add a `newDebtFiled` field to the verdict schema so inflow is visible at the gate rather than
discovered in the accounting.

**Closing.** The relay — the final fix diff's own review. See `review-gate`.

## The review round is a step, and its absence is silent

The batch is `implement → verify`. That is **not** the whole loop: review → triage → fix → re-review
sits between the workflow returning and the PR opening, and it is main-loop-owned.

Skip it and **nothing fails**. The contract is sound, every gate passes, the PR opens. The only
signals are absences — a missing plan artifact, an empty reviews directory. One run shipped a phase
to PR this way and the omission surfaced only when a human asked.

**A step whose omission produces no error must be a checkable artifact, not a remembered habit.**
Writing it in the plan's prose is not enough; the plan said so and it was read.

## Opening a door a guard closed

When a fix opens a path some guard previously refused, enumerate the states now reachable and check
each against the guard's **invariant**, not its **condition**. One fix satisfied the condition ("a
finalized record exists") while violating the invariant the guard was really protecting ("a finalized
record has been credited") — and reintroduced, within hours, the exact defect class the run existed
to close.

## The sibling-writer sweep, and its converse

Any write to a field or status means: **enumerate every sibling mutator** — services, API actions,
background tasks, signals, admin — and pin each door; the verifier **re-derives the census itself**,
because checking a provided list only checks the list against itself. The converse triggers just as
hard: **creating a new write path runs the same census** — "which existing invariants does every
sibling of this new door enforce?" is part of building the door; a rule documented at door one and
absent from door two is not a propagated rule.

When an issue asks you to pin N doors, first ask whether the invariant belongs **where no door can
bypass it** — a database constraint, a single chokepoint all doors route through — because the
storage layer does not care how many writers there are, and three individually-legal calls can
compose into the forbidden end state that three separate patches structurally cannot prevent. Then
**price the blast radius**: enforcing an invariant at the storage layer is validated against every
existing row in *every* environment, not just production, and the enumeration of what it breaks is
part of the fix.

## The full suite is the main loop's only instrument

Agents restricted to test subsets are **structurally blind** to global-state failures — suite-order
bombs, cross-slice fixture collisions — and the main loop's full run is the *only* detector for that
class. Technique matters: parallel workers inside one session, foreground, in chunks if the
environment kills long runs (backgrounded full suites have died silently at 15–22% more than once);
a runner *configured* to skip a mechanism (migrations, commit callbacks) executes any code relying
on it with exactly zero coverage, so name that gap instead of counting it as green.

The general principle: **prevention is friction; detection is the control.** Prompt prohibitions
and hooks reduce how often the boundary check fires — the boundary check (the diff over the
protected directory, the lockstep tool, the census re-run) is what actually catches; every bypass
on record was caught by a check, none by a prohibition. And census-style gates must ALSO run at the
**integration point**: two individually-clean branches have composed into a violation visible only
post-merge. Preconditions live in the launch step or the script's first act — plan-prose
preconditions get skipped, and then run only after the failure they exist to prevent.

## State safety

- **Restores come from an aside copy taken now and hash-verified — never from version control**,
  which restores to the last commit and has destroyed uncommitted work mid-mutation. Aside copies
  have a lifetime: delete each the moment it is consumed, or a stale copy silently reverts a
  completed fix with every test green.
- **A browser or UI gate needs a frozen tree**, not just a stable database — recompiling any
  artifact under a live server moves failures to unrelated tests, which then read as flakes.
- **Widening a tolerance means you have not accepted that the signal is not the thing you care
  about.** A staleness check answered a correct diagnosis with a tolerance, then blocked work with
  a five-figure false positive; the fix was comparing content. Three attempts, each confident,
  each wrong — when a threshold needs widening twice, replace the signal.
- **Announcing is not doing.** A turn that ends on "starting X now" has ended on nothing; end turns
  only on completed work or a stop predicate.
- **A killed verify stage leaves live mutations in the tree.** Verify stages mutate production
  files in place, so an externally killed verifier can leave guard-neutralizing edits *beyond its
  probe files* — two survived one kill and were caught only by re-running the shipped suites.
  After any killed or crashed verify stage, run a **mutation-residue sweep** — re-run the affected
  suites and diff for un-restored mutations — before trusting the tree.
- **A gate command is itself a guard, and must be shown able to fail.** Before trusting any gate
  the first time — a syntax checker, a linter invocation, a census script — feed it an input that
  must fail and watch it fail. More than one stock checker exits 0 without examining anything (a
  syntax check that skips module files; a length check that, called bare, checks zero files), and
  a plan's own mandated precondition has been vacuous this way. A gate that has never failed is
  unproven, exactly like a test.

## A killed measurement is relaunched, not converted into a question

Killed ≠ stopped applies to **measurements**: a probe that dies externally is relaunched, not
narrowed and not turned into an ask — one decisive re-run was killed twice, each time converted
into hedging, and when finally relaunched it settled the question in one pass. A completion-gate
red whose cause is *measured* pre-existing and outside the work's subject is **journal-and-proceed**
(entry with the evidence, plus a first-class note for the human who reviews at merge) — not a stop.
Resume has its own trap: re-running a dead agent from scratch **re-applies its work on top of its
own partial residue** — revert the residue first, or treat the orphaned diff as a draft and verify
it in the main loop.

## Prescriptive beats prohibitive, co-located beats filed

A prohibition fails at the moment of need because it does not supply the alternative; the rule that
sticks pairs them in one sentence ("never X; do Y instead") — one recurring failure ended
permanently the day the prohibition gained its prescription. Instructions that encode commands are
themselves code: **run the command once before landing the rule**, because an instruction can be
wrong in its own syntax and its author is the one person who never executed it.

The phase closes on a **debrief** — signature defect, what the reviews caught and missed, autonomy
losses, instruction audit, environment facts, and a prediction for the next phase. Measured across
one run, the debrief out-produced every review round as improvement inflow. And it is a **file at
a named path with its existence a completion-checklist box** — never "present the report": a step
a chat message can satisfy lands in conversation and dies there, which is how three consecutive
runs produced every review artifact reliably and zero debriefs. It is a numbered step, not a
habit; so is archiving what got fixed.

## The record is load-bearing

Agents act on prose they cannot cross-examine, so the record's mechanics are correctness inputs:

- **A comment that makes a checkable claim carries the evidence burden of the test it replaces.**
  "No path does X" is a census; "unreachable" is a measurement. Prefer the hedged form —
  "measured: …", "as of <ref>, the only writer is …" — over bare absolutes, and shrinking an
  absolute does not help; the only stable form names what is known today and disclaims
  completeness. **An agent that relies on a comment to justify NOT doing something verifies that
  comment first** — it is being used as evidence.
- **Attribution is a claim**: verify introduced-here vs. pre-existing against the base branch
  before journaling it; mis-attribution sends the fix to the wrong owner and the lesson to the
  wrong ledger.
- **A derived artifact is owed by any commit that CHANGES its source, not only one that adds to
  it** — a one-character rewording regenerated nothing, no test could see it, and the stale
  artifact answered users wrongly in production's language. Regeneration tools that fuzzy-match
  are not an edge case; read what they matched.
- **Archived means closed.** Open work parked inside an archived entry is invisible debt — re-file
  the residue first or do not archive. A decision-log entry is **marked superseded, never edited
  away**. Every measured figure names the commit and the selection it was taken against. And
  artifact paths are keyed **per phase**, not per plan-date — two phases of one plan writing to the
  same dated path destroyed the first phase's record.

## Handoff is where fatigue lands

The orchestrator's worst decisions cluster at one moment: translating a verdict into action — alone,
at speed, deep in a session, working from an accumulating stream rather than a written brief. Agents
get a fresh deliberate prompt; the orchestrator does not. So the handoff step gets **slower** as the
session lengthens, not faster, and it is the step most worth interrupting for a checkpoint.

## Review, then remediate

At the phase boundary the main loop runs `review-gate` with the adapter's `reviewer` — the full
method lives in that skill: checkpoint-commit the reviewed tree first, prefer findings verified by
execution, attack the previous round's fixes and their interactions hardest, check every fix at the
layer the user sees, and end every finding either fixed or journaled by explicit decision. Fixes run
on the judgment model (`model-per-role.fixer`) as a normal batch — edit, no git — and the main loop
commits them **through the same gates as any batch**. Cap the re-review rounds; at the cap, minor
residue is journaled and flagged loudly, never silently dropped — but cap-expiry with a *falling*
score and serious findings still live is a stop-and-ask, not journal-and-ship (see `review-gate`'s
triage rules; the cap exists for diminishing returns, and that case is the opposite). Review, fix
commits, and journaling are **all main-loop-owned** — never buried inside a background run, which
can't pause, commit, or journal.

## When a batch won't land

Don't retry the same move blindly. Fixing a single failing task is the inner loop (bounded attempts
with the findings in hand). If a batch still won't land, hand the **remaining** plan to
`adaptive-replanning`: re-derive what to do next from the current state, carrying the failure's cause
as a lesson — reorder, split, insert a prerequisite, or stop and say why. Finished work is left
alone; the failure is a route now known to be blocked.

## An owner's decision is not a pipeline bypass

A human ruling settles WHAT to do, never HOW fast it skips the gates: even a decided
catastrophe-severity fix runs edit → verify → review like any other change — urgency is what the
pipeline is *for*, not an exemption from it. One decided fix was hand-implemented within hours of
the ruling, outside every gate; the recovery that worked is the pattern to keep: journal the
breach, and mandate a **retroactive scoped review** of the bypassed diff as the next phase's relay
scope — which proved the fix independently AND found residue the hand-fix had not considered. The
retroactive review is the recovery, not a license.

## Resume

Durable state is the **plan + progress markers + solutions log + git** (the adapter's
`artifact-paths`), never the tool. A fresh session reads those and continues from the first
unfinished item. Log concrete outputs so later sessions know the live state.

When the runner supports resuming a fan-out, know its physics: resume replay is typically
**prefix-based** — a run that dies mid-flight forfeits everything after the divergence point, and
a whole-run resume can re-run and lose completed work. Checkpoint outputs as they arrive, and
prefer a **small one-off continuation script with the missing work inlined** over resuming the
whole run.

## The lines that never move

- The main loop owns **all git** and **all `shared-files`** writes. Agents edit and return; the main
  loop applies.
- Gated `apply` steps never run here — `mode-select` gates them.
- Structured schema returns only — commit correctness never depends on parsing prose.
- Cheap model for bulk edits; judgment model for review, fix, and domain-verify. Never one model for
  everything.
