# Testing

## The pyramid

```
        /\
       /e2e\        ← few; slow; cover the user-visible critical paths
      /------\
     / integ  \     ← some; cover service + DB; cover route + middleware
    /----------\
   /   unit    \    ← many; cover branching logic, edge cases, pure functions
  /--------------\
```

Aim for the bulk of confidence at the **integration** tier. Unit tests catch regressions in branchy logic; e2e tests prove the system fits together.

## Stack

| Tier | Frontend | Backend |
|---|---|---|
| Unit | Vitest | pytest |
| Integration | Vitest + msw (mocked network); Playwright component tests | pytest + pytest-django (real Postgres) |
| E2E | Playwright | (drive through frontend e2e) |
| Visual | Playwright trace viewer / screenshot diff (optional) | — |
| A11y | `@axe-core/playwright` | — |

## Coverage targets

- Branch coverage ≥ **80%** in CI for both apps.
- Coverage is a floor, not a goal. **Don't write tests to chase the number.**
- Files that are pure config or generated code are excluded; document the exclusion.

## What to test

- **Behaviour, not implementation.** Tests describe *what* the code does, not *how*.
- **Public surfaces only.** Don't test private helpers via reflection — test through the public API that uses them.
- **Edge cases**: empty input, single item, many items, unicode, very large, negative, exactly-the-limit, just-over-the-limit.
- **Failure paths**: invalid input, downstream error, auth failure, race condition.
- **Time / non-determinism**: freeze time (`freezegun` / `vi.useFakeTimers()`), seed RNGs.

## What NOT to test

- ORM internals — Django / Prisma test their own ORM.
- React internals — `useState` works.
- Trivial getters / setters that just forward.
- Snapshot tests of large DOM trees — they fail on every accidental change without telling you why.

## Test naming

Describe the behaviour, not the function:

```
test_create_project_emits_event_when_succeeds
test_create_project_raises_quota_exceeded_when_at_limit
test_button_calls_handler_when_clicked
test_button_does_not_call_handler_when_disabled
```

## Frontend (Vitest + Playwright)

- Component tests use **Testing Library**. Query by accessible role / label, not by class name or test id.
- `screen.getByRole('button', { name: 'Create' })` — that's the assertion that the button is reachable to a screen reader **and** the test in one line.
- Use `userEvent` (not `fireEvent`) for input simulation — it mirrors real user behaviour.
- `data-testid` is a last resort for elements with no semantic identity.

## Backend (pytest + pytest-django)

- Use `pytest` style functions (`def test_foo(...)`) not `unittest.TestCase`.
- Database fixture: `pytest-django`'s `db` / `transactional_db` markers. **Hit a real Postgres in CI** — not SQLite.
- Factories: `factory_boy`. Never raw `Model.objects.create(...)` in test bodies.
- One behavior per test. Multi-assert tests hide what's actually failing.
- Parametrize variants instead of duplicating tests.

```python
@pytest.mark.parametrize(
    'status, expected_visible',
    [
        ('active', True),
        ('archived', False),
        ('deleted', False),
    ],
)
def test_project_visibility_by_status(status, expected_visible):
    project = ProjectFactory(status=status)
    assert (project in Project.objects.visible()) is expected_visible
```

## E2E (Playwright)

- One spec per user-visible flow ("create project", "invite teammate", "export report").
- Run against a seeded test database.
- Build a small set of fixtures (`as_admin`, `as_member`) for auth.
- Use `expect(...).toBeVisible()` — it auto-retries; explicit `waitFor` calls are usually a smell.
- Trace + video on failure (Playwright config).

## Mocking

- Mock at the **boundary**, not in the middle.
- Frontend: `msw` for HTTP — it intercepts at the network layer; tests run against the real fetch.
- Backend: don't mock the ORM. Use a real test DB. Mock only third-party HTTP / SDK calls.

## Performance

- Tests run in parallel (Vitest, pytest-xdist).
- Slow tests (> 1 s) marked `@pytest.mark.slow` / `test.slow` and excluded from `pre-commit` runs.

## Anti-patterns

| Don't | Do |
|---|---|
| Test the implementation (spy on internal call) | Test the observable behaviour |
| Snapshot a 500-line DOM tree | Specific assertions |
| Mock the database / ORM | Use a real test DB |
| One test asserting 10 things | One behaviour per test |
| Sleep + retry in a test | Use auto-retrying assertions (Playwright, `waitFor`) |
| `data-testid="login-button"` on a real `<button>Log in</button>` | Query by role + name |

## Review checklist

- [ ] New behaviour has tests
- [ ] Tests query by accessible role/name where possible
- [ ] No mocked ORM
- [ ] Branch coverage ≥ 80% on changed files
- [ ] No flaky tests merged (CI green twice in a row)
- [ ] E2e for any critical user-visible path added or changed
- [ ] axe-core checks passed for any new UI page
