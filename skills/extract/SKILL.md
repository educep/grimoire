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
arc paid that price twice with one word ("despachada") and nearly a third time with a shortened
status list. Freeze the affected rule, name the exact object the answer touches, and ask the single
clarifying question.

## Shape the output

For each task: a title in the project's own vocabulary, what the input actually said (quoted, so
intent survives the translation), what the investigation found (files, root-cause hypothesis marked
as hypothesis), **testable acceptance criteria**, a priority with a reason, and its dependencies.
Deduplicate against the existing backlog and the tech-debt journal — a report may be a known entry
resurfacing, which is an update, not a new task. Then hand the list to `to-plan` (if the work needs
design) or `to-issues` (if it's ready to slice), and record decisions and open questions where the
adapter says durable state lives.
