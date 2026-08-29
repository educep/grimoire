# Project adapter — toy Node service (agnosticism proof)

> **Example adapter.** Conforms to `ADAPTER_CONTRACT.md`. Deliberately chosen to **contrast
> `saas_inventory` on every axis** — different language, module topology, reviewer, i18n, branching —
> to prove the same `skills/execute/SKILL.md` runs unchanged. If `execute` needs zero edits across
> this and the Django adapter, agnosticism holds. (Originally drafted for Go; retargeted to Node
> 2026-07-31 because the proof machine has no Go toolchain — every contrast axis survives the swap.)
> Installed at `toy-node-service/.claude/project-adapter.md`.

## `overview`

A small HTTP microservice in **Node 22** (ESM, zero dependencies: `node:http` + the built-in
`node:test` runner). Organized by feature: each capability is a self-contained folder under
`src/features/<feature>/` (routes + logic + tests together), auto-discovered by the server at
startup — features never edit shared files. No i18n. Docs in `README.md` and `docs/`.

## `repo-topology` 🔒

`single`.

## `module-topology` 🔒

**`feature-organized`.** Each feature is a self-contained folder auto-mounted by the server, so a
vertical slice touches one folder and is **already file-disjoint** from every other slice — zero
shared-file edits, not even route wiring. The batcher keeps slices whole and parallelizes them
directly. (The exact opposite of `saas_inventory`'s layer topology — the switch that proves the
batcher adapts.)

## `format`

`npx --yes prettier@3 --write .` (config in `.prettierrc.json`). Agents end in this state.

## `verify`

`node --test` (whole suite). Subset: `node --test src/features/<feature>/`. No database, no
external services — stores are in-memory. Verification shares nothing; parallel agents may run
their own subset freely.

## `apply` / `deploy` — GATED 🔒

Never run by the parallel engine — `mode-select` routes to a human-confirmed checklist:

- any deploy pipeline / container push to a live environment.
- release tag push (`git tag vX.Y.Z && git push --tags`).

(None exist yet in this toy; the field stays so the engine exercises reading it.)

## `git-conventions`

- Conventional commits: `type(scope): summary`.
- Base branch `main`. One **feature branch per issue**, merged with `--no-ff` so each issue is a
  visible unit (this repo has no remote, so the local merge stands in for the PR — contrast with
  `saas_inventory`'s one-PR-per-phase; the engine doesn't care which, it reads this field).
- **The main loop owns all git**; agents never run git.
- One git command per call.

## `model-per-role` 🔒

- `orchestrator` — the main-loop model.
- `implementer` — the cheap model (Sonnet).
- `reviewer` / `fixer` / `domain-verify` — the judgment model (Opus).

## `reviewer` 🔒

- **Inlined persona** (no registered agent type — proves the reviewer is pluggable and NOT the
  Django project's `inspector`): a generic senior code reviewer dispatched on the judgment model,
  instructed to verify by executing (`node --test`, hit the endpoints) rather than reading.
- Severity scale: `blocker` / `major` / `minor` / `nit`.
- Triage: `blocker`/`major` always fixed; `minor`/`nit` fixed only if they block later work, else
  journaled to `docs/TECH_DEBT.md`.
- Reports to `docs/reviews/{date}/`.
- `MAX_FIX_ROUNDS` = 2.

## `shared-files`

Main-loop-owned; agents surface content in their return:

- `CHANGELOG.md`
- `docs/solutions/{date}.md`
- the plan file

## `artifact-paths`

- plans: `docs/plans/{date}/`
- reviews: `docs/reviews/{date}/`
- solutions log: `docs/solutions/{date}.md`
- tech-debt journal: `docs/TECH_DEBT.md`

## `docs-lookup`

`none` for the Node standard library (the whole toy). Context7 if a third-party module ever
appears.

## `constraints`

- Zero runtime dependencies — `node:` builtins only.
- ESM throughout; every feature folder self-contained (routes.js is the only entry the server
  reads); tests colocated with the feature and runnable standalone.
- No feature may edit a file outside its own folder.

## `secrets`

`.env` (none exist yet). **Never echo it.**

## `shell-conventions`

- One command per call; no chaining; no `cd`.
- Dedicated tools over shell: `Read`/`Grep`/`Glob`/`Edit`/`Write`. Reserve Bash for `node …` and
  `npx …`.
