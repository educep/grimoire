# Grimoire++ — Merge Design & Continuation Handoff

> **What this file is.** A self-contained design document for merging two planning/execution
> systems into one **stack-agnostic** skill package modeled on Grimoire. It captures everything
> discussed so far so a fresh session (or a different machine, after a software update) can
> continue with zero context loss. Read this top-to-bottom before doing anything.
>
> **Status (2026-07-31):** PIPELINE DRAFTED FRONT-TO-BACK — all §6 decisions LOCKED (§A).
> Drafted: `ADAPTER_CONTRACT.md`, `execute`, **`review-gate`, `mode-select`, `extract`**, and two
> example adapters. TD#85 (the first real-world test) is **closed** — shipped, ~11 review rounds,
> merged, reviewer answered. **§B holds the lessons; §B7 maps each one to the artifact that now
> encodes it. Next: the two-stack agnosticism proof, then the SECOND real test — the 2026-07-30
> Notion bugs through the full pipeline starting at `extract`.**
>
> **Two threads. Do not conflate them:**
>
> 1. **The package** (this repo) — merge Grimoire + Eduardo's `macro-plan-*` machinery into a
>    stack-agnostic, publishable skill set. Next artifact: a non-Django toy adapter, then the
>    two-stack agnosticism proof (§A build plan steps 3–4).
> 2. **TD#85** (`saas_inventory`, a *different* repo) — the real-world test case. Paused
>    mid-flight, unmerged, with three known money-path defects. See **§C**.
>
> **Repo:** this is the fork `educep/grimoire` (upstream `laurentlouk/grimoire`), cloned to
> `C:\Users\Eduardo\Documents\code\grimoire`. **Decision: PUBLISH** (see §6.3).
> **Author of this handoff:** Claude (Opus 4.8), with Eduardo (eduardo@analitika.fr).
> **Started:** 2026-07-27. **Last updated:** 2026-07-30.

---

## 0. The goal in one paragraph

Take the **best of two systems** — Grimoire's short, portable, principle-based *skills* and
Eduardo's battle-tested, project-specific *execution machinery* — and produce a single package,
Grimoire-style, that is **fully stack-agnostic**. "Stack-agnostic" is the hard requirement: the
package must read identically whether the target is Django, Rails, Go, Node, Rust, a data
pipeline, or infra-only work. The current biggest weakness is that Eduardo's commands are
hard-coded to Django (pytest, `make format`, the `.po` i18n hook, `inspector`, company-scoping,
Context7). The merge must strip every such specific out of the *method* and push it into a
per-project **adapter**.

---

## A. ✅ DECISIONS LOCKED (2026-07-27) + immediate build plan

**Read this section first.** All five §6 questions are resolved. Full rationale for each is in §6
(same numbers). This is the authoritative summary — if anything below ever contradicts memory or a
later note, THIS + §6 win.

| # | Question | LOCKED decision |
|---|---|---|
| **D1** | Vertical slice vs file-disjoint batch (§6.5) | **Two steps, never collapsed:** *plan* vertical (value-first), then *batch* at execution by **module topology**. Feature-organized repo → keep slices whole, parallelize directly (demoable AND parallel). Layer-organized repo (e.g. `saas_inventory`) → break into file-disjoint horizontal groups, recombine at the PR boundary. Multi-repo → each repo a bounded scope; cross-repo feature = the vertical, per-repo work = sub-slice. **Driver of parallelism is file-disjointness, not "horizontal."** Adapter declares repo topology (single/multi) + module topology (feature/layer). |
| **D2** | Agnosticism reach (§6.1) | **Axis = authoring vs applying, NOT code vs infra.** *Authoring* (write/plan/reason — app code, data pipelines, docs, AND infra-as-code like Terraform) → the parallel `execute` engine; infra-authoring is a star case (`.tf` is file-disjoint + has a real `terraform plan` verify). *Applying* (mutates live/external state irreversibly — `terraform apply`, `rds delete`, **prod DB migrations**, releases, DNS) → ALWAYS a gated, sequential, human-confirmed checklist via `mode-select`, never a parallel/background agent. `verify`/`test` is **optional & pluggable**; `apply`/`deploy` is a declared-but-**gated** capability the engine may never invoke; "never echo secrets" guardrail. |
| **D3** | Adapter form (§6.2) | **Hybrid, docs-first.** Principle: **"Docs are the evidence, the adapter is the law — a missing README is a slice-zero we offer, not a gate we impose."** Read README+docs first (understanding), manifests second (mechanics); no README → offer to write one but don't block; draft adapter from evidence; **human confirms un-sniffable high-stakes fields** (model-per-role, the gated-apply list, reviewer persona, topologies); commit `.claude/project-adapter.md` (markdown) = runtime law. Detection only bootstraps, never drives execution. |
| **D4** | Scope (§6.3) | **PUBLISH.** Build to publishable quality (which is what enforces agnosticism); name/structure for upstreaming from day one; usable privately across Eduardo's repos meanwhile; coordinate with `laurentlouk` once the shape is proven. |
| **D5** | First build target (§6.4) | **`execute` first** — fully agnostic, adapter **co-designed** (execute is the most demanding consumer, so it earns the real contract), **proven on TWO stacks** (`saas_inventory` Django + one deliberately non-Django repo). Then, step 2, wire `adaptive-replanning` into it. |

### The immediate build plan (execute-first)

1. **Co-design the adapter contract** — the capabilities `execute` consumes by name: `format`,
   `verify` (optional), `apply`/`deploy` (gated), `model-per-role` (orchestrator/implementer/
   reviewer), `git-conventions`, `repo-topology` (single/multi), `module-topology` (feature/layer),
   `shared-files` (main-loop-owned), `artifact-paths`, `docs-lookup`, `constraints`, `secrets`.
2. **Write `skills/execute/SKILL.md`** — fully agnostic (NO tool/language/command names; reference
   adapter capabilities only). Encodes: parallel-edit / sequential main-loop-commit (main loop owns
   git); structured schema returns; model-per-role; pipeline verify; batching by module topology
   (D1); `mode-select` handoff for gated-apply (D2); durable resume.
