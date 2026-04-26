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

## 2026-04-25 — Auth MFA enrolment (TOTP + recovery codes)

**Status:** accepted

**Context:** Third auth slice. Originally scoped as one big `auth-mfa` PR; split into two — this one ships **enrolment + management** without changing the sign-in flow. The `auth-mfa-enforce` PR adds the sign-in challenge step on top.

**Decision:**
- **TOTP only** via `django-otp` + its `otp_totp` plugin. WebAuthn / passkeys deferred.
- **`MFARecoveryCode` table** — UUID v7 PK, FK to `User`, SHA-256 hex digest of the plaintext, `consumed_at` timestamp. Unique on `(user, code_hash)`. Index on `(user, consumed_at)` so "remaining codes" stays cheap.
- **10 recovery codes**, 8 chars each, sampled from a 32-char alphabet that drops visually-ambiguous characters (no `0/O/1/I/L`). Generated with `secrets.choice`. Shown **once** at enrolment + on regenerate, **stored hashed**, single-use.
- **No salting / KDF on recovery codes.** Codes are short-lived and per-account; SHA-256 is sufficient for the threat model. Documented as a deliberate deviation from "use a KDF" hygiene; revisit if recovery codes ever live longer than the account does.
- **Disable + regenerate** require **password** confirmation, not a current OTP. The user who lost their authenticator can still recover; OTP would lock them out.
- **Single `/mfa` page** that branches on enrollment status (Server Component fetches status; client component handles the multi-step flow). Linked from a small "Account" widget on the dashboard placeholder, alongside `/change-password`. Settings index is a deferred refactor.
- **TOTP issuer label** `"Keystone"` so authenticator apps display "Keystone (you@example.com)".
- **QR code** rendered via `qrcode[pil]` server-side; the resulting PNG ships as a base64 `data:image/png;base64,…` URL. The `secret` is also exposed in the response for manual entry when scanning fails.
- **Sign-in flow is unchanged in this PR.** Enrolling adds devices but doesn't gate sign-in until the next slice (`auth-mfa-enforce`) wires the 202 + verify step.

**Consequences:**
- A migration is required (`accounts.0002_mfarecoverycode` + the bundled `otp_totp_*` migrations). Reversible.
- New deps: `django-otp`, `qrcode[pil]` → pulls `pillow`. `pillow` is heavy (~6 MB) but standard for QR PNG rendering. Acceptable.
- Frontend file naming convention: `MFAEnrolFlow` failed `unicorn/filename-case` (it expects `Mfa…` not `MFA…`). Renamed components to `MfaEnrolFlow`, `MfaManagementPanel`, `MfaRecoveryCodesDisplay`. Future PRs use the same convention for acronyms in component names.
- mypy override widened: `django_otp.*` and `qrcode.*` added to `ignore_missing_imports`; `misc` added to the test-scope `disable_error_code` list (django-stubs flags many factory-generated assignments as misc).
- Throttling: enrolment endpoints are `IsAuthenticated` and use the default `UserRateThrottle` (600/min/user). The `auth` scope (5/min/IP) only protects anonymous endpoints — extending it to authenticated MFA confirm would be over-tight.

**Alternatives considered:**
- *Bundle enrolment + sign-in challenge in one PR* — splitting halves the review surface; sign-in is on the hot path and isolating that change makes rollback trivial.
- *Store recovery codes salted via Argon2 / `make_password`* — overkill for short-lived codes; SHA-256 + per-account search space (~10 × 32^8) is sufficient given DRF + IP throttling.
- *Browser-side QR rendering* — pulling a QR JS lib into the bundle when we already need server-side support for manual-entry secret was redundant.
- *`MFAChallenge` table for partial-auth state* — punted with the sign-in flow change to PR `auth-mfa-enforce`. This PR doesn't yet need session-based half-state.

**Revisit when:** WebAuthn / passkeys lands, `auth-mfa-enforce` ships (then revisit recovery-code hashing if the threat model changes), or a settings index page is introduced.

---

## 2026-04-25 — Auth MFA enforcement (sign-in challenge)

**Status:** accepted

**Context:** Closes the loop on the MFA work started in `auth-mfa-enrol`. With this PR an enrolled user signs in with email + password, gets a `202 {mfa_required: true}` instead of a session, and finishes the flow by submitting a TOTP code (or a recovery code). Users without MFA are unaffected.

**Decision:**
- **Partial-auth ticket lives in the Django session** under key `mfa_challenge` — `{user_id, remember_me, expires_at}`. **5-minute TTL**, single-use on success, persists on wrong-code so the user can retry without retyping their password.
- **TTL = 5 minutes.** Long enough for the realistic flow (password → grab phone → open authenticator → enter code), short enough to limit a leaked-ticket attack window. NIST SP 800-63B sits in this range.
- **Single `/api/v1/auth/mfa/verify/` endpoint** that accepts a single `code` field. Server **auto-detects** TOTP (6 digits) vs recovery (anything else); picking the wrong format just yields `invalid_mfa_code`.
- **No DB schema change** — partial state is session-only, recovery-code consumption uses the existing table.
- **Sign-in returns 202 (`{mfa_required: true}`) when challenge required, 200 otherwise.** The frontend's `signIn` helper now returns a discriminated union (`{kind: "signed_in", user} | {kind: "mfa_required"}`) so the form picks the branch.
- **`SignInForm` is a small state machine** (`idle → mfa_challenge`). No new route — `/sign-in` URL stays. The challenge view is a sibling component (`MfaChallengeForm`) the form swaps in.
- **`MfaChallengeForm` toggles between TOTP and recovery modes** by re-mounting via `key`, so each mode has its own validation schema (TOTP: `^\d{6}$`, recovery: `^[A-Za-z0-9]{8}$` upper-cased on submit).
- **`update_session_auth_hash` is not needed** here — `django_login` itself rotates the session for the verified user.
- **`OTP_TOTP_THROTTLE_FACTOR = 0`** in test settings only — django-otp's per-device 1-second backoff after a failed verify is the right behaviour for users but makes deterministic wrong-then-correct tests painful.

