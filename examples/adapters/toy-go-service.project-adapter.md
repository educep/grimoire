# Project adapter — toy Go service (agnosticism proof)

> **Example adapter.** Conforms to `ADAPTER_CONTRACT.md`. Deliberately chosen to **contrast
> `saas_inventory` on every axis** — different language, module topology, reviewer, i18n, branching —
> to prove the same `skills/execute/SKILL.md` runs unchanged. If `execute` needs zero edits across
> this and the Django adapter, agnosticism holds.

## `overview`

A small HTTP microservice in **Go**. Organized by feature: each capability lives in its own package
under `internal/<feature>/` (handler + service + store together). No i18n. Docs in `README.md` and
`docs/`.

## `repo-topology` 🔒

`single`.

## `module-topology` 🔒

**`feature-organized`.** Each feature is a self-contained package, so a vertical slice touches one
package's files and is **already file-disjoint** from other slices. The batcher keeps slices whole and
parallelizes them directly — no horizontal splitting needed. (This is the exact opposite of
`saas_inventory`'s layer topology — the switch that proves the batcher adapts.)

## `format`

`go fmt ./...` then `goimports -w .`. Agents end in this state before returning.

## `verify`

`go test ./...`. Subset: `go test ./internal/<feature>/...`. Race check for concurrency-sensitive
work: `go test -race ./...`. No external DB needed (stores use an in-memory fake behind an interface).

## `apply` / `deploy` — GATED 🔒

Never run by the parallel engine — `mode-select` routes to a human-confirmed checklist:

- `terraform apply` — live infra.
- `kubectl apply` / the deploy pipeline — ships to a live cluster.
- production DB migrations.
- release tag push (`git tag vX.Y.Z && git push --tags`) that triggers a release build.

## `git-conventions`

- Conventional commits: `type(scope): summary`.
- Base branch `main`. One **feature branch per issue**, opened as its own PR (contrast with
  `saas_inventory`'s one-PR-per-phase — the engine doesn't care which; it reads this field).
- **The main loop owns all git**; agents never run git.
- One git command per call.

## `model-per-role` 🔒

- `orchestrator` — Opus.
- `implementer` — Sonnet.
- `reviewer` / `fixer` / `domain-verify` — Opus.

## `reviewer` 🔒

- Agent-type **`code-reviewer`** (a generic reviewer — NOT the Django project's `inspector` persona;
  proves the reviewer is pluggable).
- Severity scale: `blocker` / `major` / `minor` / `nit`.
- Triage: `blocker`/`major` always fixed; `minor`/`nit` fixed only if they block later work, else
  journaled.
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

**Context7** (reference default): `resolve-library-id` → `query-docs` before non-trivial use of a
third-party module. `none` for the Go standard library.

## `constraints`

- `gofmt`-clean; `go vet ./...` passes.
- Wrap errors with context (`fmt.Errorf("...: %w", err)`); no naked returns.
- Tests are table-driven; concurrency-sensitive code has a `-race` test.

## `secrets`

Config/secrets in `.env` and `configs/*.local.yaml`. **Never echo them.**

## `shell-conventions`

- One command per call; no `&&`/`;`/`|` chaining; no `cd`.
- Dedicated tools over shell: `Read`/`Grep`/`Glob`/`Edit`/`Write`. Reserve Bash for `go …`, the
  `make` targets, and the test runner.
