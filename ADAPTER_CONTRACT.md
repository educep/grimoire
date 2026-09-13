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

---

## Capabilities

Each heading is a capability a skill may reference. `verify`, `apply`, `docs-lookup`,
`constraints`, and `refactoring` may be **absent** — a skill that needs an absent capability
degrades gracefully (e.g. no `verify` → review-only).

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

**If the project extends the relay with a bounded CLOSURE ROUND, declare it here** — the `review-gate`
skill defers to this capability on that point. Declare what may be fixed in it (low-severity, cheap,
in files the phase already opened), that its own scoped review is verification-only and journal-only,
and that **the closure review suspends the class-sweep obligation**, because a terminal gate that a
sweep can reopen is not terminal.

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

### `artifact-paths`

Where the pipeline's artifacts live: specs, plans, issues, reviews, solutions log, tech-debt journal.
Enables durable, tool-independent resume (state = artifacts + git, not the tool).

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
