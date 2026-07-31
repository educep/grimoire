---
name: to-plan
description: Synthesize an approved design into a plan. Use after roast, when a design spec exists and you need a written plan before slicing it into work; no interview, just synthesis of what roast already settled.
---

# Turn the design into a plan

Take the approved design (the spec `roast` produced) and what you know about the codebase, and turn them into a written plan. Do not re-interview anyone; just synthesize what is already settled.

Start by choosing the seams you will test the feature at. Prefer seams that already exist, and pick the highest one you can, since fewer seams across the codebase is better and one is ideal. Check that those seams match what the user expects before you go further.

Then write the plan to a file (the adapter's `artifact-paths` says where; for example `docs/plans/YYYY-MM-DD-topic-plan.md`). Include the problem in the user's words, the solution in the user's words, a numbered list of user stories in the form "as an [actor] I want [feature] so that [benefit]", the seams you chose, and the vertical slices. A slice is the smallest end-to-end piece that delivers something a user can see, and it cuts through whatever parts of the codebase it needs rather than building one layer on its own. Order them smallest first.

Plan in slices; do not pre-batch. The slice is the unit of **value** — what can be demoed and shipped. The unit of **parallelism** is a different thing, the file-disjoint batch, and it is derived later by `execute` from the adapter's `module-topology`: in a feature-organized repo your slices are already file-disjoint and run in parallel as they are; in a layer-organized repo they collide on shared files and `execute` will regroup them, recombining at the PR boundary so the phase stays demoable. Batching concerns must never bend the plan — a plan warped to be parallelizable stops being demoable, and the trade is not yours to make here.

Use the project's own vocabulary and respect the conventions it already follows, and do not reopen decisions the spec has already made. When the plan is agreed, hand it to `to-issues`.
