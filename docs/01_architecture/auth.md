# Authentication & Authorization

## Default: Django sessions, server-driven

For dashboards (the primary use case for this template), the default is:
- **Django session auth** for first-party web app.
- **DRF SessionAuthentication + CSRF** for API calls from the same origin.
- **Token auth** (DRF) only for non-browser API clients (CLI, mobile).

This keeps the security model simple, leverages Django's mature session handling, and avoids the JWT footguns (revocation, sliding expiry, storage).

## When to deviate

| Need | Approach | Why |
|---|---|---|
| Mobile app | Issue access + refresh tokens (short-lived JWTs) | Sessions don't fit native clients |
| Cross-origin SPA | Same-origin via reverse proxy, **or** OAuth2 / OIDC | Avoid third-party-cookie pitfalls |
| SSO from corporate IdP | OIDC via `mozilla-django-oidc` or Auth.js | Standard, audited |
| API to API | mTLS or signed JWTs (short-lived) | No user interaction |

Document the chosen flow in `decisions-log.md`.

## Session config

```python
SESSION_ENGINE = "django.contrib.sessions.backends.cache_db"  # Redis + DB fallback
SESSION_COOKIE_AGE = 60 * 60 * 8         # 8 hours active
SESSION_SAVE_EVERY_REQUEST = True        # rolling expiry
SESSION_COOKIE_SECURE = True             # prod only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
```

## CSRF

- **All** state-changing requests carry the CSRF token. Django middleware enforces this.
- `@csrf_exempt` is forbidden without a written reason in the view's docstring.
- Frontend reads the cookie via `getCookie('csrftoken')` and sends it as `X-CSRFToken`.

## Roles & permissions

Three layers, in order:

1. **Authentication** — is this user logged in? (`request.user.is_authenticated`)
2. **Authorization (role)** — does this user have the role? (`is_staff`, custom roles via `django-guardian` or `django-rules`)
3. **Authorization (object)** — does this user own / belong-to this object?

Object-level checks are mandatory for any tenant-scoped data. Example:

```python
def get_queryset(self) -> QuerySet[Project]:
    return Project.objects.filter(account=self.request.user.account)
```

Never trust client-provided `account_id` / `tenant_id`.

## Password policy

- Argon2 (Django default since 4.x).
- Minimum length 12; common-password blacklist (Django built-in `CommonPasswordValidator`).
- No rotation requirement (NIST SP 800-63B); rotate only on suspected compromise.

## MFA

- TOTP (RFC 6238) via `django-otp` for staff and high-privilege roles.
- WebAuthn for end users where threat model justifies the UX cost.
- Recovery codes generated at enrolment, stored hashed.

## Account lockout / brute force

- 5 failed attempts within 15 minutes → 15-minute lockout (per IP + per username).
- Use `django-axes` or built equivalent.
- Login failures logged with structured fields.

## Logout

- Server-side session destruction.
- Client clears local storage + IndexedDB on logout.
- "Log out everywhere" option clears all sessions for the user.

## Audit trail

- Authentication events (login success / failure, logout, MFA enrolment, password change, role grant) write to an `audit_event` table.
- Retention: at least 90 days; longer if compliance demands.

## API tokens

- Personal tokens are rotatable, revocable, and scoped (read-only / read-write / admin).
- Store hashed (SHA-256), never plaintext.
- Display the plaintext token exactly once at creation.
- Short-lived JWTs only — never issue 30-day JWTs to browsers.

## Review checklist

- [ ] Session cookies `Secure` + `HttpOnly` + `SameSite=Lax`
- [ ] CSRF enforced on all write endpoints
- [ ] Object-level permissions on every tenant-scoped queryset
- [ ] No client-provided tenant / user IDs trusted
- [ ] MFA available (and required for staff)
- [ ] Failed-login lockout active
- [ ] Auth events written to audit log
- [ ] Tokens hashed at rest; rotation flow documented
