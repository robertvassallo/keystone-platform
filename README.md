# Keystone Platform

Multi-tenant SaaS platform — Django + Next.js + Postgres. Email-only auth, optional MFA, password reset + email verification, per-tenant user management, invite-based onboarding.

This repo is the running product. The boilerplate that seeds new projects of the same shape lives at [`keystone`](https://github.com/robertvassallo/keystone); new projects fork from there, not from here.

## What's shipped

- **Auth** — sign-up / sign-in / sign-out, email-only login, Django sessions, "remember me," password reset, change password, RFC 7807 error bodies
- **MFA** — optional TOTP enrolment + 10 hashed recovery codes; sign-in challenge with a 5-minute partial-auth ticket
- **Email verification** — soft-block; banner on every dashboard route until the user clicks the link
- **Tenancy** — shared-schema multi-tenant; one tenant per user, many users per tenant; tenant-scoped queries; explicit `Account.owner`
- **Invites** — owner sends an email invite; recipient lands on `/accept-invite`, sets a password, joins the inviting tenant; revoke + 7-day TTL
- **Roles** — `IsTenantOwnerOrStaff` gates admin actions; `is_staff` reserved for platform-staff (Keystone employees)
- **Tenant rename** — owner edits name + slug from `/settings/account`
- **Profile fields** — first / last name; computed `display_name` shown across the dashboard
- **Users admin** — paginated list with search + status filter, detail page, all tenant-scoped
- **CI** — GitHub Actions runs lint / typecheck / tests on every PR; `web` and `api` are required checks for `main`

## Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 15 (App Router) + React 19 + TypeScript strict |
| Styling | Tailwind 3 + SCSS modules + design tokens |
| Backend | Django 5 + DRF + Python 3.12 (mypy strict) |
| Database | Postgres 16 |
| Package managers | pnpm 9 + uv |
| CI | GitHub Actions (Postgres service container) |

Versions and rationale: `docs/01_architecture/stack.md`.

## Quick start

```bash
# Install deps
pnpm install
uv sync

# Bring up the dev DB (Postgres + Redis)
docker compose -f infra/docker/compose.dev.yml up -d

# Migrate
uv run --directory apps/api python manage.py migrate

# Run dev servers (two terminals)
uv run --directory apps/api python manage.py runserver
pnpm --filter @keystone/web dev
```

Web at <http://localhost:3000>, API at <http://localhost:8000>. Detailed install (Linux / macOS / WSL): `docs/01_architecture/dev-setup.md`.

## Layout

```
.
├── apps/
│   ├── api/             # Django + DRF
│   │   └── apps/accounts/   # User, Account, Invite, MFA
│   └── web/             # Next.js (App Router, RSC-first)
│       └── src/
│           ├── app/         # routes
│           ├── features/    # accounts, users, invites
│           └── shared/      # ui primitives, lib helpers
├── packages/
│   ├── tokens/          # design tokens → CSS + Tailwind preset + .d.ts
│   └── config/          # shared eslint / tailwind / tsconfig presets
├── infra/
│   └── docker/          # compose.dev.yml (Postgres + Redis)
├── .github/
│   ├── workflows/       # CI (lint / typecheck / tests)
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── docs/
│   ├── 01_architecture/   # stack, data-model, security, auth, monorepo, dev-setup, api-conventions
│   ├── 02_standards/      # semantic-html, css-sass, tailwind, ts, react, python, sql, a11y, testing, git-workflow, project-structure
│   ├── 03_ux/             # tokens, dashboard-layout, forms, data-display
│   └── 04_ai/             # decisions-log, agents, prompting, review-checklist
├── CLAUDE.md            # AI working agreement (read first)
└── README.md            # this file
```

## Working on the platform

Start with **`CLAUDE.md`** — it has the hard rules, the doc-router table, and the workflow every PR follows. Decisions baked into the codebase live in `docs/04_ai/decisions-log.md` (the source of truth for "why is it like this?").

To start a feature in Claude Code:

```
/new-feature <slug>
```

This branches off `main`, asks for scope, and runs the standard plan → implement → test → PR flow.

## Tooling expected

Node 22 LTS · pnpm 9 · Python 3.12 · uv · Postgres 16 (Docker is fine) · VS Code recommended.

Full install commands for Linux / macOS / WSL plus the Docker path for the dev DB: `docs/01_architecture/dev-setup.md`.

## License

Proprietary — see `LICENSE`. (`UNLICENSED` for the npm and pyproject distributions; internal use only.)