**Consequences:**
- A user who closes the browser mid-challenge loses the session (browser-close session semantics) and must sign in again — acceptable.
- The 5-min TTL means a slow user can be punished if they walked away. Mitigated by the "Use a recovery code instead" toggle and the fact that re-signing in is one form away.
- Auto-detection of TOTP vs recovery is convenient but means a 6-digit recovery code (impossible with our 8-char alphabet but worth flagging) would be misclassified. Today the code shapes don't overlap.
- No `update_session_auth_hash` on the verify path — fine because there's no prior session to preserve, but worth being explicit so a future refactor doesn't flip this.

**Alternatives considered:**
- *Explicit `is_recovery_code` flag in the API* — UX-equivalent, more bytes per call, more branches in the client. Skipped.
- *Dedicated `MFAChallenge` DB table* — would let admins revoke active challenges, but a 5-min session-only ticket is sufficient and adds no migration / hot table. Revisit if multi-device challenge state becomes a thing.
- *One-attempt ticket (consume on any verify call)* — more secure but punishes mistypes hard. The 5/min auth-scope throttle already caps brute-force.
- *Separate `/sign-in/verify` route* — clean URL, but the state-machine refactor in `SignInForm` keeps the URL stable and avoids a router round-trip. Better UX.

**Revisit when:** WebAuthn / passkeys lands, "trust this device for 30 days" enters scope, step-up MFA on sensitive actions (`change_password`, `disable_mfa`) is needed, or `django-axes` ships and we want to coordinate lockouts.

---

## 2026-04-25 — Users-list — first non-auth feature

**Status:** accepted

**Context:** First feature that isn't auth. Validates the granular feature-folder layout end-to-end on a read surface and gives staff a way to see who's signed up.

**Decision:**
- **Resource separation.** New `apps/web/src/features/users/` folder rather than extending `features/accounts/`. The `accounts` feature owns the auth flows; `users` owns the resource view of users. Matches "one feature folder per domain" — when a `User` detail page or invite-user form lands, it goes here.
- **URL.** `GET /api/v1/users/` (top-level resource), backed by `apps/accounts/api/users_urls.py` (a sibling of the auth `urls.py` file). Two URL modules in the same Django app split by **resource** (auth flows vs. resource views) — clean separation without spawning a second Django app for what's still User-the-model.
- **Permission gate.** New reusable `config.permissions.IsStaff` (subclass of `IsAuthenticated` adding `is_staff=True`). Returns **403** to non-staff, **401** to anonymous. Frontend SSR catches the 403 and renders an "Access required" panel.
- **Pagination = offset.** `?page=N&page_size=25` (max 100). Deviates from the cursor default in `api-conventions.md`. Justification: this is an admin list of bounded size and `sql.md` explicitly OKs offset for "< 10K items" admin lists. Offset supports "jump to page 5" out of the box; cursor doesn't.
- **Response shape.** `{ data: [...], page: { page, page_size, total } }`. Same envelope as the cursor shape in `api-conventions.md` but with `page`/`page_size`/`total` instead of `next_cursor`/`prev_cursor`. Documented as the offset variant.
- **Default sort.** `-created_at` then `-id` (deterministic tie-break for same-instant rows). No sort UI in this PR.
- **Inline table primitive.** `UsersList` is built directly in `features/users/components/UsersList/` with raw `<table>` + `<th scope>` + `<caption>` + relative-time cells with absolute `title`. **Not** promoted to a `shared/ui/DataTable/` yet — per the project-structure rule, "promote on second consumer". Promote when a second list ships.
- **Skeleton + empty + error states designed**, per `data-display.md`. Empty state is theoretically unreachable (the staff user is always at least one row) but designed for completeness.
- **Status badges pair colour with text.** Active / Inactive / Staff. No colour-only signalling — meets WCAG / `accessibility.md`.

**Consequences:**
- The `tenant_id` column on `User` is intentionally **not** in the list view. When the `Account` model lands and tenants matter, the column comes back, ideally with a tenant filter.
- The `users` Django URL namespace and the `users` web feature folder share a name — consistent with the resource. The `accounts` Django app retains both auth URLs and the new `users` URL module.
- The new `IsStaff` permission lives in `config/permissions.py` so other apps can reuse it without importing from `accounts`.

**Alternatives considered:**
- *Cursor pagination* — correct for large lists; overkill for a bounded admin table where "go to page 5" is the natural verb. Revisit if the user count ever grows past ~10K.
- *Building a shared `DataTable` primitive now* — premature; we don't yet know the second table's shape. Keep it inline; promote on the second consumer.
- *Putting the URL at `/api/v1/admin/users/`* — telegraphs staff-only but adds a fake resource segment. The 403 already makes the gate clear.
- *Spawning a separate `users` Django app* — would just import the `User` model from `accounts`. Two URL modules in one app is simpler.

