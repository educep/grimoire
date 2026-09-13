# /macro-plan-extract

**Phase 1 of the planning pipeline: task extraction.** Take whatever arrived — a transcript, client
notes, bug reports, feature requests, review findings, a slice of the backlog, or all of them at
once — and produce an investigated, prioritized issue list that Phase 2 can compile into an
execution plan.

> *Compiles from the skills:* [`extract`](../skills/extract/SKILL.md) (the extraction discipline —
> invoked operatively, not cited), [`roast`](../skills/roast/SKILL.md) (for design-shaped input),
> [`to-issues`](../skills/to-issues/SKILL.md) (how an issue speaks),
> [`refactoring-discipline`](../skills/refactoring-discipline/SKILL.md) (when an item wants a file
> that is already too long).
> *Reads the adapter capabilities:* `overview`, `artifact-paths` (where the issue list is written),
> `backlog` (what a deferred or falsified item becomes), `constraints`, `reviewer` (the gate the
> investigation route's small fix still runs), `integration-branch` and `git-conventions` (the
> tail), `code-graph` *(optional)*, `docs-lookup` *(optional)*.

## Input

`$ARGUMENTS`

If it names a file, read it. If it is inline text, use it. If there is nothing, ask for the source
material rather than inventing a subject.

## YOUR PERSISTENCE CONTRACT — you write the issue list

One file, `TODO.md`, in a **round-keyed directory** under the adapter's `artifact-paths` plans root.
Pick the round key now: every downstream root — reviews, solutions — uses the **same** one. **List
the parent directory first**; a directory that already exists holding different work means you need
your own key, never a shared one, because a collision on `TODO.md` overwrites the other plan.

______________________________________________________________________

## Step 0 — Route the ITEMS by kind, before extracting anything

**Route per ITEM, not per input.** Real input mixes kinds. Split it into items first (a light pass
of Step 2), classify each, and then — **settled items are extracted FIRST, always**. Never serialize
eight settled items behind one owner interview or one investigation: extract the settled subset now,
queue each non-settled item through its route, and feed its output — a spec, or a proven diagnosis —
back into the same list when it lands.

Three kinds, and the tell for each is **who holds the missing answer**:

- **Settled** — bug reports, review findings, decided features: the *what* is known and the
  acceptance criteria are writable today. Go to Step 1.
- **Design-shaped** — a feature idea, an under-specified request: the *what* is still open, and the
  tell is that you would have to **guess an acceptance criterion**. The **OWNER** holds the missing
  answer. **Invoke `Skill(roast)` NOW and follow it** — interrogate the design with the human, one
  question per message, explore-before-ask, until it is settled and written as a spec under the
  adapter's `artifact-paths` specs location. Only then come back and extract from the spec.
- **Diagnosis-shaped** — a flake, a "fails only when…", an unknown mechanism, a reachability
  question: the tell is that you would have to **guess a MECHANISM**, and the **TREE** holds the
  missing answer. **Run the investigation NOW, in this session, before extracting that item** — see
  the investigation route below. Routing this kind at the owner is wrong twice over: it asks a
  question the owner cannot answer, and it parks work an experiment settles today. Extracting anyway
  plans against a guess. *An input that **supplies** a mechanism without proof is still
  diagnosis-shaped whenever acting on it requires believing that mechanism — the entries that
  arrive with a confident mechanism attached are the ones whose mechanism is wrong.*

**The threshold between design-shaped and a needs-clarification stub** (both claim a small
owner-held question): **if ONE precise question settles the item, it is a stub** — park it with that
question written down and keep extracting. **Roast is for items where the answers interact** — where
each answer spawns the next question, or where several acceptance criteria would have to be guessed
together. A blocking one-question-per-message interview about a label is ceremony; a parked stub for
a whole feature is a guess deferred, which is worse.

**When both non-settled tells fire on one item** — the owner holds the *what*, the tree holds a
feasibility mechanism the *what* depends on — **the owner question goes first**: it is cheaper and
may kill the investigation. *Unless* the owner's decision depends on the tree's answer, in which
case investigate **exactly that dependency**, nothing more, then take the finding into the
interrogation. Say in the issue list which case it was.

