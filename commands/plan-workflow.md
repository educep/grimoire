# /plan-workflow

**Phase 2 of the planning pipeline: dispatch planning.** Take the issue list Phase 1 produced and
turn it into a dependency-aware, batch-ordered execution plan — one self-contained stage contract
per batch, plus a thin orchestration guide (`WORKFLOW_PLAN.md`) that a cold session can resume from.

> *Compiles from the skills:* [`mode-select`](../skills/mode-select/SKILL.md) (is this even the
> right mode), [`to-plan`](../skills/to-plan/SKILL.md) and
> [`to-issues`](../skills/to-issues/SKILL.md) (how the plan and its issues speak),
> [`execute`](../skills/execute/SKILL.md) (batching, dispatch, the commit boundary, the record),
> [`review-gate`](../skills/review-gate/SKILL.md) and [`review`](../skills/review/SKILL.md) (the
> phase-end loop, the relay, the closure round),
> [`refactoring-discipline`](../skills/refactoring-discipline/SKILL.md) (a split is its own issue at
> the front), [`adaptive-replanning`](../skills/adaptive-replanning/SKILL.md) (a batch that will not
> land).
> *Reads the adapter capabilities:* `overview`, `module-topology`, `format`, `verify`,
> `apply`/`deploy`, `git-conventions`, `integration-branch`, `release-branch` *(optional)*,
> `model-per-role`, `reviewer`, `shared-files`, `backlog`, `records`, `artifact-paths`,
> `constraints`, `refactoring`, `orchestration-tool` *(optional)*, `code-graph` *(optional)*,
> `docs-lookup` *(optional)*, `shell-conventions` *(optional)*.

> **FIRST ACTION, before reading anything else here: check whether the adapter's
> `orchestration-tool` is actually in YOUR tool list.** If it is not — the normal case for a
> dispatched executor, which runs below the depth where orchestration tools are granted — **skip
> this command's script appendix entirely**. Hand-dispatch each stage with the agent tool and carry
> each stage's schema as an enumerated RETURN FORMAT section inside its prompt. Everything else here
> still applies: the batching, the serialization analysis, the coverage table, the ceremony, and
> `WORKFLOW_PLAN.md` itself. *(The check costs one glance, and it belongs where the reader starts: a
> dispatched executor once read a whole template section of scripts it could not run before reaching
> the sentence saying so.)*

> **Read the project adapter FIRST. It is law.** Every project specific below — the format and
> verify commands, the model per role, the reviewer persona and severity scale, the shared files,
> the constraints, the docs-lookup route and its library names — comes from that file. Where
> anything here and the adapter disagree, **the adapter wins**, and you should fix this command.
>
> **Four facts shape every decision in this document:**
>
> 1. **A background run cannot pause for the human.** It runs to completion; it cannot stop and
>    wait. So review gates, triage and approval pauses live in the **main loop**, *between*
>    dispatches — never inside one.
> 2. **Dispatched agents share ONE working directory.** Isolation per agent is banned (see Rule 4).
>    Dispatch does not buy you more parallelism; it buys encoded dependencies, validated structured
>    returns, background execution and resume.
> 3. **Git is ALWAYS main-loop-owned.** The dispatched agents never run git. They do edits, tests
>    and structured returns; the main loop commits sequentially afterwards.
> 4. **Every dispatched agent's RULES block names the shared files BY PATH and says "surface content
>    in your return; never write these."** The git prohibition does not imply it — measured: a
>    one-off fix script whose rules forbade git but not shared-file writes had its agents authoring
>    backlog entries and re-ticking the plan's own acceptance boxes. This applies to EVERY dispatch,
>    one-offs included.

## Input

`$ARGUMENTS`

If it names a file, read that issue list. If it names none, take the most recent `TODO.md` under the
adapter's `artifact-paths` plans root.

## Where this fits

```
/macro-plan-extract → TODO.md → /plan-workflow → the phases run
```

This is the **only** Phase-2 command. Human-gated and infrastructure work needs no second command:
Step 0 routes it to a main-loop checklist inside the same plan.

## YOUR PERSISTENCE CONTRACT — plan, reviews and debrief are all FILES

- `WORKFLOW_PLAN.md` and the per-batch stage contracts go in the **same round-keyed directory** as
  the `TODO.md` they compile, under the adapter's `artifact-paths` plans root.
- **Every review round writes a FILE** — r0, every fix round, the relay, and the closure review —
  under the reviews root, phase-keyed and round-suffixed. A dispatched reviewer **returns** its
  report and writes nothing, so **whoever dispatched it owns the write**: inside a phase that is the
  executor, not the orchestrator. *(Stated because it failed on two consecutive phases in the host
  project: one round's closure findings existed nowhere in the tree, and the next phase lost both of
  its review rounds — twenty-six findings — recoverable only because the reviewer agents happened to
  still be resumable. "Journal-only" names where a finding may not GO; it was read as permission not
  to file at all.)*
- **The debrief is a FILE** at the reviews root, and its existence is a completion-checklist box.
  "End the phase report with a debrief" was satisfied by conversation three runs running, and zero
  of those debriefs survive, while every review report — a file at a named path — still exists.

______________________________________________________________________

## Process

### Step 0 — Is dispatch even the right mode?

Before authoring ten batch contracts, confirm the work is dispatch-shaped. This table encodes the
`mode-select` criteria; invoke that skill directly if the shape is unclear or changes mid-flight.

| Work shape | Mode |
|---|---|
| Feature phases, many file-disjoint edits | **dispatched batches** (this command) |
| Correctness-critical logic (money, tax, tenancy, idempotency, concurrency, auth) | **dispatched batches with a domain-verify stage** |
| Anything on the adapter's gated `apply` list — deploys, production migrations, resource deletes, DNS | **main-loop checklist**, human-confirmed, never a background agent |
| A small one-off fix | **neither** — do it in the main loop under the standard tail: a branch cut from an up-to-date `integration-branch`, the adapter's `reviewer` gate over the diff, one PR |

**Then check the `orchestration-tool` availability** as the header says. If it is absent, the plan is
**identical in contract and different in mechanism**: hand-dispatch, one call per stage, each schema
carried as an enumerated return-format section in the prompt. Record the substitution in the plan's
§ Deviations. Do not emit scripts you cannot run.

**Hybrid is normal and correct.** A plan may dispatch its code issues and run its infrastructure
steps as a main-loop checklist. Don't force one mode over a whole plan. Gated-apply issues are said
out loud in `WORKFLOW_PLAN.md`, routed to the checklist — and they still count for the Step 9
coverage check.

### Step 1 — Read the law, and VERIFY the capabilities this plan binds

Read the adapter and the project's overview documents.

**Then verify, don't just read.** The adapter is prose and its claims expire. For each capability
this plan will actually bind — `verify` and `reviewer` always; `refactoring` if any file is near the
cap; `git-conventions` and `integration-branch` always; any push-time check the `verify` capability
names — **check its operative claims against the tree**: run the guard, measure the file, read the
hook configuration. An adapter sentence used as a precondition is a gate, and **a gate must be shown
able to fail before it is trusted**.

