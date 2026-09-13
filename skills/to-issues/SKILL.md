---
name: to-issues
description: Break a plan into independently grabbable issues, one vertical slice each. Use after to-plan to turn a plan into tracked work in your issue tracker (Jira, Linear, GitHub Issues, or other) before building starts.
---

# Break the plan into issues

Break the plan into small tracer-bullet issues, one thin vertical slice each. A slice cuts through whatever parts of the codebase it needs, can be demoed on its own, and is small enough to fit in one fresh context window. Never carve the work up by layer — the issue is the unit of **value**. (Parallelism is a separate, later concern: at execution time, `execute` groups issues into file-disjoint batches using the adapter's `module-topology`, and in a layer-organized repo that grouping may be more horizontal than the slices are. That is a batching decision made there, never a reason to plan by layer here.)

Explore the affected code first. If some groundwork would make the real change easier, do that as slice zero: make the change easy, then make the easy change. For a wide mechanical change like a rename or a retype whose reach will not fit in one slice, sequence it as expand then contract. Add the new form next to the old one, move the call sites over in batches, and only then delete the old form. Do not attempt it as one big rewrite.

For each slice, capture a title in the project's own vocabulary, who will build it, the files it touches, what success looks like, its dependencies, and its order (smallest first). Then create one issue per slice in your tracker (Jira, Linear, GitHub Issues, or other), linked to the parent project or ticket and tagged with its slice number, with block and is-blocked-by links between them so nothing runs ahead of an unmet dependency. Ordering is a default, not a straitjacket: any issue whose blockers are all done is fair to pick up, so work the frontier.

Before showing anyone the breakdown, run the coverage check — the anti-silent-drop guarantee: every piece of the plan appears in exactly one issue; the union of the issues is the whole plan with nothing left over; every dependency points at an issue that actually exists (no work that lives only as a "deferred to issue N" mention inside another issue's text); and no issue depends on one ordered after it. A plan that fails this check has already lost work — silently, which is the worst way.

## How an issue speaks

- **Certifications are forbidden.** An issue says what to CHECK, never what is "already verified" —
  an acceptance criterion asserting an outcome unconditionally once made an agent write a test
  blessing the defect it existed to catch. A mandated test is a spec too: demand that the test be
  shown to fail. And an acceptance criterion is a **runnable check**, not a sentence — a sentence
  can be arithmetically impossible and nobody notices, least of all its author, who is also its
  grader.
- **Every number is a hypothesis.** State counts, site lists and censuses as "measured on <date> —
  re-derive before acting", because the executor who trusts a stated census ships the stale half.
  The plan's own worked examples are hypotheses too: check the example actually discriminates the
  correct implementation from the wrong one before building acceptance on it.
- **So is every other claim in the input.** A pre-existing backlog entry's counts, its stated
  mechanism, its blast radius, its prescribed fix, and the premise of any ruling it cites are all
  hypotheses to be falsified by measurement and *reported* — never implemented against once
  falsified. Measured: an entry's recorded blast radius of two branches was 415 failures across 73
  files; another entry's prescribed remedy, executed as written, would have deleted the very
  coverage it existed to protect; a third was false at the moment it was written.
- **A filed list of sites is a LOWER BOUND with a stated blindness.** An entry names the sites the
  round that filed it could see, and that round was usually fenced — often by a detector whose own
  blind spots the entry silently inherits. Reading the entry as the scope inherits the blindness;
  one such list named three sites and a proper derivation found a fifth live site and a second
  carrier class nobody had named. **So the first step of the fix re-derives the population with a
  predicate that does not share the filing guard's seed** — and when a predicate's precision comes
  out at a few percent, **the axis is wrong, not the threshold**: the derivation that worked changed
  what it keyed on, from where a value flowed to what the value *is*.
- **A hazard is not a defect, and an entry that cannot state the mechanism says so.** "This function
  takes no lock" names a hazard; a contention claim is actionable only when it states the cycle —
  what each side holds, what it then wants, and what state must exist for both sides to be live at
  once. An entry that cannot state that must say *"the mechanism is underived; deriving it is the
  first deliverable"*, because deriving it is usually larger than the fix and an entry that hides
  that mis-sizes its own phase. The same shape covers any claim that needs a population before it
  needs a patch: until you know what state makes both sides live, you cannot write a failing test,
  and without a failing test the "fix" is an argument.
- **Ask where the invariant lives before enumerating doors.** If the issue is "pin N write paths",
  first ask whether the invariant belongs where no door can bypass it — a storage-level constraint,
  one shared chokepoint — and then include what enforcing it there breaks (every environment, not
  just production) in the issue's scope.
- **Irreversible-consequence work ships alone.** A money movement (or anything that changes
  published figures) is its own issue, its own commit, legible in isolation — never a rider.
- **An issue number is an identifier, not an order.** New work appends; renumbering breaks every
  reference already in reviews, commits and the journal.
- **Refusal is a legitimate outcome.** An issue disproven by execution keeps its record: criteria
  struck through with the disproof, never ticked, and the sources that caused the wrong premise
  (headers, test names, docstrings) corrected so the next round does not repeat the path.

Show the proposed breakdown as a numbered list and get the user's sign-off before you create anything. Then take them one issue at a time.
