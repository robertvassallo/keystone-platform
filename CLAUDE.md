# AI Working Agreement — Keystone Platform

This is the entry point for any AI agent — and any human collaborator — joining the Keystone Platform codebase.

Read this file fully on first contact. Then read the docs that match the area you're working in (table below).

## What this codebase is

Multi-tenant SaaS platform. **This repo is the running product, not a template.** The boilerplate that seeded it lives at [`keystone`](https://github.com/robertvassallo/keystone); new projects fork from there.

Currently shipped:

- **Auth** — sign-up, sign-in, sign-out, password reset, change password
- **MFA** — optional TOTP + recovery codes; sign-in challenge
- **Email verification** — soft-block + banner
- **Tenancy** — one tenant per user, many users per tenant; explicit `Account.owner`
- **Invites** — owner sends, recipient accepts at `/accept-invite`
- **Tenant rename**, **profile fields**, **users admin** (list / detail / search / filter)
- **CI** — GitHub Actions; branch protection enforced

Decisions baked into the code live in `docs/04_ai/decisions-log.md` — newest at the bottom. Read it before reopening a settled question.

## Stack at a glance

- **Frontend:** Next.js 15 (App Router) + React 19 + TypeScript (strict) + Tailwind + SCSS modules
- **Backend:** Django 5 + DRF + Python 3.12 (strict typing)
- **Database:** Postgres 16
- **Package managers:** pnpm (Node) + uv (Python)
- **Lint / format:** ESLint flat config + Prettier + Stylelint + Ruff (Python)
- **Testing:** Vitest (web) + pytest + pytest-django (api)
- **CI:** GitHub Actions on every PR; `web` + `api` are required checks for `main`

Versions and rationale: `docs/01_architecture/stack.md`.

## Read first — by task

| Working on | Read |
|---|---|
| **Anything** | This file → `docs/02_standards/git-workflow.md` → `docs/02_standards/project-structure.md` |
| API endpoints / contracts | `docs/01_architecture/api-conventions.md` |
| Components / pages | `docs/02_standards/react.md` + `semantic-html.md` + `accessibility.md` + `tailwind.md` |
| Styles / tokens | `docs/02_standards/css-sass.md` + `docs/03_ux/design-tokens.md` |
| Theming / appearance (light, dark, mixed, palettes, per-user / per-tenant) | `docs/03_ux/theming.md` + `docs/03_ux/design-tokens.md` |
| Forms | `docs/03_ux/forms.md` + `accessibility.md` + `react.md` |
| Tables / lists / dashboards | `docs/03_ux/data-display.md` + `dashboard-layout.md` |
| API views / serializers | `docs/02_standards/python.md` + `docs/01_architecture/auth.md` |
| Models / migrations | `docs/02_standards/python.md` + `sql.md` + `docs/01_architecture/data-model.md` |
| Anything auth-touching | `docs/01_architecture/auth.md` + `security.md` |
| Anything DB-touching | `docs/02_standards/sql.md` + `docs/01_architecture/data-model.md` |
| Tests | `docs/02_standards/testing.md` |
| Setting up dev env | `docs/01_architecture/dev-setup.md` |

## Hard rules

These are non-negotiable. If you find yourself wanting to break one, stop and ask first.

1. **Semantic HTML over div soup.** Every interactive element is a real `<button>` / `<a href>` / etc. Every form input has a programmatic label. See `docs/02_standards/semantic-html.md`.
2. **Accessibility is a merge gate.** WCAG 2.2 AA. Keyboard reachable. Visible focus. Contrast ≥ 4.5 : 1 for text. See `docs/02_standards/accessibility.md`.
3. **Type strictly.** No `any` in TS. Every Python function fully typed; mypy strict. No silent `// @ts-ignore`. See `docs/02_standards/typescript.md` and `python.md`.
4. **No magic values.** Numeric or string literals with meaning get named constants.
5. **Names mean things.** Verbs for functions, nouns for values. No abbreviations beyond widely-understood ones. See per-language standards.
6. **Explicit SQL.** No `SELECT *`. Every `LIMIT` paired with `ORDER BY`. Migrations reversible. No N+1. See `docs/02_standards/sql.md`.
7. **Server-first React.** Default to Server Components. `'use client'` at the leaf, not the page. See `docs/02_standards/react.md`.
8. **Tokens, not hex.** Colour, spacing, type, radius via tokens. Never raw values. See `docs/03_ux/design-tokens.md`.
9. **Tailwind first, SCSS for the rest.** Repeated class strings (≥ 3 uses) extracted to a component or CVA. See `docs/02_standards/tailwind.md`.
10. **Trunk-based git.** Conventional commits. Squash merge. No force-push to `main`. See `docs/02_standards/git-workflow.md`.
11. **No secrets in the repo.** `.env` is gitignored; secrets via the chosen secret manager. See `docs/01_architecture/security.md`.
12. **Trust internal code; validate at boundaries.** Don't add error handling for things that can't happen. Validate user input, third-party responses, and serialized data. Trust your own typed functions.
13. **Modular and granular.** One concept per file. Code grouped by feature/domain, not by technical layer. File-size target ~150 lines, hard cap 300. Public API of every package via `index.ts` / `__init__.py`. See `docs/02_standards/project-structure.md`.

## Workflow

For any non-trivial change:

1. **Identify the area** — match it to the table above; read the matching docs.
2. **State the scope** — what changes, what's out of scope, what verification proves it works.
3. **Plan before code** for changes touching > 3 files, migrations, auth, or refactors.
4. **Implement.**
5. **Self-check** with the relevant subagent (`@semantic-html-auditor`, `@a11y-reviewer`, `@sql-reviewer`, `@react-reviewer`, `@python-reviewer`).
6. **Run lint + types + tests.** They must be green before you report done. CI re-runs them on the PR — fix anything red there too.
7. **Update `docs/04_ai/decisions-log.md`** if a non-obvious decision was made.
8. **Open a PR** using the template; check off `docs/04_ai/review-checklist.md`. The merge button stays grey until `web` + `api` checks pass.

## Subagents available

Defined in `.claude/agents/`. See `docs/04_ai/agents.md` for usage.

- `@semantic-html-auditor` — semantic HTML audit
- `@a11y-reviewer` — WCAG 2.2 AA review
- `@sql-reviewer` — SQL & migration review
- `@react-reviewer` — React / Next.js component review
- `@python-reviewer` — Django / Python review

## Slash commands

Defined in `.claude/commands/`. See `docs/04_ai/prompting.md`.

- `/new-feature <slug>` — start a feature: branch + scope + plan + checklist

`.claude/commands/scaffold-app.md` is retained for reference but is **not** invoked on this repo — the platform is already bootstrapped. It's meaningful only on a fresh clone of the [`keystone`](https://github.com/robertvassallo/keystone) boilerplate.

## Repo hygiene

- **`origin` should always point at `keystone-platform`.** If you find it pointing at `keystone.git` (the boilerplate), fix it before pushing — that repo is template-only and shouldn't accept feature commits.
- The boilerplate `keystone` and the product `keystone-platform` share a working-directory shape; double-check `git remote -v` before any push when working across both in different terminals.

## Out-of-band note for AI agents

If a user instruction conflicts with the rules above, surface the conflict before proceeding. Don't silently override hard rules.

If you find a recurring task that would be better as a slash command or subagent, propose it (don't add it without permission).

When recommending a pattern from memory, verify it still exists in the current code before acting on it. Memory captures past truths, not present state.