**Revisit when:** A second list-style page ships (promote `DataTable` to `shared/ui`), the user count starts approaching the offset-pagination ceiling (~10K rows), or a tenant filter is needed once `Account` lands.

---

## 2026-04-25 — Users detail page

**Status:** accepted

**Context:** First detail surface on a resource. Click an email in the `/users` table → land on a read-only profile page. Validates the layered selectors/views pattern on a single resource and the `<dl>` definition-list semantics for label/value pairs.

**Decision:**
- **Detail serializer is richer than the list serializer.** `UserDetailSerializer` adds `is_superuser` and `updated_at` on top of `UserListItemSerializer`. The list endpoint stays slim (small over the wire); the detail endpoint returns the full picture without column constraints.
- **URL pattern uses `<uuid:id>`** at the Django routing layer (`/api/v1/users/<uuid:id>/`). Garbage ids are rejected with a routing-level 404 before the view runs.
- **Soft-deleted users → 404.** The default manager already filters `deleted_at IS NOT NULL`; the detail view doesn't override it. Deleted user looks identical to "never existed" — privacy-leaning default. Distinct "this user has been removed" state is a future call when admin recovery flows ship.
- **Server-side fetch returns a discriminated union** `{ kind: "ok"|"forbidden"|"not_found" }` so the page can branch cleanly without try/catch — same shape as the list page's forbidden branch, plus `not_found`.
- **Email cell becomes a `<Link>`** in the existing `UsersList` table. Per `data-display.md` "a clear linked column (usually first)".
- **`UserDetailCard`** uses `<dl>` + `<dt>` + `<dd>` for label/value pairs (the right semantic per `semantic-html.md`). Inline in `features/users/components/UserDetailCard/`. **Not** promoted to a `shared/ui/DefinitionList` primitive yet — same "promote on second consumer" rule as the table.

**Consequences:**
- Two separate serializers for the same model is intentional; renaming or merging them would force the list to ship more bytes than it needs.
- `tenant_id` shows on the detail page even though it's still nullable today. When the `Account` model lands, the field becomes a link to the tenant.

**Alternatives considered:**
- *One unified `UserSerializer`* — simpler but ships `is_superuser` + `updated_at` to the list view that doesn't display them. Rejected.
- *Distinct "removed" state for soft-deleted users* — useful for staff investigating a complaint, but not yet justified. Will revisit if admin recovery / restoration flows ship.
- *Modal detail instead of a route* — page is shareable + bookmarkable + browser-back-navigable; that's worth the URL.

**Revisit when:** A second `<dl>`-style detail page ships (promote `DefinitionList` to `shared/ui`), per-user MFA / sessions / audit panels need to render on this page, or admin "restore deleted user" flows enter scope.

---

## 2026-04-25 — Tenancy: Account model + sign-up auto-create + tenant-scoped queries

**Status:** accepted

**Context:** The biggest architectural slice yet. Picks up the long-deferred multi-tenancy decision recorded in the bootstrap (shared schema with `tenant_id`) and finally puts an `Account` model behind the column. Existing users get one Account each via a backfill; from this PR on, sign-up is one transaction that creates both.

**Decision:**
- **`Account` model** in `apps/accounts/models/account.py` — UUID v7 PK, `name`, `slug`, audit cols, soft-delete cols. **No explicit `owner` FK** in this PR; with one-User-per-Account today, the owner is implicit (the single user whose `tenant` FK points at this account). When invite / membership flows ship, an explicit owner field lands alongside the membership table.
- **One-to-many User → Account, modelled as one-to-one in practice.** `User.tenant = ForeignKey(Account, on_delete=PROTECT, related_name="users", db_column="tenant_id")` — column stays `tenant_id`, Python attribute is now `tenant`. This is the same shape as a true 1:N relationship; we just only ever create one user per account in this PR. Membership becomes a real 1:N when invites ship.
- **Three migrations to flip `User.tenant_id` to `NOT NULL` safely**:
  - `accounts.0003_account` — schema only: `CreateModel(Account)` + `set_accounts_updated_at` trigger. Reverses cleanly.
  - `accounts.0004_backfill_user_tenants` — data only: `RunPython` creates one `Account` per existing `User` (name = `<email-local>'s account`, slug = `<email-local>` with collision suffix) and sets `tenant_id`. Reverses by clearing `tenant_id` and dropping every Account.
  - `accounts.0005_user_tenant_fk_not_null` — schema: `SeparateDatabaseAndState`. The state op renames the field (`tenant_id` → `tenant`) and changes its type to ForeignKey. The DB op is a `RunSQL` that adds `NOT NULL` and `FOREIGN KEY ... DEFERRABLE INITIALLY DEFERRED`. The column name stays `tenant_id` end-to-end.