3. **Author two adapters:** (a) `saas_inventory` (Django: layer-organized; `verify`=pytest;
   `format`=make format; commit-gate=`.po` hook; reviewer=`inspector`; models=opus/sonnet;
   gated-apply=terraform/aws/prod-migrate). (b) A small **non-Django toy** (e.g. Node or Go:
   feature-organized; `verify`=`npm test`/`go test`; `format`=prettier/gofmt).
4. **Prove agnosticism:** hand-craft a tiny 2–3 issue plan for the toy repo, run `execute`, confirm
   it works on BOTH adapters with **zero edits to the skill** — only the adapter differs. That is the
   agnosticism proof the publish decision (D4) requires.
5. **Step 2 (after the proof):** wire `adaptive-replanning` (fix-loop + replan-loop) into `execute`.

> **Real-world first test (Eduardo, 2026-07-27):** beyond the non-Django toy, the *real* first
> proof will be an **already-planned feature living in `saas_inventory/docs/plans/`** — a genuine
> feature waiting to be implemented. The toy proves agnosticism (zero skill edits across stacks);
> the planned `saas_inventory` feature proves the engine actually ships real work. Pick the specific
> plan when we reach the proof step.

### Don't-lose-track checklist for any future session
- Read **§A** (this) → **§6** (rationale) → **§7** (guardrails that never move) before touching code.
- Source-of-truth files: **§1b** (Eduardo's commands) and **§9** (file map).
- Package shape / skill inventory & provenance: **§4**.
- Progress marker: _**DRAFTED** (2026-07-27): `ADAPTER_CONTRACT.md` + `skills/execute/SKILL.md` +
  both example adapters (Django + toy Go). **DRAFTED (2026-07-31): `review-gate`, `mode-select`,
  `extract`** — the pipeline now exists front-to-back, each new skill carrying the TD#85 lessons
  (§B7 maps every lesson to its artifact); `execute` upgraded with D7 + verification ownership;
  `ADAPTER_CONTRACT` upgraded (`verify` operational declarations, encoding constraint). **Next:**
  the two-stack agnosticism proof (run `execute` + `review-gate` against the toy adapter with zero
  skill edits), then the SECOND real-world test — the 2026-07-30 Notion bugs (password email /
  user recreation) through the FULL pipeline starting at `extract`. Then wire `adaptive-replanning`
  operationally._

---

## B. ⚠️ Lessons from the first real run (TD#85, 2026-07-28/29)

The first real-world test was TD#85 in `saas_inventory` (a human review → a business
decision → 5 vertical slices → 2 review rounds → 34 findings). It shipped, and the review
gate caught a real catastrophe. **But it did not run as a pipeline**, and understanding
why is more valuable than the feature itself.

### B1. `execute` was written and then never used

All the work was done by hand in the main loop: no batching, no parallel implementers, no
structured returns, and **model-per-role exercised only for the reviewers** — every
mechanical edit was performed by the orchestrator on the expensive model, serially. The
skill describing the machinery existed; the machinery never ran.

### B2. Why — the mode decision was made once and never revisited

`mode-select` was applied correctly *at the start*: slice 1 was a single file, and the
decision table rightly says "small one-off → just do it in the main loop." Then the work
grew to five slices, three reports, two new management commands, and two fix rounds — and
**nobody re-asked the question.** The mode gate behaved as a one-time entry decision when
it needed to be a recurring checkpoint.

> **Fix (D6):** `mode-select` gets a **re-evaluation trigger**, not just an entry gate.
> Re-ask when the work crosses a threshold — slice count, fix rounds, files touched, or a
> review returning more than a handful of findings. And `execute` names the smell
> directly: *if you are hand-rolling what this skill describes, that is the signal to
> switch modes.*

### B3. Durable artifacts are loop steps, not documentation

`solution/<date>/solutions.md` — the resume artifact the whole design leans on — was
**never written** for the entire arc, and only noticed when the user asked. That is not
carelessness so much as structure: in a real `execute` run the commit phase *contains* the
"append to the solutions log" step, so it cannot be skipped. Done by hand, it is a habit,
and habits get dropped.

> **Fix:** the artifacts are not paperwork, they are the parts of the loop that only get
> written **if the loop actually runs**. `execute`'s commit phase must own them explicitly.

### B4. What the run *did* validate

- **The review gate works, and is the strongest jewel.** An independent judgment-model
  reviewer returning machine-triagable findings → triage → fix → re-review caught a 💀
  that the author (me) had introduced, and then caught a *second* 💀 introduced **by the
  first fix**. Nothing else in the exercise would have found either.
- **Adversarial verification of one's own work is not optional.** Two of the most serious
  findings across both rounds were self-inflicted repairs — a DB constraint that made
  legitimate refunds impossible, and an "improvement" that broke an existing API flow.
- **The `roast`-style gate is real value.** The investigation before coding caught that
  the business decision was under-specified against the data model. Without it, the
  obvious implementation would have shipped wrong.
- **Preconditions matter** (already folded into `execute`): a named agent type that fails
  to resolve degrades silently into a weaker generic agent. **Corrected root cause
  (Eduardo, 2026-07-30):** the inspector *was* registered all along — the mdformat
  pre-commit hook had been destroying the YAML frontmatter of `.claude/agents/*.md` and
  `.claude/skills/*.md`, making the definitions unparseable, so dispatch silently
  degraded. Fixed by `c278e594` (the "unrelated" tooling commit riding the TD#85 branch —
  that is exactly why it is there); the registered agents resolve again. Refines the
  lesson: the check is "does the name resolve *now*", because breakage can come from
  tooling corrupting a definition, not only from a name that was never registered.

### B5. Honest scorecard for the package

| Jewel | Exercised? |
|---|---|
| Review gate + triage + fix loop | ✅ fully, and it paid for itself twice |
| Adaptive replanning (fix loop) | ✅ implicitly — two rounds, each replanned from findings |
| Investigation-before-dispatch | ✅ caught the under-specified decision |
| Parallel-edit / sequential-commit | ❌ never ran |
| Model-per-role for implementation | ❌ orchestrator did everything on the expensive model |
| Structured schema returns | ❌ not used |
| Durable resume artifacts | ❌ skipped until prompted |

