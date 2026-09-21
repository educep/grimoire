# Project adapter — contract

> **What this is.** The specification for a repo's `.claude/project-adapter.md`. Grimoire skills are
> **stack-agnostic**: their operative behavior never depends on a language, tool, or command.
> Everything project-specific lives here, in the adapter, and skills reference it **by capability
> name** (e.g. "run the project's `verify` command"). One adapter per repo, committed, so it travels
> and shows up in diffs. (Illustrative examples of common stacks are fine in skills and here; what's
> forbidden is a skill's control flow *requiring* a given stack. Examples illustrate; the adapter
> dictates.)
>
> **Governing principle (design decision D3):** *"Docs are the evidence, the adapter is the law —
> a missing README is a slice-zero we offer, not a gate we impose."* The adapter is **drafted from**
> the README + docs + manifests, but the **high-stakes fields are human-confirmed**, and the committed
> file — not runtime detection — is the source of truth every session obeys.

---

## How an adapter gets created

1. Read the repo's **README + docs first** (understanding), then manifests (`pyproject.toml`,
   `package.json`, `go.mod`, `*.tf`, `Makefile`, CI config) for the mechanical commands.
2. If there's **no/thin README**, *offer* to write one (a slice-zero that sharpens every skill) —
   but **don't block**: degrade to manifest-sniffing + reading the code and proceed.
3. **Draft** this file from that evidence.
4. **Human confirms the un-sniffable, high-stakes fields** — marked 🔒 below. These cannot be
   detected and getting them wrong is expensive or dangerous: `model-per-role`, the `apply` gated
   list, `reviewer`, and both topologies.
5. **Commit** it. From now on it is law; detection never overrides it.

### The install interview

Some capabilities name a thing the project may not have yet. **A consumer that finds one missing
STOPS AND ASKS; it never guesses** — so the questions are asked once, at install, rather than by
every command that trips over the gap. For each, the question and the proposal to make when the
answer is "none":

| capability | the question | when the answer is "none" |
|---|---|---|
| `integration-branch` | Which branch does finished work merge into, and which branch do phases cut from? | **Propose creating one**, and say why: feature → integration → release keeps an unreviewed phase off the branch that deploys. A single-branch project may decline — record the decline, because every stacked-PR, retarget and release rule downstream has then collapsed to one branch and consumers must say so. |
| `release-branch` | Which branch deploys? | Record `none`. The release-PR step is then skipped, and skipped out loud. |
| `backlog` | Where is the durable list of open work, and where do closed items go? | **Offer to create one, and ask where it lives** — the recommended template is in the capability below. Do not invent a path silently; a backlog nobody opens is the same as no backlog. |
| `records` | Where do the four record surfaces live — backlog, decision log, phase-keyed artifacts, practice doc? | Offer to create a minimal version of each missing one. An orchestrator without record surfaces produces phases that evaporate. |
| `ceremony-tiers` | Does every phase run the same review-and-verification ceremony, or is it chosen per phase by size and risk? | Record `one tier`, and say which. Consumers then run that ceremony for every phase and must say the choice collapsed rather than silently skipping the selection step. |
| `orchestration-tool` | Is there a harness tool that runs scripted multi-agent workflows, and how is it invoked? | Record `none`. Plain agent dispatch is the path — it is the default anyway, so nothing is lost but the accelerator. |
| `verify` | …and which checks run at push/merge that a commit-time gate does not catch? | Record `none`, and say that opening a PR needs no hand-run check. |
| `code-graph`, `docs-lookup` | Is the tool installed / reachable? | Record `none`. Consumers answer the question the expensive way and **say** they did. |

The interview is a conversation, not a form: ask only what the repo did not already answer, and
confirm the 🔒 fields even when a draft filled them in.

---

## Capabilities

Each heading is a capability a skill or command may reference. `verify`, `apply`, `docs-lookup`,
`constraints`, `refactoring`, `release-branch`, `ceremony-tiers`, `orchestration-tool`,
`code-graph`, `config-dirs` and `shell-conventions` may be **absent** — a consumer that needs an
absent capability degrades gracefully (e.g. no `verify` → review-only) and **states what it
skipped**. Everything else is required, and a consumer that finds it missing stops and asks rather
than guessing.

### `overview`

One paragraph: what the project is, primary language(s), and where the docs live. Drafted from the
README.

