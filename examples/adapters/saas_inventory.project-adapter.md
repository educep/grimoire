# Project adapter — saas_inventory (Cuadra / InventoryManager)

> **Example adapter.** Conforms to `ADAPTER_CONTRACT.md`. Reconstructed from the project's
> `macro-plan-*` commands, `WORKFLOW_check.md`, and `CLAUDE.md`. Copy to
> `saas_inventory/.claude/project-adapter.md` to use. 🔒 fields were human-confirmed, not detected.

## `overview`

Multi-tenant SaaS inventory-management app ("Cuadra"). Backend: Python / **Django** + DRF + Celery.
Frontend: Django templates with HTMX + Alpine + Tailwind. Spanish (`es`) i18n throughout. Docs live
in `CLAUDE.md`, `docs/`, `docs/dev/`. Ecuador SRI e-invoicing is a correctness-critical domain.

## `repo-topology` 🔒

`single` — one Django monolith repo.

## `module-topology` 🔒

**`layer-organized`.** Django apps share layer files (`models.py`, `views_reports.py`,
`views_exports.py`) and a single `locale/es/LC_MESSAGES/django.po`. Vertical slices collide on these,
so the batcher must split work into **file-disjoint** groups and recombine at the PR boundary. This is
why the `.po` hook (below) forbids two string-adding issues in one batch.

## `format`

`make format`. Static checks: `make lint`, `make mypy`. Every agent leaves the tree `make
format`-clean before returning.

## `verify`

Tests run against a **local Postgres in Docker — never RDS**.

- Setup first: `docker-compose -f docker-compose.test.yml up -d` (DB `inventory_test`, host port 5432).
- Full suite: `.venv\Scripts\python.exe -m pytest --no-header -p no:cacheprovider` (Windows venv;
  ~35 min). Or `.\run_tests_local.ps1`.
- Subset: pass node IDs or file paths.
- `config/settings.py` auto-selects `envs/.env.test` when pytest is imported.

New behavior must include tests, **including cross-tenant isolation cases**.

## `apply` / `deploy` — GATED 🔒

The parallel engine may **never** run these — `mode-select` routes them to a human-confirmed
checklist (see the `docs/plans/2026-07-04/` deployment plan for the pattern):

- `terraform apply` — mutates live AWS infra.
- AWS CLI destructive ops — e.g. `aws rds delete-db-instance`, bucket deletes.
- **Production DB migrations** on RDS (as dangerous as `terraform apply`).
- Elastic Beanstalk deploys / releases; DNS (Route 53) changes.

Log concrete outputs (bucket names, queue ARNs, EB CNAMEs) to the solutions log so later sessions
know live state.

## `git-conventions`

- Commit message: `type(scope): summary`. **No `Co-Authored-By` footer.**
- Base branch `dev`. **Never commit to `main`.**
- **One integration branch + one PR per phase**; every issue commits linearly onto it (one commit per
  issue); no per-issue sibling branches, no merges.
- **The main loop owns all git**; agents never run any git command.
- **One git command per Bash call** — never chain with `&&`/`;`/`|`.
- When committing via Bash, prefix with `PATH="$PWD/.venv/Scripts:$PATH"` so the `makemessages-check`
  pre-commit hook finds Django. If a hook modifies a file (re-sorts `requirements.txt`, runs
  mdformat), `git add` it and re-commit.
- PRs follow `.github/pull_request_template.md`.

## `model-per-role` 🔒

- `orchestrator` — **Opus** (main loop, stays light).
- `implementer` — **Sonnet** (bulk file edits, ~5x cheaper).
- `reviewer` / `fixer` / `domain-verify` — **Opus** (judgment-critical). For SRI / tax / money /
  tenant-scoping, use the `sri-expert` agent-type on the verify stage.

## `reviewer` 🔒

- Agent-type **`inspector`** (`.claude/agents/inspector.md`) — do NOT inline the review command.
- Severity scale: 💀 CATASTROPHE / 😱 DISGRACE / 😒 EYESORE / 🔍 NITPICK.
- Triage: 💀/😱/😒 **always fixed**; 🔍 fixed only if leaving it would block later TODO work, else
  **journaled to `docs/dev/TECH_DEBT.md`**.
- Inspector diffs `origin/dev...{phase-branch}` (the whole integrated phase). Reports saved to
  `reviews/{YYYY-MM-DD}/review_phase_{N}[.r{round}].md`.
- `MAX_FIX_ROUNDS` = 2; anything still unfixed after the cap is journaled and flagged loudly.

## `shared-files`

Main-loop-owned; agents surface content in their return, never write these:

- `solution/{YYYY-MM-DD}/solutions.md`
- `docs/dev/TECH_DEBT.md`, `docs/dev/TECH_DEBT_ARCHIVE.md`
- the plan file (`docs/plans/{date}/TODO.md` / `WORKFLOW_PLAN.md`)

## `artifact-paths`

- plans: `docs/plans/{YYYY-MM-DD}/`
- reviews: `reviews/{YYYY-MM-DD}/`
- solutions log: `solution/{YYYY-MM-DD}/solutions.md`
- tech-debt journal: `docs/dev/TECH_DEBT.md`

## `docs-lookup`

**Context7** (the reference default). Before any non-trivial API use: (1) `resolve-library-id` with
the library name, (2) `query-docs` with a specific question. Library table + workflow in
`.claude/skills/context7-docs/SKILL.md` (Django, djangorestframework, celery, …).

## `constraints`

- No file exceeds **700 lines**.
- **Multi-tenancy: scope every queryset by company** (`filter(company=request.user.company)`).
- Querysets use `select_related` / `prefetch_related` (avoid N+1).
- i18n: wrap user-facing strings; add Spanish to `django.po`, run `compilemessages`;
  `makemessages-check` must be green on every commit.

## `secrets`

Credentials in `envs/.env*` (`envs/.env.test`, …) and any `tfvars`. **Never echo them.**

## `shell-conventions`

- One command per Bash call; no `&&`/`;`/`|`; no `cd` before a command (use absolute paths / working
  dir).
- Dedicated tools over shell: `Read` not `cat`/`head`/`tail`; `Grep` not `grep`/`rg`; `Glob` not
  `find`/`ls`; `Edit` not `sed`/`awk`; `Write` not `echo >`. Reserve Bash for `make …`, `pytest`,
  `python manage.py …`, `pre-commit`.

## Commit-gate note (batching constraint)

The `makemessages-check` hook fails any commit whose tree has source strings not yet in `django.po`.
Therefore **no two string-adding issues may share a batch** — the clean-tree boundary that lets a
commit pass only happens between batches (in the main-loop commit phase).
