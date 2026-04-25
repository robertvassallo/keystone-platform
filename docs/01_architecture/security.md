# Security Baseline

Minimum bar for any project built from this template. Document deviations in `decisions-log.md`.

## Threat model snapshot

Assume:
- Untrusted clients (browsers, mobile, scripts) reach the API.
- Authenticated users may attempt to act outside their tenant / role.
- Dependencies may have known vulnerabilities; CI must surface them.
- Logs may be reviewed by humans — never log secrets or full PII.

## Secrets

- **Never** committed. `.env`, `.env.*` are in `.gitignore`.
- Local: `.env` per app, loaded via `python-dotenv` (api) or Next.js built-in.
- Staging / prod: secret manager (AWS Secrets Manager, GCP Secret Manager, Doppler, 1Password Connect — pick one and document).
- Rotate on suspected compromise; rotation steps documented in `infra/scripts/rotate-secrets.md`.

## Settings split (Django)

```
config/settings/
  base.py         # safe defaults; no secrets
  dev.py          # DEBUG=True, local overrides
  test.py         # in-memory cache, eager Celery
  prod.py         # DEBUG=False, hardened
```

`DJANGO_SETTINGS_MODULE` selects the file. Prod settings enforce:

```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

## OWASP top-10 baseline

| Risk | Default control |
|---|---|
| **A01 Broken access control** | Permission checked at view boundary; multi-tenant queries filtered by tenant. |
| **A02 Cryptographic failures** | TLS everywhere; secrets in manager; bcrypt / Argon2 for passwords. |
| **A03 Injection** | ORM only — no raw SQL with string interpolation; parameterized queries. |
| **A04 Insecure design** | Threat-model new features in PR description for anything touching auth / payments / PII. |
| **A05 Security misconfig** | Prod settings file enforces hardening; CI checks `DEBUG = False`. |
| **A06 Vulnerable components** | `pnpm audit` + `pip-audit` in CI; renovate for updates. |
| **A07 Identification & auth** | Django sessions (default) or JWT short-lived + refresh; MFA for staff. |
| **A08 Software & data integrity** | Lockfiles committed; CI integrity check on built artifacts. |
| **A09 Logging & monitoring** | Structured JSON logs; alerts on auth failures / 5xx spikes. |
| **A10 SSRF** | URL allow-list for any server-side fetch of user-supplied URLs. |

## CSP & headers (Next.js)

Set in `next.config.mjs` via `headers()`:

```
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-...';
                         style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;
                         connect-src 'self' https://api.example.com;
                         frame-ancestors 'none';
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## CORS

- API allows only known origins. No `*` in production.
- Credentials only when needed; configure cookies with `SameSite=Lax` / `Secure`.

## Rate limiting

- Django: `django-ratelimit` or DRF throttles on auth + write endpoints.
- Next.js: rate-limit any public route handler that calls a downstream service.
- Default: 60 req/min per IP for unauthenticated, 600 req/min per user for authenticated.

## Logging hygiene

- **Never** log: passwords, tokens, full credit card / SSN, full email body, OTP codes.
- **OK to log**: user IDs, tenant IDs, request IDs, timing, status codes, error class.
- Structured JSON log lines; correlation ID on every log.

## Dependency review

- CI runs `pnpm audit --prod` and `pip-audit` on every PR; failures block.
- Critical / high severity → fix before merge.
- Document any waived advisory with reason + expiry in `decisions-log.md`.

## Review checklist

- [ ] No secrets in repo (`gitleaks` clean)
- [ ] Prod settings enforce HTTPS + secure cookies + CSP
- [ ] All write endpoints CSRF-protected
- [ ] Multi-tenant queries filter by tenant at the query layer (not just UI)
- [ ] No raw SQL with string interpolation
- [ ] Dependency audit clean or waivers documented
- [ ] Logs reviewed for accidental PII / secret leakage