- **Sign-up auto-creates the tenant.** `services/sign_up.py` wraps both inserts in a single transaction. Slug derived from the email's local part (`re.sub(r"[^a-z0-9]+", "-", local).strip("-")`); collisions get `-2`, `-3`, … suffixed. Invite-only flows are deferred.
- **Tenant resolution = application-layer filtering.** `list_users` and `get_user_by_id` now require `tenant_id` and add `.filter(tenant_id=...)`. **No Postgres RLS in this PR.** Defense-in-depth via RLS is a follow-up — adding middleware that calls `set_config('app.current_tenant', …)` plus per-table policies plus error handling for unset tenant is its own PR-sized concern. Documented in the May-9 retired routine context.
- **`/users` and `/users/<id>` are now tenant-scoped.** Backwards-incompatible behavior change vs. the previous PR — staff in tenant A no longer sees users in tenant B. Cross-tenant detail lookups return **404** (privacy default, matches the soft-deleted-user posture).
- **`UserSerializer`** (used by `/me`, `/sign-in`, `/sign-up`) gains nested `tenant: { id, name, slug } | null` instead of `tenant_id`. **`UserDetailSerializer`** also nests tenant. **`UserListItemSerializer`** keeps the plain `tenant_id` UUID — list rows are within the staff user's own tenant, the name would be redundant on every row. The frontend `User` type updates to match.
- **New `GET /api/v1/account/`** endpoint — returns the signed-in user's tenant via `AccountSerializer` (id, name, slug, computed `owner_email`, created_at). New URL module `apps/accounts/api/account_urls.py`.
- **New `/settings/account`** page — Server Component, renders `AccountCard` (semantic `<dl>`/`<dt>`/`<dd>`). Linked from the dashboard Account widget for all signed-in users.
- **Dashboard placeholder gains a small uppercase tenant line** above the "Dashboard" h1, derived from `me.tenant.name`.
- **Factory cascade.** `UserFactory` now defaults to `tenant = factory.SubFactory(AccountFactory)`. Tests creating multiple users in one tenant explicitly pass `tenant=existing_account`. Tests for selectors / views that previously created N users in one global namespace got the explicit shared-tenant treatment.

**Consequences:**
- The dev DB needs a wipe (`docker compose down -v`) before this PR runs cleanly on existing local data — the data migration backfills, and a stale state can break things. Same caveat as the bootstrap's `AUTH_USER_MODEL` swap.
- Migration round-trip (forward + reverse) verified on a fresh DB.
- `tenant_id` on `User` is the canonical column; the FK column matches via `db_column`. Code reads / writes use `user.tenant` (the Account instance) and `user.tenant_id` (the UUID) interchangeably per Django's FK conventions.
- The May-9 scheduled remote agent (`trig_01UiMD8Tw4aRPsVckaiQciXY`) is now obsolete — it was queued to do this exact migration. Disabled via `RemoteTrigger` after this PR merges.

**Alternatives considered:**
- *DB-per-tenant.* Strong isolation but heavy ops overhead (per-tenant migrations, backups, connection pools). Originally requested in the bootstrap but switched to shared-schema before any code shipped.
- *Postgres RLS now.* Defense-in-depth is the right long-term move, but adds middleware + policies + error handling — its own PR. Application-layer filtering is sufficient for the threat model today.
- *Explicit `owner` FK on `Account` from day one.* Avoided to dodge the chicken-and-egg of `User.tenant` requiring an Account that requires an `owner` User. With the implicit-owner approach via the reverse relation, the create order is unambiguous. Add explicit ownership when membership ships.
- *`/api/v1/me/tenant/` instead of `/api/v1/account/`.* Either works; the resource-style URL aligns with `api-conventions.md`'s "plural lower-snake-case noun" guidance better than nesting under `/me`.
- *Squashed single migration.* Three steps make the intent obvious and let `migrate accounts 0003` (schema only) be a useful state if anyone wants to inspect mid-flight.

**Revisit when:** Invite / membership flows ship (replace auto-create + add explicit `owner`), Postgres RLS enters scope (lift filtering from application to DB), per-tenant subdomains or path prefixes are needed, a "tenant admin" role distinct from `is_superuser` is introduced, or the user count per tenant grows large enough that explicit `select_related("tenant")` becomes load-bearing.

---

## 2026-04-25 — Users-list search + status filter

**Status:** accepted

**Context:** Extension of the `/users` admin list. Staff need to find a specific user by email and slice the table by activity / role state without scrolling. Filter state must be shareable / bookmarkable.

