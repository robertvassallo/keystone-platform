# Project Structure

A cross-cutting principle: **modular and granular**. The shape of the directory tree is the first thing a new contributor sees. Make it tell the truth about what the project does.

## Why granular

- A 600-line file scares people off; a 60-line file invites editing.
- Small files have small blame radius — one edit affects one concept.
- Imports become documentation: `from apps.projects.services import archive_project` is self-explanatory.
- Git diffs and code review focus on real changes, not on which 80-line block within a mega-file shifted.
- Searching by file name lands on the right place faster than searching by symbol within a file.

## The two big rules

### 1. **One concept per file**

A "concept" is one of:

- One React component (its sub-components live in the same folder, but each in its own file once they're > a few lines).
- One custom hook.
- One Django model.
- One service function (a single business operation: `create_project`, `archive_project`).
- One selector / query function.
- One serializer.
- One API view.

A file is named for the concept it contains. `archive_project.py` exports `archive_project`. `ProjectList.tsx` exports `ProjectList`.

### 2. **Feature folders over technical-layer folders**

Group code by the **feature** (or domain) it belongs to, not by what kind of code it is.

```
features/projects/         ← all things "projects": components, hooks, api calls, types
features/billing/          ← all things "billing"
shared/ui/                 ← generic primitives reusable across features
```

NOT:

```
components/                ← every component in the app, mixed
hooks/                     ← every hook
api/                       ← every API call
```

Technical-layer folders work fine for ~5 features; they collapse at scale.

## File-size targets

| Tier | Target | Hard cap |
|---|---|---|
| Pure functions / utilities | < 50 lines | 100 |
| Components / hooks / services / views | < 150 lines | 300 |
| Configuration / constants files | < 100 lines | 200 |
| Generated code / migrations | unlimited | unlimited |

A file approaching the hard cap is a signal to split, not to refactor for compactness.

## Granularity by example

### Backend — Django app

```
apps/api/apps/projects/
├── __init__.py
├── apps.py                       # Django AppConfig
├── admin.py                      # Django admin registration
├── urls.py                       # url include for this app
├── models/
│   ├── __init__.py               # re-exports each model
│   ├── project.py                # one model
│   ├── milestone.py
│   └── deliverable.py
├── managers/
│   ├── __init__.py
│   ├── project_manager.py
│   └── milestone_manager.py
├── services/                     # business operations — one function per file
│   ├── __init__.py
│   ├── create_project.py
│   ├── archive_project.py
│   ├── invite_collaborator.py
│   └── recalculate_progress.py
├── selectors/                    # read queries — one function per file
│   ├── __init__.py
│   ├── list_active_projects.py
│   ├── get_project_summary.py
│   └── search_projects.py
├── api/
│   ├── __init__.py
│   ├── urls.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── project_create_view.py
│   │   ├── project_list_view.py
│   │   └── project_detail_view.py
│   └── serializers/
│       ├── __init__.py
│       ├── project_serializer.py
│       ├── milestone_serializer.py
│       └── deliverable_serializer.py
├── events/
│   ├── __init__.py
│   ├── project_created.py
│   └── project_archived.py
├── tasks/                        # Celery tasks
│   ├── __init__.py
│   └── send_progress_digest.py
├── migrations/
└── tests/
    ├── __init__.py
    ├── services/
    │   ├── test_create_project.py
    │   └── test_archive_project.py
    ├── selectors/
    ├── api/
    └── models/
```

The `__init__.py` of each subdirectory re-exports the public symbols, so callers import from the package, not from a deep path:

```python
# apps/api/apps/projects/services/__init__.py
from .create_project import create_project
from .archive_project import archive_project
from .invite_collaborator import invite_collaborator
from .recalculate_progress import recalculate_progress

__all__ = ["create_project", "archive_project", "invite_collaborator", "recalculate_progress"]
```

Callers:

```python
from apps.projects.services import create_project
```

NOT:

```python
from apps.projects.services.create_project import create_project
```

### Frontend — feature folder

```
apps/web/src/features/projects/
├── index.ts                       # public API of this feature
├── types.ts
├── components/
│   ├── ProjectList/
│   │   ├── ProjectList.tsx
│   │   ├── ProjectListRow.tsx
│   │   ├── ProjectListEmpty.tsx
│   │   ├── ProjectListSkeleton.tsx
│   │   ├── ProjectList.module.scss
│   │   ├── ProjectList.test.tsx
│   │   └── index.ts
│   ├── CreateProjectButton/
│   │   ├── CreateProjectButton.tsx
│   │   ├── CreateProjectDialog.tsx
│   │   ├── CreateProjectForm.tsx
│   │   ├── CreateProjectButton.test.tsx
│   │   └── index.ts
│   └── ProjectStatusBadge/
│       ├── ProjectStatusBadge.tsx
│       └── index.ts
├── hooks/
│   ├── useProjects.ts
│   ├── useCreateProject.ts
│   ├── useArchiveProject.ts
│   └── index.ts
├── api/
│   ├── listProjects.ts
│   ├── createProject.ts
│   ├── archiveProject.ts
│   └── index.ts
└── lib/
    ├── projectStatusLabel.ts
    └── isProjectArchivable.ts
```

The route file in `app/` is thin and imports from the feature:

```tsx
// apps/web/src/app/(dashboard)/projects/page.tsx
import { ProjectList, CreateProjectButton } from '@/features/projects';
import { listProjects } from '@/features/projects/api';

export default async function ProjectsPage() {
  const projects = await listProjects();
  return (
    <main>
      <PageHeader title="Projects" actions={<CreateProjectButton />} />
      <ProjectList projects={projects} />
    </main>
  );
}
```

### Shared / cross-feature code

```
apps/web/src/shared/
├── ui/                            # generic primitives — no business logic
│   ├── Button/
│   ├── Card/
│   ├── Field/
│   └── DataTable/
├── lib/
│   ├── cn.ts
│   ├── fetcher.ts
│   └── formatDate.ts
└── hooks/
    ├── useDebounce.ts
    └── useMediaQuery.ts
```

Promote from feature folder → `shared/` only when **two or more** features use it. Don't promote in anticipation.

## When to split a file

**Always split when:**
- A file passes the hard cap (300 lines for components / services / views).
- A file contains two unrelated exports.
- You catch yourself searching the file with `Cmd+F` for landmarks.

**Often worth splitting when:**
- A component has a clearly-named sub-component used only by it (extract to its own file in the same folder).
- A service has a helper that's >15 lines (extract to a sibling file).
- Tests for one file balloon past 200 lines (split tests by behaviour).

**Don't split when:**
- The pieces are tightly coupled and always change together.
- The split forces awkward "import to re-export" plumbing with no other benefit.

## Index / barrel files

Every package directory has an `index.ts` (TS) or `__init__.py` (Python) that re-exports the public symbols. This serves three purposes:

1. **Stable import paths** — internal reorganisation doesn't break callers.
2. **Public API documentation** — `index.ts` shows at a glance what the package offers.
3. **Encapsulation** — files not re-exported are internal; tooling can enforce this.

Don't over-barrel: a barrel that re-exports from a barrel that re-exports from a barrel is busywork. One layer between caller and implementation is enough.

## Naming

- **Files**: match the primary export. `ProjectList.tsx` exports `ProjectList`. `archive_project.py` exports `archive_project`.
- **Folders**: lowercase kebab-case (`apps/web/src/features/projects`); React component folders PascalCase to match the component (`ProjectList/`).
- **No generic names** like `utils.ts`, `helpers.ts`, `misc.py`, `common/`. Name what's actually inside (`formatDate.ts`, `permissions.py`, `currency-utils.ts`).

## Anti-patterns

| Don't | Do |
|---|---|
| `views.py` with 12 view classes | `api/views/<one_view_per_file>.py` |
| `components/Button/Card/Modal/...` (one big folder) | `features/<x>/components/...` + `shared/ui/...` |
| `utils.ts` with 30 functions | One function per file under `lib/`, or grouped by domain |
| `models.py` with 8 models | `models/{model_one,model_two,…}.py` |
| `services.py` with 15 functions | `services/{create_x,archive_x,...}.py` |
| Re-exports across 4 layers of barrels | One barrel per package, max |
| Folder named `common/`, `shared/`, `helpers/` without sub-naming | Name the actual concern |
| Promoting code to `shared/` "in case" someone reuses it | Promote on second consumer |

## Review checklist

- [ ] Each file holds one concept; named for that concept
- [ ] Code grouped by **feature** (or **domain**), not by technical layer
- [ ] No file approaches the hard cap (300 lines)
- [ ] Each package has a clear public API via `index.ts` / `__init__.py`
- [ ] No generic catch-all folders (`utils/`, `common/`, `helpers/`)
- [ ] Internal-only files not exported from the package barrel
- [ ] Tests mirror source structure
- [ ] Code lives in a feature folder until a second consumer warrants promotion to `shared/`
