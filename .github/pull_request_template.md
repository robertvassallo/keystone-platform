## Summary

<!-- One paragraph: what user-visible change does this deliver, and why? -->

## Scope

- **Area:** [ ] Frontend  [ ] API  [ ] DB / migrations  [ ] Infra / config  [ ] Docs
- **Linked issue / ticket:** <!-- #123 -->
- **Out of scope:** <!-- explicitly note anything intentionally not addressed -->

## Test plan

<!-- How a reviewer can verify this works. Steps a human would take. -->

- [ ]
- [ ]
- [ ]

## Screenshots / recordings

<!-- For UI changes — before / after if visual. Drop in GIFs for interactions. -->

## Pre-merge checklist

- [ ] Lint clean (`pnpm lint`, `ruff check .`, `stylelint`, `sqlfluff lint .`)
- [ ] Types clean (`tsc --noEmit`, `mypy .`)
- [ ] Tests added / updated; all green
- [ ] Migrations are reversible (DB changes only)
- [ ] No secrets, no `.env` files committed
- [ ] Semantic HTML / a11y reviewed (`@semantic-html-auditor`, `@a11y-reviewer`)
- [ ] SQL reviewed (`@sql-reviewer`) — DB changes only
- [ ] Decisions worth remembering recorded in `docs/04_ai/decisions-log.md`

## Risk / rollback

<!-- What could go wrong? How do we roll back? Any feature flag? -->

---

<!--
Conventional commit format expected on the squash-merge title:
  feat(scope): summary
  fix(scope): summary
  chore(scope): summary
  docs(scope): summary
  refactor(scope): summary
-->