**Decision:**
- **Filter contract.** `GET /api/v1/users/?q=<str>&status=<active|inactive|staff>`. Both optional, both compose with AND. `q` is case-insensitive substring match against `email` (`email__icontains`), trimmed and capped to 200 chars. `status` is a server-side enum (`UserStatus` StrEnum); unknown values are silently dropped to `None` rather than 400'd — keeps URL-shared links resilient and matches the lenient-on-input posture of the rest of the API.
- **Status semantics, single dropdown.** `active = is_active=True`, `inactive = is_active=False`, `staff = is_staff=True`. Categories overlap (a staff user is also active) but the dropdown picks one at a time; combinatorial multi-select is deferred until a second consumer asks. Keeps the URL flat (one param, one value) and avoids the "is_active=true&is_active=false" two-checkbox problem.
- **No trigram index, no `pg_trgm`.** Plain `ILIKE` is fine for the bounded admin-list shape (tenant-scoped, sub-10k rows). Adding `pg_trgm` + a GIN index has migration + extension cost without a hot-path justification yet. Revisit if a tenant's user count starts giving slow queries.
- **No `q` debounce.** The filter form uses an explicit "Apply" submit (or Enter); the status select submits on `change`. Debouncing every keystroke would create URL-history noise (every step of typing pushes a route) and a filter chip flicker. Submit-on-intent is calmer and lets the back button do the obvious thing.
- **URL is the single source of truth.** `UsersListFilters` is a leaf client component using `useRouter()` + `usePathname()` to push the next URL on submit / change. The page is a Server Component reading `searchParams.{q,status}`. No client-side filter state lives outside the URL.
- **Pagination preserves filters.** `UsersListPagination` accepts a `filters` prop and merges `q` / `status` into `?page=N&q=…&status=…`. **Filter changes drop `page`** — the URL is rebuilt from scratch on every filter submit, so the user lands on page 1 of the new result set. Standard "filter mutation resets pagination" UX.
- **Two empty states.** `UsersListEmpty` ("No users yet") stays for the unfiltered zero case; new sibling `UsersListNoMatches` renders when `isFiltered && rows.length === 0`. The no-matches state links to `/users` (clean URL) as the "Clear filters" action — the filter bar's "Clear all" button does the same thing client-side.
- **Filter chips render below the form.** Each active filter is an `inline-flex` chip with an X-button. Per-chip clear preserves the other filter; "Clear all" wipes both. Each chip's clear button has a specific `aria-label` (`"Clear search filter alice"`, `"Clear status filter Staff"`) so screen readers announce *which* filter is being removed.
- **Backend doesn't 400 on unknown `status`.** Same posture as ignoring an out-of-range `page` — clamp / drop and continue. The selector + view both handle this; the test suite explicitly covers `status=garbage` returning the unfiltered total.

**Consequences:**
- The frontend `User` type (`@/features/users`) gains a `UserStatus` union and a `UsersListFilters` interface; the public barrel re-exports `UsersListFiltersValue` to dodge a name clash with the React component.
- `list_users` and `listUsersServer` now both take optional `q` + `status` kwargs; existing call sites that don't pass them continue to work unchanged.
- The "Apply" button is a real submit `<button>` so Enter inside the search field also triggers it — no synthetic Enter handler.
- The form is `role="search"` with an aria-labelled section heading; the chips region uses readable labels rather than `aria-live` (filter changes are direct page navigations, not live updates, so a region announcement would be redundant with the URL change).

**Alternatives considered:**
- *Multi-value status (`?status=active,staff`)* — flexible, but the UX (multi-select dropdown / checkbox group) carries weight that one ask doesn't justify yet. Single-value covers the 90% admin task.
- *Debounced live search* — feels modern but creates URL-history pollution and double-fetches on most keystrokes. Submit-on-Enter has no downside for an admin list and keeps the back button sane.
- *`q` matching `email + first_name + last_name`* — fields don't exist on the model yet; revisit when profile fields land.
- *Search by UUID id* — admin paste-a-uuid would be handy, but `id ILIKE` doesn't work on UUIDs and adding a separate field path complicates the contract. Punt until asked.
- *Returning 400 on unknown `status`* — stricter, but a stale shared link with a renamed value would 400 unhelpfully. Lenient drop matches the rest of the API.

**Revisit when:** A second list-style page ships (promote the filter bar to a `shared/ui` `FilterBar` primitive at the same time as `DataTable`), `pg_trgm` becomes worth the migration cost, multi-value status is requested, or column-sort UI lands (the URL-state pattern extends naturally — `?sort=…&q=…&status=…`).

---

## 2026-04-25 — CI: GitHub Actions for lint / typecheck / tests

**Status:** accepted

**Context:** Through the first nine PRs, every merge gate has been "I ran the sweep locally and it's green." That's fine for a solo project but not durable — a hot-fix PR rebased badly, a missed file, an env-specific lockfile drift would all slip through. Wiring the local sweep into a GitHub Actions workflow turns "green locally" into a portable, reproducible signal and unblocks future branch protection.