Findings go in `WORKFLOW_PLAN.md`'s **Deviations** section and are amended **before launch**:
planning time is the sanctioned amendment window, and the adapter is frozen mid-run. A lesson the
plan needs is already backported into this command or the adapter; the tree — not a lessons ledger —
is the authority on whether an adapter claim still holds.

### Step 2 — Read and analyze the issue list

Per issue determine:

- **which files it modifies** (from its "Files to touch");
- **which issues it depends on** — file conflicts, migration order, logical prerequisites;
- **whether it is correctness-critical** (money, tax, tenancy, idempotency, concurrency, auth) —
  those get a domain-verify stage in Step 6;
- **estimated size**, in the units your harness bills.

### Step 3 — Build the dependency graph

- **File-level conflicts** — two issues editing the same file cannot share a batch. The second agent
  must not build on the first's uncommitted edits.
- **Migration ordering** — schema before data before constraint.
- **Logical dependencies** — create the model before adding the reference to it.
- **Structural prerequisites** — split an oversized file before editing its parts.

**Batch on real file conflicts only.** A serialization rule inherited from a gate that has since
moved is a rule that shapes your whole topology for nothing: check the adapter's `verify` capability
for what actually runs at commit versus at push, and say explicitly in the plan when a reader might
expect a constraint that no longer exists.

### Step 4 — Batches inside phases

**The batch is the unit of parallelism; the phase is the unit of review and PR.**

Two issues share a batch **only if their file sets are disjoint** and neither's output is the
other's input. If they overlap, they are two batches — the main-loop commit between batches is what
resets the tree. Keep batches small (one to four issues): easier to review, easier to resume.

**The file set includes the VERIFY footprint, not just the edit footprint.** Verify stages mutate
production files in place (positive controls, mutations), so a "file-disjoint" pair whose verifiers
touch the same module will collide — one verifier reads the other's un-restored mutation and raises
a correct alarm about a transient state. Union each issue's edit set with its verify-mutation
targets, **including the modules it merely renders or traverses**, then intersect. Where only the
verify sets overlap, serialize the verify stages and write the reason into the contract's header.
Mutation-versus-traversal collides; traversal-versus-traversal usually does not.

Ordering rules within a phase:

1. **Structural refactors first** (file splits, renames) — they unblock everything else, and per
   `refactoring-discipline` a split is its own issue at the front, never a rider on a feature commit.
2. Bug fixes before features — fixes establish the correct baseline.
3. Data-shape changes before the surfaces that read them.
4. Security fixes are high priority regardless of stated priority.

Group batches into **phases** with a thematic label. **A phase ships as one PR.**

#### Branches — stack while the parent is unmerged; a merged parent means cut fresh

- Phase 1's branch is cut from the adapter's `integration-branch`. A later phase is cut from the
  previous phase's branch **only while that branch is still unmerged** — no dependency judgment
  beyond that. Once the parent PR has merged, the next phase cuts from the integration branch, and
  the plan's cut-from line is superseded by the merge; record the supersession in the tracker.
- **Where PRs do stack, they merge bottom-up and each dependent is RETARGETED before the one beneath
  it merges.** Merging a base branch and deleting it in the same act closes its dependents rather
  than retargeting them, and a closed PR whose base no longer exists can be neither reopened nor
  re-based — the only recovery is a new PR, which loses the original's review thread. Delete
  branches only once the whole stack has landed.
- **If the adapter says the project has a single branch**, all of the above has **collapsed** — say
  so in the plan rather than leaving the reader to wonder which step was skipped.
- Name branches by the project's `git-conventions` type prefix and a phase slug — never `phase/N`.
  Record the concrete name for every phase in `WORKFLOW_PLAN.md`.
- Every issue in a phase commits **linearly** onto that phase's branch (one commit per issue). Never
  create per-issue sibling branches; never merge branches. Linear accumulation means a later issue
  touching a shared file just adds on top — there is no branch-versus-branch conflict to resolve.
  *(The one narrowing, from `git-conventions`: a batch that DELETES a module commits by
  importability, because the commit removing the module and the commits removing its references are
  only jointly valid and commit-time hooks run against the staged tree.)*
- Accepted trade-off: rejecting an early phase outright requires rebasing the phases stacked above it.

#### Phase close — the regeneration commit

If the adapter's `verify` capability names a check that **mutates the tree** — a regenerated
catalog, lockfile or schema snapshot — the phase regenerates it **once**, at phase close, before the
review gate, committed on its own. Record it as a step in the plan; **agents never run it**, and the
main loop inspects the resulting diff rather than leaving it as silent drift.

### Step 5 — Write self-contained issue prompts

Each prompt is what one dispatched agent receives. It must be fully self-contained — the agent has
NOT read the issue list. It contains:

1. Priority, a sentence of context, and a one-sentence task.
2. Numbered concrete steps referencing **exact file paths and SYMBOLS — never line numbers.** Line
   numbers are stale the moment a prior phase lands; a symbol survives every upstream edit short of
   a rename, and a rename fails loudly. **Check steps ⊇ acceptance before emitting** — an acceptance
   criterion claiming a scope the steps never name is a spec error the agent will resolve in your
   absence. At runtime the tie-break is: **steps are authoritative**; the gap is journaled, never
   silently absorbed. **Every count or census a prompt states is a HYPOTHESIS the agent re-derives
   before acting** — a plan that named two instances where three existed would have shipped a wrong
   string on a confirmation dialog by following its own census.
3. **The docs-lookup call, inlined literally** — the exact tool names and the relevant library names
   copied from the adapter's `docs-lookup` capability. Never write "see file X for the library
   table": an agent must not read a file to learn a tool call. Include the rule that an unreachable
   route is reported in notes, never silently replaced by training data. *(Capability absent → say
   so in the prompt, so the agent knows the expensive path is the intended one.)*
4. **Test requirements**: new behaviour gets tests; any user-facing change is verified **at the layer
   the user sees** (render the real surface with the real data shape, not just the layer beneath it);
   the project's `constraints` get their own case where they are the thing at risk; and **no test may
   derive its expected values from the code under test.** That last one is not pedantry — a
   thirty-six-case transition matrix that built its expectations from the very table it was testing
   stayed green when a forbidden transition was opened. It pinned nothing, in exactly the place the
   issue existed to protect.
5. **The sibling-writer sweep, whenever the issue writes or guards a field or a status**: grep every
   sibling mutator — services, endpoints, tasks, signals, admin, buttons — and pin each door;
   disabling the guard must redden a test at EVERY door. Prefer moving the guard INTO the shared
   choke point over per-door copies. This is the single most repeated miss on record, and it
   happened because prompts never asked for it.
