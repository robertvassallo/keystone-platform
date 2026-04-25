# Data Display

## Choosing the right pattern

```
                  ┌──────────────────────────────────┐
                  │ Is each item structured the same? │
                  └─────────────┬────────────────────┘
                            yes │           │ no
                                ▼           ▼
                   ┌──────────────────┐   list / feed
                   │ Need to compare? │
                   └────┬─────────────┘
                    yes │      │ no
                        ▼      ▼
                     table   cards
```

| Pattern | Use when |
|---|---|
| **Table** | Many homogeneous rows, comparison across columns matters, sorting / filtering, bulk actions |
| **Card grid** | Visual identity per item matters (avatar, image), browsing not comparing |
| **List** | Lightweight items, single primary attribute, occasional metadata |
| **Detail / split** | Drilling into one item's full content |
| **Chart** | Trends, distributions, comparisons over a continuous variable |
| **KPI tiles** | A small fixed set of headline numbers |

## Tables

### Structure

- `<table>` + `<thead>` + `<tbody>` + `<th scope>` + `<caption>`. Always.
- First column: identifier or primary attribute. Last column: row actions (kebab menu).
- Numeric columns right-aligned. Text columns left-aligned. Date columns left-aligned with relative-time tooltip showing absolute.

### Sorting

- Click column header to sort. `aria-sort="ascending" | "descending" | "none"`.
- Default sort is meaningful (most recent created, most-relevant). Don't default to alphabetical unless it's truly the user's primary lens.
- Multi-column sort is rare; only enable when the data justifies it.

### Filtering

- Filters live above the table in a sticky bar.
- Active filters render as removable chips.
- Filter state in URL search params.

### Pagination vs infinite scroll

| Use pagination when | Use infinite scroll when |
|---|---|
| Users compare across pages, jump to a page, share a deep link | Browse-style content with no notion of "page 5" |
| Total count is meaningful | Total count isn't visible / useful |
| Default for dashboards | Used for feed-style streams (notifications, audit log) |

- Cursor-based pagination preferred over offset for large datasets.
- Always show: current range ("1–25 of 142"), page size selector, prev/next.

### Bulk actions

- Checkbox column at the leftmost position.
- Select-all in header selects the **current page**, not the whole dataset; offer a "Select all 142 matching" affordance only after the page-level select.
- Action bar appears above the table when ≥ 1 row is selected; shows count and applicable actions.

### Row interaction

- Whole-row click expands or navigates only when there's a clear "view detail" action and no other primary interaction in the row.
- Otherwise: a clear linked column (usually first) or a "View" action.
- Don't hide important actions in a hover-only menu — they're invisible on touch.

### Density

- Default `comfortable` density.
- Density toggle when users typically work in long sessions or scan many rows (audit logs, financials).

### Sticky elements

- Table header sticky inside its scroll container.
- First column sticky for wide tables on narrow screens.

## States

Every data area has these four states. Design all of them, not just the happy path.

### Loading

- Skeleton placeholders matching the eventual layout. Same row count as the typical first page.
- For tables, dim header text but keep it visible — users can still grok the columns.
- Avoid centred spinners for areas larger than ~120 px.

### Empty (no data yet)

```
┌──────────────────────────────────────────┐
│            [illustration / icon]          │
│            No projects yet                │
│  Create your first project to start       │
│  tracking milestones and budgets.         │
│                                           │
│       [ Create project ]                  │
└──────────────────────────────────────────┘
```

- Illustration (small, optional) + headline + supporting line + primary action.
- Headline is the absence ("No projects yet"), not an instruction ("Click here to create").

### Empty (filtered)

- Same layout, different copy: "No projects match your filters."
- Action: "Clear filters", not "Create project" — they have data, they're just looking past it.

### Error

- Headline + plain-language description + retry button + (optional) error reference.
- Don't expose stack traces. Do expose a request id so support can find it.

## KPI tiles

```
┌────────────────────┐
│ Active projects    │
│ 142                │
│ ▲ 12% vs. last week│
└────────────────────┘
```

- **Tile = number + label + trend indicator** (delta vs a comparison period).
- Trend uses both colour (success/danger) and direction icon — never colour alone.
- Don't pile 12 tiles in a row; group related metrics, hide secondary in a "More metrics" toggle.

## Charts

- Pick the chart for the question:
  - **Line** — trend over time
  - **Area** — trend over time, magnitude matters
  - **Bar** — comparison across discrete categories
  - **Stacked bar** — composition + comparison
  - **Pie / donut** — only with ≤ 4 slices, share-of-total — usually a bar is better
  - **Heatmap** — two-dimensional density
- Always label axes. Always include the unit.
- Use semantic colour tokens; don't reach for the chart library's defaults.
- Tooltip shows the precise value; the axis shows rounded.
- Empty / no-data state for charts looks like the table empty state.

## Counts

- "142 projects" — show the total, contextual. People want to know how much they're looking at.
- For very large numbers, abbreviate (`1.2K`, `4.5M`) but show full on hover.

## Time / dates

- Relative ("2 minutes ago") in the cell, absolute ("2026-04-24 18:42 UTC") in a tooltip / `<time datetime="...">`.
- Timezone defaults to user's browser; persist preference once set.
- Sort by absolute, never the relative string.

## Anti-patterns

| Don't | Do |
|---|---|
| `<div>` grid styled to look like a table | `<table>` with proper semantics |
| Centered spinner for the whole table area | Skeleton rows |
| Page-load shows zero rows with no message | Empty state |
| Hide actions until row hover | Show kebab menu always |
| Sort by column without `aria-sort` | Set `aria-sort` correctly |
| "Click here to create" empty-state CTA | Action verb on its own ("Create project") |
| Pie chart with 9 slices | Bar chart |
| Colour-only trend indicator | Colour + arrow + label |

## Review checklist

- [ ] Right pattern picked (table vs cards vs list)
- [ ] Loading, empty, filtered-empty, and error states designed
- [ ] Table semantics correct (`<th scope>`, `<caption>`)
- [ ] Sort / filter state in URL
- [ ] Bulk-action UX consistent with the rest of the app
- [ ] Trend indicators don't rely on colour alone
- [ ] Counts and totals visible
- [ ] Dates render relative + absolute
