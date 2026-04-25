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

## 2026-04-25 — Auth-core: custom User on email, sessions, RFC 7807

**Status:** accepted

**Context:** First user-visible feature. The runbook prescribes Django sessions for the dashboard, but the project also requires a custom user model from day one (so we can carry `tenant_id` and skip the painful `AUTH_USER_MODEL` swap later) and email-only login.

**Decision:**
- **Custom `User` model** in `apps/api/apps/accounts/`, subclassing `AbstractBaseUser` + `PermissionsMixin`. `USERNAME_FIELD = "email"` (no `username` field). UUID v7 primary key via `uuid-utils`. Audit + soft-delete columns (`created_by`, `updated_by`, `deleted_at`, …) per `data-model.md`. `tenant_id` is a nullable `UUIDField` today; becomes required when the `Account` model lands.
- **`uq_user_accounts_email_active`** is a partial unique index (`WHERE deleted_at IS NULL`) so a soft-deleted user doesn't squat on the email forever.
- **`set_updated_at` Postgres trigger** applied via `RunSQL` in `accounts/migrations/0001_initial.py`. Future models that want it call the same function (created here).
- **Sessions:** rolling 8h with `SESSION_COOKIE_AGE = 28800`; default `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`. "Remember me" overrides per-session via `request.session.set_expiry(REMEMBER_ME_DURATION)` = **30 days**.
- **DRF auth class:** custom `config.authentication.SessionAuth` (subclass of `SessionAuthentication`) that returns a non-empty `authenticate_header`. Without this, DRF rewrites unauthenticated 401s to 403, which violates the `api-conventions.md` contract.
- **Errors are RFC 7807** end-to-end via `config.exception_handler.problem_details_handler`, wired through `REST_FRAMEWORK.EXCEPTION_HANDLER`. Error type IRIs use `about:blank#<code>` until we publish a public docs site.
- **Frontend dev proxy:** `next.config.mjs` rewrites `/api/*` → `http://localhost:8000/api/*` so the browser sees same-origin (sessions + CSRF cookies travel without CORS). Production handles this at the load balancer.
- **Client/server boundary on the API client:** server-only fetch (`apiFetchServer` + `getMeServer`) lives in separate modules and uses `import "server-only"`; the feature's public `api/index.ts` deliberately does **not** re-export them, so the client bundle never pulls `next/headers`.
- **Sessions backend:** still `db` (Django default). Promoting to `cache_db` + Redis is deferred to the PR that wires Redis-backed cache for other reasons.

**Consequences:**
- Migrating away from Django's built-in `User` later would be expensive — accept the lock-in.
- `auth_user` table is **not** created; the migration tree starts at `accounts.0001_initial` after `auth.0012`. Existing dev databases must be wiped (`docker compose down -v`) before re-migrating.
- Tests need a `conftest.py` `cache.clear()` autouse fixture so DRF throttle counters don't leak between tests; otherwise the throttle test fails the entire suite.
- factory_boy + django-stubs interactions are noisy; tests get a relaxed mypy override (`disallow_untyped_calls = false`, `disallow_untyped_decorators = false`).
- Forms use `react-hook-form` + `zod`. The feature pulls in `@hookform/resolvers`, `zod`, `react-hook-form` as runtime deps and `vitest`, `@testing-library/*`, `jsdom`, `@vitejs/plugin-react` as dev deps.

**Alternatives considered:**
- *Stock Django `User`.* Free up front; the swap to a custom model after data exists is a multi-week project. Not worth the deferral.
- *DRF default `SessionAuthentication` + accepting 403 for unauthenticated.* Simpler but breaks the documented `401 = unauthenticated, 403 = forbidden` API contract.
- *CITEXT for case-insensitive email.* Avoided to keep migrations portable; we lowercase on write in the manager + form schemas instead.
- *Re-exporting `getMeServer` from the feature barrel.* Tried; webpack pulled `next/headers` into the client bundle. Splitting the barrel is the only stable fix.

**Revisit when:** A second tenant-aware feature ships (then enforce `tenant_id NOT NULL`), Redis is wired into Django (move sessions to `cache_db`), or the public errors documentation site exists (swap `about:blank#…` for canonical URLs).

---

## 2026-04-25 — Auth password-reset + change-password

**Status:** accepted

**Context:** Second slice of the auth feature, building on `auth-core`. Need a forgot-password flow, a tokenised reset link from email, and a change-password page for signed-in users — all without leaking which addresses are registered.

**Decision:**
- **Token strategy:** Django's built-in `default_token_generator` (HMAC over `pk + last_login + password_hash + timestamp`). No new DB schema. Single-use is automatic — once the password changes, the embedded hash invalidates every outstanding token.
- **Token expiry:** `PASSWORD_RESET_TIMEOUT = 3600` (1 hour). Deviates from Django's 3-day default; aligned with NIST short-lived recovery tokens.
- **Account-non-enumeration:** the request endpoint always returns **204** regardless of whether the email is known. Inactive users are silently skipped too. Forgot-password tests assert that no email is sent for unknown / inactive addresses.
- **Reset URL shape:** `{FRONTEND_URL}/reset-password?uid=<base64>&token=<token>` — `uidb64` + `token` separately, matching Django's stock pattern. `FRONTEND_URL` is env-driven, default `http://localhost:3000`.
- **Email format:** plain-text + minimal HTML alternative (no branded templates). Subject + bodies live in `apps/api/apps/accounts/templates/accounts/emails/`. Dev backend stays `console`.
- **`change_password` session policy:** call `update_session_auth_hash(request, user)` after the save so the **current session stays alive**; every other session for the same user is invalidated implicitly because Django ties session validity to the password hash. No "log out everywhere" toggle today — it's the default.
- **Status-code mapping:** `422 invalid_reset_token` for bad/expired tokens, `422 wrong_current_password` for change-password mismatch (both domain-rule failures, not validation), `400` for weak passwords. Keeps the API contract from `api-conventions.md`.
- **Client schema validation:** `changePasswordSchema` rejects `currentPassword === newPassword` at the form layer to avoid a server round-trip for the obvious case.

**Consequences:**
- No DB migration. Tokens live nowhere — you can't list active reset tokens, only consume them.
- A user requesting a reset from two different devices invalidates the first email when they use the second (the password hash changes). Acceptable — only the most recent reset wins.
- Tests use `freezegun` to time-travel for token expiry assertions. Added as a dev dep.
- factory_boy + django-stubs interactions stay noisy; we widened the test mypy override with `disable_error_code = ["arg-type", "assignment", "attr-defined"]` and removed the per-line `# type: ignore` clutter.

**Alternatives considered:**
- *Custom `PasswordResetToken` table* — gives revocation + multi-device fan-out but adds a migration + a hot table for what's currently fine without one. Revisit if we need device-attached resets or admin revocation.
- *Magic-link sign-in* — rolled out as part of password-reset would broaden the scope to a third feature; not worth coupling.
- *Force re-sign-in after change-password* — simpler but worse UX. The current device just changed the password; making the user type it again immediately is friction without security benefit.
- *Constant-time response for unknown emails* — we kept the simpler "early return" path. A timing attacker could in principle distinguish. Acceptable risk for now; revisit if the API is exposed to a high-volume adversary.

**Revisit when:** A second password-reset path appears (magic link, social), an explicit "log out everywhere" toggle is requested, or branded transactional email enters scope.

---

<!-- Add new decisions above this line. Keep most recent at the top. -->
