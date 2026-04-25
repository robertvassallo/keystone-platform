# Monorepo Layout

> This document describes the **target** layout for when application code lands. Today
> the repo holds workflow + standards docs only.

## Top-level

```
.
├── apps/
│   ├── web/                # Next.js 15 (App Router, RSC)
│   └── api/                # Django 5 + DRF
├── packages/
│   ├── ui/                 # Shared React component library (semantic primitives + tokens)
│   ├── tokens/             # Design tokens — single source: tokens.json → CSS vars + TS consts
│   ├── types/              # Shared TS types (e.g. generated OpenAPI client)
│   └── config/             # Shared lint / tsconfig / tailwind presets
├── infra/
│   ├── docker/             # Dockerfiles, docker-compose for dev
│   ├── migrations/         # Standalone SQL migrations not owned by Django (rare)
│   └── scripts/            # Cross-cutting CLI tools (db dump, seed, etc.)
├── docs/                   # This tree
├── .claude/                # AI workflow
├── .vscode/  .github/      # Editor + GitHub integration
└── pyproject.toml  package.json  pnpm-workspace.yaml
```

## Granularity principle

Code is organised **by feature / domain**, not by technical layer, and split into small files (one concept per file). The full principle and review checklist live in `docs/02_standards/project-structure.md`. The trees below show the target shape.

## Conventions

### `apps/`
- Each app is independently runnable and deployable.
- Each app owns its own `.env`, its own dependency manifest, and its own deploy target.
- No cross-app imports — go through `packages/`.

### `apps/web/` — Next.js feature folders

```
apps/web/
├── src/
│   ├── app/                    # Next.js App Router — routes only, thin
│   │   ├── (marketing)/
│   │   ├── (dashboard)/
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   ├── billing/
│   │   │   └── layout.tsx
│   │   ├── api/                # Next.js route handlers (rare; prefer Django API)
│   │   └── layout.tsx
│   ├── features/               # one folder per feature; each is self-contained
│   │   ├── projects/
│   │   │   ├── components/{ProjectList,CreateProjectButton,...}/
│   │   │   ├── hooks/
│   │   │   ├── api/
│   │   │   ├── lib/
│   │   │   ├── types.ts
│   │   │   └── index.ts        # public surface
│   │   ├── billing/
│   │   ├── auth/
│   │   └── settings/
│   ├── shared/
│   │   ├── ui/                 # generic primitives (Button, Field, Card, DataTable)
│   │   ├── lib/                # utilities (cn, fetcher, formatDate)
│   │   └── hooks/
│   └── styles/
│       └── globals.scss
├── public/
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

Routes in `app/` are thin: they import from `features/<feature>` and arrange them. Business logic lives in the feature folder.

### `apps/api/` — Django per-domain apps

```
apps/api/
├── manage.py
├── pyproject.toml
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── test.py
│   │   └── prod.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                       # one Django app per domain
│   ├── accounts/
│   ├── projects/
│   │   ├── models/             # one model per file
│   │   │   ├── project.py
│   │   │   ├── milestone.py
│   │   │   └── deliverable.py
│   │   ├── managers/
│   │   ├── services/           # one business operation per file
│   │   │   ├── create_project.py
│   │   │   ├── archive_project.py
│   │   │   └── invite_collaborator.py
│   │   ├── selectors/          # one read query per file
│   │   ├── api/
│   │   │   ├── views/          # one view per file
│   │   │   ├── serializers/    # one serializer per file
│   │   │   └── urls.py
│   │   ├── events/
│   │   ├── tasks/              # Celery
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── urls.py
│   │   ├── migrations/
│   │   └── tests/
│   ├── billing/
│   └── notifications/
└── tests/                      # cross-app integration tests
```

Each subfolder of a Django app has an `__init__.py` that re-exports the public symbols, so callers do `from apps.projects.services import create_project` — they never reach into a deep path.

### `packages/`
- Library code shared between apps. Pure TS / pure Python — no app-specific config.
- Versioned implicitly (workspace protocol, not published).
- `packages/ui` exports semantic primitives (Button, Field, Card, DataTable). It does not contain page-level components.
- `packages/tokens` is the single source of design tokens. Build step generates:
  - `tokens.css` (CSS custom properties)
  - `tokens.ts` (typed constants)
  - `tailwind.preset.ts` (Tailwind theme extension)

### `infra/`
- Anything that doesn't ship inside an app's container: docker-compose for local Postgres + Redis, seed scripts, db backup tooling.

### `docs/`
- The contract for AI agents and humans alike. Standards live here. See `docs/00_overview.md`.

## Workspace tools

- **pnpm** workspaces declared in `pnpm-workspace.yaml` — `apps/*` and `packages/*`.
- **uv** workspaces declared in root `pyproject.toml` — `apps/api` and any future Python packages.
- **Turborepo** (optional) for task pipelining once the build graph justifies it. Not required for single-app projects.

## Running locally (target)

```
docker compose -f infra/docker/compose.dev.yml up -d   # Postgres + Redis
pnpm install
uv sync --workspace
pnpm --filter web dev          # Next.js on :3000
uv run --project apps/api manage.py runserver  # Django on :8000
```

## Anti-patterns

- A `lib/` or `shared/` folder at the repo root that isn't a published package.
- App code importing directly across `apps/web` ⇄ `apps/api` boundaries.
- A single `package.json` covering both web and shared packages — use the workspace.
- Generated code committed to the repo without a regen script and a CI check.