**Conclusion (as of round 3):** the *thinking* half of the merged package proved itself; the
*execution* half remained unproven because it was never invoked.

### B6. Rounds 4–5 — what changed that conclusion

Rounds 4 and 5 finally exercised subagent dispatch, and the results are the most useful
evidence in the whole exercise.

**The review gate is the package's strongest jewel, by a wide margin.** Five rounds, and
*every* round found a real money-path defect. Scores: 6 → 5 → 6 → 4. Round 2's score went
*up* after two correct fixes, because their **interaction** was nobody's job. Nothing else
in the exercise would have caught any of it.

**Adversarial review of one's own repairs is not optional — it is the main event.** The
most serious findings across all five rounds were *self-inflicted fixes*:

| Round | The fix | What it broke |
|---|---|---|
| 1 | DB constraint stopping over-refund | Blocked *legitimate* refunds (rounding residue) |
| 2 | Backfill to repair history | Re-armed round 1's catastrophe across the whole estate |
| 3 | Per-line unit inference | Broke ordinary multi-line refunds via the main UI |
| 4 | PATCH guard keyed on money | Missed the units-without-money direction |

Same root every time, in the reviewer's words: **"reasons about the state it is designing
and not about the state it is creating."** That sentence belongs in the package.

**"Confident prose, code that doesn't deliver" is a distinct, recurring failure.** Twice a
long accurate comment described a technique the code did not perform: a missing
`atomic = False` (so a NOT VALID/VALIDATE split bought nothing), and `_credit_headroom`
documented in four places as preventing something it does not prevent. Documentation that
overstates a guarantee is *worse than none*, because reviewers and future maintainers stop
checking. Worth an explicit rule in `execute` or `review-gate`.

**Test honesty needs to be a named review dimension.** Repeatedly, tests passed by
construction: an assertion on the wrong key, a guard whose test never reached it, a
substring check that could not fail, coverage lost in a file split. The operative check —
now in `execute` — is *delete the change mentally and name which test goes red.*

**Dispatch worked, and the orchestrator must still verify.** The Opus implementer fixed
13 of 16 findings with **zero regressions** — better than the main loop had been managing.
But it **died mid-task on an API error**, leaving a 20-file diff on disk that had never
been linted, typed or tested by its author. It happened to be green (1785 passed), but that
was luck, not process.

> **Fix (D7):** a dispatched agent's completion is **not** evidence. `execute`'s commit
> phase must re-run the gates itself — lint, types, migration drift, tests — regardless of
> what the agent reported, and must treat a crashed agent's output as an unreviewed draft
> rather than as work in progress. Also: agents can die holding the field; the orchestrator
> needs to inventory the tree (`git status`) before deciding anything.

**Two operational hazards worth encoding in the adapter:**
- **Concurrent test runs destroy a shared test database.** Two suites collided here and
  wrecked it. Parallel agents must not each run the suite; the main loop owns verification.
- **A permission-classifier outage blocks every mutating tool** (Edit/Write/Agent/Bash)
  while leaving reads working. Not something a skill can fix, but worth knowing the symptom:
  the fix is to change permission mode, not to retry or switch worker model.

### B7. Lessons from rounds 6–11 and the closure — NOW ENCODED (2026-07-31)

The full harvest of the arc, each lesson folded into a package artifact. This table is the
proof the learning left the war story and entered the method:

| Lesson (evidence) | Where it now lives |
|---|---|
| **Execution-based review beats static reading.** Seven converging static rounds; a fresh reviewer who *ran* its suspicions found a 💀 on pass one. "Render the fragment three ways instead of arguing." | `review-gate` §Execute, don't read |
| **Verified at the layer below the one the user sees** — green serializer test, dead page; a model property no view could reach. Recurred twice. | `review-gate` (named blind spot) + `execute` review section |
| **Fix-interaction is nobody's job** — score rose after two correct fixes (r2); one fix made the other unreachable in a single commit (marker/bucket). | `review-gate` §The main event |
| **Claim vs. delivery** — "the two writers serialize" (one branch did); `_credit_headroom` "load-bearing" for a load it can't bear; a careful cp1252 comment guarding dead code. Prefer removal-by-deletion over protection-by-prose. | `review-gate` §The main event |
| **Checkpoint-commit the reviewed tree** so line refs stay valid and fixes land as readable diffs. | `review-gate` §Review the exact tree |
| **Scores are snapshots**; convergence of one method ≠ clean; rotate reviewer/method when scores converge. | `review-gate` §Convergence |
| **Structural fix over narrower predicate** — six rounds of added clauses lost to one round of deleting the ambiguity (rebind the object; delete the dead marker). | `review-gate` §Change its shape |
| **D7: an agent's completion is not evidence** — inventory the tree, re-run every gate in the main loop, treat a crashed agent's diff as an unreviewed draft. | `execute` §Commit |
| **Shared verify infrastructure** — parallel agents never run the full suite; main loop owns verification. | `execute` §Run a batch + `ADAPTER_CONTRACT` `verify` |
| **Flake families are named by fixture, not file** — else every new victim file reads as a new regression. Pin wall-clock-aligned test windows (throttle epochs) instead of racing them. | `ADAPTER_CONTRACT` `verify` |
| **The paraphrase trap** — a decision-owner answer that differs from the offered options is a *question, not an answer* ("despachada"; "pagada o crédito parcial"). Freeze the rule, ask ONE precise question naming the object. | `extract` §Don't launder ambiguity + `review-gate` §Convergence |
| **D6: the mode decision goes stale** — re-select on thresholds; hand-rolling `execute` by hand IS the signal. | `mode-select` §Rule 3 |
| **Operator output encoding** — one `←` crashed the report on cp1252 redirect, on exactly the rows it existed to flag. | `ADAPTER_CONTRACT` `constraints` example |
| **Fixtures can exercise a bug path without asserting it** — every refund fixture used a DRAFT invoice; nobody asked where the invoice ended up. Assert the end-state of every entity the operation touches. | `review-gate` §Test honesty |
| **Deferrals are said out loud** — every finding fixed or journaled by explicit decision; "no, filed as #N" is a valid resolution, silence is not. | `review-gate` §Triage |

