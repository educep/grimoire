---
name: extract
description: Turn messy raw input — reviewer messages, bug reports, chat transcripts, meeting notes, review findings — into an investigated, prioritized task list. Use as the front door when work arrives as prose instead of a spec; feeds to-plan or straight to to-issues.
---

# Extract the real tasks

Raw input lies in both directions: it under-describes (a screenshot and one sentence hiding three
distinct defects) and it over-describes (a wish that reads as a requirement). This skill turns it
into a task list someone could execute cold — **investigated, deduplicated, prioritized, with
testable acceptance criteria** — written to the adapter's `artifact-paths`.

## Investigate before you write

Every claim gets checked against the actual system before it becomes a task: read the code the
report implicates, reproduce what can be reproduced, follow the path the user followed. An
un-investigated task list is just the input re-formatted. Investigation is also what splits bundles
— "password email doesn't arrive and the deleted user can't be re-created" is one message but
probably two defects with two owners (a send failure and a uniqueness residue), and only reading the
code tells you. Where the input references artifacts you can open — screenshots, logs, linked pages
— open them; where it references ones you cannot, say so in the task rather than guessing.

## Don't invent work; don't launder ambiguity

Nothing goes on the list that the input plus the investigation doesn't support — no "while we're at
it". When something is genuinely unclear, it becomes a **needs-clarification** item with the one
precise question attached, not a guessed task. And the sharpest trap of all: **when a decision
owner's answer differs from the options they were offered — a status list paraphrased, a term that
doesn't exist in the system, a narrower set than what was proposed — that is a question, not an
answer.** Acting on the paraphrase costs a full round trip through implementation and review; a real
arc paid that price twice over a single word of the owner's paraphrase, and nearly a third
time over a shortened status list. Freeze the affected rule, name
the exact object the answer touches, and ask the single clarifying question.

Two qualifiers keep the needs-clarification lane honest. **Search the record before asking at
all**: the recorded text that can answer a question includes the decision log wherever it lives —
one escalated "product decision" was already settled, in writing, in the owner's own notes, which
made the ask not just blocking but redundant; an inconsistency with an already-decided rule is a
defect to fix, not a policy question to re-open. And when the question is genuinely open but
**reversible and cheap to redo, attach a draft answer** marked as the default you will proceed
with — a blocking ask with no draft is how a two-sentence item stalls for weeks.

## Backlog entries are claims that expire

When the input *is* the backlog — a debt journal, an issue list — every entry gets re-derived
against the tree before it becomes work, exactly like any other raw report. One reconciliation
round found five entries stale or wrong on measurement: two already fixed, one premise void, one
undercounting its own sites, one claiming a fix that covered half its instances. *The backlog was
not too large; it was unreconciled.* An entry that names counts or sites states them as of a date;
planning from entry text without re-derivation plans the stale half.

## Shape the output

For each task: a title in the project's own vocabulary, what the input actually said (quoted, so
intent survives the translation), what the investigation found (files, root-cause hypothesis marked
as hypothesis), **testable acceptance criteria**, a priority with a reason, and its dependencies.
Deduplicate against the existing backlog and the tech-debt journal — a report may be a known entry
resurfacing, which is an update, not a new task. Then **return the list to whatever invoked you**
— where a command or another agent called this skill, go back to that caller and continue
there. Only when this skill is running as a step of the standalone skill pipeline does the list
pass onward to `to-plan` / `to-issues`; if a caller invoked you, handing off instead of
returning skips the rest of that caller's work. Record decisions and open questions where the
adapter says durable state lives.