### `repo-topology` 🔒

`single` or `multi`. If `multi`, list each repo and its role (e.g. `backend`, `frontend`, `infra`).
Drives whether a vertical slice is one-repo or spans repos (decision D1).

### `module-topology` 🔒

`feature-organized` (feature folders / bounded contexts — vertical slices are naturally
file-disjoint) or `layer-organized` (shared `models`/`views`/one i18n catalog — vertical slices
collide). **This is the switch the batcher uses** (D1): feature → keep slices whole and parallelize;
layer → break into file-disjoint groups, recombine at the PR boundary.

### `format`

The command that leaves the working tree formatted and statically clean. Every implementer ends in
this state before returning. May be `none`.

**Declare what it does NOT cover, and how to invoke it without the project's task runner.** Two
mechanical facts, each of which has let a real defect through: a lint command scoped to the source
directories does not cover the **test tree**, so a static error introduced in a test module passes
every gate until the linter is pointed there explicitly; and a **dead-code detector finds what a
linter does not** — stranded returns left behind by collapsing call sites onto a shared helper
passed the linter and were refused at full confidence by the dead-code hook. Also give the direct
form of each command: a task runner is not always on the path of the machine an agent is running on,
and its "command not found" reads like a broken toolchain rather than a missing binary.

### `verify` *(optional)*

