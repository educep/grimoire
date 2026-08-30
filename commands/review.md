# /review

Review code in the **current session**, without dispatching a subagent.

> **Why this exists alongside the reviewer agent.** The agent form is for orchestrated runs, where a
> parent needs findings back as data. This form is for a human who wants a review *now*, in the
> conversation they are already in, at no extra context cost. Same method, different caller — which
> is exactly why each states its own persistence contract rather than sharing an assumption.

## 1. Load the method

**Read the `review` skill (`skills/review/SKILL.md`) and follow it** — scoping, reachability rating,
plant-over-inspection, output shape, triage dispositions.

**Then read the adapter's `reviewer` capability** for this project's checklist, severity names, and
fix-round cap.

## 2. YOUR PERSISTENCE CONTRACT — print by default, save only when asked

- **Default: print the report into the conversation. Write no file.**
- **If the invocation gives a path**, write the complete report there and confirm the path.
- **Never infer a path from convention.** A review with nowhere stated to go goes to the screen.

*(The agent form writes nothing at all; an orchestrated stage has the orchestrator write the file.
Three callers, three answers — stated separately on purpose. The one time this was left unstated,
an executor polled for a file nobody was going to write, 191 times.)*

## 3. What you were given

$ARGUMENTS

**If no arguments**: review the staged changes plus any files named in the conversation.

**If reviewing a branch, use an explicit baseline** — the adapter's `git-conventions` capability
names the integration branch, so the range is `<integration-branch>...HEAD`. State the baseline in
the report. A local-baseline guess (last commit, last fetched head, last branch point) produces
inconsistent reports between machines and between runs, which is how two reviewers of the same
branch end up disagreeing about scope rather than about code.

## 4. After the report

Apply the skill's triage dispositions. Anything genuinely deferred goes to the project's backlog per
the adapter's `artifact-paths` — **recording is total**; the round cap gates fixing, not recording.
