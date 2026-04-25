---
description: Start a new feature — create a branch, scaffold the change list, and surface relevant standards docs.
argument-hint: "<feature-slug> [short description]"
---

You are starting a new feature: **$ARGUMENTS**.

Follow this workflow exactly.

## 1. Branch

Create a feature branch off the current default branch:

```
git switch -c feat/$ARGUMENTS
```

If `$ARGUMENTS` contains a space, slugify the part before the first space and use the rest as the branch description.

## 2. Confirm scope

Ask the user (in one message):
- What user-visible change does this deliver?
- Which area of the stack? (Frontend / API / DB / cross-cutting)
- What's explicitly out of scope?

Wait for the answer before continuing.

## 3. Surface relevant standards

Based on the area, list which docs you'll follow:

| Area | Read |
|---|---|
| UI / pages | `docs/02_standards/react.md`, `semantic-html.md`, `accessibility.md`, `tailwind.md` |
| API / views | `docs/02_standards/python.md`, plus `docs/01_architecture/auth.md` if auth-touching |
| DB / models | `docs/02_standards/sql.md`, `docs/01_architecture/data-model.md` |
| Styles / tokens | `docs/02_standards/css-sass.md`, `docs/03_ux/design-tokens.md` |

## 4. Plan

Output a numbered task plan covering: schema/model changes → backend changes → frontend changes → tests → docs/decisions-log update. No code yet.

## 5. Pre-merge checklist (paste into the PR body)

```
- [ ] Lint clean (pnpm lint, ruff check, stylelint, sqlfluff)
- [ ] Types clean (tsc --noEmit, mypy)
- [ ] Tests added; all green
- [ ] Migrations reversible (if DB change)
- [ ] A11y reviewed (run @a11y-reviewer)
- [ ] SQL reviewed (run @sql-reviewer if DB change)
- [ ] Decision recorded in docs/04_ai/decisions-log.md (if non-obvious)
```

Do not start writing code until the user approves the plan.
