# grimoire

*A spellbook for coding agents: portable skills you cast on your own workflow.*

Open-source [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for Claude Code and other SKILL.md-compatible agents. Each skill is a portable workflow an agent discovers and runs on its own, living in `skills/<name>/SKILL.md`. A JS orchestrator that chains them end-to-end is coming.

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
