# /pr-review

Review the **whole open PR** — every commit on this branch against the integration branch — and
**write the report to a file**.

> *Compiles from the skills:* [`review`](../skills/review/SKILL.md).
> *Reads the adapter capabilities:* `reviewer` (persona, checklist, severity scale, triage),
> `integration-branch` (the baseline), `artifact-paths` (where the report file goes),
> `constraints` (the project invariants a diff can violate), `backlog` (where a deferred finding
> lands).

> **Load the SKILL, not the reviewer AGENT file.** That file is the *dispatchable* form of the same
> reviewer and its persistence contract is the opposite of this one's: it returns the report and
> writes nothing, because its caller owns the artifact. **This command writes its own file (Step 6).**
> Every caller of the review skill states its own persistence contract; inheriting another caller's
> is how you end up following an instruction written for a different situation.

## 1. Load the method

**Read the `review` skill and follow it** — scoping, reachability rating, plant-over-inspection, how
to falsify a written claim, the output shape, the triage dispositions.

**Then read the adapter's `reviewer` capability** for this project's checklist, its severity names if
it renames the defaults, and its fix-round cap. The skill owns the method; the adapter owns what to
hunt for. Neither is restated here.

## 2. YOUR PERSISTENCE CONTRACT — you write the report file

This command's deliverable is a **file**, written before you report done, at the path Step 6 derives
from the adapter's `artifact-paths`. Print the report as well; the file is what survives.

*(The agent form writes nothing at all; the in-session `/review` command prints unless given a path;
an orchestrated stage has the orchestrator write the file. Four callers, four answers — stated
separately on purpose.)*

## 3. Gather the diff

The baseline is the adapter's `integration-branch`, stated explicitly in the report so two reviewers
of the same branch cannot disagree about scope:

```bash
git log --oneline <integration-branch>..HEAD      # the commits in this PR
git diff <integration-branch>...HEAD --stat       # the files it touches
git diff <integration-branch>...HEAD              # the diff itself
```

**If the adapter says the project has a single branch**, the baseline is the merge base with it and
you say so in the report — a collapsed rule is stated, never silently skipped.

## 4. Read the changed files in full

For every **modified or added** source file in the diff, read the **complete file**, not just the
changed lines. Context matters: an authorization hole or a pathological query usually lives *outside*
the changed lines, in the code the change now reaches.

Skip what carries no reviewable logic — generated files, vendored dependencies, lockfiles, binary
assets, and whatever the adapter's `config-dirs` marks as machine-read configuration. Prioritise the
files where this project's `constraints` can actually be violated; the adapter names them.

## 5. Apply the checklist systematically

Go through **every** category the adapter's `reviewer` capability declares, plus the
stack-independent categories the `review` skill lists, and skip none. Do not narrow to what the diff
"looks like it is about": a reviewer that narrows stops enumerating, and run after run the most
severe finding is one door outside the pointed scope.

Where a claim can be tested by mutating the code and running the affected tests, **do that instead
of reasoning about it** — and restore the tree, verifying the restore, before you return. A mutation
beats an assertion, including yours.

## 6. Write the report, then save it

Produce the prose report in the shape the adapter declares (the `review` skill's default shape if it
declares none), **and always also the machine-triagable list** — `(severity, file, one-line summary)`
per finding — so a caller that acts on this report does not have to parse your narrative.

The report states, at the top: the branch, the **explicit baseline**, and the date. For every
high-severity finding: an exact `file:line`, its **reachability** (who can trigger this, and how),
and a concrete fix. End with the summary the adapter's severity scale implies, and a closing
judgment proportional to what you found.

Then save it:

1. Take the branch name and today's date.
2. Write the **complete** report under the adapter's `artifact-paths` review root, in that root's
   round-keyed directory, named for the branch (replace path separators in the branch name).
3. **List the parent directory first.** The roots are keyed by round, not by bare date: a directory
   that already exists and holds *different* work means you pick your own key rather than sharing
   it — a shared key overwrites the other round's records.
4. Confirm the exact path you wrote to.

## 7. After the report

Apply the skill's triage dispositions. Anything genuinely deferred gets an entry in the project's
`backlog` with its severity intact — **recording is total**; the fix-round cap gates fixing, never
recording. A finding that exists only inside this report's prose is one file nobody opens away from
being lost.

**Fixing is not this command's job.** Hand the report to `/fix-review`, which triages it and
dispatches the fixes.
