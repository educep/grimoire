# grimoire

*A spellbook for coding agents: portable skills you cast on your own workflow.*

Open-source [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for Claude Code and other SKILL.md-compatible agents. Each skill is a portable workflow an agent discovers and runs on its own, living in `skills/<name>/SKILL.md`. The `workflow-orchestrator` skill chains them end-to-end into managed rounds of work.

## Install

Install every skill in this repo with the [`skills`](https://skills.sh) CLI:

```sh
npx skills add laurentlouk/grimoire
```

Or install a single skill:

```sh
npx skills add laurentlouk/grimoire/roast
```

Skills land in `.claude/skills/` (project) or `~/.claude/skills/` (global). Invoke one in Claude Code with `/roast`, or let the agent trigger it automatically from the description.

## Skills

The full pipeline runs `extract` → `roast` → `to-plan` → `to-issues` → `mode-select` → `execute` → `review-gate`, with `workflow-orchestrator` managing whole rounds end to end. `tdd` and `refactoring-discipline` are the disciplines for writing and reshaping the code; `adaptive-replanning` describes how an unattended build loop recovers when a step fails. Each one is useful on its own.

| Skill | What it does |
| ----- | ------------ |
| [`extract`](skills/extract/SKILL.md) | Turns messy raw input — reviewer messages, bug reports, transcripts, meeting notes — into an investigated, prioritized task list. The front door when work arrives as prose instead of a spec. |
| [`roast`](skills/roast/SKILL.md) | Stress-tests a plan or design before any code is written. It reads the code and existing patterns first, then interrogates the design one question at a time until you reach shared understanding. |
| [`to-plan`](skills/to-plan/SKILL.md) | Turns an approved `roast` design into a written plan. No interview, just a synthesis of what was settled, sliced into small vertical increments. |
| [`to-issues`](skills/to-issues/SKILL.md) | Breaks a plan into independently grabbable issues, one vertical slice each, in your tracker (Jira, Linear, GitHub Issues, or other). |
| [`mode-select`](skills/mode-select/SKILL.md) | Chooses how a piece of work should run — inline, a main-loop checklist, dispatched agents, or a background workflow — and re-chooses whenever the shape of the work changes. |
| [`execute`](skills/execute/SKILL.md) | Runs an approved plan of issues into committed work: parallel agents edit, the main loop commits, correctness is verified. |
| [`review-gate`](skills/review-gate/SKILL.md) | Runs an independent adversarial review of finished work, triages its findings, and drives the fix loop until the work is genuinely clean. For every phase boundary and every merge. |
| [`workflow-orchestrator`](skills/workflow-orchestrator/SKILL.md) | Makes the main session a meta-orchestrator: it launches one background executor per round, audits the executor's report against git before merging, merges on a clean audit, and lands the bookkeeping. |
| [`tdd`](skills/tdd/SKILL.md) | Test-driven development discipline: red, green, refactor, one behavior at a time, tested through the public interface. |
| [`refactoring-discipline`](skills/refactoring-discipline/SKILL.md) | Structural refactoring of oversized files: diagnoses whether size is structural (split by responsibility, interface-preserving) or cosmetic (refuse to split), and never chops a file to satisfy a line count. |
| [`adaptive-replanning`](skills/adaptive-replanning/SKILL.md) | How an unattended build loop recovers from a failed step: replan the remaining work from the current state instead of restarting or retrying blindly. |
| [`review`](skills/review/SKILL.md) | The review *method*: how to scope a review, rate by reachability, prefer a plant to an inspection, report, and dispose findings. Loaded by every caller that reviews. It holds neither the project's checklist (that is the adapter's) nor where the report goes (that is the caller's). |
| [`code-graph`](skills/code-graph/SKILL.md) | Build and use a structural graph of the project's own code to answer reachability cheaply — *can X actually produce Y?* Ships a working **language-agnostic** builder. Optional: it needs a tool install. Carries the rule that makes an imperfect graph safe — **it may only ever ADD candidates, and is never evidence for a negative.** |

> **One executable, and it is deliberate.** Everything else here is prose you can read before
> adopting it. `skills/code-graph/scripts/build_code_graph.py` is the exception: a code graph is
> useless as a description of how to build one, and the wrapper turned out to be genuinely
> language-agnostic — graphify's own detect/extract carry the tree-sitter grammars, so nothing in it
> names a language. Point your adapter's `code-graph` capability at it, or write your own; consumers
> depend on the capability, never on the script.

## Agents and commands

Skills are the semantics; **something has to call them.** These are the callers the skills above
expect to exist. They are thin on purpose — each loads a skill and adds only what the skill
deliberately leaves open.

| File | What it is |
| ---- | ---------- |
| [`agents/reviewer.md`](agents/reviewer.md) | The reviewer as a **dispatchable agent**, for orchestrated runs. **Install it under the agent-type name your adapter declares** — a named agent type that fails to resolve degrades silently into a weaker generic review. It **returns** the report and writes no files. |
| [`commands/review.md`](commands/review.md) | The same reviewer as an in-session **slash command**, for reviewing now without paying for a subagent. Prints unless given a path. |

> **The rule these two exist to demonstrate: every caller declares where its report goes, even when
> the answer is "nowhere".** The three callers of the `review` skill differ — the agent returns, the
> command prints, an orchestrated stage has the orchestrator write the file — so none of them can
> inherit another's answer. In the host project the agent was silent about persistence while the
> workflow command told the orchestrator to save what the agent returned, under a note claiming the
> two were "kept in sync". An executor dispatched the agent and then polled the reviews directory
> **191 times** for a file it was itself responsible for writing. A caller silent here is a defect in
> that caller.

## How it works

**Skills carry the semantics; your project supplies the specifics.** Nothing in `skills/` names a
language, framework, test runner, or file layout — wherever a skill needs a project fact (how to
run tests, what the review persona is, which commands are too dangerous for automation), it asks
your repo's **project adapter** for it by capability name. The same skill files run unchanged
against a Django monolith or a zero-dependency Node microservice; only the adapter differs.

There are two ways to run them:

- **À la carte** — invoke any skill directly (`/roast`, `/tdd`, `/review-gate`, …) or let the
  agent trigger it from the description. Each is self-contained.
- **Orchestrated rounds** — tell the main session *"you are the workflow orchestrator"*. It loads
  `workflow-orchestrator` and becomes a meta-orchestrator that never edits code itself: it
  sequences the backlog, launches **one background executor per round** (the executor runs the
  pipeline — `extract` → `roast` → `to-plan` → `to-issues` → `mode-select` → `execute` →
  `review-gate` — and opens a PR, never merging), then **audits the executor's report against
  git** before anything merges, merges on a clean audit, lands the bookkeeping, and stops. The
  agent hierarchy is capped at three tiers by design — orchestrator → executor → the executor's
  implementation/review subagents, which are leaves — so delegation never nests deeper.

## Auxiliary artifacts

The skills read and maintain a small set of per-project artifacts. None of them live in this
repo — they live in *your* repo (or your agent harness), and **when one doesn't exist yet, it is
created from scratch as the first act of working in a new project**:

1. **The project adapter — `.claude/project-adapter.md`** (spec:
   [`ADAPTER_CONTRACT.md`](ADAPTER_CONTRACT.md)). The law of your repo: format/verify commands,
   repo and module topology, model-per-role policy, the gated `apply` list, the reviewer, where
   artifacts go. Missing? The contract's creation flow bootstraps it: draft from README + docs +
   manifests, a human confirms the un-sniffable 🔒 fields, commit — from then on the file, not
   runtime detection, is the source of truth. Skills reference capabilities by name and degrade
   gracefully when an optional one is absent. Real examples in
   [`examples/adapters/`](examples/adapters/): a production Django SaaS adapter and a toy Node
   service deliberately opposite to it on every axis (the agnosticism proof).

2. **The orchestrator's memory.** Persistent per-project notes the orchestrator reads before
   anything moves and updates at every round close: current state (branch, counts, what is
   deployed), the ordered queue, any round in flight, and measured lessons. Where it lives
   depends on your harness (Claude Code keeps a per-project memory directory outside the repo);
   the location matters less than the discipline — state is re-derived from git and the artifacts
   when in doubt, never trusted stale. **In a brand-new project it simply doesn't exist**: the
   orchestrator's Orient step starts it from scratch, together with the record surfaces below,
   before launching the first round.

3. **Record surfaces, committed in your repo.** A backlog + its archive (work that names a
   tree-change vs. records with reopen triggers), a decision log (dated, attributed product
   decisions — a decision recorded only in code is invisible), round-keyed artifact directories
   (plans / reviews / solutions), and a practice doc where measured lessons get backported into
   the law. New project → the orchestrator creates minimal versions before the first round; an
   orchestrator without record surfaces produces rounds that evaporate.

## Recommended `CLAUDE.md` setup

`roast` works best when your agent reads the project's documentation before asking you anything. Add this to your project's `CLAUDE.md` (or `AGENTS.md`) so the docs-first behavior applies everywhere, not just inside the skill:

```markdown
## Explore before asking; don't guess

If a fact is discoverable — in the project's documentation (`README`, `docs/`, ADRs,
specs, runbooks), the code, schemas, API contracts, config, or git history — find it
yourself before putting the question to the user, and never state a discoverable fact
as a guess. Reserve questions for decisions only the user owns: product/UX calls, cost
or vendor trade-offs, priorities, and context that lives outside the codebase. When
exploration is inconclusive, say what you checked and what's still unknown, then ask.
```

## License

[MIT](LICENSE)
