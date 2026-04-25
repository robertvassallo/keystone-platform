# Dashboard Layout

## Shell anatomy

```
┌─────────────────────────────────────────────────────────────┐
│  <header> — global nav, search, user menu                   │
├──────────┬──────────────────────────────────────────────────┤
│          │  <main> — page content                           │
│ <nav>    │   ┌────────────────────────────────────────────┐ │
│ side     │   │  page header — title, primary actions      │ │
│          │   ├────────────────────────────────────────────┤ │
│          │   │  page body — tables, charts, forms         │ │
│          │   │                                            │ │
│          │   └────────────────────────────────────────────┘ │
│          │  optional <aside> — context panel, slide-over   │
└──────────┴──────────────────────────────────────────────────┘
```

- Exactly one `<main>`, one `<nav>` (primary), one `<header>`.
- Side `<nav>` is the **primary** navigation; the `<header>` may include a secondary nav or breadcrumbs but does not duplicate links.
- `<aside>` opens for context-specific content (a row's detail, a filter panel) and closes back to the main view.

## Breakpoints (token names)

| Name | Min width | Use |
|---|---|---|
| `xs` | 0 | Phone (default) |
| `sm` | 640 | Large phone, small tablet |
| `md` | 768 | Tablet portrait |
| `lg` | 1024 | Tablet landscape, small desktop — sidebar collapses to icons |
| `xl` | 1280 | Desktop — sidebar expanded |
| `2xl` | 1536 | Wide desktop — multi-column dashboards |

Mobile-first CSS; layers added at higher breakpoints.

## Sidebar behaviour

- **xs / sm / md** — sidebar lives behind a hamburger; opens as an overlay sheet; closes on selection.
- **lg** — collapsed by default (icon rail, ~64 px). Hover expands; click-to-pin available.
- **xl+** — expanded by default (~256 px). Collapse-to-rail toggle persisted in `localStorage`.

Open / close transitions respect `prefers-reduced-motion`.

## Density modes

Three modes, user-selectable in settings, default `comfortable`:

| Mode | Row height | Padding scale | Font |
|---|---|---|---|
| `comfortable` | 48 px | default | base |
| `compact` | 36 px | -1 step | sm |
| `dense` | 28 px | -2 steps | xs |

Density implemented via a `data-density` attribute on `<html>`; CSS custom properties shift with it.

## Page header

Standard structure for every dashboard page:

```tsx
<header className="page-header">
  <div className="page-header__leading">
    <Breadcrumb items={...} />
    <h1>Projects</h1>
    <PageMeta>{count} active · last sync 2m ago</PageMeta>
  </div>
  <div className="page-header__actions">
    <Button intent="secondary">Export</Button>
    <Button intent="primary">New project</Button>
  </div>
</header>
```

- `<h1>` is the page subject (singular dashboard pages: "Projects", "Billing", not "Project Management Dashboard").
- Primary action is **rightmost** and is the only `intent="primary"` button on the page header.

## Filter / search bar

- Sits between the page header and the data area.
- Sticky at the top of the scroll container, not the page.
- Active filters render as removable chips below the input.
- Clear-all action when ≥ 2 filters are active.
- Filter state lives in URL search params — sharable, browser-back works.

## Data area

- Default to a table view for tabular data; cards or list for non-tabular.
- See `data-display.md` for table/list/card decision tree and state shells (loading, empty, error).

## Right-side context panel (optional `<aside>`)

- Use case: row detail, comments, audit history.
- Width: `360–480 px`; collapses below `lg`.
- Has its own `<h2>` title.
- Closing returns focus to the row that opened it.

## Modal vs slide-over vs page

| Use modal when | Use slide-over when | Use a page when |
|---|---|---|
| Quick decision (confirm, small form) | Context (entity detail) keeps the underlying view | Multi-step or > 1 screen of content |
| Blocks the underlying flow | Doesn't block the underlying flow | Bookmarkable / shareable URL needed |

## Spacing rhythm

- Page padding: `space-6` (24 px) at sm, `space-8` (32 px) at lg+.
- Section gap (between distinct content blocks within `<main>`): `space-8`.
- Element gap inside a card: `space-4`.

## Empty / loading / error states

Every data area has all three states designed:

- **Loading** — skeleton placeholders matching the eventual layout, never a centred spinner on a large area.
- **Empty** — illustration / icon + headline + supporting text + primary action ("Create your first project").
- **Error** — headline + plain-language description + retry action + (optional) error reference for support.

## Responsive checklist

- [ ] Sidebar collapses correctly at `lg` and `md`
- [ ] Page header actions reflow / collapse to overflow menu on narrow widths
- [ ] Tables become responsive cards or scroll horizontally with sticky first column on `<md`
- [ ] Modals fill the screen on phone widths
- [ ] No horizontal scroll on `<body>` at any breakpoint
- [ ] Density mode applies cleanly across components
- [ ] All transitions respect reduced motion
