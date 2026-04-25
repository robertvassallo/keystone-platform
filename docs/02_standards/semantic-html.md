# Semantic HTML

## Why

- **Accessibility** — assistive tech depends on landmarks, roles, and labels.
- **Maintainability** — the meaning of the markup is in the tags, not the class names.
- **SEO** — search engines weight semantic structure; document outline matters.
- **Resilience** — semantic markup degrades gracefully when CSS / JS fails.

## Rules

### Use the right element

| Need | Element |
|---|---|
| Primary content area | `<main>` (one per page) |
| Site / page navigation | `<nav>` |
| Self-contained content unit | `<article>` |
| Themed grouping with a heading | `<section>` |
| Tangentially related content | `<aside>` |
| Page or section header | `<header>` |
| Page or section footer | `<footer>` |
| Action button | `<button>` |
| Hyperlink | `<a href>` |
| Heading | `<h1>`–`<h6>` |
| Emphasis | `<em>` (stress) / `<strong>` (importance) |
| Tabular data | `<table>` with `<thead>`, `<tbody>`, `<th scope>` |
| Ordered / unordered list | `<ol>` / `<ul>` |
| Description list | `<dl>` |

### Heading hierarchy

- Exactly one `<h1>` per page — describes the page itself.
- Don't skip levels. `<h2>` → `<h4>` is an error.
- Heading text reflects the document outline, not the visual size. Use CSS for size.

### Forms

- Every input has a programmatically associated `<label>` (`for`/`id` pair, or wrapping label).
- Group related controls in `<fieldset>` with a `<legend>`.
- Required fields use `required` (and `aria-required="true"` for legacy AT support).
- Errors connect via `aria-describedby` to the input.
- Inside a `<form>`, non-submit buttons must have `type="button"`.

### Links vs buttons

- `<a href>` navigates (URL changes, history entry).
- `<button>` performs an action without navigation.
- `<a href="#">` is never correct. If it's an action, it's a `<button>`.

### Lists

- A series of items is a list. Use `<ul>` / `<ol>`.
- Inline-styling a `<div>` to look like a list breaks screen readers.

### Tables

- Use only for tabular data — not for layout.
- `<th scope="col">` and `<th scope="row">` are mandatory for screen readers.
- Provide `<caption>` describing the table's purpose.

## Anti-patterns

| Don't | Do |
|---|---|
| `<div onClick={...}>` | `<button onClick={...}>` |
| `<a href="#" onClick>` | `<button>` |
| `<span class="heading">` | `<h2>` (etc.) |
| `<b>`, `<i>` for meaning | `<strong>`, `<em>` |
| `<div class="nav">` | `<nav>` |
| Multiple `<h1>` | One `<h1>` |
| `<input>` with `placeholder` only | `<input>` with `<label>` |
| `<div role="button">` | `<button>` |

## Review checklist

- [ ] Exactly one `<h1>` per page
- [ ] Headings in order, no level skips
- [ ] All interactive elements use `<button>` / `<a href>` (no clickable `<div>`)
- [ ] Every form input has a programmatic label
- [ ] Landmarks (`<main>`, `<nav>`, `<header>`, `<footer>`) used appropriately
- [ ] Tables have `<thead>`, `<tbody>`, `<th scope>`, `<caption>`
- [ ] No `<a href="#">`
- [ ] Native elements preferred over ARIA (ARIA is a fallback, not a default)

The `@semantic-html-auditor` agent enforces this checklist.