**Skills drafted this round:** `review-gate`, `mode-select`, `extract` — the pipeline
front-to-back now exists on paper (extract → roast → to-plan → to-issues → mode-select →
execute → review-gate, with adaptive-replanning wired conceptually into execute's failure
path). Still owed: the two-stack agnosticism proof (run `execute` against the toy adapter
with zero skill edits), and wiring `adaptive-replanning` operationally.

---

## C. 🔧 LIVE WORK — TD#85 in `saas_inventory` (paused mid-flight)

**This is a *separate* codebase from the package.** It is the real-world test case, and it
is currently unfinished. Everything below is a pointer, not a duplicate — the authoritative
detail lives in that repo.

**Where:** `c:\Users\Eduardo\Documents\code\saas_inventory`, branch
`fix/td85-sales-by-seller-finalized-invoices` (off `dev`). **PR #224 → `dev`**
(https://github.com/educep/saas_inventory/pull/224), 22 commits, clean tree. **EIGHT**
review rounds: r1–r5 in-loop, r6/r7 by independent Opus reviewer agents (scores
6→5→6→4→3→1 MERGE), then a whole-PR review by Eduardo's own reviewer that **executed**
its findings and scored 6/10 — it found the path seven rounds never took: a partial
refund promoted a DRAFT invoice into `SALE_STATUSES`, making revenue APPEAR
(`_sync_invoice_credit_status`, no status guard). All eleven findings fixed in
`9a4956c2` (incl. TD#94's payload semantics and TD#97's slice-zero `refund_math.py`
extraction, forced by the 700-line ceiling). A **ninth** round (PR review r2, 3/10)
then caught that fix round's own miss: the page-visibility fix shipped as dead code —
the view renders a str-money dict, `"5.00" > 0` raises a TypeError django's smartif
silently swallows, and the green test had asserted on the serializer and a model
instance, never the page. All six r2 findings fixed in `a4f25ad6`; suite fully green
(1982/1982, no flakes). **Lessons for §B: (1) the review gate keeps paying — the
eighth look, fresh eyes + execution, beat seven rounds of static analysis; (2) the
recurring miss-shape is "verified at the layer below the one the user sees" — a page
feature is only tested by rendering the page through the real view with the real
data shape; (3) existing refund fixtures all used DRAFT invoices, so the whole suite
exercised the laundering path without ever asserting where the invoice ended up.**
A **tenth** round (PR r3, 2/10) verified everything and found only edges — a
non-cp1252 `←` crashing the operator report under Windows redirect, and the drift
gate paying a 23s TCP timeout dialing the remote DB per commit — all five findings
fixed in `bc79bf0c`, including moving the refund-everything hazard into the service
signature itself (`REFUND_ALL` sentinel default; explicit None/[] refused by the
contract). Scores across ten rounds: 6→5→6→4→3→1→6→3→2, plus an r4 verification pass
that found one dead-code cleanup (`dbcc3358`).

**CLOSED 2026-07-30:** PR #224 merged → `dev`, release PR #225 merged → `main`, and
the reviewer answered on Notion (reply posted in the main discussion). Her response
resolved TD#96 (sale is invoice-level, no dispatch gate — matches what shipped) and
opened **TD#100** (her "pagada o crédito parcial / pago indispensable" is NARROWER
than the released SALE_STATUSES — clarifying question posted, rule frozen until she
answers). **She also filed new bugs (2026-07-30, screenshots on the page): password
email to new users not sent, no recovery path, deleted user cannot be recreated
("ya está creado"). These are the designated NEXT TEST CASE for the skills package:
run the pipeline (extract → roast-if-needed → to-plan → to-issues → mode-select →
execute → review-gate) on them end-to-end, applying every §B lesson.**

**What it does:** the sales reports (by seller, by channel, by vendor) count only orders
with a *finalized* invoice (`Invoice.SALE_STATUSES`) and show revenue **net of partial
refunds**, via two new persisted fields — `Order.refunded_amount` and
`OrderItem.refunded_quantity` — which **must stay in sync**.

**Read these to resume, in order:**
1. `solution/2026-07-29/solutions.md` — the operational handoff: what shipped, what was
   deleted and why, deployment notes, what is still open.
2. `docs/specs/2026-07-28-sales-by-seller-net-revenue-design.md` — the design, incl. §4a
   (why the backfill was deleted) and §4b (why per-line inference was reverted).
3. `docs/dev/TECH_DEBT.md` entry TD#85.
4. `reviews/2026-07-30/review_td85.r5.md` — **the current blocker list.** Also r1–r4 in
   `reviews/2026-07-28/` and `reviews/2026-07-29/`.

**State (2026-07-30, after the r5 fix round):** all three r5 😱 **FIXED in `7d00b909`**,
plus the 😒/🔍 batch (R5-4, 7, 8, 9, 10, 11, 12, 13a, 16). The fixes, for the record:
- R5-1: the guard now trips on **either** field (`refunded_amount > 0` OR any line's
  `refunded_quantity > 0`); producer and refusal each pinned by a new test.
- R5-2: `update()` re-reads the Order under `select_for_update()` inside its atomic
  block before the destructive branch — same lock order as every other writer. Pinned by
  a stale-instance direct-`update()` test (which also closed R5-14).
- R5-3: docs corrected, not code, in **five** places (code docstring, spec §4b, TD#85,
  solutions.md, canary test docstring): `_credit_headroom` caps money; units are not
  derivable from money; the desync is refused at its producer.

**D7 vindicated en route:** the inherited "1785 green" was sequence luck — the re-run
gates found R5-7's assertion failing deterministically on a fresh DB. Also: two auth
tests flake under `-n auto` only (shared cache across xdist workers, documented in
solutions.md); a different one failed on each of two full runs.

**Verified on the committed tree:** full suite 1898 passed / 1 isolated-verified flake,
ruff clean, mypy clean, migration gate clean, es catalog decompile-verified. The
pre-commit **migration-drift gate** (`tools/check_migrations_current.py`) is in.

