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

### `apply` / `deploy` — GATED 🔒

The commands that **mutate live or external state irreversibly** — deploys, `terraform apply`,
resource deletes, prod DB migrations, releases, DNS changes. **List each one explicitly with what it
does and its danger.** The parallel engine may **NEVER** invoke anything here; `mode-select` routes
these to a **human-confirmed, sequential checklist** (decision D2). A README rarely says "this deletes
prod" — that's why this list is human-confirmed, not detected.

### `git-conventions`

Commit message format (e.g. `type(scope): summary`), branch naming, base branch, footer rules, and
the invariant that **the main loop owns all git** — implementer agents never run git.

### `model-per-role` 🔒

Model IDs by role — the crown-jewel policy (never one model for everything):

- `orchestrator` — the main loop (judgment; stays light).
- `implementer` — bulk file edits (cheap).
- `reviewer` / `fixer` / `domain-verify` — judgment-critical (a wrong call is costly).

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