The roast route is an **operative invocation, not a reminder**: actually call the skill. If it is
not available, **STOP and say so** — do not improvise the method from memory; a half-remembered
interrogation reads like the real one and settles nothing. Skipping it on design-shaped input is how
under-specified decisions become confidently wrong plans.

### The investigation route (diagnosis-shaped input)

1. **Reproduce before you explain.** Make the failure deterministic first — isolate one variable,
   hold everything else constant. A mechanism you have not reproduced is a hypothesis, and entry
   hypotheses are wrong more often than they are right. *(Two measured rounds stand behind this: one
   whose fix was conditional on an answer nobody had, and one that closed three flake entries by
   **falsifying both** standing hypotheses — the entries blamed the scheduler and the transaction
   machinery; the causes were the wall clock and a lazily-imported route table.)*
2. **Every mechanism claim cites its reproduction command.** Verify the CAUSAL half: a real symbol
   at a real line is not evidence for the effect it is offered as proof of. For flake work, masking
   is forbidden — retries, quarantine groups, reordering, flaky marks, widened waits. If one seems
   genuinely right, that is a decision to surface, not a fix to ship.
3. **Checkpoint the finding with the owner before acting on it** when the diagnosis changes product
   behaviour, implicates production code, or contradicts a recorded decision. A tests-only or
   docs-only fix with a proven mechanism proceeds without one.
4. **Then extract — or ship.** With the mechanism proven the work is plannable. If what remains is
   sizeable, continue at Step 1 and write the list **from the proven answer**, citing the
   reproduction in every issue it grounds. If the fix is small — the common case, because a proven
   diagnosis usually names a small fix — ship it in this session under the tail below, and skip the
   list.
