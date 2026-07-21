# agent-skills

Open-source [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) for Claude Code and other SKILL.md-compatible agents.

Skills are portable workflows an agent discovers and runs on its own. Each lives in `skills/<name>/SKILL.md`.

## Install

Install every skill in this repo with the [`skills`](https://skills.sh) CLI:

```sh
npx skills add laurentlouk/agent-skills
```

Or install a single skill:

```sh
npx skills add laurentlouk/agent-skills/roast
```

Skills land in `.claude/skills/` (project) or `~/.claude/skills/` (global). Invoke one in Claude Code with `/roast`, or let the agent trigger it automatically from the description.

## Skills

These three chain into a design-to-work pipeline — `roast` → `to-plan` → `to-issues` — but each is useful on its own.

| Skill | What it does |
| ----- | ------------ |
| [`roast`](skills/roast/SKILL.md) | Relentlessly stress-tests a plan or design **before any code is written** — exploring the code and existing patterns first, then interrogating the design one question at a time until you reach shared understanding. |
| [`to-plan`](skills/to-plan/SKILL.md) | Synthesizes an approved `roast` design into a written plan — no interview, just synthesis of what's already settled, sliced into smallest-valuable-first vertical increments. |
| [`to-issues`](skills/to-issues/SKILL.md) | Breaks a plan into independently-grabbable issues as vertical slices in your issue tracker (Jira, Linear, GitHub Issues, or other), ready to implement one at a time. |

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
