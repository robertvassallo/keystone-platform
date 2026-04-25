# Subagents

Subagents are specialised review / research agents defined in `.claude/agents/*.md`. Each has its own context window and toolset, so the main conversation isn't polluted by the details of a focused task.

## When to invoke

- **Bounded review tasks** — pre-merge audits where you want a focused opinion.
- **Independent research** — exploring a part of the codebase you're not currently working in.
- **Parallelisable work** — kicking off three reviews at once.

Don't use subagents for:
- Implementation. Subagents review and report; you (or the main agent) implement.
- Tasks where you need the result in your own context — the subagent's full reasoning isn't visible to you, only its summary.

## The agents in this repo

### `@semantic-html-auditor`

Audits HTML / JSX for semantic correctness — landmark elements, heading order, button-vs-link, form labelling. Output: a punch list with file:line references.

**Run:** before any UI ships. Especially after AI-generated UI code, which often defaults to `<div>`-soup.

### `@a11y-reviewer`

Reviews UI changes against WCAG 2.2 AA. Focus areas: keyboard reachability, focus order, contrast, motion preference, ARIA.

**Run:** before any UI ships. Pair with `@semantic-html-auditor` — they overlap intentionally; a11y is broader.

### `@sql-reviewer`

Reviews raw SQL and ORM queries for correctness, performance, and migration safety. Catches `SELECT *`, missing indexes, N+1, lock-heavy migrations.

**Run:** before any DB-touching change merges. Critical for migrations.

### `@react-reviewer`

Reviews React / Next.js component changes. Focus: server vs client boundary, hook discipline, render performance, composition patterns.

**Run:** for any new component or significant refactor.

### `@python-reviewer`

Reviews Django / Python changes. Focus: typing, layering (views / services / models), ORM discipline, security defaults.

**Run:** for any backend change.

## How to invoke

In the main conversation, prefix with `@`:

```
@semantic-html-auditor: review the changes in apps/web/src/app/projects/
@a11y-reviewer: review the same change set
```

You can chain: run `@semantic-html-auditor` first; if it's clean, run `@a11y-reviewer`.

## Brief the subagent

Subagents start fresh. They don't see your conversation. The prompt must be self-contained:

```
@react-reviewer: review apps/web/src/app/projects/page.tsx and ProjectList.tsx.
Context: new feature adds CSV export, with a server-rendered list and a client
button. I'm worried about the boundary — whether 'use client' is in the right
place. Report under 200 words.
```

## When to add a new subagent

Add a new agent in `.claude/agents/<name>.md` when:

- You find yourself repeatedly asking the same review question.
- A standards doc has been written that needs an enforcer.
- A specialist domain emerges (e.g. `@chart-reviewer` once data viz becomes complex).

Don't add an agent for:

- One-off tasks.
- General-purpose review (use the main agent).
- Anything you can't write a clear, narrow brief for.

## Agent definition format

```markdown
---
name: agent-name
description: One sentence — when to use this agent
tools: Read, Grep, Glob, Bash
model: sonnet
---

System prompt: who the agent is, what it enforces, what it outputs.

## Output format

Specify exactly the format you want, so the result is parseable / consistent.

End with a one-line verdict: PASS / PASS WITH NOTES / BLOCK.
```

Keep agent prompts under ~150 lines. They're not where standards live — standards are in `docs/02_standards/*`. The agent points at the standards doc and enforces it.

## Anti-patterns

- **Subagents that implement code.** They don't have your context; they'll go off-script. Subagents review and report.
- **Vague briefs.** "Review my changes" leaves the agent inventing the scope.
- **Running an agent for trivial changes.** A typo fix doesn't need `@react-reviewer`.
- **Parallel agents on overlapping concerns.** Two agents flagging the same issue wastes context.

## Review checklist (when adding a new agent)

- [ ] Frontmatter complete: `name`, `description`, `tools`, `model`
- [ ] Description is one sentence and answers "when do I use this?"
- [ ] Body points at the standards doc(s) it enforces
- [ ] Output format is specified
- [ ] Ends with PASS / NOTES / BLOCK verdict
- [ ] ≤ 150 lines