6. **Mandated tests are specs — check they CAN fail.** If a prompt mandates a specific test, the
   agent confirms the test is capable of going red for the behaviour it claims to pin, and **says so
   if it cannot**. An acceptance criterion that says "X must succeed" unconditionally certifies
   whatever the success hides.
7. The hard constraints (see § Subagent constraints), and "end in a `format`-clean state".
8. The structured return schema.

**Escalate only what is genuinely underivable.** Before writing a blocking question, check whether
the answer already exists in **(a)** the brief, **(b)** an adapter or command rule, or **(c)** a
policy header in the file you are blocked on. If yes to any: **at plan time, write it into the plan
as decided, with the basis quoted and overridable in one line; mid-execution, act and report in one
line.** Never a menu.

Two tells that you already have the answer: **you can label an option "the human's own fallback"**
(the brief pre-authorized it, so taking it is executing the instruction, not deciding beyond it),
and **a policy file states the default** — decision rules live in unexpected places, and the header
of a project's own exemption or baseline file routinely settles the question that stopped the run.
*Measured: a planner hit a file at exactly its hard cap and raised a three-option menu that stopped
the run, having itself labelled option 1 "your own fallback"; all three options were resolvable from
that file's header plus the brief.* **Reserve blocking for a decision that changes what ships AND
has no written default** — a shipped behaviour contradicting a written constraint, where either
resolution is defensible, is the case that genuinely needs the human, and that one must still be
escalated. This rule guards against escalating *less*, not more.

**Never certify anything as already-checked.** Write what the agent must verify, never what you have
verified for it. A prompt that said a particular test "needs no change — it is the correct model"
was wrong, and the agent believed the certification over the evidence in front of it, hardening
everything except the one case that was actually broken. If you think a spot is suspicious, say
"check X"; if you believe it is fine, say nothing and let the agent find out.

**If an issue requires breaking something to prove a test fails**, the file being broken appears in
`filesTouched` **anyway** — a crashed agent leaves the sabotage in place, and a file it never
"changed" is a file nobody diffs.

The per-issue commit message goes in the plan's static recipe, not in the agent's hands.

### Step 6 — Author one stage contract per batch

Write each to the plan's round-keyed directory. Follow § A of the **Output format**. Requirements:

- **One return schema per stage, enumerated and validated**, so returns are data instead of prose to
  be parsed. Anything the main loop must not get wrong lives in the schema or a numbered step, never
  in surrounding prose.
- **Model per role, explicitly, on every dispatch** (adapter `model-per-role`): implementers on the
  cheap tier; verify, domain-verify, review and fix on the judgment tier, or a domain agent type
  where the project declares one. **Never let a verify stage silently inherit the implementer's
  model.**
- **Default to parallel** edit agents for a file-disjoint batch.
- **Every batch gets `edit → verify`.** Not just the correctness-critical ones. A batch with no
  verify stage sends a cheap model's mistakes straight to the review gate unchecked, and the verify
  stage costs a fraction of the implementer. Correctness-critical batches additionally use a domain
  agent type where one exists.
- **The verify prompt requires MUTATION, not reading.** This is the single technique that actually
  finds defects: break the source deliberately and check that a test goes red. Real results from one
  batch — six independent mutations of a module left all thirty-seven of its tests green; opening a
  forbidden transition left all thirty-six matrix cases green; a test survived a forced exception
  inside the block it was meant to exercise. Require a stated **minimum of three mutations per
  issue**, each reported with what was mutated and which test reddened. *"I read the diff and it
  looks correct" is a failed verification, not a passed one.*
- **The contract partitions its own return** — see § A. Do not return a flat list and expect the
  main loop to remember to check verdicts.
- **No git anywhere inside it.**

### Step 7 — The phase-end review and remediation loop

The review is the **closing act of every phase**, driven by the **main loop** — it commits and
writes the records, and a dispatched run can do neither. Encode it in `WORKFLOW_PLAN.md`, in the
single § Execution loop section. It is the `review-gate` skill's loop; what follows is what the plan
must state explicitly.

1. **Review.** With the phase branch checked out and all its commits in, dispatch the adapter's
   `reviewer` agent type on the **judgment tier**, scoped to `<integration-branch>...<phase-branch>`
   — the whole integrated phase in one diff. Save the COMPLETE report to the reviews root, phase-
   and round-keyed. Require a **machine-triagable findings list** (severity, file, one-line summary)
   alongside the prose.

   **Dispatch shape, written into the plan's § Execution loop verbatim:** dispatch the reviewer
   **without a name parameter** where naming a child changes how its result returns, synchronously
   rather than in the background; **the report is the call's RETURN VALUE and the reviewer writes no
   file** — the dispatcher writes the review file from what returned. **Never poll the tree for a
   reviewer's output**; the same read-only command twice with no state change between is a hard
   stop. This sentence belongs in the generated plan, because that section — not this command, and
   not the launch brief — is what the executor has open at the moment it dispatches.

   **Tell it WHAT CHANGED, never WHAT TO LOOK FOR.** Give the diff scope and the file list and stop
   there. A prompted reviewer narrows to what it was pointed at and stops enumerating, which is
   precisely how seven converging static rounds on one PR missed a catastrophe that a fresh,
   unprompted reviewer found on its first pass by enumerating every route itself. On round ≥ 1, add
   only the **already-resolved** findings, so settled ground is not re-litigated — and never a list
   of suspicions. If a phase genuinely needs a specific check, encode it as a **test** or a verify
   stage, where it runs every time; do not smuggle it into the reviewer's prompt, where it costs
   coverage.

2. **Triage** by the adapter's `reviewer` dispositions — that capability is the single source, and
   **recording is TOTAL; the cap gates the fixing, never the recording.** High severities are always
   actionable. A lowest-severity finding verified real, local and cheap folds into the current fix
   round; one real but not worth doing now is **recorded in the `backlog`, marked not scheduled,
   with the reason and the report path**; a refuted one is rejected with its refutation, preferably
   by execution. **Nothing is silently dropped**: every finding ends fixed or recorded by explicit
   decision.

3. **Gate on the actionable set — never on the score.** A score is a snapshot of one reviewer's one
   method; a falling score means that method is exhausted, not that the work is clean. Continue only
   when the actionable set is **empty**.

4. **Remediate.** If actionable findings remain and the round is below the adapter's fix-round cap
   (**the value, the definition of a round, and the trajectory clause all live in the adapter's
   `reviewer` capability — read them there; never restate a number here or in a generated plan**),
   dispatch a fix round with the triaged, file-disjoint finding groups **inlined into the contract**
   — arguments have arrived empty silently often enough that inlining is the default, and an empty
   finding set is an ERROR, never a no-op that dispatches zero agents. Fixers run on the **judgment
   tier**. The main loop re-runs the gates, commits the fixes onto the phase branch, increments the
   round and **re-reviews** — fixes re-enter the gate, because the worst findings are usually in the
   previous round's fixes.