**Decision:**
- **Single workflow file** (`.github/workflows/ci.yml`), two parallel jobs (`web` + `api`). One file is enough at this size; split when a third pipeline (deploy / release / e2e) lands.
- **Triggers:** `pull_request` (any branch) + `push` to `main` only. Feature branches get CI on PR, `main` gets a re-run after the squash-merge — the post-merge run is the one that gates `main` health.
- **Concurrency** keyed on `github.ref` with `cancel-in-progress` on **non-main only**. Pushing twice to a PR cancels the first run (saves CI minutes); pushes to `main` always finish so the merge-commit run is never truncated.
- **No matrix.** One Node version (22), one Python version (3.12), one OS (`ubuntu-24.04`). Matches the pinned versions in `docs/01_architecture/stack.md`. Cross-version testing adds noise; CI's job is "do this exact stack still work", not compatibility scouting.
- **No path-filtering.** Every PR runs every check. Bootstrap-era simplicity. When a typical run takes long enough to feel painful (>5 min wall clock), we'll add `paths:` filters to skip the api job on docs-only PRs etc. — but we're far from that.
- **Permissions = `contents: read` at the workflow level.** Least-privilege; jobs that need more (e.g. PR-comment bots, deploy actions) elevate inside the job. We have none today.
- **Action version pinning at the major** for actions that publish moving major tags (`actions/checkout@v5`, `actions/setup-node@v5`); pinned to a specific version (`astral-sh/setup-uv@v8.1.0`) for actions that don't. setup-uv stopped publishing `@v8` / `@v8.0` moving tags in v8.0.0 as a supply-chain hardening posture (post-tj-actions). SHA-pinning across the board is the next step when the project has external contributors or compliance constraints; for now, this mixed posture keeps Dependabot updates lightweight where possible.
- **All actions on Node 24.** `actions/checkout`, `actions/setup-node`, and `astral-sh/setup-uv` were on Node 20 in v4 — bumped on the second post-merge run when GitHub surfaced the Node 20 deprecation warning. The forced-Node-24 deadline is June 2 2026; better to bump now than chase the deadline.
- **Postgres via service container** (`postgres:16-alpine`), not Docker Compose. GitHub Actions services start before the job's first step, expose ports on `localhost`, and have built-in healthchecks — much less ceremony than running `docker compose up` inside the job. CI gets its own DB (`keystone_ci`) so future workflow concurrency on the same runner doesn't collide.
- **`uv sync` from repo root**, not `--project apps/api`. The `pyproject.toml` workspace config picks up `apps/api`; `uv sync` resolves the whole workspace lockfile in one pass.
- **Migration step before pytest**, not just `pytest`. `pytest-django` would create + migrate its own test DB anyway, but running `manage.py migrate --noinput` against the empty `keystone_ci` DB first is a real signal — it caught the local "wipe DB before re-migrating" caveat from PR #8 and would catch a broken three-step migration tree before the test phase did.
- **`pnpm install --frozen-lockfile`** so a missed `pnpm-lock.yaml` update fails CI loudly instead of silently mutating the lockfile.
- **`postinstall` builds tokens** automatically, so the workflow doesn't need an explicit `pnpm run build:tokens` step. Same path as a fresh local clone.
- **Build job included** (`next build` under `NODE_ENV=production`). Type errors and Server Component / client-bundle boundary violations sometimes only surface at build time; `tsc --noEmit` doesn't catch the latter.
- **`timeout-minutes: 10`** on each job. Caps a hung step at 10 min instead of the default 6h. Generous compared to current run time (~3 min web, ~4 min api locally) but not absurd; tighten if a job ever idles near it.

**Consequences:**
- Branch protection (require `web` + `api` checks) is a one-time GitHub repo-settings action, deferred — visible in this PR's checks, but not enforced until configured.
- Stylelint and SQLFluff aren't wired into the project yet, so the workflow doesn't run them. The PR template lists them aspirationally; the CI workflow follows actual tooling, not the template.
- The GitHub-hosted `ubuntu-24.04` runner has Node, Python, and Docker pre-installed. We still install them via the official setup actions to control the version pin — slightly redundant on this runner, but the workflow stays portable to runners without pre-warmed toolchains.
- `uv` cache is enabled via `setup-uv@v4`; first CI run on a new branch is a cold cache (~30s install), subsequent runs warm.
- Concurrency = `cancel-in-progress: true` on PRs means a chatty rebase loop won't queue 5 runs deep. Worth it.

**Alternatives considered:**
- *Multiple workflow files (`ci-web.yml`, `ci-api.yml`)* — would let GitHub treat them as independent required checks for branch protection. Same effect achieved with two jobs in one file (each job is selectable as a required check). Less file sprawl.
- *Run `pytest` with `--no-migrations`* — faster, but loses the "do migrations apply cleanly on a fresh DB" check that the explicit `migrate` step provides. The cost (~1s) isn't worth optimising.
- *Use Docker Compose inside CI* (`docker compose -f infra/docker/compose.dev.yml up -d`) — symmetric with local dev but slower start and less idiomatic; service containers are GitHub Actions' first-class primitive.
- *Build tokens in an explicit step* — redundant given `postinstall`. If the postinstall step ever stops being mandatory, add an explicit `pnpm run build:tokens` step and document the change.
- *Pin actions to commit SHAs* — strictly safer (no surprise behavior change from a re-tagged `@v4`). Defer until external contributors or compliance enter scope; meanwhile the major-tag posture matches every other repo of this size.
- *Add CodeQL / dependency-review* — separate workflow file, separate concern. When security tooling lands, it gets its own file.

**Revisit when:** Branch protection is enforced (turn each job into a required check), a third pipeline (deploy, release, e2e) is needed (split workflows), CI run time grows past ~5 min wall clock (add path filters and / or cache more aggressively), an external contributor opens a PR (re-pin actions to SHAs and consider `pull_request_target` policy), or stylelint / SQLFluff get wired into the project (add steps).

---

## 2026-04-25 — Email verification — soft-block + grandfather-existing

**Status:** accepted

**Context:** Sign-up creates accounts with no proof the address belongs to the human at the keyboard. Production-readiness gap: a signed-up user could be a typo / impersonation. Need a verification flow that pushes users to confirm their email without locking the bootstrap path against a delivery failure.

