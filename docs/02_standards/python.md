# Python (Django)

## Why semantic Python

- Type hints turn whole categories of bugs into editor-time errors.
- Layered structure (views → services → models) keeps each layer testable in isolation.
- Django defaults are good — most "best practices" are just *not* opting out.

## Style

- PEP 8 enforced by Ruff. 100-column line limit.
- Snake_case for functions / variables / modules; PascalCase for classes; UPPER_SNAKE for constants.
- f-strings only — no `%` or `.format()`.
- `pathlib.Path` over `os.path`.
- No mutable default arguments (`def f(x=[])` — never).

## Type hints

- **Every** function: parameters and return type.
- No `Any` without a documented reason.
- `list[str]`, not `List[str]` (3.9+ syntax).
- `X | None`, not `Optional[X]`.
- Generic containers fully parameterised.
- mypy strict mode mandatory.

```python
def list_active_projects(account_id: AccountId, *, limit: int = 50) -> list[Project]:
    """Return active projects for the account, newest first."""
    return list(
        Project.objects
        .filter(account_id=account_id, status=ProjectStatus.ACTIVE)
        .order_by('-created_at')[:limit]
    )
```

## Project layout (Django) — granular

One Django app per domain. Inside each app, every layer is a **package** (folder with `__init__.py`), not a single module. One concept per file. Full principle: `docs/02_standards/project-structure.md`.

```
apps/api/
├── manage.py
├── config/
│   ├── settings/{base,dev,prod,test}.py
│   ├── urls.py
│   └── asgi.py / wsgi.py
├── apps/
│   ├── accounts/
│   │   ├── models/                        # one model per file
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   └── membership.py
│   │   ├── managers/
│   │   │   ├── __init__.py
│   │   │   └── account_manager.py
│   │   ├── services/                      # one business operation per file
│   │   │   ├── __init__.py
│   │   │   ├── create_account.py
│   │   │   ├── invite_member.py
│   │   │   └── deactivate_account.py
│   │   ├── selectors/                     # one read query per file
│   │   │   ├── __init__.py
│   │   │   ├── list_active_accounts.py
│   │   │   └── get_account_summary.py
│   │   ├── api/
│   │   │   ├── views/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── account_create_view.py
│   │   │   │   └── account_list_view.py
│   │   │   ├── serializers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── account_serializer.py
│   │   │   └── urls.py
│   │   ├── events/                        # one event per file
│   │   ├── tasks/                         # one Celery task per file
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── services/
│   │       ├── selectors/
│   │       ├── api/
│   │       └── models/
│   └── projects/...
└── tests/                                  # cross-app integration tests
```

The `__init__.py` of each package re-exports the public symbols, so callers always import from the package — never from a deep path:

```python
# apps/accounts/services/__init__.py
from .create_account import create_account
from .invite_member import invite_member
from .deactivate_account import deactivate_account

__all__ = ["create_account", "invite_member", "deactivate_account"]
```

```python
# Caller — clean
from apps.accounts.services import create_account

# Caller — wrong; reaches into the package
from apps.accounts.services.create_account import create_account
```

File-size targets:
- One service / selector / view / serializer per file — typically 30–80 lines.
- One model per file — usually 50–150 lines including managers, properties, validators.
- Hard cap 300 lines on any file. Past that, split.

## Layering

- **Views** are thin. They parse input, call a service, format output.
- **Services** hold business logic. Pure functions or stateless classes. Take primitives / DTOs, return primitives / DTOs / models.
- **Selectors** hold read queries — no side effects.
- **Models** hold invariants (validators, constraints, properties). No HTTP, no I/O beyond the ORM.
- **Serializers** are the boundary. Never return raw model instances from a view.

```python
# api/views/project_create_view.py — thin
class ProjectCreateView(APIView):
    def post(self, request: Request) -> Response:
        serializer = CreateProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = create_project(
            account=request.user.account,
            **serializer.validated_data,
        )
        return Response(ProjectSerializer(project).data, status=201)

# services/create_project.py — one operation, one file
def create_project(*, account: Account, name: str, ...) -> Project:
    """Create a project, enforce per-account quota, emit event."""
    if account.projects.active().count() >= account.project_quota:
        raise QuotaExceeded
    with transaction.atomic():
        project = Project.objects.create(account=account, name=name, ...)
        emit_event('project.created', project_id=project.id)
    return project
```

## ORM rules

- Querysets returned from manager methods, not constructed inline.
- `select_related('account')` for foreign-key access; `prefetch_related('milestones')` for reverse / m2m.
- Use `.only()` / `.values()` / `.values_list()` when only a subset of columns is needed.
- Never `.update()` in a loop — use bulk operations (`bulk_update`, `bulk_create`).
- Never `Model.objects.all()` returned to a view without filter / pagination.
- See `sql.md` for query-level rules.

## Settings

- Split: `base`, `dev`, `prod`, `test`. Never one giant `settings.py`.
- Secrets via environment, parsed with `django-environ` or `os.environ`.
- Safe defaults in `base`; prod hardens; test uses fast in-memory backends.

## Errors

- Custom domain exceptions (`QuotaExceeded`, `NotEntitled`) — never bare `Exception`.
- Catch the narrowest exception. Don't silently swallow.
- Convert domain exceptions to HTTP status codes at the view boundary, not in services.

## Logging

- `structlog` (or `logging` configured to JSON in prod).
- Include: request_id, user_id, tenant_id, event_name.
- Never log: secrets, full PII, OTP codes.

## Tests

- `pytest` + `pytest-django`, **not** `django.test.TestCase` (unless transactional behavior is needed).
- `factory_boy` for object creation, never raw `Model.objects.create` in test bodies.
- One assertion per test where possible — name the test after what's being asserted.
- Coverage floor 80% (configured in `pyproject.toml`).
- Test file mirrors source: `apps/projects/services/billing.py` ↔ `apps/projects/tests/services/test_billing.py`.

## Anti-patterns

| Don't | Do |
|---|---|
| `def f(x):` | `def f(x: int) -> int:` |
| `from typing import List, Optional` | `list[X]`, `X \| None` |
| Business logic in `views.py` | Service function |
| `Model.objects.filter(...)` in a view | Manager / selector method |
| `try: ... except Exception:` | Catch the narrowest exception |
| Mutable default arg | `None` + `if x is None: x = []` inside |
| Sliding `Optional[X]` mixed with omitting the field | Pick a convention; document it |
| `print(...)` for debug | Logger |

## Review checklist

- [ ] Every function typed; mypy strict passes
- [ ] Views are thin; logic in services
- [ ] Querysets via managers / selectors
- [ ] `select_related` / `prefetch_related` for traversal
- [ ] No `csrf_exempt` without a written reason
- [ ] Custom exceptions for domain errors
- [ ] Tests via pytest + factory_boy; coverage ≥ 80%
- [ ] Settings split; secrets via env