5. **Close with the relay; open the next phase with backlog intake.** Whichever way the loop exits —
   actionable set empty, or cap spent — the final fix round's diff gets a **scoped,
   verification-only review** before the phase is declared done, so no code ships unreviewed. Its
   findings are **recorded as phase-labelled entries, never fixed in-phase**; fixing would start an
   unreviewed round N+1.

   **The departure clause**, the single exception: an **introduced-here regression with user-facing
   impact** may be fixed in-phase iff the fix is a minimal diff, carries its own mutation proof in
   the commit, and the phase then ends with a **second scoped relay on that fix's diff** (the
   recursion terminates because the diff shrinks each pass; without the re-relay the departure
   commit is itself the unreviewed round the relay exists to prevent). **Cosmetic and prose findings
   NEVER ride the departure commit** — recording them costs one entry, folding them in widens the
   unreviewed surface, and the first live departure fixed five of eight findings while its summary
   reported one. The summary must state the departure's full scope.

   **The closure round**, where the project's `reviewer` capability declares one: after the relay,
   residue that is **low-severity, cheap, and in files the phase already opened** is fixed in ONE
   bounded round, then a **scoped verification-only review of that closure diff alone** runs, and
   ITS findings are recorded only — the loop ends there, guaranteed. **The closure review SUSPENDS
   the class-sweep obligation**: the sweep rule says an in-class instance in an already-opened file
   is in scope, and at the closure review that would reopen the loop the closure round exists to
   end. **A terminal gate that a sweep can reopen is not terminal**, so the closure guarantee wins.

   **Every recorded entry carries the `backlog` capability's provenance line** — phase, round, and
   exit state — because intake triages by it. The exit states are not interchangeable: a clean or
   cap-spent exit is routine residue and prime intake material; **`needs-human` means the AGENT
   halted on a stop predicate** and the entry is under-triaged by construction with a pending
   question. **An external interruption is not an exit state at all** — killed is not stopped, the
   loop resumes, and nothing is recorded because of it. *(But after three identical kills, change
   METHOD, not scope: a narrower probe of the same shape keeps buying the same kill, whereas the
   same coverage in a form the harness will finish is what works.)*

6. **Archive the outflow.** Recording has TWO directions. Before closing, move every backlog entry
   this phase RESOLVED — by an issue, a fix round, or incidentally — into the archive with a
   resolution note. The journal is only a backlog while fixed entries leave it; in one run, stale
   open entries reached eighteen percent of it because inflow was a numbered step and outflow was a
   habit.

7. **Close.** Write the debrief file. Present the report — score trajectory, what was fixed, what
   was recorded — open or refresh the phase's PR, and continue to the next phase, whose first act is
   the intake above.

#### The four stop predicates

The plan drives phases **in sequence without stopping**, halting only on:

0. **Nothing else.** In particular, a held issue is not a stop — it auto-enters a fix round. If you
   are about to ask the human "should I fix this first or run the next batch", the answer is that it
   was never theirs to answer: scheduling, ordering and remediation are all yours. **A question
   whose answer is derivable from recorded text is not a stop** — if the adapter, a skill or the
   plan already prescribes the action and its guardrails are derivable from recorded decisions,
   derive, apply, and report prominently. **When a skill covers the decision, invoking it IS the
   autonomous path.** *(Canary: an agent asked the human whether to split a file the phase was about
   to extend from three directions, while `refactoring-discipline` plus the adapter prescribed the
   front-of-phase split and the plan's own section supplied the guardrail. The entire answer was on
   disk.)*
1. Actionable findings survive the adapter's fix-round cap — record them and flag loudly.
2. The replan budget is exhausted on a batch that will not land (see `adaptive-replanning`).
3. A genuine product decision surfaces — stop and ask; never guess.
4. Any step on the adapter's gated `apply` list.

**Merging a PR is never automatic** — that is always the human's call.

### Step 8 — Write the orchestration guide

Write `WORKFLOW_PLAN.md` per § C of the **Output format**: the coverage table, the phase/batch/branch
table, the **static commit recipe**, the **progress tracker**, the per-phase reviewer *scope* (files
changed only — never a hunt list), the § Execution loop, resume instructions, deviations, and the
completion checklist.

### Step 9 — Coverage check (MANDATORY — before you emit anything)

The anti-silent-drop guarantee. Do ALL of this and **report the result**:

1. **Build the issue → batch map.** Enumerate every issue number in the source list. Record which
   phase and batch each lands in — or which main-loop checklist, for gated-apply work.
2. **Every issue appears in exactly ONE batch.** The union of all batches equals the full issue set.
   Flag by number: **missing** issues (in the list, in no batch — including any that exists only as
   a "handled in Issue K" mention) and **duplicated** issues. Check that the number of stage
   contracts equals the number of batches.
3. **Dependency order holds.** For every edge A → B, assert A's phase ≤ B's phase, and within a
   phase that A's batch precedes B's.
4. **Cross-references resolve.** Grep the prompts and the source list for "deferred to Issue",
   "lands in Issue", "handled in Issue", "depends on Issue", "see Issue" — every referenced number
   must be a real, slotted issue.
5. **Remediate, don't note-and-ship.** A missing or misordered issue is a STOP-and-fix: add the
   stage contract, the phase entry and the commit-recipe row, then re-run the check until it passes.

Record the outcome as a **Coverage** table in `WORKFLOW_PLAN.md` and state explicitly: "All {N}
issues slotted; dependency order verified."

______________________________________________________________________

## Output format

### A) Per-batch stage contract

One per batch, in the plan's round-keyed directory. Where the adapter declares an
`orchestration-tool`, encode this as that tool's script; where it does not, this **is** the dispatch
plan and each schema becomes an enumerated RETURN FORMAT section in the agent's prompt. The contract
is the same either way.

**The edit stage's return schema** — no branch field: every issue commits onto the phase branch, and
the main loop knows the target.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["issue", "filesTouched", "featureCommit", "status", "notes"],
  "properties": {
    "issue": { "type": "number" },
    "filesTouched": { "type": "array", "items": { "type": "string" } },
    "featureCommit": { "type": "string" },
    "status": { "type": "string", "enum": ["done", "already-fixed", "blocked"] },
    "notes": {
      "type": "string",
      "description": "repro result, decisions, docs-lookup failures, anything the human must see"
    }
  }
}
```

**The edit prompt**, fully self-contained (the agent has not read the issue list):

```
{Priority + one-sentence task.}