**Decision:**
- **Soft-block, not hard-block.** Unverified users sign in and see a banner ("Verify your email") on every dashboard route. Sensitive actions (change-password, MFA disable, future tenant rename) are **not** gated on verification *yet* — that posture lands in a follow-up if/when the gap matters. Reason: hard-blocking sign-in on bootstrap day-one is fragile (mail deliverability) and the platform doesn't have many sensitive actions worth gating today.
- **Schema = one nullable timestamp.** `User.email_verified_at: timestamptz null`. No separate `EmailVerificationToken` table — Django's `default_token_generator`-style HMAC tokens carry their own validity envelope. No index on `email_verified_at` either; the only filter we run on it (`me` payload null check) is per-row, not a scan.
- **Two-migration shape per `sql.md`.** `0006` adds the column. `0007` is a `RunPython` data migration that backfills `email_verified_at = created_at` for every pre-existing row — pre-existing accounts were created by an admin / sign-up before this PR existed, treating them as unverified would mean a banner-flood on day-one with no value behind it. From this PR on, only fresh sign-ups land with `email_verified_at IS NULL`.
- **Custom token generator.** `EmailVerificationTokenGenerator` subclasses `PasswordResetTokenGenerator` with two changes:
  - `_make_hash_value` excludes `user.password` and `user.last_login`, includes `user.email_verified_at`. Reason: a user who signs up → signs in (updating `last_login`) → clicks the email link must not have the link fail. The verification flow's "self-invalidating" property is via `email_verified_at` flipping non-null on success, not via login state.
  - `check_token` reads `EMAIL_VERIFICATION_TIMEOUT` (24 h) instead of `PASSWORD_RESET_TIMEOUT` (1 h). Verification email tolerates more delivery delay than reset.
  - Different `key_salt` so tokens from one flow can't be replayed against the other (covered in tests).
- **24h TTL.** Long enough for typical deliverability latency + the user actually opening their inbox; short enough that a stolen link doesn't outlive the user noticing. Reset tokens stay at 1h (NIST recommendation for high-stakes flows).
- **Sign-up wiring uses `transaction.on_commit`.** The verification email fires *after* the transaction commits, so a rollback never leaks an email referencing a user who doesn't actually exist.
- **Idempotent verify endpoint.** Already-verified user double-clicks the link → 204, no re-stamp on `email_verified_at`. Stops a stale email from rewriting the verification timestamp.
- **`POST /email-verification/request/` is authenticated.** Re-sending the link requires a session — anonymous "send a link to this email" would be an account-enumeration vector. Throttled by the `auth` scope (5/min/IP).
- **`POST /email-verification/confirm/` is public.** No session needed — the user clicks from email and may or may not be signed in. `auth` throttle scope still caps abuse.
- **`/verify-email` is a top-level route**, not under `(auth)/` or `(dashboard)/`. Reason: works for both signed-in and signed-out users (a user might sign in first, then click the link from email). The `(auth)/` layout redirects signed-in users to `/`, which would break the signed-in-and-verifying flow.
- **Server-side confirm.** The verify page calls `confirmEmailVerificationServer` from a Server Component, not a Client Component. The user clicks the link; the page renders the result on the server. No round-trip through the client bundle, no flicker, no "loading…" state for what's a single network call.
- **`UserSerializer.email_verified_at` is exposed read-only** so `/me` carries the flag. Frontend `User` type updates to match; banner condition is `me.email_verified_at === null` in the dashboard layout.
- **Banner is a Client Component** (the resend button needs an event handler), rendered conditionally by the **Server Component** dashboard layout. State machine inside the banner: `idle → pending → sent | throttled | error`. 429 maps to a calmer "slow down" message than the generic error.

**Consequences:**
- Adds two reversible migrations. Round-trip verified (`migrate accounts 0005` then forward).
- Existing `User` factory tests had to add `email_verified_at: null` to fixture objects after the type change (caught by `tsc --noEmit`).
- Sign-up tests now use `@pytest.mark.django_db(transaction=True)` for the email-on-commit assertion since `on_commit` only fires inside a real transaction (not the wrapping rollback that pytest-django uses by default).
- Future "change email" flow (when it lands) re-uses this same machinery — issue a token to the *new* address, mark verified on click. The existing token generator's `email_verified_at` hash component handles the invalidation.
- The dashboard layout now does an extra string check on every render, not a real cost. Conditional render of the banner Client Component avoids hydrating it for verified users.

**Alternatives considered:**
- *Hard-block sign-in* — strongest posture but punishes users on bad email deliverability. Acceptable for a B2B SaaS where the admin can manually verify; not the right default for bootstrap. Add as a per-tenant setting later.
- *Custom `EmailVerificationToken` table* — gives admin "list outstanding tokens" + revoke. Adds a hot table for a feature with no admin surface today. Stateless tokens are simpler.
- *Reuse `default_token_generator`* — convenient but `last_login` in the hash means a sign-up → sign-in → click flow breaks. The custom generator is mandatory for soft-block.
- *Email-only token (no uid)* — looks cleaner in the URL but means the token has to encode the user identity, doubling its length. Two-segment `?uid=&token=` matches the existing reset-password pattern and keeps the link short.
- *Existing-users get `email_verified_at = NULL`* — strictly correct from a "we never verified them" angle, but creates a banner-storm on day one with no actionable value (the existing users don't know what's happening, no email arrives). Backfill with `created_at` is the operationally-sane choice.
- *Verify-email page rendered client-side* — would let us show a fancy spinner during confirm, but the call is single and fast; server render avoids the loading flicker entirely.

**Revisit when:** Hard-blocking sign-in on unverified is wanted (per-tenant policy?), email-change flow lands (re-use the same generator + a new `email_pending` column), `/me` becomes too chatty for the banner check (move to a dedicated cheap endpoint or cache), or admin-side "verify on behalf of" tooling is needed.

---

