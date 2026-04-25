# React (Next.js App Router)

## Server vs client — the most important boundary

- **Default to Server Components.** They render on the server, ship no JS to the client, and can read data directly.
- Add `'use client'` **only** when the component needs:
  - State (`useState`, `useReducer`)
  - Effects (`useEffect`, `useLayoutEffect`)
  - Browser APIs (`window`, `document`, `localStorage`)
  - Event handlers (`onClick`, `onChange`)
  - React Context consumers
- Push `'use client'` to **leaf** components. A client wrapper around a tree of server components beats a client tree.
- A page being interactive does not mean the whole page is a client component — split it.

```tsx
// app/projects/page.tsx — Server Component (no 'use client')
import { ProjectList } from './ProjectList';
import { CreateProjectButton } from './CreateProjectButton'; // 'use client'

export default async function ProjectsPage() {
  const projects = await fetchProjects();
  return (
    <main>
      <h1>Projects</h1>
      <CreateProjectButton />
      <ProjectList projects={projects} />
    </main>
  );
}
```

## Component anatomy

- One component per file. File name = component name (PascalCase).
- Adjacent: `Component.tsx`, `Component.module.scss` (if needed), `Component.test.tsx`, `Component.stories.tsx`, `index.ts` (re-exports).
- Co-locate hooks / sub-components in the folder when they're used only by this component; promote to a shared package once a second consumer appears.

## Feature folders

The `app/` directory holds **routes only** — page files are thin and import from feature folders. Feature code lives in `src/features/<feature>/`. Cross-feature primitives live in `src/shared/`. Full principle: `docs/02_standards/project-structure.md`.

```
apps/web/src/features/projects/
├── index.ts                       # public API
├── types.ts
├── components/
│   ├── ProjectList/
│   │   ├── ProjectList.tsx
│   │   ├── ProjectListRow.tsx     # sub-component, used only here
│   │   ├── ProjectListEmpty.tsx
│   │   ├── ProjectListSkeleton.tsx
│   │   ├── ProjectList.module.scss
│   │   ├── ProjectList.test.tsx
│   │   └── index.ts
│   ├── CreateProjectButton/
│   └── ProjectStatusBadge/
├── hooks/
│   ├── useProjects.ts
│   ├── useCreateProject.ts
│   └── index.ts
├── api/
│   ├── listProjects.ts
│   ├── createProject.ts
│   └── index.ts
└── lib/
    ├── projectStatusLabel.ts
    └── isProjectArchivable.ts
```

Route file is thin:

```tsx
// apps/web/src/app/(dashboard)/projects/page.tsx
import { ProjectList, CreateProjectButton } from '@/features/projects';
import { listProjects } from '@/features/projects/api';

export default async function ProjectsPage(): Promise<JSX.Element> {
  const projects = await listProjects();
  return (
    <main>
      <PageHeader title="Projects" actions={<CreateProjectButton />} />
      <ProjectList projects={projects} />
    </main>
  );
}
```

File-size targets:
- Components / hooks: **< 150 lines target**, hard cap 300.
- Pure helpers (`lib/`): < 50 lines target.
- Past the hard cap, split — the file holds more than one concept.

## Props

- `interface FooProps { ... }` — exported alongside the component.
- Required props before optional. No `defaultProps` (deprecated for function components).
- Compose, don't configure:
  ```tsx
  // Bad
  <Card hasHeader title="..." hasFooter footer={...} />
  // Good
  <Card>
    <Card.Header title="..." />
    <Card.Body>...</Card.Body>
    <Card.Footer>...</Card.Footer>
  </Card>
  ```
- `as` prop pattern allowed for primitive components (`<Button as="a" href="...">`), implemented via `React.ElementType` + `ComponentPropsWithoutRef`.

## State

- Local first. Lift state only when two siblings need it.
- Don't store derived state. Compute from props in render.
- Server state (data fetched from API) lives in **TanStack Query** (client) or fetched in a Server Component. Don't shoehorn it into local state.
- Form state in **React Hook Form** + Zod. Don't hand-roll.
- Global UI state (theme, current tenant) in Context — small surface, no business logic.

## Hooks discipline

- Top of the function, unconditional, ordered consistently.
- Custom hooks: `useThing`. Return either a value or `[value, setter]` tuple — pick one and stick with it.
- `useEffect` dependency arrays exhaustive. If you need to silence the linter, your effect is wrong.
- Avoid `useEffect` for derived data — compute in render.
- Cleanup functions for subscriptions, timers, listeners.

## Performance

- Don't pre-optimise. Measure first.
- `React.memo` / `useMemo` / `useCallback` only when:
  - You measured a render cost, **or**
  - A child uses `memo` and needs a stable reference.
- `key` is **stable + unique**. Never the array index for reorderable lists.
- Suspense boundaries placed at the **loading shape** boundary, not the page root.
- For large lists: virtualise (`@tanstack/react-virtual`).

## Forms

- React Hook Form + Zod resolver.
- Schema is the source of truth — generate the TS type from the Zod schema.
- Server-side validation re-runs the same schema (shared package).

## Errors

- `error.tsx` boundary per route segment for runtime errors.
- `not-found.tsx` for 404s.
- Throw `notFound()` / `redirect()` from server components when appropriate.
- Client component errors logged to the observability platform via an `ErrorBoundary` wrapper.

## Accessibility (sees `accessibility.md`)

- Every interactive element is a semantic HTML primitive.
- Build complex widgets (modals, comboboxes, tabs) on top of vetted primitives — Radix UI, Headless UI — not from scratch.
- Test focus order with the keyboard before merging.

## Anti-patterns

| Don't | Do |
|---|---|
| `'use client'` at page root | Push to the leaf needing interactivity |
| `useEffect(() => { fetch(...) }, [])` in a server-rendered context | Fetch in the Server Component |
| `useState` to store something derivable from props | Compute in render |
| `useEffect` to sync two state values | Lift / reduce / derive |
| `key={index}` on a reorderable list | Use a stable id |
| Custom modal / combobox from scratch | Radix UI / Headless UI primitive |
| `<div onClick>` | `<button>` (see `semantic-html.md`) |
| Prop drilling 4 layers deep | Context, composition, or co-location |

## Review checklist

- [ ] `'use client'` only where required, at the leaf
- [ ] No `useEffect` for derived state or for fetching that could happen on the server
- [ ] Exhaustive effect deps; no eslint-disable
- [ ] Stable `key`s on lists
- [ ] Forms via React Hook Form + Zod
- [ ] Complex widgets built on Radix / Headless UI
- [ ] Each component file has one component
- [ ] Composition pattern used over boolean prop flags
