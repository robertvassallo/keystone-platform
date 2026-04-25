# Pre-Merge Review Checklist

The single canonical checklist used by the PR template, the `/new-feature` command, and human reviewers. If a check doesn't apply, mark it N/A — don't silently skip.

## 1. Correctness

- [ ] Behaviour matches the intent in the PR description
- [ ] Edge cases covered (empty / one / many / max / over-max / unicode / negative)
- [ ] Failure modes handled (network error, downstream timeout, auth failure)
- [ ] No silently swallowed exceptions
- [ ] No magic numbers or strings without a named constant

## 2. Code quality

- [ ] Names accurately describe the thing or action
- [ ] Functions small (≤ ~25 lines target, ~60 hard cap)
- [ ] No code that's commented out
- [ ] No dead code (unreferenced exports, unreachable branches)
- [ ] No `console.log` / `print` debug statements
- [ ] No `TODO` without a linked issue / ticket

## 3. Types

- [ ] TypeScript: no `any`; no unjustified `as`; no `// @ts-ignore`
- [ ] Python: every function fully typed; mypy strict passes
- [ ] Shared types live in `packages/types` (or imported from there)

## 4. Tests

- [ ] New behaviour has tests
- [ ] Tests describe behaviour (their names tell you what's being asserted)
- [ ] Tests query by accessible role/name (frontend) where possible
- [ ] No mocked ORM / database
- [ ] Branch coverage on changed files ≥ 80%
- [ ] CI green twice in a row (no flakes)

## 5. Linters / formatters

- [ ] `pnpm lint` clean
- [ ] `ruff check .` clean
- [ ] `stylelint` clean
- [ ] `sqlfluff lint` clean (if SQL changed)
- [ ] `prettier` / `ruff format` applied (auto via PostToolUse hook)

## 6. UI changes

- [ ] Semantic HTML — `@semantic-html-auditor` run, PASS
- [ ] Accessibility — `@a11y-reviewer` run, PASS or PASS WITH NOTES
- [ ] Loading / empty / filtered-empty / error states designed and implemented
- [ ] Responsive at xs / md / lg / xl breakpoints
- [ ] Reduced motion respected
- [ ] Visual review against the design (or a written exception)

## 7. Backend changes

- [ ] `@python-reviewer` run, PASS
- [ ] Views thin; business logic in services
- [ ] ORM access via managers / selectors
- [ ] Permissions enforced at the view boundary
- [ ] Multi-tenant queries scoped to the user's tenant

## 8. DB changes

- [ ] `@sql-reviewer` run, PASS
- [ ] Migration reversible (tested both directions)
- [ ] No `SELECT *`; no N+1
- [ ] Indexes for `WHERE` / `ORDER BY` / `JOIN` columns present
- [ ] Lock-aware: `CREATE INDEX CONCURRENTLY`, no blocking `ALTER TABLE` on hot tables
- [ ] Money via `numeric`; time via `timestamptz`

## 9. Security

- [ ] No secrets in the diff
- [ ] No new `csrf_exempt` without a written reason
- [ ] User input never interpolated into SQL strings
- [ ] No new third-party origins added to CSP without review
- [ ] PII not logged

## 10. Performance

- [ ] No N+1 introduced (verify via query count or trace)
- [ ] Lists paginated
- [ ] Large payloads streamed, not buffered
- [ ] Bundle size impact noted (web) — > +20 KB gzipped requires justification

## 11. Documentation

- [ ] Standards docs updated if a new pattern was introduced
- [ ] `docs/04_ai/decisions-log.md` entry added for non-obvious decisions
- [ ] Public API changes documented (OpenAPI schema regenerated if applicable)
- [ ] Inline comments added only where the *why* is non-obvious

## 12. Git hygiene

- [ ] Branch name follows convention
- [ ] Commits are atomic and conventional
- [ ] PR ≤ 400 lines (or split agreed in advance)
- [ ] Merged via squash; no merge commits on `main`

## 13. Risk & rollback

- [ ] Risk section in PR filled in
- [ ] Rollback plan stated
- [ ] Feature flag / kill switch in place if behavior is risky
- [ ] If risky and shipping, a follow-up is scheduled to verify health