How correctness is checked: test command(s), and/or static checks (`terraform plan`, linters,
type-checkers). Include **how to run a subset** and **any required setup** (e.g. "start the test DB
container first"). Absent → skills that would verify fall back to review-only. Authoring
infra-as-code points this at `terraform validate`/`plan` (decision D2).

Two operational declarations that save real incidents:

- **State whether verification shares infrastructure** (one test database, one live service). If it
  does, **only the main loop runs the full verification** — two concurrent suites from parallel
  agents will destroy the shared state. Agents verify subsets at most.
- **Name any known flaky-test families by the fixture or resource that defines them**, not by file
  (e.g. "anything consuming the browser/live-server fixtures times out under full parallel load;
  green in isolation"). Named by file, every new victim file gets misdiagnosed as a fresh
  regression; named by fixture, one line of doc absorbs the whole family. Also note environmental
  test hazards worth pinning (e.g. throttle windows aligned to the wall clock — pin the clock in
  those tests rather than racing it).

Three more that are cheap to write down once and expensive to re-derive every phase:

- **If the full run exceeds the harness's ceiling, declare the CHUNKS verbatim and the partition
  proof.** Name each chunk's command, and the check that the chunks' collected counts sum to the
  whole suite's collected count — that sum, not repetition, is what guarantees nothing escaped.
  Green chunks are **banked**: never re-run one "to make sure", and never kill and restart a chunk
  that nears the ceiling (a restart pays for the whole chunk again and forfeits the arithmetic).
  Declaring the protocol without its commands is what makes every phase re-derive the boundaries;
  the counts themselves drift and are an example, not a target.
- **State the runner's fail-fast default, and that a BLAST RADIUS is measured with it off.** A
  population cannot be swept from a truncated list: under a low fail-fast cap, a partial run once
  reported eleven failures where the whole suite held fourteen, and the sweep would have shipped
  with three survivors. A change whose reach is unknown runs the suite once uncapped, sweeps the
  complete list, then runs it again as the proof. The cap is for the edit-run loop, never for
  measurement.
- **Say how a long run is launched and watched**: detached with progress printed, then waited on
  inside a single foreground call. A run backgrounded inside a turn dies with the turn, and a run
  piped through a truncating filter writes nothing until it ends — both read as a hung suite.

**Where a lighter review tier skips the full run, the verification set it DOES run is the whole
proof — so derive it from the doors the diff touches, and re-derive it after every fix round.** One
round inherited its set from the plan; a fix round then touched a new entry point, the set was not
re-derived, and nine pre-existing tests in three directories the set did not cover went red on the
integration branch's doorstep. List each production symbol the diff changed, search the test tree for
its callers, and add every directory that hits one; a fix that nothing pins gets its pin in the same
round.

**Say what a DELETION owes beyond the tests of the files it touched.** Removing an artifact — a
module, a page, a script, an asset — silently invalidates everything KEYED on it elsewhere: census
rows that enumerate it, frozen ratchet or baseline entries that list it, reachability guards that
assert it is reached, and companion assets loaded only by it. None of those live among the deleting
work's own files, so a per-item verification is blind to them by construction and a review scoped to
the diff sees a clean removal. Declare that a batch containing a deletion runs the full set once
before its PR opens, and name the keyed artifacts this project actually keeps, so the sweep has a
list instead of an instinct. *(Measured: one dead page's removal broke two frozen ratchet rows and
stranded a script nothing loaded any more; the whole-suite run was the only thing that caught
either.)*

**Name the checks that run at PUSH or MERGE rather than at commit, and that the executor therefore
runs BY HAND before opening a PR.** A gate that fires once per branch is the one nobody has seen
fail during the work, and it is discovered at the worst moment — by whoever pushes, with the phase
already closed. Some of these also *mutate* the tree when they run (a regenerated catalog, lockfile
or schema snapshot), which makes them main-loop-only and makes "run it by hand, then inspect the
diff" part of the phase, not an afterthought. List each one and say which mutate. Absent → say the
project has none, so nobody goes looking.

### `apply` / `deploy` — GATED 🔒

The commands that **mutate live or external state irreversibly** — deploys, `terraform apply`,
resource deletes, prod DB migrations, releases, DNS changes. **List each one explicitly with what it
does and its danger.** The parallel engine may **NEVER** invoke anything here; `mode-select` routes
these to a **human-confirmed, sequential checklist** (decision D2). A README rarely says "this deletes
prod" — that's why this list is human-confirmed, not detected.

### `git-conventions`

Commit message format (e.g. `type(scope): summary`), branch naming, base branch, footer rules, and
the invariant that **the main loop owns all git** — implementer agents never run git.

- **Every commit message goes through a FILE, never an inline argument.** A shell interprets what it
  finds in an inline message: a backtick runs a command substitution and silently eats the clause
  around it, and a quote-dense message can break the parse outright. Write the message, then commit
  from it.
- **A DELETION batch commits by IMPORTABILITY, not one-commit-per-issue.** The one-commit-per-issue
  rule assumes every issue leaves a tree that loads. A batch that removes a module does not: the
  commit removing the module and the commits removing its references are only *jointly* valid, and
  commit-time hooks run against the staged tree, so the intermediate states fail the gate rather
  than the review. Group every reference-removing issue for a deleted module into ONE commit and say
  in the message which issues it carries, so the plan's issue list still reconciles. This is a
  narrowing for one shape, not a licence to batch unrelated issues.

### `integration-branch`

**The branch finished work merges into, and the branch a phase cuts from.** Required: every review
baseline (`<integration-branch>...HEAD`), every branch-cut rule, every PR target and every "is the
base in sync with its remote" precondition in the pipeline is expressed against it. A consumer that
has to guess takes whatever happens to be checked out, and a shared checkout legitimately ends a run
on someone else's branch.

Declare: its name; whether a later phase cuts from it or from the previous phase's still-unmerged
branch; and that **merging a PR is always the human's call**, never a command's.

**A project with a SINGLE branch is a valid answer, and it is not silence.** Say so explicitly,
because then every stacked-PR, retarget and release rule downstream has **collapsed to one branch**,
and a consumer must say it collapsed rather than quietly skipping the step — a skipped step and an
inapplicable step read identically in a report, and only one of them is fine. Work still happens on
a branch and still opens a PR; there is simply no second target to retarget to.

### `release-branch` *(optional — a project may have none)*

The branch that deploys. Where it exists, the pipeline's last act is a release PR from the
integration branch to it, and the rule that no phase branch ever targets it directly.

Absent → **the release-PR step is skipped and the skip is stated**. Note why this one is optional:
not because it needs a tool installed, but because the *thing itself* may not exist. Consumers need
the same if-absent branch either way, which is why the contract's test (rule 4) is about what a
consumer must carry, not about what makes a project unusual.

### `model-per-role` 🔒

Model IDs by role — the crown-jewel policy (never one model for everything):

- `orchestrator` — the main loop (judgment; stays light).
- `implementer` — bulk file edits (cheap).
- `reviewer` / `fixer` / `domain-verify` — judgment-critical (a wrong call is costly).
- `derivation` — **read-only: the judgment model, dispatched with NO write tools.** For a census or
  reachability question whose answer decides what the phase does. *Measured: this role produced one
  round's most valuable output — it found that most of a table's rows were already closed by a
  mechanism the plan had never looked for, and that the plan's proposed remedy was inert — and the
  executor's own reading was that it did so **because** it could not edit. With no fix to write, the
  cheapest path is to measure honestly rather than to justify a diff.* Give it the question and no
  write tools.

### `reviewer` 🔒

The review persona / agent-type, its severity scale, the triage rule (which severities are always
fixed vs. journaled), and where reports + the tech-debt journal live. The review loop is
**main-loop-owned**, never inside a background run.

**Declare whether the persona is a registered agent type or an inlined persona file**, and state the
fallback. A named agent type that fails to resolve degrades silently into a weaker generic review —
whether because it was never registered or because its definition file was corrupted (e.g. a
formatter destroying its frontmatter, which parses as "no such agent"). So this must be *checked
before dispatch*, not discovered at launch (see `execute`'s preconditions).

**Declare the project's CHECKLIST here.** The `review` skill owns the review *method* — scoping,
reachability rating, plant-over-inspection, output shape, triage — and deliberately does **not** own
what to hunt for, because a checklist is stack-specific and a Django one is worthless in a Rust
project. List the categories a reviewer must apply and the severity each defect class earns.

**Every caller of the reviewer must declare WHERE ITS REPORT GOES — even when the answer is
"nowhere".** There are normally three, and they differ:

| caller | writes the report? |
|---|---|
| the dispatched reviewer **agent** | **no** — it *returns* it; the caller owns the artifact |
| an in-session **slash command** | yes, if given a path; otherwise prints |
| an **orchestrated review stage** | the **orchestrator** writes it, from the returned findings |

*Measured in the host project 2026-08-29: the agent definition said nothing about files while the
workflow command told the orchestrator to save what the agent returned — under a note claiming the
two were "kept in sync". An executor dispatched the agent and then polled the reviews directory
**191 times** for a file it was itself responsible for writing, with no terminating condition.*
**A caller that is silent about persistence is a defect in that caller**, and the silence is
invisible until it costs a runaway loop.

**Say that EVERY review round's report is a FILE, and name who writes it.** One per round — the
relay's and any closure review's included — written before the round is reported done, at the
`artifact-paths` location. Since the dispatched reviewer returns and writes nothing, **whoever
dispatched it owns the write**; inside a phase that is the executor, not the orchestrator. *(Added
after this failed on two consecutive phases: one round's closure findings existed nowhere in the
tree, and the next phase lost both of its review rounds — twenty-six findings — recoverable only
because the reviewer agents happened to still be resumable. The cause was this section: it named the
relay's report as a file and said nothing about the rounds', and "journal-only" was read as
permission not to file at all.)*

**If the project varies the review ceremony, declare the STOPPING RULE by measurement, not by
schedule.** The shape that works: full ceremony while phases still yield serious findings; after N
consecutive phases with zero high-severity findings across all rounds and the relay, the default
tier drops to light; any serious finding at the light tier resets the counter and the next phase runs
full. The counter's source is the review reports themselves, never a restated number.

**Declare which findings RESET that counter, with TWO tests that must both hold.** *Subject* — the
finding's **own** file, not the file it talks about: a serious finding in a test that proves a
product defect is a product finding, while one against the test tree, the tooling or a document is
journaled and dispositioned like any other and does **not** reset. *Cut point* — **would the finding
exist against the tree the phase branched from?** If it would, the phase reported a defect it
inherited: journal it, file it with its provenance, and do not reset, **whatever file its wording
lives in**. In-diff is the wrong axis, because a comment a phase writes *about* an older defect puts
the finding inside the diff while the defect stays older than the branch. A phase is charged for the
code it wrote, not for the honesty of looking around it — charge it for the latter and runs learn to
stop looking. *(Both halves were reached by falsifying an earlier wording of this same rule, twice,
inside one review loop.)*

**And say whose evidence the counter is counting.** A clean phase at a lighter tier is one review
pass; a clean phase at the full tier is several plus a relay. A threshold calibrated on the second
does not automatically transfer to the first, so a project running both tiers records that as an
open question against its own threshold rather than assuming it holds.

**If the project extends the relay with a bounded CLOSURE ROUND, declare it here** — the `review-gate`
skill defers to this capability on that point. Declare what may be fixed in it (low-severity, cheap,
in files the phase already opened), that its own scoped review is verification-only and journal-only,
and that **the closure review suspends the class-sweep obligation**, because a terminal gate that a
sweep can reopen is not terminal.

### `ceremony-tiers` *(optional — a project may run one ceremony for everything)*

Whether the ceremony a phase runs is **chosen per phase, at planning time, by the size and risk of
the work** — and by what. A project with a single ceremony declares that explicitly, because a
consumer must be able to say the choice *collapsed* rather than quietly skipping the step. Optional
here for `release-branch`'s reason, not rule 4's: the second tier may simply not exist.

Where more than one tier exists, declare each of these:

- **The tiers, and the shape of each.** What the full tier runs; what the light one **drops** and
  what it **keeps**. The split that works: light drops the *ceremony* — the relay, the closure
  round, the closure review, the debrief, the solutions log — and keeps the *work*: the
  implementers, ONE review pass, ONE fix round with the gates re-run after it, and the executor's
  own full verification run, once, at its close. Add the one exception worth its cost: **a second
  review pass over the fix diff, mandatory whenever the first pass returned a finding at the top
  severities and forbidden otherwise** — at a cap of one round the fix is otherwise the only
  unreviewed change in the phase, which is the state the relay exists to prevent at the full tier.
  **Light drops ceremony, never the suite**: say that in the declaration, because a tier loses a
  gate nobody decided to remove whenever a run is left to infer it.
- **The selector, as a rule a plan can apply before the code exists**: a size threshold, and a RISK
  criterion that is a **floor** no other input may lower. The risk criterion needs a mechanical
  definition or it is re-argued every phase. The shape that works separates **ADDS** from
  **TOUCHES**. A phase **ADDS** a risk surface when its diff creates a place where such a decision
  is made for the first time — a new record type carrying the protected relation, a new serializer
  or form with a writable relation to a protected record, a new route or view over protected data, a
  new permission predicate or gate, a new field or computation that determines money — and **ADDS
  forces the full tier**. A phase **TOUCHES** one when it changes an existing one: a new filter on
  an existing door, a changed predicate, a refusal branch, a re-read of a protected row, a changed
  cap — and **TOUCHES allows light**. The test is one question: **can the reviewer name a thing of
  one of those kinds that did not exist before this phase?** Declare this project's list of kinds;
  the question is the same everywhere.
- **Where the verdict is WRITTEN, and the exact sentinel a downstream command gates on.** One fixed
  header line in the plan, carrying the tier *and* the reading that produced it — the count, and
  each risk call in the definition's own words rather than a paraphrase of what the work does. A
  tier chosen in conversation and not written down is re-chosen by every reader, and a paraphrased
  reading reads as a contradiction to the next one.
- **The per-issue exception**, if the light tier has one. An item that TOUCHES the risk surface
  without ADDING one does not raise the whole phase: it carries a flag and gets the full tier's
  per-item verification alone. **Declare that the flag is set TWICE and that the second reading
  binds** — the plan flags what it can see before the code exists, and every implementer's return
  declares whether its own diff touched the risk surface, which mandates the verifier whatever the
  plan said. A classification written in prose before implementation is exactly the one that misses.
- **The audit each tier owes at merge**, which the orchestrating consumer reads. Name what the full
  tier's audit re-runs and what the light one's runs **instead**, so a lighter merge audit is a
  decision on the record rather than an omission.
- **What a light-tier report must still carry, capped.** The verdicts, the PR, the gate output
  verbatim, the findings with their dispositions, and one section for proposals, deviations and
  **anything the run measured that contradicts or extends a rule in the adapter**. That last item is
  not decoration: the debrief is how a run amends the law, and dropping the debrief must not drop
  the channel.

**The release run's condition is a TREE comparison, never a claim about when a run last happened.**
Name the paths that count as code — sources, configuration, templates, assets, tests, tooling,
translations. Compare the release commit's tree for exactly those paths against the tree of the last
commit that had a full green run: equal → the run is skipped and the skip is stated with the command
that proved it; different in any of them → it runs, however recently some branch was green. A
phase's green is green for ITS branch point, and the integration branch receives merges and
sanctioned bookkeeping afterwards. A delta confined to documents, reports and records is bookkeeping
and triggers nothing. *(Measured: a full re-run over identical code was started at a release and
stopped by the owner as pure waste.)*

**Declare where the executor brief TEMPLATES live, one per tier.** The orchestrating consumer FILLS
a template rather than composing a brief per launch, so their paths are a project fact it needs;
the rule about why lives with that consumer.

**Do not declare what the tiers cost as a saving you have not measured.** The reason to record cost
at all is to falsify the prediction that motivated the tiers — so state the per-phase readings and
what they did or did not confirm. The one on record: dropping ceremony removed the *ceremony*
overhead and **not** the verification depth, because a phase's cost tracks its item count and the
proof depth each item demands, and the light tier reduces neither of those and must not — they are
what it kept on purpose. A small light phase with deep per-item proofs can cost more than a smaller
full one, and that is the selector behaving correctly.

### `config-dirs` *(optional)*

Directories holding **machine-read configuration** rather than prose — agent definitions, skill
manifests, harness settings. Two rules follow:

- **Prose formatters must never touch them.** A markdown formatter that doesn't understand YAML
  frontmatter will rewrite the opening `---` as a thematic break and fold the keys into a heading.
  The file still looks fine to a human and is silently unloadable by the tool — agents and skills
  stop registering with no error anywhere. Exclude these paths from any format-on-commit hook.
- **Quote frontmatter string values.** An unquoted `:` inside a description breaks the YAML parse
  the same silent way.

### `shared-files`

Files only the main loop may write (e.g. a solutions log, the tech-debt journal, the plan/issue
tracker). Implementer agents surface content for these in their structured return; the main loop
applies it. Parallel writes corrupt them.

**Say that "main-loop-owned" names the actor that MERGES, not whoever happens to hold the main loop
of their own process.** A phase executor is the main loop of its own session and still may not write
these: it proposes content in its return and the merging session writes it. Stated because the
phrase once read as self-granting to an executor, which was correctly told by its own relay that an
outflow duty on a shared record was unperformed — and the only correct response was to hand it up.

### `backlog`

**Defined by what it must DO, not by where it lives**: a durable list of open work with **stable
IDs** and an **archive** for closed items. A tracker, a journal file, a label in an issue system —
the shape is the project's; the three properties are not. Every triage disposition in the pipeline
("journaled", "deferred", "not scheduled", "resolved → archived") names this capability, and a
disposition with nowhere to land is a finding that was dropped.

Why each property, each paid for:

- **Stable IDs** — a finding is cited from a review report, a commit message, a plan and a PR body.
  Renumbering breaks every citation at once, so an ID is sticky even after its entry is archived.
- **An archive** — a journal whose fixed entries stay listed is lying about the backlog. Outflow is
  a triage duty equal to inflow: whatever resolves an entry archives it, in the same phase.
- **Durability** — a finding that exists only in a summary's count is already lost; a count cannot
  be triaged, cited or reopened.

**Recording is TOTAL; the round cap gates the FIXING, never the recording** (see `reviewer`). And a
record with no tree-change to make is still a record: give it its ID and write it **directly into
the archive**, born closed, with the condition that would reopen it — so it lands where something
reads it rather than in a report nobody opens.

**The host conventions below ship as the RECOMMENDED TEMPLATE the install interview offers, not as
requirements.** Take them if you have nothing; keep yours if you do:

- sticky numbering with a header stating the **next free ID**, so two sessions cannot mint the same one;
- born-archived records for findings with no tree-change;
- a `**Provenance**:` first line on every entry — which phase, which round, and the exit state it
  was journaled at — because a journaled finding's meaning depends on when and why it was journaled,
  and intake cannot see that without it;
- an amendment blockquote at the TOP of an entry rather than an edit to its body, so a decision that
  changed the entry is visible above the text it changed;
- a status line under any rollup entry (`N of M items remain — …`), because a 90 %-consumed rollup
  looks identical to an untouched one.

### `records`

The four surfaces the pipeline keeps honest. Name where each lives; **if one is absent at install,
create a minimal version** rather than running without it:

1. **The backlog** and its archive — the `backlog` capability above.
2. **A decision log** — dated, attributed product decisions, newest first: what was decided, by
   whom, and what it superseded. A decision recorded only in the code it produced is invisible from
   any other code, and one recorded only in a backlog entry disappears when that entry is archived.
   Mark superseded entries rather than editing them away.
3. **Phase-keyed artifacts** — plan, review reports, solutions log, per the `artifact-paths`
   capability.
4. **A practice doc** — where a measured lesson is backported into the law, one section per failure
   the project actually paid for. It is the reason a run improves the next run instead of the
   conversation it happened in.

**Who writes them: the actor that MERGES, and nobody else.** That rule already lives in
`shared-files` — cross-reference it, do not restate it, and note that a phase executor is the main
loop of its own session and still may not write these: it proposes content in its return and the
merging session applies it.

### `artifact-paths`

Where the pipeline's artifacts live: specs, plans, issues, reviews, solutions log, tech-debt journal.
Enables durable, tool-independent resume (state = artifacts + git, not the tool).

**Key the roots by ROUND, not by date, and say so here.** A bare date collides the moment a second
piece of work starts the same day, and the collision silently overwrites the first round's plan.
Declare the key (a date plus a short round slug is the shape that works), that **all roots use the
SAME key for one round**, that artifacts inside are **phase-keyed** (one file per phase and per
review round — never a sibling phase's section overwritten), and that a consumer **lists the parent
directory before writing**: an existing directory holding different work means you need your own
key, never a shared one.

### `orchestration-tool` *(optional)*

A harness tool that runs **scripted multi-agent workflows** — encoded stage dependencies, validated
structured returns, background execution, resume from a run id. Declare how it is invoked, what its
script language and authoring reference are, and whether resume re-runs a stage from scratch.

**Absent → plain agent dispatch is the path, and that is the default everywhere in this package**:
one dispatch per stage, each carrying its schema as an enumerated return-format section in the
prompt. The tool is an accelerator, never a requirement — the contract is identical either way and
only the mechanism differs. Say that substitution happened; do not emit scripts you cannot run.

**Declare it even if it is usually available, because availability is per-depth.** A tool granted to
a main session is commonly *absent* to a background executor running below it, so every consumer
must carry the dispatch path anyway and must check its own tool list before assuming the scripted
one. Two resume hazards worth writing down if the tool has resume: a stage re-run from scratch
applies its work **on top of its own residue** if the dead stage left edits in the shared tree, and
a whole-run resume can re-run stages that already completed.

### `code-graph` *(optional)*

A structural graph of the project's own code — symbols and the edges between them — that makes the
expensive questions cheap: **reachability** (*"can X actually produce Y?"*, the causal half of a
compound claim), call-site censuses, consumer hunts. Declare **how to build it, how to check its
staleness, and where it lives**.

**The one rule that makes an imperfect graph safe: it may only ever ADD candidates to check. It is
NEVER evidence for a negative.** *"Nothing calls X"* is the conclusion it cannot support, and the one
that deletes live code. Declare what your generator cannot see — templates, runtime registration
(signals, task autodiscovery, reflective dispatch), string-keyed lookup — because those absences are
precisely where a confident negative would be wrong.

**Also declare**: that it is **never committed** (it decays every commit), and the staleness check,
which must be **cheap enough to run on every orient**. A graph that is trusted without a freshness
check is worse than no graph, because its answers arrive with the same confidence either way.

*This capability is optional under the contract's own test: it requires installing a tool the project
does not otherwise need.* Consumers must degrade — absent means "answer the question the expensive
way", never "fail".

**A working reference implementation ships with the package**:
[`skills/code-graph/scripts/build_code_graph.py`](skills/code-graph/SKILL.md) — language-agnostic
(graphify's own detect/extract carry the tree-sitter grammars), code-only, no LLM, with the
three-state staleness check described above. Point this capability at it and you have the whole
thing; write your own if your project needs different extraction. Either way **the declaration lives
here**, so consumers depend on the capability rather than on any particular builder.

### `docs-lookup` *(optional)*

How to fetch current API docs before coding. **Reference default: Context7** (resolve-library-id →
query-docs, before any non-trivial API use). May also be a devdocs command, or `none`. The discipline
is "verify the API against current docs rather than trusting training data"; the tool is
adapter-supplied.

*Optional under the same test — it depends on a documentation service being reachable. When it is
not, **say so**; never silently fall back to training data for an API detail.*

### `constraints` *(optional)*

Project invariants a skill must honor (e.g. max file length, "scope every query to the tenant",
"wrap user-facing strings for i18n", "operator-facing console output stays ASCII" — a single
non-ASCII marker can crash a redirected report on a legacy-encoding console, precisely on the rows
it existed to flag).

**Declare what the product may ASSERT while a gate's data ships ahead of the gate.** A reversibility
ruling often forces the split — land the data first, enforce it second, each independently
revertible — and that opens a window in which the product *displays* a difference it does not
enforce. The window is not a bug and needs no backlog entry, but showing a difference is itself a
claim made to a customer, and no plan, entry or ruling will have anticipated it. The rule that
generalises: **render a capability only where it is granted, and never render a mark for where it is
not.** An absent line is true both before and after the gate ships, so no copy changes when the gate
lands; an explicit negative mark is false for as long as the gate is missing, and a customer can
check it.

### `refactoring` *(optional)*

Read by the `refactoring-discipline` skill. Declares:

- **Thresholds**: the soft line count that triggers diagnosis before adding code, and the hard
  limit that fails a commit (if a hook enforces one). The gap between them is the headroom to
  split calmly instead of mid-commit under a failing gate.
- **Census**: the command that lists the largest source files, so the skill measures instead of
  guessing.
- **Test layout**: where relocated tests go, and any collection/marker conventions a move must
  preserve.
- **Interface surface**: the project's list of things that count as public interface when code
  moves — import paths that need re-exports, framework registrations keyed to module paths,
  task/queue names derived from module paths, migration or serialization state bound to a
  module's location. Each entry exists because moving it has broken something before.

Absent → the skill uses its generic defaults and treats every cross-module reference as
interface until proven otherwise.

### `secrets`

Where secrets / credential files live and the rule: **never echo them**. Especially relevant for
infra repos (`tfvars`, `.env`).

### `shell-conventions` *(optional)*

Harness constraints for unattended runs: one command per call (no `&&`/`;`/`|` chaining), prefer
dedicated file/search tools over shell equivalents. Keeps parallel, permission-gated execution clean.

Three harness hazards worth declaring per machine, because each is silent and each has corrupted a
measurement:

- **Multi-line bodies passed inline through the shell are not always transported byte-for-byte.**
  On some hosts an escape level is stripped in transit and quote-dense bodies break the parse — the
  script then runs, its pattern matches nothing, and the symptom looks like a defect in the code
  under test. **Write the script, the commit message or the body to a FILE and run the file.** On
  record this has produced a literal control byte inside a pattern, a null byte inside a source
  file, a mutation that printed success without landing, and a commit message with a clause eaten by
  substitution.
- **Evidence can be STALE rather than absent.** A file read can serve content from before the last
  edit, and a scratch filename reused across rounds will be read as this round's result — one
  leftover output file showed a plausible passing line from a previous round. Key scratch paths by
  round, and re-read through a different tool when a result surprises you.
- **Any copy, hash, patch or restore is done in BINARY, and the line-ending rule is keyed on the
  path's declared text attribute, not on who wrote the file.** Text-mode writes, formatting hooks
  and version-control normalisation all rewrite endings, and a hash taken over decoded text cannot
  see it. Declare which paths the project normalises and which it leaves alone — a blanket rule is
  wrong in both directions — and name the cheap detector (the version-control tool's own end-of-line
  listing; a shell count of carriage returns is not one).

---

## Contract rules

1. **Skills reference capabilities, not stacks.** Illustrative examples of tools/languages are fine;
   what's forbidden is a skill's *operative behavior* requiring a given stack — the command comes from
   here.
2. **The committed adapter is law.** Detection only bootstraps a draft; it never overrides the file
   at runtime (otherwise resume drifts).
3. **🔒 fields are human-confirmed.** They cannot be safely detected.
4. **Absent optional capabilities degrade gracefully** — a skill states what it skipped, never guesses.
   **What makes a capability optional is a test, not a judgement: does it require installing a tool
   the project does not otherwise need?** If yes it is optional and every consumer needs an
   if-absent-skip branch; if no it is required and a consumer may refuse to run without it. The test
   is checkable, where "is this essential?" invites a fresh argument every time someone adds a
   capability. *(It classifies correctly on cases that feel borderline: a code graph needs an install,
   so it is optional; a docs-lookup service must be reachable, so it is optional — and both must fail
   loudly rather than silently substituting a guess.)*
5. **The `apply` list is a safety boundary.** Anything on it is off-limits to the parallel engine,
   full stop.
