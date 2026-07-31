---
name: to-issues
description: Break a plan into independently grabbable issues, one vertical slice each. Use after to-plan to turn a plan into tracked work in your issue tracker (Jira, Linear, GitHub Issues, or other) before building starts.
---

# Break the plan into issues

Break the plan into small tracer-bullet issues, one thin vertical slice each. A slice cuts through whatever parts of the codebase it needs, can be demoed on its own, and is small enough to fit in one fresh context window. Never carve the work up by layer — the issue is the unit of **value**. (Parallelism is a separate, later concern: at execution time, `execute` groups issues into file-disjoint batches using the adapter's `module-topology`, and in a layer-organized repo that grouping may be more horizontal than the slices are. That is a batching decision made there, never a reason to plan by layer here.)

Explore the affected code first. If some groundwork would make the real change easier, do that as slice zero: make the change easy, then make the easy change. For a wide mechanical change like a rename or a retype whose reach will not fit in one slice, sequence it as expand then contract. Add the new form next to the old one, move the call sites over in batches, and only then delete the old form. Do not attempt it as one big rewrite.

For each slice, capture a title in the project's own vocabulary, who will build it, the files it touches, what success looks like, its dependencies, and its order (smallest first). Then create one issue per slice in your tracker (Jira, Linear, GitHub Issues, or other), linked to the parent project or ticket and tagged with its slice number, with block and is-blocked-by links between them so nothing runs ahead of an unmet dependency. Ordering is a default, not a straitjacket: any issue whose blockers are all done is fair to pick up, so work the frontier.

Before showing anyone the breakdown, run the coverage check — the anti-silent-drop guarantee: every piece of the plan appears in exactly one issue; the union of the issues is the whole plan with nothing left over; every dependency points at an issue that actually exists (no work that lives only as a "deferred to issue N" mention inside another issue's text); and no issue depends on one ordered after it. A plan that fails this check has already lost work — silently, which is the worst way.

Show the proposed breakdown as a numbered list and get the user's sign-off before you create anything. Then take them one issue at a time.