5. **The tail** — spelled out because this route does not pass through Phase 2, which normally
   supplies it:
   - a branch cut from an up-to-date adapter `integration-branch` (**run `git branch --show-current`
     first**: a shared checkout legitimately ends a previous run on someone else's branch);
   - commits at proof points, not only at the end, following `git-conventions`;
   - **the adapter's `reviewer` gate over the diff** before the PR — a decision is not a pipeline
     bypass, and urgency is what the pipeline is for;
   - resolved `backlog` entries annotated with their commit refs, with the archive cut named as
     post-merge work **and an owner for it**: if a separate session merges, name that session; if
     you are the whole pipeline, the cut is YOURS after the merge and is not skippable;
   - entries **not** closed get a dated status block holding the proven mechanism — **a no-fix
     outcome with a proven mechanism is a legitimate deliverable; a plausible-but-unproven fix is
     not**;
   - one PR following the project's PR template, **left open and unmerged**. Never merge; never push
     to the `release-branch`.

______________________________________________________________________

## Step 1 — Read the project's law

Read the adapter (it is law) and whatever overview document the project keeps. This grounds every
extracted task in the actual codebase rather than in the input's vocabulary.

## Step 2 — Extract the raw tasks

**Invoke `Skill(extract)` and follow its discipline** alongside the steps here — same operative
rule: a missing skill is a STOP, not a shrug. The two sharpest parts of that discipline, which these
steps do not restate:

- **Don't launder ambiguity.** A genuinely unclear item becomes a needs-clarification entry carrying
  **one precise question**, never a guessed task.
- **The paraphrase trap.** When a decision-owner's answer differs from the options they were
  offered, that is a question, not an answer: freeze the rule, name the object, ask.

From the input, identify every actionable item — explicit requests, implicit problems (complaints,
confusion, things that "don't work"), review findings, feature requests, and the usability issues
that arrive disguised as opinions.

## Step 3 — Deduplicate and group

Merge overlapping items into one issue. Group items that are one change seen from two sides ("add
field X" + "show X in the form"). Separate genuinely independent concerns, even when they arrived in
one sentence. **Deduplicate against the existing `backlog` too** — an item may already have an ID,
and a second entry for it splits its history.

## Step 4 — Investigate each task

For each extracted task, **read the relevant source files**: what exists today, what must change
(exact files, exact symbols), what it depends on, and what the acceptance criteria should be.

**Do NOT guess file contents. Read them.**

**A backlog entry naming a FALSE CLAIM in shipped prose has TWO admissible resolutions — correct the
claim, or make it true — and the plan must not pick one without checking what the code's current
shape is buying.** Where the claim concerns how often something is read or recomputed, the current
count is usually load-bearing: ask what goes stale before choosing. *(Measured: a plan picked "make
it true" without the check; the implemented change breached a limit under a concurrent writer and
refused legitimate work, and the whole implement-verify-revert cycle was that phase's single largest
cost.)* **A falsified plan claim is a first-class deliverable**: journal it as a marked erratum,
redesign, and put the measured reason in the commit message so it survives the plan file.

**When your re-derivation disagrees with the backlog entry that produced the task, you may overrule
it — but QUOTE the entry's own words where they disagree, and say why.** A "do not re-litigate this"
note binds only where the entry did not already state the contrary; writing one over an entry that
says the opposite converts your wrong reading into a binding instruction, and the executing agent
will honour it against its own verifier's dissent.

**Verify the CAUSAL half of every compound claim you write.** *"X, so Y"* and *"Y — see X"* are two
claims and they are never equally cheap. Confirming that X exists where you say is not evidence for
Y. Every falsehood that shipped from one investigated round had the same shape: a real symbol at a
real line, offered as the mechanism for an effect it cannot produce. Verify Y independently, or
delete the "so".

**If a task wants a file that is already over the project's soft length threshold** (adapter
`refactoring`), run `refactoring-discipline`'s diagnosis now and, if it prescribes a split, schedule
that split as its own issue at the FRONT of the work — decided and reported, never asked.

## Step 5 — Prioritize

| Mark | Priority | Criteria |
|------|----------|----------|
| 🔴 | Critical / blocking | Security holes, crashes, data corruption, blocks other work |
| 🟠 | High | Wrong behaviour, missing core functionality, bad experience on a key flow |
| 🟡 | Medium | Code quality, naming, non-critical usability |
| 🟢 | Low / polish | Cosmetic, nice-to-have, minor cleanup |

## Step 6 — Write the list

______________________________________________________________________

## Output format — `{plans-root}/{round-key}/TODO.md`

````markdown
# {Project} — Development TODO

> Sources:
> - {source 1} ({date}) — Issues {range}
> - {source 2} ({date}) — Issues {range}

---

## Priority legend

| Mark | Priority |
|------|----------|
| 🔴 | Critical / blocking |
| 🟠 | High |
| 🟡 | Medium |
| 🟢 | Low / polish |

---

## Issue N — {short title} {priority}

**Context**: {1–2 sentences on why this matters}

### Root cause investigation (if a bug)

- [ ] {step, with the command that reproduces it}

### Data / schema change (if applicable)

- [ ] {file} — {what changes}
  ```
  {concrete snippet}
  ```
- [ ] Generate and apply the migration, if the project has migrations.

### Interface / API (if applicable)

- [ ] {file} — {what changes}

### User-facing surface (if applicable)

- [ ] {file} — {what changes}

### Files to touch

```
{file}  — {reason}
```

### Acceptance criteria

- [ ] {concrete, testable criterion}

______________________________________________________________________

(repeat per issue)

______________________________________________________________________

## Cross-cutting tasks

### After completing Issues {X, Y, Z}

- [ ] {shared task}

______________________________________________________________________

## Completion checklist

- [ ] All N issues resolved
- [ ] The adapter's `verify` gate green
- [ ] {the project's own checks, from its `constraints`}
````

______________________________________________________________________

## The code graph *(adapter `code-graph`, optional)*

If the capability is declared, run its staleness check and use the graph for the expensive
structural questions — reachability (*can X actually produce Y?*, the causal half of a compound
claim), call-site censuses, consumer hunts. **The one rule that makes an imperfect graph safe: it
may only ever ADD candidates to check — it is NEVER evidence for a negative.** *"Nothing calls X"*
is the conclusion it cannot support, and the one that deletes live code. Absent → answer the
question the expensive way, and say that you did.

## Rules

1. **Be specific.** Every sub-task names exact file paths and **symbols** — function, class, method —
   never line numbers. A line number is stale the moment an earlier issue lands; a symbol survives
   every upstream edit short of a rename, and a rename fails loudly.

2. **Include the concrete shape.** For a data change, show the field. For a fix, show before/after.

3. **Acceptance criteria must be testable** — not "works correctly" but "the user does X, sees Y,
   and the record holds Z". **Ask TWO questions of every criterion; they catch opposite defects and
   you need both:**

   > **(a) What state of the world makes this print FAIL?** If you cannot name it, the criterion
   > certifies nothing.
   > **(b) Can the work this gates actually SATISFY it?** If no correct implementation can pass, the
   > criterion is a gate nothing can clear.

   **(b) is the one people skip, and its defect is the more corrosive.** A criterion that cannot be
   met is not obeyed — it is waved through on an unwritten looser reading, and once one has been
   waved through, the next actor reads every criterion as advisory. *Measured: a plan demanded a
   "pure deletion" diff from an edit that removes a clause from the **interior of a line**, which
   necessarily emits an added line. The shipped commit was one insertion and one deletion — the
   criterion was false on the accepted diff and the round shipped anyway. The same plan's sibling
   issue carried the correct form ("deletions and one reflowed line only"), so the carve-out was
   known and dropped.*

   For **(a)**, three unfalsifiable criteria shipped in one plan, each unfalsifiable a different
   way, and all three passed a plan review:
   - **Wrong scope** — *"the diff over {a whole source directory} must be empty after Batch 2"*,
     false on its face because another issue in the same batch legitimately edits a file under it.
     Name the file, not its ancestor directory.
   - **Arithmetically impossible** — *"the two neighbouring band tests must stay green"* under a
     mutation that widens the band's upper bound, which necessarily reddens every test above the
     band. A gate whose predicate contradicts the mutation it gates can only ever fail.
   - **A tool that skips the path** — a criterion naming a formatter run against a path that
     formatter **excludes**, so the check can only ever print "skipped". **Run the command once
     while writing the criterion.** A hook that excludes the path you name is indistinguishable from
     a hook that passed.

4. **Don't invent work.** Extract only what is stated or clearly implied. Flag anything uncertain as
   a needs-clarification entry with its one question.

5. **Respect the project.** Follow the adapter's `constraints` and the conventions its overview
   documents.

6. **Number issues sequentially** and keep related sub-tasks inside one issue.

7. **Prose discipline — the plan's own writing is unverified code.** Everything in a plan that is
   not a command is a claim, and agents execute claims as specifications. Four rules, each measured:

   1. **When a claim is over-stated, DELETE the over-claim.** Do not rewrite it with a qualifier and
      do not add evidence to support it. A deleted clause cannot be false; a hedged one is a new
      claim carrying the same burden. Over six passes at one over-claim, every pass that *rewrote*
      it introduced a new false clause, because a hedge attaches fresh evidence and each attachment
      is a new claim; the single pass that produced zero false claims deleted it, cited nothing, and
      ran net-negative on lines.
   2. **The documentation test is SOLE RECORD versus RESTATEMENT** — never artifact-count-per-diff-size.
      For each document a plan would mandate, ask: *is this the only home of this content, or a
      second copy of something already recorded?* Sole home → it ships regardless of diff size (a
      debrief, a decision-log entry and a review report are never trimmed). Second copy, or narrative
      restating the diff → cut it. *A size table was tried and deleted: it needed a human override
      twice in two consecutive exchanges, both times because the artifact it cut was the only home
      of its content.*
   3. **Never write a number into a document that is not that number's source.** A file's length
      lives in the file, a backlog census in the backlog, a test count in the test run. Write the
      **property** — "over the soft threshold", "the actionable set emptied" — never the
      measurement. A copied number is a claim that decays on the next commit with no reader who
      would notice.
   4. **A fix that invalidates a comment updates it in the same edit.** No gate catches this class —
      not lint, not types, not tests; only a reader. When a change alters a mechanism, grep the
      neighbourhood for prose that describes it **before** committing.

______________________________________________________________________

## After writing

Tell the human:

1. Where the list was saved.
2. How many issues were extracted, grouped by priority.
3. Anything parked as needs-clarification, with its one question.
4. That the next step is **`/plan-workflow`**, which consumes this `TODO.md` directly and produces
   the batch-ordered execution plan with the review and fix loop embedded. Human-gated or
   infrastructure work needs no second command: that command's Step 0 routes it to a main-loop
   checklist inside the same plan.