**Open, pending Eduardo:** R5-5 (`refund_order_async`: delete vs log-and-file), R5-6
(factor the 288-line `_refund_manual_order` — third ask, own round), R5-13b
(`responses=` on `@extend_schema`), R5-15 (cherry-pick `c278e594` to `dev`). Then a
**round-6 review** of the (small) r5-fix diff, then PR, then the Notion reply.

**Not done, deliberately:** the human reviewer on the Notion page has **not** been answered.
That is the last step, and the message has changed twice — it must say her figures will
barely move (DRAFT is transient by design) and that netting is exact going forward but
**not retroactive at all**.

**Accepted and closed:** `rumdl` was evaluated and dropped (rough issue tracker); the
unrelated tooling commit `c278e594` on this branch is accepted; deleting orders from prod
was considered and rejected (the code now defends itself instead).

---

## 1. The two source systems

### 1a. Grimoire (this repo) — portable *method*
Five skills, each a ~15-line `SKILL.md` with `name` + `description` frontmatter. Tool-agnostic,
description-triggered, portable. Located in `skills/<name>/SKILL.md`:

- **`roast`** — stress-test a design *before* code. One question per message, explore-before-ask,
  sparring-partner not rubber-stamp. Produces a spec (`docs/specs/YYYY-MM-DD-topic-design.md`).
- **`to-plan`** — synthesize an approved spec into a written plan. Choose **seams** (highest,
  fewest — one is ideal); user stories ("as an [actor] I want [feature] so that [benefit]");
  vertical slices; no re-interview. Produces `docs/plans/YYYY-MM-DD-topic-plan.md`.
- **`to-issues`** — break a plan into independently grabbable, tracer-bullet issues, one thin
  vertical slice each. Slice-zero groundwork ("make the change easy, then make the easy change");
  expand-then-contract for wide mechanical changes; block / is-blocked-by links; work-the-frontier.
- **`tdd`** — red/green/refactor, one behavior at a time, tested **through the public interface**,
  assert the whole value from an *independent* source, mock only at edges, never mock your own
  code, refactor only on green.
- **`adaptive-replanning`** — how an unattended build loop recovers from failure. **Fix loop**
  (inner: retry the same task with findings in hand, capped attempts) vs **replan loop** (outer:
  re-derive the *remaining* plan from the current state, budgeted). Failure = information. Stops
  on product decisions instead of guessing. **Theory only — no skill currently uses it.**

### 1b. Eduardo's `macro-plan-*` system — battle-tested *machinery*
Lived in the `saas_inventory` project (Django SaaS, "Cuadra / InventoryManager"). **RETIRED
2026-07-31** — the commands and `WORKFLOW_check.md` were deleted from that repo once the grimoire
pipeline was installed (its commit `842a5333`; git history keeps them — recover with
`git show 842a5333^:<path>`). Historical source files:

- `c:\Users\Eduardo\Documents\code\saas_inventory\.claude\commands\macro-plan-extract.md`
- `c:\Users\Eduardo\Documents\code\saas_inventory\.claude\commands\macro-plan-dispatch.md`
- `c:\Users\Eduardo\Documents\code\saas_inventory\.claude\commands\plan-workflow.md`
- `c:\Users\Eduardo\Documents\code\saas_inventory\WORKFLOW_check.md` (the meta / decision layer)
- `c:\Users\Eduardo\Documents\code\saas_inventory\docs\plans\2026-07-05\FIX_FAILING_TESTS_PROMPT.md`
  (a live specimen of a perfect self-contained handoff prompt)

Pipeline (three **sibling** commands — NOT a chain):

```
/macro-plan-extract → TODO.md → ( /plan-workflow  OR  /macro-plan-dispatch )
```

- **`macro-plan-extract`** — raw input (transcripts, client notes, bug reports, feature requests,
  code-review findings) → structured, prioritized, **investigated** `TODO.md`. Reads real source
  files (no guessing), dedups/groups, priority scale 🔴🟠🟡🟢, testable acceptance criteria,
  "don't invent work / flag needs-clarification." Output: `docs/plans/{YYYY-MM-DD}/TODO.md`.
- **`macro-plan-dispatch`** — `TODO.md` → `TODO_DISPATCHER.md`: chat-driven, human-in-the-loop,
  batch-ordered, dependency-aware execution with self-contained subagent prompts + review gates.
- **`plan-workflow`** — `TODO.md` → `WORKFLOW_PLAN.md` + `workflows/batch_*.workflow.js`: the
  workflow-tool-native sibling. Background execution, validated structured schema returns, resume.

**Eduardo already knows the two dispatch commands are ~80% duplicated** (dependency-graph analysis,
batching rules, subagent constraints, git model). That duplication is intentional to consolidate.

---

## 2. The full extraction (best of both)

### 2a. Best of Grimoire — keep as portable method

