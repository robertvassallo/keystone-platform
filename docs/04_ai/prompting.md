# Prompting Claude Code

A good prompt produces a focused change. A bad prompt produces a sprawling, half-finished change you have to review line by line.

## Anatomy of a good prompt

```
[Goal in one sentence]
[Why it matters / user impact]
[Concrete files / regions to change]
[Out of scope — what NOT to touch]
[Verification — how you'll know it worked]
```

## Example — tight prompt

> Add CSV export to the Projects page.
>
> Users currently have no way to extract project data; support has been pasting from screenshots.
>
> - New action: Export button in the page header on `apps/web/src/app/projects/page.tsx`.
> - Streams CSV via a new API route `apps/api/apps/projects/api/views.py:ProjectExportView`.
> - Columns: id, name, status, owner_email, created_at.
>
> Out of scope: filtering, scheduled exports, formats other than CSV.
>
> Verify: click Export → download starts; file opens in Excel and Numbers; row count matches the table.

## Example — bad prompt

> Make the dashboard better.

Why bad: no goal, no scope, no acceptance. The agent has to invent all of this and you'll re-do it.

## Rules of thumb

- **State the *why*.** It's not redundant — it shapes the dozen small decisions inside the change.
- **Name files when you know them.** Don't make the agent guess.
- **Define out-of-scope explicitly.** Otherwise the agent will "improve" adjacent code and balloon the diff.
- **Include verification.** A clear acceptance criterion is the difference between "I think it works" and "I tested it."
- **One concern per prompt.** If you find yourself writing "and also", you have two prompts.

## When to use Plan mode

Trigger Plan mode (`/plan`) before:
- Anything that touches > 3 files.
- Anything involving migrations or auth.
- A refactor.
- A change you'd want a senior engineer to design-review.

Don't use Plan mode for:
- Typo fixes.
- Renames within a single file.
- Small, well-scoped bug fixes.

## When to delegate to a subagent

| Task | Agent |
|---|---|
| Pre-merge HTML review | `@semantic-html-auditor` |
| Pre-merge a11y review | `@a11y-reviewer` |
| Pre-merge SQL / migration review | `@sql-reviewer` |
| React component review | `@react-reviewer` |
| Django / Python review | `@python-reviewer` |

Subagents don't share your conversation context — give each one a self-contained brief.

## Context to include in prompts

When asking the agent to make a change, include:

- The standards that apply (`docs/02_standards/X.md`).
- The agreed pattern in the codebase (link to an existing canonical example).
- Any constraint that isn't obvious from the code (rate limits, downstream dependency, deploy schedule).

When asking the agent to debug, include:

- The exact reproduction steps.
- The observed behaviour vs the expected.
- The error message / log line / stack trace.
- What you've already tried and ruled out.

## What NOT to put in prompts

- Long file pastes when a path + line range suffices.
- Stale context from earlier in the session — remind only what's still relevant.
- Multiple unrelated tasks bundled together.

## Iteration

- Read the diff. Don't trust the agent's summary of what it changed.
- If the change is wrong: state *what's wrong* and *what you want instead*. Don't re-prompt the original task and hope.
- If the agent keeps drifting on the same point, save it as feedback (the agent has memory tooling that can persist preferences).

## Slash commands available in this repo

| Command | Use |
|---|---|
| `/new-feature <slug>` | Start a new feature: branch, scope, plan, checklist |

(Add new ones to `.claude/commands/`.)
