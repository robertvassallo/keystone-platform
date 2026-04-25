# Git Workflow

## Strategy: Trunk-based with short-lived branches

- One long-lived branch: `main`.
- Feature branches off `main`, merged via PR, deleted after merge.
- Branches live **hours to a few days**, not weeks.

## Branch naming

```
<type>/<slug>[-<issue-id>]
```

| Type | When | Example |
|---|---|---|
| `feat/` | New user-visible functionality | `feat/dashboard-export-csv` |
| `fix/` | Bug fix | `fix/login-redirect-loop` |
| `chore/` | Tooling, deps, build | `chore/upgrade-next-15.5` |
| `refactor/` | Internal restructuring without behaviour change | `refactor/extract-billing-service` |
| `docs/` | Docs-only change | `docs/data-model-tenancy` |
| `test/` | Tests-only change | `test/projects-quota-edge-cases` |
| `revert/` | Revert of a merged change | `revert/dashboard-export-csv` |

Slug: lowercase, kebab-case, ≤ 5 words, descriptive.

## Commits

### Conventional Commits

```
<type>(<scope>): <subject>

<body — optional>

<footer — optional, e.g. "Fixes #123" or "BREAKING CHANGE: ...">
```

- `type` matches the branch types above.
- `scope` is the affected area (e.g., `web`, `api`, `auth`, `db`).
- Subject in imperative mood, lowercase, no period, ≤ 72 chars.
- Body wraps at 72 chars; explains *why*, not *what*.

### Atomic commits

- One logical change per commit. A commit that mixes a refactor with a bug fix is two commits.
- Commit reverts cleanly to a working state.
- No "WIP" / "fix typo from previous commit" noise — squash before merge or rebase locally.

## PR rules

### Size

- Target: ≤ 400 lines diff (excluding generated / lockfile changes).
- A PR larger than 800 lines must be split unless reviewer agrees in advance.

### Requirements before requesting review

- All checks green (lint, types, tests).
- PR description filled in (template covers it).
- No commented-out code, no `console.log`, no `TODO` without an issue link.
- Self-review the diff in GitHub before requesting human review.

### Review

- At least one approving reviewer.
- Reviewer can request changes; author resolves and re-requests.
- Author merges (squash) — not the reviewer.

### Merge

- **Squash merge** — single commit on `main`, message follows Conventional Commits format.
- **No merge commits** on `main` — keep history linear.
- **No force-push to `main`** — ever. Hooks block it.

## Rebasing & history

- Rebase your branch onto `main` before requesting review (catches conflicts early).
- Force-push to **your own** branch is allowed; force-push to `main` is banned.
- Don't rewrite history of a branch others are committing to.

## Reverts

- A bad change merged to `main` gets reverted, not "fixed forward" under time pressure.
- The revert PR explains: what was reverted, why, and what's needed for a re-attempt.

## Hooks

- **Pre-commit** (locally; via `husky` + `lint-staged`): format + lint changed files; block on errors.
- **Pre-push**: run typecheck + test on changed paths.
- CI runs the full lint / typecheck / test suite; pre-push is fast feedback only.

## What NEVER goes in git

- Secrets — `.env` files, tokens, certificates.
- Generated artifacts — build output, coverage reports, `.next/`.
- Personal config — `.idea/`, `.vscode/settings.local.json`.
- Large binaries — use Git LFS or store outside the repo.

## Tagging & releases

- Semver tags on `main`: `vMAJOR.MINOR.PATCH`.
- A tag triggers the release pipeline (when one exists).
- Pre-release tags: `v1.2.3-beta.1`, `v1.2.3-rc.1`.

## Anti-patterns

| Don't | Do |
|---|---|
| Long-lived feature branches | Merge often; ship behind a flag if needed |
| `git push --force` to a shared branch | Only force-push your own branch |
| Bundling refactor + bug fix in one PR | Split into two |
| 800-line PRs without warning | Pre-coordinate the split |
| Commits like `fix`, `wip`, `more` | Conventional commits |
| `git pull` on a shared branch (creates merge commit) | `git pull --rebase` or `git fetch + rebase` |
| Committing `package-lock.json` and `pnpm-lock.yaml` together | One package manager, one lockfile |

## Review checklist

- [ ] Branch named per the convention
- [ ] Commits are atomic, conventional, imperative subject
- [ ] PR ≤ 400 lines (or split agreed)
- [ ] No secrets, no generated files
- [ ] Self-reviewed diff before requesting review
- [ ] Linear history; squash-merged
