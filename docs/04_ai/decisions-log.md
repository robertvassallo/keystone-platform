# Decisions Log

Lightweight ADRs (Architecture Decision Records). One entry per non-obvious decision. Recent first.

## When to add an entry

- A choice that overrides a default in this template.
- A trade-off where the chosen path isn't obviously the best — record why.
- A decision whose context will be lost if not written down ("we picked X because of an incident in Q2").
- A waived dependency advisory or temporary workaround that needs to be revisited.

## When NOT to add an entry

- Bug fixes — the commit message captures it.
- Refactors that don't change behaviour.
- Trivial dependency upgrades.

## Entry template

```markdown
## YYYY-MM-DD — Title (short, declarative)

**Status:** accepted | superseded by <link>

**Context:** What is the situation? What constraints exist?

**Decision:** What we're going to do.

**Consequences:** What changes as a result. Positive and negative.

**Alternatives considered:** Other options we looked at and why we passed.

**Revisit when:** What signal would make us reopen this? (e.g., "tenant count > 1000",
"if the bundle exceeds 300 KB gzipped", "in 90 days").
```

---

## 2026-04-24 — Adopt Django + Next.js + Postgres as the canonical stack

**Status:** accepted

**Context:** Setting up a starter template for full-stack web / dashboard projects. Need a stack that's productive for the dashboard / SaaS shape, with mature ORM, type safety on both ends, and a clean separation between server-rendered marketing pages and interactive dashboards.

**Decision:** Django (5.x, REST Framework) + Next.js (15.x, App Router) + Postgres (16.x). Python 3.12 + Node 22 LTS. pnpm + uv as package managers.

**Consequences:**
- Two languages to maintain (Python on the API, TS on the frontend).
- Strong defaults: Django auth / admin / ORM are mature; Next.js App Router gives us RSC + streaming.
- Shared types via OpenAPI generation, not via direct imports.
- Deploy story split — backend container vs Vercel-style frontend.

**Alternatives considered:**
- **Full-stack TypeScript (NestJS + Prisma + Next.js):** Single language, but loses Django's batteries-included productivity for admin / forms / migrations.
- **FastAPI + Next.js:** Faster API request handling, but no built-in admin / migrations / auth — we'd build a lot of plumbing.
- **Laravel / Rails:** Mature, similar tradeoffs to Django; team familiarity favoured Django.

**Revisit when:** Team composition shifts toward TS-only, or Django's RSC story changes meaningfully.

---

## 2026-04-25 — Bootstrap workspaces (apps/web + apps/api + packages)

**Status:** accepted

**Context:** First-time bootstrap of the Keystone template. Need to pin the choices the runbook in `docs/04_ai/first-project.md` flags as escalation points (project name, multi-tenancy, license, secrets, auth) before touching code.

**Decision:**
- **Project name:** `keystone-platform` (root `package.json`); Python distribution `keystone-api` (apps/api).
- **License:** Proprietary (`UNLICENSED`). Bundled `LICENSE` is an all-rights-reserved notice.
- **Multi-tenancy:** Shared schema with `tenant_id` + Postgres RLS — the template default per `docs/01_architecture/data-model.md`. The actual `tenant_id` columns and RLS policies land with the first tenant-scoped feature; bootstrap only records the strategy.
- **Secrets manager:** `.env` only for local development. Production secret-manager choice (1Password / AWS SM / Doppler / Infisical) is deferred until we deploy.
- **Auth:** Django sessions + DRF `SessionAuthentication` + CSRF — the template default per `docs/01_architecture/auth.md`. No JWT.
- **Stack pinning:** Next.js 15.5 (React 19.1) + Tailwind **3.x** (not 4) — `create-next-app@latest` ships Next 16 + Tailwind 4 today; we downgraded to keep alignment with `docs/01_architecture/stack.md` and the preset-based Tailwind config the docs assume.
- **Local services:** Postgres 16 + Redis 7 via `infra/docker/compose.dev.yml` (already in the template). No host-level Postgres install required.
- **Tokens:** `packages/tokens/dist/` is git-ignored; a root `postinstall` runs `node packages/tokens/build.mjs` so a fresh `pnpm install` produces a working stylesheet.

**Consequences:**
- Tenant isolation is enforced at the query layer (manager / selector + RLS), not via separate databases or schemas — keeps backups, migrations, and ops simple.
- Sessions mean the dashboard frontend must be same-origin (or behind a reverse proxy that preserves the session cookie). A future mobile / cross-origin client will need a separate token endpoint per `auth.md`.
- Tailwind 3 lets us use the `@keystone/config` preset directly. When Next.js officially recommends Tailwind 4 across the board, revisit.
- The `.env`-only secrets posture is fine for solo dev but ships nothing for prod; deployment work must pick a manager and document it before the first deploy.

**Alternatives considered:**
- *DB-per-tenant.* Stronger isolation but heavy ops overhead (per-tenant migrations, backups, connection pools). Worth revisiting if a customer with data-residency requirements appears.
- *JWT auth.* Simpler for non-browser clients but loses sessions' built-in revocation and CSRF story; not justified for a same-origin dashboard.
- *Tailwind 4.* Newer architecture but breaks the preset pattern documented in `docs/02_standards/tailwind.md`. Revisit when the CSS-first config story stabilises.

**Revisit when:** A second deployment target appears (mobile, partner SPA), a tenant requires data residency, the team adopts a chosen secret manager, or the docs are updated to assume Next 16 / Tailwind 4.

---

<!-- Add new decisions above this line. Keep most recent at the top. -->