## 2026-04-25 — Profile fields (first_name, last_name, display_name)

**Status:** accepted

**Context:** The User model has had `email` as the only display surface since auth-core. Sign-out button, dashboard "Signed in as", and the eventual invite-email subject ("Alice Anderson invited you…") all benefit from a friendlier handle. This PR adds optional name fields and a profile-edit page; nothing is required, nothing changes about sign-up.

**Decision:**
- **Two columns, AbstractUser-shape exactly.** `first_name: CharField(max_length=150, blank=True, default="")` and `last_name: CharField(max_length=150, blank=True, default="")`. Matches Django's `AbstractUser` so future code that assumes that shape (admin, third-party packages) Just Works. The 150-char ceiling is Django's; longer names get caught at the schema layer rather than in business logic.
- **Empty string default, not null.** Lets the DB default fill existing rows in a single non-blocking migration with **no separate backfill step**. Django's `CharField(blank=True)` convention is empty string; semantically the same as null for a "not set" name and avoids the constant `if name is None else name` dance throughout the code.
- **`display_name` is a Python property, not a column.** Computed as `f"{first_name} {last_name}".strip() or email_local_part or email`. Reasoning: (1) two sources of truth for the same logical value invites drift; (2) users rarely want a separate "display name" — `Alice Anderson` is what they want to be called. If a per-user override becomes a real ask (e.g. preferred name distinct from legal name), add a third nullable column then; until then, the property is enough.
- **Display fallback chain.** Full name → email local part → email. The email-local-part fallback ("alice" instead of "alice@acme.com") is friendlier than the raw email and works for users who haven't set names yet — including all pre-existing accounts. Banner-storm avoided because no one is forced to do anything.
- **`PATCH /api/v1/auth/me/` on the existing `MeView`.** Not a new endpoint at `/api/v1/auth/profile/`. The `me` resource is the user's own resource; partial-update via PATCH is the RESTful primitive. Keeps URL surface tight.
- **`MeUpdateSerializer` whitelists writable fields.** Only `first_name` and `last_name` are accepted; unknown keys are silently dropped (DRF default). A user can't sneak `is_staff: true` past the serializer because the serializer doesn't even define those fields. Test explicitly covers `is_staff` and `email` being ignored.
- **`update_profile` service, not in-view persistence.** The view validates → calls service → re-serializes. Service does the trim + length cap + `update_fields=["first_name", "last_name", "updated_at"]` save. Same layered pattern as the rest of the app.
- **`UserSerializer` exposes `display_name` as read-only.** Frontend never recomputes; the `User` type carries `display_name` everywhere and components use it directly. Single source of truth lives in Python.
- **`ProfileForm` is a Client Component** (RHF + Zod, same posture as `ChangePasswordForm`). The page that renders it is a Server Component that fetches `me` and passes `initial` as a prop — no client-side fetch on mount, no flicker, no auth round-trip on the client.
- **Form button disabled until dirty.** Stops the no-op submit. Combined with `router.refresh()` after a successful save, the UI re-fetches `me` on the page that just saved (the layout's "Signed in as" line updates if you go back to the dashboard).
- **No sign-up form change.** Sign-up stays email + password. Profile is filled in (or not) after the fact. Reasoning: one-step sign-up is the friendliest possible flow, and required fields can always be added later as a per-tenant policy.

**Consequences:**
- Single migration (`0008_user_profile_fields`). Reversible — both `RemoveField`s. No data migration needed.
- Existing User type fixtures in tests need `first_name`, `last_name`, `display_name` added (caught immediately by `tsc --noEmit`).
- `MeView.patch` is the first non-GET method on `/me/`. Future expansions (avatar URL, notification settings) extend `MeUpdateSerializer` without splitting the endpoint.
- Dashboard "Signed in as" line now shows display name with email parenthesised when they differ (e.g. "Signed in as **Alice Anderson** (alice@acme.com)"). When they match (no profile fields, email-local-part fallback equals email), only the display name shows.
- `/settings/profile` joins `/settings/account` under the same path prefix; a `/settings/` index page becomes obvious next.
- The users list still shows email-as-primary. Updating that to show `display_name` is a deliberate punt — keeps this PR tight, and the list churn isn't load-bearing for the invites flow.

**Alternatives considered:**
- *Single `name` field instead of first / last* — culturally awkward (mononyms, multi-part surnames, name-order conventions vary). Two fields plus a `display_name` derivation handles all these cleanly and matches AbstractUser convention.
- *Required at sign-up* — biggest UX cost of any sign-up addition; deferred until invites land and we know what minimum metadata an invitee needs to be useful.
- *Storing `display_name` as a column* — duplicate state, drift risk. The property is one line and runs free.
- *Dedicated `/profile/` endpoint* — the user-the-resource is `/me/`. Adding a parallel `/profile/` route splits one resource across two URLs. Not worth the API surface bloat.
- *Updating users-list / users-detail in this PR* — extra churn on a feature that already covers the user-visible "I want to set my name" flow. Cleaner as a follow-up if it matters.

**Revisit when:** Invites ship (probably bundles this with display in invite-emails), per-tenant required-fields policy enters scope (move name validation out of MaxLength-only), preferred-name distinct from legal-name is requested (add a third column), or a `/settings/` index page lands and the profile/account/security split needs a top-level overview.

---

<!-- Add new decisions above this line. Keep most recent at the top. -->