You are editing the shared working directory. DO NOT run ANY git command. DO NOT write
{the shared record surfaces, BY PATH, from the adapter's `shared-files`} — those are
main-loop-owned; surface their content in your notes instead.
{The project's shell conventions, from the adapter, if it declares any.}

Docs lookup — before using any API you are not certain of: {the adapter's docs-lookup calls,
inlined literally, with the library names relevant to THIS issue}. If the route is unreachable,
say so in notes — do NOT silently fall back to training data.

Steps:
1. {concrete step, exact file path and symbol}
2. …
N.   Reproduce the finding on the current branch BEFORE fixing it.
N+1. Add or extend tests; assert through the real surface the user sees, not the layer beneath it.
N+2. {Any project constraint that applies — from the adapter's `constraints`.}
N+3. Run the adapter's `format` command. Verify ONLY your own subset — never the full suite.

Acceptance: {testable criteria}.

Return via the schema: issue, filesTouched (mark new files), featureCommit, status, notes.
```

**The verdict schema must make an unverifiable claim visible.** Free-prose evidence lets a verifier
that only *read* the diff return `passed: true` in confident language. Require the commands it ran
and the mutations it performed as structured fields, so "I ran nothing" is legible without reading
prose:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["issue", "passed", "commandsRun", "mutations", "positiveControlReproduced",
               "mainLoopSteps", "evidence", "gaps"],
  "properties": {
    "issue": { "type": "number" },
    "passed": {
      "type": "boolean",
      "description": "THE CODE FIX ONLY. Steps only the main loop may perform go in mainLoopSteps, not into a false here — a designed handoff is not a failed fix."
    },
    "commandsRun": {
      "type": "array", "items": { "type": "string" },
      "description": "Commands you actually executed. Empty means you did not verify."
    },
    "mutations": {
      "type": "array",
      "description": "Minimum 3. Each: what you broke, the EXPECTED reddens, and what actually went red (or NONE — a survivor). Expected-vs-observed mismatches on a re-run are how operator errors get caught.",
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["mutated", "expectedReddens", "testThatReddened"],
        "properties": {
          "mutated": { "type": "string" },
          "expectedReddens": { "type": "string" },
          "testThatReddened": { "type": "string" }
        }
      }
    },
    "positiveControlReproduced": {
      "type": "boolean",
      "description": "You neutralized the fix IN PLACE (git is barred — no checkout), confirmed the original bug actually reproduces, then restored and verified the restoration. If you could not reproduce it, fix your harness before judging anything — never report a pass with an instrument that was never pointed at the bug."
    },
    "mainLoopSteps": {
      "type": "array", "items": { "type": "string" },
      "description": "Designed handoffs pending — steps ONLY the main loop may perform. Sound fix + pending handoffs is NOT a fail."
    },
    "evidence": { "type": "string" },
    "gaps": { "type": "string" }
  }
}
```

**The verify prompt**, which every batch gets, on the judgment tier:

```
Adversarially verify that Issue {N}'s edits actually satisfy: {acceptance}. Files: {filesTouched}.

POSITIVE CONTROL FIRST: neutralize the fix in place, confirm the original bug reproduces (record
it), restore, and verify the restoration. An instrument that never saw the bug proves nothing —
and a control that does not fail is more often an unlanded mutation than a broken guard, so
confirm the mutated file actually changed before crediting it.

Then MUTATE — at least three ways, recording the EXPECTED reddens BEFORE running. A mutation that
reddens nothing is a finding, not a formality. For layered or redundant guards, prove each layer
INDEPENDENTLY: neutralize the others and drive a route that bypasses them — guards only ever
tested together are one guard plus decorations. Pick DISCRIMINATING inputs, not edge values: a
boundary value can make a guard invisible, and a structurally minimal fixture (one row, one item,
one tenant) cannot observe accumulation, per-row guards, or a scoping filter at all.

Assert the PERSISTED END-STATE — re-read the record or file after the operation — never the call
sequence: a fix whose effect is overwritten lines later passes every call-level check.

If the change guards or writes a field or status, RE-DERIVE the writer census yourself (grep the
writes plus every route) and prove the guard at every door on YOUR list — checking the provided
list only checks the list against itself.

GENERATION FRAMING — read this as the main instruction, not a footnote. You are generation N of a
lineage: each previous fix closed a defect and opened a NEW one of the same class. On one run that
held FIVE times consecutively and the fixer caught none of them; every one was found by a verify
stage told, in as many words, that its job was to find the input its own fix breaks. Passing the
acceptance criteria is the FLOOR, not the finding. Your real job is to construct the input on
which the NEW code is wrong and the OLD code was right.

If you find nothing, say in gaps exactly WHICH falsification you attempted and why it failed. An
empty finding-set with no described falsification attempt is itself a finding against you.

SCRATCHPAD: agents in this batch run in PARALLEL against ONE shared working directory. Name every
aside copy, probe and scratch file after YOUR OWN issue number — never a generic name. A generic
name has caused one agent to write another issue's file over a source module. Before mutating a
file, COPY IT ASIDE and restore from the copy, hash-verifying the restore — a version-control
checkout restores to the last commit and destroys uncommitted work, which during a batch is
almost always present. Delete every aside copy the moment it is consumed.

Run the relevant tests, never the full suite. Restore everything before returning. No git.
```

**The contract partitions the result — the main loop must not have to remember a rule.** A held
issue that reaches the commit phase looking committable is how a flagged defect ships. **Three
buckets, not two**: a sound fix pending a main-loop handoff must not masquerade as a failure.

```
sound      = verdict.passed AND commandsRun is non-empty AND positiveControlReproduced
committable    = sound AND mainLoopSteps empty
pendingHandoff = sound AND mainLoopSteps non-empty
held           = everything else
```

`WORKFLOW_PLAN.md` then says: commit `committable`; perform each `pendingHandoff` item's
`mainLoopSteps` yourself, then commit it; feed `held` into a fix round. A shape the main loop cannot
misread.

> **Put shared constraints in EVERY prompt block, including the verify prompt.** Where the edit
> prompts interpolate a shared constraints string and the verify prompt is assembled separately, a
> rule placed only in that string does not reach the verifiers — and the verifiers run last, longest
> and in parallel. Measured: the scratchpad-collision rule was added to the shared string after it
> bit once, and the very next collision was **between the two verify agents**, one of which wrote
> six hundred lines of the wrong module over a source file. Its own hash check caught it. When you
> add a batch-wide rule, grep the contract for every prompt block and confirm it appears in each.

### B) The fix-round contract

One per remediation round, run while the phase branch is already checked out so fix agents edit
exactly the code the reviewer reviewed. **Inline the ACTIONABLE findings as a constant — do not rely
on arguments.** Arguments have arrived empty often enough (silently → zero agents dispatched) that
inlining is the default, not the workaround. Pre-group them so parallel fix agents stay
file-disjoint: co-located findings go to one agent. **An empty finding set is an ERROR, not a
no-op.** **Fixers run on the judgment tier** — a wrong fix is expensive, and fix rounds are where
the worst defects are born.

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["findingId", "filesTouched", "fixCommit", "resolved", "notes"],
  "properties": {
    "findingId": { "type": "string" },
    "filesTouched": { "type": "array", "items": { "type": "string" } },
    "fixCommit": { "type": "string" },
    "resolved": { "type": "boolean", "description": "true if the finding is fully addressed" },
    "notes": { "type": "string" }
  }
}
```

The fix prompt is `/fix-review`'s agent prompt: the finding verbatim, the files it may touch, the
constraints, "reproduce it if a test can express it, fix it, add a regression test that FAILS
without your change", verify your subset only, no git, no shared-record writes, and the return
schema. **A fix sweeps the CLASS, not the pointed instance** — and the class sweep is only as wide
as its vocabulary: for claims in prose (comments, docstrings, citations) the sweep is READING the
neighbours, because a false comment need contain none of your grep terms.

### C) The orchestration guide — `WORKFLOW_PLAN.md`

````markdown
# Workflow Plan — {plan name}

> Each batch fans out file-disjoint edit agents and returns validated contracts. Every issue in a
> phase commits linearly onto one branch, shipped as a **single PR**. **Git, shared-record edits,
> and the review gate stay in the main loop.**

Source plan: [`TODO.md`](./TODO.md). Project law: the adapter.

## Coverage (Step 9 — every issue is slotted)

| Issue | Phase | Batch | Correctness-critical? |
|---|---|---|---|
| {1} | {1} | {1} | {yes → domain-verify stage / no} |

End with: "All {N} issues slotted; no issue exists only as a dependency reference; dependency order
verified."

## Deviations

{Adapter claims this plan verified and found stale; the mechanism substitution if the
orchestration-tool is absent; any capability that is absent and what was skipped because of it.}

## Serialization constraints

{Only the REAL ones: which issues share files — edit set ∪ verify-mutation set — and therefore
cannot share a batch. If a reader might expect a constraint that no longer applies, say so.}

## Execution order

```
PHASE 1 — {title}   branch: {type}/{slug-1}   (cut from the integration branch)
  Batch 1 → {contract 1}: Issue {A} ‖ Issue {B}   (file-disjoint)
            COMMIT ORDER onto {type}/{slug-1}: {A}, then {B}.
  Phase close: {regeneration commit, if any} → ★ REVIEW + remediation → PR → integration branch

PHASE 2 — {title}   branch: {type}/{slug-2}   (cut per Step 4 § Branches: from {slug-1} while it
                                               is unmerged, else from the integration branch)
```

## Static commit recipe (the main loop owns git)

Fixed values — commit correctness never depends on parsing a return.

| Phase (branch) | Issue | Commit message | Files to stage |
|---|---|---|---|
| 1 (`{type}/{slug-1}`) | {A} | `{type(scope): … (Issue A)}` | {explicit list, incl. NEW files} |

## Progress tracker (tick as you go — this is what a cold session resumes from)

- [ ] Phase 1 — branch cut from {base}
  - [ ] Batch 1 dispatched
  - [ ] Issue {A} committed
  - [ ] Issue {B} committed
  - [ ] {regeneration commit}
  - [ ] Review r0 — score, actionable count, report file written
  - [ ] Fix round 1 (if needed) / actionable set empty
  - [ ] Relay review — report file written
  - [ ] Debrief file written
  - [ ] PR opened

## Reviewer scope (per phase)

{For each phase, ONLY: the diff range and the list of files it touched. **No hunt list, no "look
for X".** On re-review rounds, add the findings ALREADY RESOLVED — nothing else. Phase-specific
checks belong in tests or a verify stage, not in the reviewer's prompt.}

## Execution loop

Preconditions, at the start of every phase:

- Working tree clean, **and the base branch in sync with its remote** — a stray unpushed local
  commit otherwise folds silently into the phase PR.
- **No other session is operating in this checkout, or in any worktree of this repository.** A
  worktree isolates the working tree and index only; the object database, every branch, the stash
  and the hooks are shared. A clean tree says nothing about this.
- The adapter's `verify` setup is up.
- **Every named agent type resolves right now.** Check it, don't defer it — a name that fails to
  resolve degrades silently into a weaker generic agent that reads like the real one. The cheap
  check is to read the definition's first lines and confirm its frontmatter parses.
- Cut the phase branch per Step 4 § Branches, running `git branch --show-current` FIRST.

Then, per batch in order:

1. Dispatch the batch's stage contract.
2. **Commit only what it returns as `committable`.** A `held` issue does not stop the run and does
   not go to the human: feed its gaps into a fix round, re-run the gates, re-verify. Its edits stay
   in the tree; the other issues commit around it.
3. **Re-run the gates yourself** — format, lint, types, the relevant tests — regardless of what any
   agent reported. A dispatched agent's completion is not evidence, and a crashed agent's diff is an
   unreviewed draft even if the tree happens to be green. Inventory the tree before deciding
   anything. **If the batch changed a module's public shape** (signatures, imports, patched
   attributes), run that module's SIBLING suites too — agents are barred from the full suite, so the
   main loop is the only actor who can catch a batch silently breaking tests that patch what it
   deleted.
4. **Diff any generated artifact, and any file an issue broke-then-restored, before staging.**
   Prose is not a control: an agent told not to regenerate a catalog did it anyway.
5. Stage the agent's `filesTouched` **plus anything your own gate run modified**, or that churn
   rolls into the next issue's commit and blurs the boundaries. **Stage by PATH, not by directory
   sweep** — then read the status again and check for unstaged files the commit's story requires.
6. Commit per the static recipe, one issue at a time.
7. In the same commit phase: apply the record content the agents surfaced, tick this tracker, and
   append to the solutions log. These are loop steps, not paperwork — done by hand at the end of a
   long day they are simply forgotten.

**Before the phase's FIRST commit, and again AFTER the phase's LAST commit, run the claim audit over
your OWN prose** — the same audit the verify stage runs over agent output.

**The second pass runs after the last commit, not before it, and this is not a detail.** A claim
audit is a *snapshot*: it certifies the tree as it stood when it ran. Prose written before the final
commit is stale by construction. Measured: a round whose audit reported two failures had **eight**,
and every one of the six it missed was a number correct at audit time and wrong by the time the
phase ended. The audit did not fail; it was pointed at the wrong moment.

Over every document you wrote or edited this phase:

- **every NUMBER** — re-derive it by running its command and counting mechanically, not by eye;
- **every LINE-NUMBER citation** — open the file and confirm the content is there. Your own edits
  shift them, including edits to the file you are citing;
- **every absolute** — "only", "never", "always", "the first", "the sole" — prove it over the whole
  file, or **delete the absolute**;
- **every "X causes Y"** — verify Y independently. X existing where you said is not evidence for Y.

Fix what fails **by deleting**, never by rewriting with a qualifier. **Report the failure count**; a
silent zero is not credible on a run that has produced this class before.

At phase close:

```
round = 0; cap = {the adapter's `reviewer` fix-round cap — value, round definition, trajectory
                  clause. Never restate the number.}
loop:
  1. reviewer agent (adapter `reviewer` type, JUDGMENT tier) diffing
     <integration-branch>...<phase-branch>; the report is the RETURN VALUE; YOU write it to the
     reviews root as review_phase_{N}.r{round}; require a machine-triagable findings list.
  2. triage per the adapter's `reviewer` dispositions (recording is TOTAL; the cap gates fixing).
  3. if ACTIONABLE empty  → break        # the gate is the actionable set, NOT the score
     if round >= cap      → record the unfixed, flag loudly, STOP
     else: dispatch the fix round with the finding groups INLINED
           re-run the gates → commit fixes → round++ → re-review
  3b. after EVERY fix round: re-run any push-time or generated-artifact check the adapter names —
      a clean diff on the generated file is not proof of lockstep, and fix rounds can add inputs
      after the phase's regeneration commit. Where the check is a pattern scan, use a tool whose
      failure mode you have tested: an engine that REJECTS your pattern exits in a way a shell
      conditional reads exactly like "no match", which is a vacuous gate.
  3c. ON EXIT (either exit): the RELAY — a scoped, verification-only review of the final fix
      round's diff. Findings → phase-labelled records with the provenance line, NEVER a new fix
      round; then the bounded CLOSURE round if the adapter declares one, and its own scoped
      verification-only review, whose findings are recorded only. Each of those reviews writes
      its own FILE. When a relay finding is resolved as a SIDE EFFECT of an already-planned step,
      record it WITH the resolution stated — recording it live would file a false record, and
      fixing it would breach the rule.
  4. WRITE THE SEVEN-SECTION DEBRIEF to the reviews root (template: this command's § Debrief — a
     COMMAND-file section; the plan does not contain it). Present the report citing it; open or
     refresh the PR; continue to the next phase, whose FIRST act is backlog intake.
```

## Resume

State is artifacts plus git, never a tool's memory: the tracker above, the committed history, and
the review files say where a cold session is. **Before resuming a failed stage, revert the dead
agent's edits or verify its orphaned draft in the main loop** — a re-run applies its work ON TOP of
its own residue, and a crashed agent's diff is an unreviewed draft, not lost work.

## Completion checklist

> **This is the round's ONLY completion checklist.** The issue list keeps its per-issue acceptance
> boxes — they are the original *specification* and are never re-ticked to mirror execution — and
> links here for round-level completion. Do not restate any box below in another file; a second copy
> is a drift generator, not a convenience. *(Measured: two hand-maintained checklists over the same
> facts drifted apart four consecutive times in one round, the stale side inverting on every fix.)*

- [ ] All N issues resolved, or closed as already-fixed with a regression test and evidence.
- [ ] New behaviour has tests; user-facing changes asserted at the layer the user sees.
- [ ] The adapter's `verify` gate green (main loop), `format` clean, static checks clean.
- [ ] The adapter's `constraints` hold across the diff.
- [ ] Each phase shipped as ONE PR following the project's template; one commit per issue.
- [ ] Commits follow `git-conventions`.
- [ ] Every review finding fixed or recorded by explicit decision; resolved backlog entries archived.
- [ ] Every review round's report file exists — r0, each fix round, the relay, the closure.
- [ ] Per-phase debrief file exists (the artifact with the worst survival record when left to chat —
      its existence IS this box).
````

______________________________________________________________________

## If the adapter declares an `orchestration-tool`

Everything above is the contract; this is the mechanism, and it applies only when the tool exists
**in your own tool list**. Author its scripts per the tool's own authoring reference, and carry
these hazards — each measured, none of them specific to one tool:

- **Keep the script's metadata a pure literal** — no variables, calls, spreads or interpolation —
  where the tool parses it statically.
- **Nothing non-deterministic in the script**: a clock read or a random value breaks resume. Vary
  labels by index instead.
- **Mind the quoting of prompt bodies.** Where prompts are embedded strings, a stray quote character
  of the embedding kind is a defect in prose that looks like content. The dangerous variant fails at
  RUNTIME rather than at parse time — a doubled quoting character can form a *valid* construct with
  the wrong meaning, and it dies mid-run. **A parity count is NOT a check** (doubled characters
  satisfy it): track quote state, and **grep the finished script before every launch**.
- **Syntax-check with a checker PROVEN against a broken control.** Measured: a plan mandated a
  checker that exits zero *without parsing* the file class it was pointed at, so it green-lit
  anything — a vacuous gate its planner had "verified" with. Feed your checker a deliberately broken
  script and watch it throw, first.
- **Keep every schema SPARSE.** A large output schema can be rejected before the run starts. The
  schema carries the FIELDS the gate must not miss; instructions live in the prompt.
  Schema-enforcement is not schema-verbosity.
- **Keep the three stoppage causes apart**: a rejected launch is yours to fix; provider overload is
  a relaunch; a quota limit is neither. Three causes, three responses — do not diagnose one as
  another.
- **Resume is cached from the divergence point.** A mid-run death forfeits everything after it, and
  a whole-run resume can re-run and lose completed stages. Checkpoint outputs as they arrive and
  recover with a small one-off script carrying the missing work inlined.
- **A killed verify stage leaves IN-PLACE production mutations** beyond its own probe files. After
  any killed or crashed verifier, run a **mutation-residue sweep** — re-run the affected suites and
  diff the tree for un-restored mutations — before trusting anything.
- **A validated contract proves shape, not truth.** One editor did the work and returned a
  placeholder contract with a fake file list. The main loop's own tree inventory is the control.

______________________________________________________________________

## Rules

01. **One contract per batch; two issues share one only if their file sets are disjoint** — edit set
    ∪ verify-mutation set. The main-loop commit between batches is the only reset there is.

02. **One integration branch + one PR per phase.** The branch-cut rule lives in **Step 4 § Branches**
    and is stated only there. Issues commit linearly; never sibling branches, never merges.

03. **Git is forbidden inside every dispatched agent.** The main loop owns every git command,
    sequentially. Every issue prompt says so explicitly.

04. **No per-agent isolation.** Agents edit the shared project directory directly. An isolated
    checkout cannot load whatever the project leaves untracked — environment files, installed
    dependencies, built assets — so an agent there edits blind and its verify stage has nothing to
    run; and where verification shares infrastructure, the isolation buys nothing anyway. *(Session-
    level worktrees for long-lived separate actors are fine; one actor per worktree, and repo-wide
    operations belong to one designated actor.)*

05. **Structured schema returns are mandatory** on every dispatch. No prose parsing. The contract
    partitions its own output. Anything the main loop must not get wrong belongs in the data or in a
    numbered step, never in surrounding prose — that is the general rule behind most of the others.

06. **Model per role, explicitly, on every dispatch.** Cheap tier for bulk edits; judgment tier for
    verify, domain-verify, review and fix. Never one model for everything, and never a verify stage
    inheriting the implementer's.

07. **Every batch pipelines edit → verify**, and every verify prompt requires **at least three
    mutations**, each reported with what was broken and which test reddened.

08. **Never certify anything as already-verified in a prompt.** State what to check, never what you
    checked. And every acceptance criterion names the single artifact that goes red — a criterion no
    correct implementation can satisfy gets waved through on an unwritten looser reading, after
    which every criterion reads as advisory.

09. **The commit recipe is static.** File lists and messages live in `WORKFLOW_PLAN.md`; an agent's
    notes are for the human summary only.

10. **The main loop owns the shared records** (the backlog, the decision log, the solutions log, the
    plan files) and re-runs every gate itself before committing. "Main-loop-owned" names the actor
    that MERGES — a phase executor is the main loop of its own session and still proposes rather
    than writes.

11. **The phase ends with the review and remediation loop**, main-loop-driven, gated on the
    **actionable set** and never on the score. Fixes re-enter the gate. Past the cap, record loudly.

12. **Docs-lookup is inlined literally** into every issue prompt from the adapter's capability —
    tool names and library names, never a file reference — with the "report unreachable in notes"
    rule.

13. **Where scripts are involved, the script-authoring hazards above are not optional reading**, and
    a gate that has never been shown to fail is not a gate. *(This rule's own history is the canary:
    it once named the wrong symptom for a real cause — right about the mechanism, wrong about the
    effect — and a planner who had read it shipped the defect anyway, because the symptom it warned
    about is not the symptom that occurs.)*

14. **Prevention is friction; detection is the control.** A hook, a prompt prohibition or a
    permission rule reduces how often the boundary check has to fire — it never replaces it. Every
    prohibition worth having gets a detection at the commit or push boundary that does not care HOW
    the violation happened. *(One project's generated-artifact guard was bypassed three different
    ways; the boundary check caught all three.)*

15. **Every issue must be slotted (Step 9).** Union of batches == the full issue set, no duplicates,
    no issue existing only as a "deferred-to" reference, dependency order verified. A miss is a
    STOP-and-fix, not a footnote.

16. **Announcing is not doing.** A main-loop turn never ends on "starting X now" — that is a stall,
    not a stop. End a turn only on completed work or a genuine stop predicate. Self-stall is an
    autonomy failure of the same rank as asking a derivable question.

______________________________________________________________________

## Debrief (a FILE at the reviews root — mandatory; its existence is a completion-checklist box)

Answer from EVIDENCE — a file, a command, a moment — never generalities; "nothing to report" beats a
platitude. Seven sections:

1. **Avoidable difficulty**: the three costliest difficulties better instructions would have
   prevented — what happened, what it cost, and **the exact replacement sentence** you would want to
   have received.
2. **Off the charts**: what no instruction even began to cover; what you improvised; whether it
   worked; rule or judgment?
3. **Autonomy losses**, ranked by time lost, each classified: (a) missing instruction, (b) wrong
   instruction, (c) instruction you missed — and what made it miss-able, (d) environment or harness,
   (e) genuinely needed the human.
4. **Instruction audit**: (a) which need to be MORE explicit — quote them, name the ambiguity,
   propose the tightened wording; (b) which are NOISE — never used, duplicated, deletable; (c) which
   you RE-READ mid-phase, because those are the load-bearing ones and they must stay findable.
5. **Environment**: which shell and interpreter your commands actually ran under, and any failure
   traceable to an environment mismatch.
6. **The phase's signature defect**: name the recurring defect-shape, count the instances, and name
   the single check that catches the class.
7. **Prediction**: the one thing most likely to bite the NEXT phase that you can see and its agent
   cannot.

**The debrief is triaged like backlog intake** — it is improvement inflow, not commentary — and that
triage includes the standing question: **does anything here contradict or extend an ADAPTER rule?**
If yes, record it with its provenance for the between-runs amendment window; the adapter is frozen
mid-run.

______________________________________________________________________

## Subagent constraints (embed in EVERY dispatched prompt)

- **No git.** Any git command is the main loop's job.
- **No writes to the main-loop-owned shared records** — named BY PATH — surface the content in notes.
- **Never run the full test suite.** The adapter's `verify` capability names it and names who may run
  it; where verification shares infrastructure, two concurrent runs destroy it. Verify your own
  subset.
- **Never BACKGROUND a long test run**, and that applies to the main loop's phase-close run too.
  Measured: three backgrounded attempts were killed at ninety-odd percent of their collected items
  with zero failures reported in any of them, while every foreground run completed. **The cause was
  never established** and the obvious hypothesis was refuted by the third data point — so the rule
  is procedural, not a mechanism to re-derive from one observation. Where a full run exceeds the
  harness ceiling, run it as **foreground chunks** and **prove the chunks are a partition**: their
  collected-item counts must sum to the whole suite's collect count. That sum is what makes chunking
  a measurement rather than a sample. Three facts that make it work: **derive the collection roots
  rather than assuming them** (assuming a subset partitions the suite costs a re-derivation
  mid-close); **a slow suite needs sub-chunking** by its own timing, not by directory tidiness; and
  **piping a long run through a truncating filter buffers everything**, so a killed run shows nothing
  at all — redirect to a file and read the file. Always ask the runner to name failures as they
  happen; a truncated capture that names its failure is a diagnosis, and one that does not is
  nothing.
- **Never tear down shared verification infrastructure** — it is shared, and taking it down at the
  end of your verification breaks the next actor's first command. Lifecycle belongs to the main loop.
  *(Including by another route: if the project's runner tears it down on exit, pass whatever flag
  keeps it up.)*
- **Follow the project's test-file naming conventions** from the adapter, including any prefix its
  hooks key on — a collection hook's exclusion pattern is the authority on its own trigger, not a
  remembered list of names.
- **Multi-line content you surface for the main loop** goes in notes as plain text; the main loop
  commits from a FILE, never from an inline multi-line argument.
- **Do not regenerate any shared generated artifact** — the main loop does that once, at phase
  close, and inspects the diff.
- **One shell command per call**, and the project's other shell conventions from the adapter. *(State
  this once and move on. Measured: several agents chained anyway, and escalating the wording across
  successive prompts did not stop the next one; every violation was harmless and several were
  self-disclosed. Prevention is friction, detection is the control — check the diff instead of
  spending prompt budget re-arguing it.)*
- **Dedicated tools over shell equivalents**, per the adapter's `shell-conventions`.
- **End in a `format`-clean state**, with your subset of tests passing.

______________________________________________________________________

## After writing

Tell the human:

1. Where `WORKFLOW_PLAN.md` and the per-batch contracts were saved.
2. The phase/batch structure as a summary table — which batches are single-agent, which are
   parallel, and which carry a domain-verify stage and why.
3. **The Step 9 coverage result**: "All {N} issues slotted; dependency order verified", or the list
   of missing or misordered issues you fixed. Confirm the contract count equals the batch count.
4. **A per-role cost estimate**, since the roles differ by several times: implementer runs versus
   judgment-tier verify, review and fix runs.
5. The exact prompt to paste to start Phase 1.
6. The preconditions that must hold before it: the adapter's `verify` setup up, every named agent
   type resolving, and any one-time hook installation the project requires in this clone.