| Idea | Keepable essence |
|---|---|
| **roast** | Design interrogation before code. **Eduardo's system has NO equivalent** — it starts at task-extraction and assumes the "what" is decided. This is the biggest gap in Eduardo's pipeline. |
| **vertical slice** | Smallest *demoable end-to-end* piece as the unit of value. (Contrast with Eduardo's batch = unit of *parallelism* — see §2c tension.) |
| **to-plan seams** | Test at the highest, fewest seams; one is ideal. |
| **tdd** | Red/green/refactor, public interface, assert-whole-value-from-independent-source, mock only at edges, refactor only on green. Eduardo's system only says "add/extend tests" — no discipline. |
| **adaptive-replanning** | Fix-loop vs replan-loop. Eduardo's system is **plan-once**: on failure it retries the same Issue N or resumes from runId — it never re-derives the remaining plan. This is Eduardo's biggest capability gap. |
| **the packaging** | ~15 lines, tool-agnostic, description-triggered, portable. |

### 2b. Best of Eduardo's system — the machinery Grimoire lacks

| Idea | Keepable essence |
|---|---|
| **extract** | Messy raw input → investigated, prioritized tasks. Grimoire has no messy-reality front door. |
| **execution engine** | **Parallel agents EDIT; main loop COMMITS sequentially; one shared working tree; agents never run git.** The single most valuable operational insight. Grimoire has nothing like it. Rationale: parallel subagents share one working dir — a stray `git checkout` from one derails the others; parallel commits are racy. Only safe model = parallel edit, sequential main-loop commit. |
| **structured schema returns** | Each agent returns a validated JSON contract (issue, filesTouched, featureCommit, status, notes) — a malformed prose return can't corrupt the commit phase. |
| **Step-9 coverage check** | Every issue slotted in exactly ONE batch; union of batches == full TODO set; dependency order verified (prerequisite's phase ≤ dependent's); no issue exists only as a dangling "deferred-to Issue K" reference. Anti-silent-drop guarantee. Grimoire has nothing like it. |
| **review gate** | Dedicated Inspector persona + severity scale (💀 CATASTROPHE / 😱 DISGRACE / 😒 EYESORE / 🔍 NITPICK) + triage (💀/😱/😒 **always fixed**; 🔍 fixed only if it blocks later work, else journaled to `TECH_DEBT.md`) + `MAX_FIX_ROUNDS` cap (default 2). Review loop is **main-loop-owned** (a workflow can't pause, commit, or journal). |
| **model-per-role** ⭐ | Orchestrator = **Opus** (stays light). Implementers = **Sonnet** (bulk edits, ~5x cheaper). Reviewer / Fixer / domain-verify = **Opus** (judgment-critical). *Never one model for everything.* **This is Eduardo's single biggest hard-won lesson and it lives ONLY in `WORKFLOW_check.md` notes — it is NOT yet baked into any command file.** Must be first-class in the merge. |
| **mode-select decision table** | Workflow vs dispatch vs main-loop-checklist vs just-do-it-inline. Key reframe: **"workflows do NOT buy more parallelism"** (same shared-tree + serialization limits). They buy: (1) encoded pipeline verify stages, (2) structured schema returns, (3) background execution + resume, (4) determinism/reproducibility, (5) loop-until-dry adversarial sweeps. |
| **pipeline verify stage** | `pipeline(edit → verify)` so each edit is checked the moment it lands — verification is *encoded*, not something you must remember to invoke. Highest-value workflow pattern. Edit stage = cheap model, verify stage = judgment model / domain agent. |
| **durable resume** | Durable state = plan file + progress checkboxes + `solution/<date>/solutions.md` + `git log` — **not the tool**. A fresh session reads those and continues from the first unchecked box. Log concrete outputs (bucket names, ARNs, CNAMEs) so later sessions know live state. |
| **self-contained handoff** | One issue = one fresh context window. See `FIX_FAILING_TESTS_PROMPT.md`: ground rules, exact setup commands, categorized problem analysis, fix-vs-refactor decision, "green-by-deletion is failure" guardrails, log-it, PR. |
| **guardrails that never move** | (1) Git + shared-file writes stay main-loop-owned; agents surface content in their return, the main loop applies it. (2) The review & remediation loop lives in the main loop, never inside a workflow. |

### 2c. Known tension to resolve during design
Grimoire's **vertical slice** (organize by user-visible value, cuts through all layers) directly
conflicts with Eduardo's **file-disjoint batch** (organize by parallelism, must NOT share files).
A true vertical slice touches many layers/files → a poor unit for file-disjoint parallel agents.
The merge must make this trade **explicit**: value-sliced planning, then a distinct
parallelism-aware batching step for execution. Do not silently pick one.

---

## 3. The merge principle (the "how")

The reason Eduardo's commands can't already be a Grimoire-style package is that they **fuse method
with project config**. Grimoire is portable *because* it carries zero specifics.

> **SKILL = portable method. ADAPTER = the project/stack specifics.**
> **No skill's *operative behavior* may depend on a specific tool, language, framework, or command.**
> The skill states the *role*; the adapter supplies the *concrete*. If a skill would have to run
> "Django ORM" or "`make format`" as its actual instruction, that is the tell it is leaking — it must
> instead reference an **adapter capability**.

**Refinement (Eduardo, 2026-07-27) — example vs. dependency.** Implicit references to common stacks
(git, python, react, js, terraform, …) as *illustrative examples* are allowed and encouraged for
readability — "the `verify` command (e.g. `pytest` / `npm test` / `go test`)." The invariant is
narrower than "never name a tool": **a skill's control flow must not *require* a given stack** — the
command still comes from the adapter. Examples illustrate; the adapter dictates. (`git` itself is kept
concrete as a near-universal assumption; fully abstracting VCS is over-engineering.) The `docs-lookup`
capability keeps **Context7** as its reference default (resolve-library-id → query-docs before
non-trivial API use).

Examples of the seam:

| Skill says (agnostic) | Adapter supplies (per project) |
|---|---|
| "leave the tree formatted and checked" | `make format` / `prettier -w` / `gofmt` / `cargo fmt` |
| "run the project's test suite" | `pytest` / `go test ./...` / `npm test` |
| "respect the project's commit-gate hook" | the `.po` i18n hook / a lint gate / nothing |
| "verify with a domain reviewer" | `sri-expert` / `inspector` / a generic reviewer |
| "look up current API docs before coding" | Context7 / devdocs / none |
| "cheap model for bulk, judgment model for review" | actual model IDs (Sonnet / Opus / other) |

Stack-agnostic goal (per Eduardo, 2026-07-27): must cover **any language/framework**, and the
open question (see §6) is whether it must also cover **non-code work** (data pipelines, infra-only,
docs). That decision sets how abstract `execute` and `review-gate` need to be.

---

## 4. Proposed merged package ("Grimoire++")

### 4a. Pipeline shape

```
INPUT
 ├─ ambiguous idea ─► roast ──────► spec                     [grimoire, keep]
 └─ settled backlog ► extract ────► tasks                    [eduardo, generalize] NEW to grimoire
                          │
                     to-plan (seams, vertical slices)        [grimoire, keep]
                          │
                     to-issues + coverage + dependency graph [grimoire + eduardo Step 9] UPGRADE
                          │
                     mode-select  ◄── decision table         [eduardo WORKFLOW_check] NEW
                          │
                     execute  ◄── parallel-edit / seq-commit / schema /
                          │        model-per-role / pipeline-verify   [eduardo engine] NEW (the big one)
                     tdd discipline INSIDE each agent         [grimoire, keep]
                          │
                     review-gate  ◄── inspector + triage + TECH_DEBT  [eduardo] NEW
                          │
                     adaptive-replanning WRAPS the loop       [grimoire theory → finally operational]
                          │
                     durable resume (plan + checkboxes + solutions + git)  [eduardo]
                          ▲
              project-adapter  ── supplies ALL specifics to every skill above   NEW (portability seam)
```

### 4b. Skill inventory (provenance)

| Skill | Source | Change |
|---|---|---|
| `roast` | Grimoire | keep ~as-is |
| `tdd` | Grimoire | keep ~as-is |
| `adaptive-replanning` | Grimoire | keep as theory + **wire into `execute`** so it's finally operational |
| `to-plan` | Grimoire | ✅ UPGRADED 2026-07-31 — explicit slice-vs-batch hand-off: plan in value slices, never pre-batch; `execute` derives parallelism from `module-topology` (D1) |
| `to-issues` | Grimoire + Eduardo | ✅ UPGRADED 2026-07-31 — Step-9 coverage check (exactly-one-issue, union==plan, no dangling deferred refs, dependency order) + the D1 hand-off note |
| `extract` | Eduardo | ✅ DRAFTED 2026-07-31 — generalized, + the paraphrase-trap lesson (§B7) |
| `mode-select` | Eduardo | ✅ DRAFTED 2026-07-31 — decision table + D6 re-evaluation rule |
| `execute` | Eduardo | ✅ DRAFTED 2026-07-27, upgraded 07-31 (D7, verification ownership). Absorbs `dispatch` + `plan-workflow` |
| `review-gate` | Eduardo | ✅ DRAFTED 2026-07-31 — the proven crown jewel: severity triage + execute-don't-read + fix-interaction + claim-vs-delivery + test honesty + convergence/rotation (§B7) |
| `project-adapter` | NEW | ✅ `ADAPTER_CONTRACT.md` drafted + upgraded; two example adapters |

Net: 3 Grimoire skills survive as-is, 2 upgraded, 4 new from Eduardo, + the adapter.
Two biggest wins: `execute` gives Grimoire the back-end it totally lacks; wiring
`adaptive-replanning` into `execute` finally makes the replan loop operational (Grimoire had the
theory but never used it; Eduardo had the machinery but never replanned).

---

## 5. The project-adapter contract (draft — to be finalized)

Each target repo carries ONE adapter (form TBD — see §6). It declares the capabilities skills
reference by name. Draft capability set:

- **format** — command to leave the tree formatted/checked (`make format`, `prettier -w`, …).
- **test** — command(s) to run the suite; how to run a subset; any required setup (e.g. "start
  the test DB container").
- **commit-gate** — pre-commit hooks that can fail/modify a commit (e.g. the `.po`
  `makemessages-check`); how to satisfy them.
- **git-conventions** — commit message format (`type(scope): summary`), branch naming, base
  branch (`dev`/`main`), footer rules (e.g. "no Co-Authored-By").
- **models** — model IDs per role: orchestrator, implementer (cheap), reviewer/fixer/verify
  (judgment). (model-per-role, §2b ⭐.)
- **reviewer** — the review persona/subagent-type + severity scale + triage rules + where reports
  and `TECH_DEBT` live.
- **docs-lookup** — how to fetch current API docs (Context7 / devdocs / none).
- **constraints** — project invariants (e.g. "≤700 lines/file", "tenant-scope every query").
- **shared-files** — the files only the main loop may write (`solutions.md`, `TECH_DEBT.md`,
  `TODO.md`).
- **artifact-paths** — where specs/plans/issues/reviews/solutions live.

---

## 6. Decisions (ALL RESOLVED 2026-07-27 — see §A for the summary table)

1. **Agnosticism reach** — **RESOLVED 2026-07-27.** The axis is NOT "code vs infra" but
   **authoring vs applying**:
   - **Authoring** (write/refactor files, plan, reason — app code, data pipelines, docs, AND
     infra-as-code like Terraform/CloudFormation) → handled by the parallel `execute` engine.
     Infra authoring is a *star* use case: `.tf` modules are usually file-disjoint (parallelize
     well) and have a real verify stage (`terraform validate`/`plan`, `tflint`, `checkov`) — a
     perfect `pipeline(edit → verify)`.
   - **Applying** (mutates live/external state irreversibly — `terraform apply`, `aws rds delete`,
     prod DB migrations, cutting a release, DNS flips) → ALWAYS routed by `mode-select` to a
     gated, sequential, human-confirmed **checklist mode** (never a parallel/background agent).
     Still first-class in the package, just a different mode; durable resume logs real outputs
     (ARNs, bucket names, EB CNAMEs) to `solutions.md`.
   - Crucially this axis gates dangerous **code** deploys too (a prod migration is as irreversible
     as `terraform apply`) — which a naive "infra=gated, code=engine" split would wave through.
   - Adapter consequences: `verify`/`test` is **optional & pluggable** (pytest / `terraform plan` /
     none → degrades to review-only for docs); a declared-but-**gated** `apply`/`deploy` capability
     the parallel engine may NEVER invoke; a "never echo secrets/`tfvars`" guardrail.
2. **Adapter form** — **RESOLVED 2026-07-27.** Hybrid, docs-first. Principle:
   **"Docs are the evidence, the adapter is the law — and a missing README is a slice-zero we
   offer, not a gate we impose."** Onboarding a repo:
   1. Read **README + docs first** (architecture, conventions, deploy story, topology) — primary
      source of *understanding*; manifests (`pyproject`/`package.json`/`*.tf`) are secondary, only
      for mechanical commands. (This is Grimoire's own "explore before asking" house style, which
      `roast` already runs on.)
   2. **No/thin README → OFFER to prepare one** (a textbook slice-zero: sharpens every downstream
      skill + leaves a durable artifact). But **offer, don't block** — a docs-less legacy repo must
      still degrade gracefully to manifest-sniffing + code-reading and let work proceed today.
   3. **Draft the adapter FROM that evidence** (docs + manifests).
   4. **Human confirms the un-sniffable, high-stakes fields**: model-per-role, the **gated-apply
      list** (safety-critical — a README rarely says "this script deletes prod"), reviewer persona,
      repo topology (single/multi), module topology (feature/layer). Docs *inform* these but never
      *replace* explicit confirmation.
   5. **Commit the adapter = runtime law** (deterministic; detection only ever bootstraps, never
      drives execution — otherwise resume drifts).
   Form: **markdown, one heading per capability**, at `.claude/project-adapter.md`, committed so it
   travels and shows in diffs. (Markdown over YAML because the consumer is the model and policy
   carries prose nuance YAML can't; YAML is the fallback if strict machine-parseability is wanted.)
3. **Scope** — **RESOLVED 2026-07-27. PUBLISH.** Build to publishable quality (which is also
   what enforces stack-agnosticism — writing for a stranger's repo makes every leak obvious), and
   the intent is to ship it to the community. Consequences: name/structure for upstreaming from day
   one; keep it usable privately across Eduardo's own repos in the meantime; open a light
   coordination with the upstream author (`laurentlouk`) once the shape is proven. The
   "would this survive publication?" bar is now a real requirement, not just a discipline.
4. **First build target** — **RESOLVED 2026-07-27: `execute` first** (option a). Fully agnostic,
   adapter **co-designed** (it's the most demanding consumer, so it forces the adapter contract to be
   real and complete instead of a theoretical schema a skeleton-first path would later invalidate →
   rework across 8 skills). **Proven on two stacks** (`saas_inventory` Django + one non-Django repo)
   because the publish decision (D4) means agnosticism must be *demonstrated*, not asserted. It stands
   alone — a hand-crafted 2–3 issue mini-plan is enough input; we don't need `extract`/`to-plan`/
   `to-issues` first. **Step 2:** wire `adaptive-replanning` into `execute` (the jewel-4 synthesis).
   Rejected alternative: skeleton-first (all 9 stubs) — gives the whole shape but yields a theoretical
   adapter `execute` would reshape; better to let the hardest consumer earn the contract.
5. **Vertical-slice vs file-disjoint-batch** (§2c) — **RESOLVED 2026-07-27.** Two explicit
   steps, never collapsed: *plan* in vertical slices (value-first, demoable), then a *batcher*
   derives execution units. The real driver of parallelism is **file-disjointness**, not
   "horizontal vs vertical" — horizontal decomposition doesn't automatically parallelize (it can
   pile every feature onto the same `models.py`). The true switch is **module topology**:
   - Same repo, **feature/module-organized** (feature folders, bounded contexts): vertical slices
     are already file-disjoint → keep them whole, parallelize directly. Demoable AND parallel.
   - Same repo, **layer-organized** (classic MVC, shared `models.py`/`views_*.py`/one `.po`):
     vertical slices collide → break into file-disjoint (more horizontal) groups to recover
     parallelism; recombine at the PR boundary so the *phase* stays demoable even when a *batch*
     isn't. **This is `saas_inventory`'s situation** — the dispatch machinery fighting the `.po`
     hook and shared `views_*.py` is the symptom of layer-organized code forcing horizontal batching.
   - **Multi-repo** (the coder): each repo is a bounded scope; parallelism lives within a repo; the
     cross-repo feature is the vertical, per-repo work is the sub-slice.
   The **adapter declares two things**: repo topology (single vs multi) AND module topology
   (feature- vs layer-organized). The batcher uses module topology to decide whether to keep slices
   whole or trade down to horizontal groups. Degenerate default: a single-layer repo (the coder's
   case) is slice-primary-sequential for free; a full-stack single repo gets parallelism.

---

## 7. Guardrails that must survive the merge (do not negotiate these away)

1. **Git + shared-file writes stay main-loop-owned.** Agents never run git; never write
   `solutions.md` / `TECH_DEBT.md` / `TODO.md`. They surface content in their structured return;
   the main loop applies it. (Parallel writes corrupt shared files; a stray `git checkout` from
   one agent derails the others in the shared tree.)
2. **The review & remediation loop lives in the main loop, never inside a workflow.** A workflow
   can't pause for the human, commit, or journal to `TECH_DEBT.md`.
3. **model-per-role, always.** Cheap model for mechanical bulk; judgment model only where the
   correctness of the judgment matters (review/fix/domain-verify).
4. **Step-9 coverage check before any plan ships.** No issue may exist only as a dependency
   reference; union of batches == full issue set; dependency order verified.
5. **Structured schema returns** for every dispatched agent — no free-text prose parsing in the
   commit phase.
6. **Durable, tool-independent resume** — state lives in plan file + checkboxes + solutions log +
   git, so a fresh session continues from the first unchecked box.

---

## 8. How to continue (next session)

1. Read this file end-to-end.
2. Re-read the five source files listed in §1b for verbatim detail (they hold specifics this
   summary compresses).
3. Resolve the §6 open questions with Eduardo (short conversation — he dislikes multiple-choice
   grids; ask in prose, one thread at a time, sparring-partner style à la `roast`).
4. Pick the first build target (§6.4) and author it under `skills/<name>/SKILL.md`, obeying the
   §3 merge principle (no stack names leak) and §7 guardrails.
5. Prove agnosticism with at least one non-Django adapter before scaling to all skills.

---

## 9. Source-of-truth file map

| Path | Role |
|---|---|
| `skills/roast/SKILL.md` … `skills/adaptive-replanning/SKILL.md` (this repo) | Grimoire's 5 skills |
| `saas_inventory/.claude/commands/macro-plan-extract.md` | Eduardo's task-extraction front door |
| `saas_inventory/.claude/commands/macro-plan-dispatch.md` | Chat-driven execution plan |
| `saas_inventory/.claude/commands/plan-workflow.md` | Workflow-native execution plan |
| `saas_inventory/WORKFLOW_check.md` | Meta layer: mode-select, model-per-role, guardrails, resume |
| `saas_inventory/docs/plans/2026-07-05/FIX_FAILING_TESTS_PROMPT.md` | Specimen self-contained handoff prompt |
| `grimoire/MERGE_DESIGN.md` (this file) | The synthesis + continuation handoff |

_End of handoff. Nothing built yet; §6 is where work resumes._
