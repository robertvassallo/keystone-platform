# Accessibility

Target: **WCAG 2.2 AA**. The `@a11y-reviewer` agent enforces these rules; run it before any UI ships.

## Core principles (POUR)

- **Perceivable** — content can be presented in ways users can perceive.
- **Operable** — UI works with keyboard, touch, and pointer.
- **Understandable** — content and operation can be understood.
- **Robust** — works across assistive technologies, now and future.

## Keyboard

- Every interactive element reachable with `Tab`, activated with `Enter` / `Space`.
- Visible focus indicator on every focusable element. Use `:focus-visible`, not `:focus`. Never `outline: none` without an equivalent.
- Logical tab order matches visual order. No `tabindex > 0`.
- Focus trapped within open modals / sheets; focus returns to the trigger on close.
- Skip-to-content link as the first focusable element on every page.

## Screen reader

- Use semantic HTML first. ARIA is a fallback when no native element fits.
- Single `<h1>` per page; headings in order.
- All form inputs have a programmatic label.
- Icon-only buttons have `aria-label` describing the action ("Delete project", not "Delete").
- Status updates that aren't focused use `aria-live="polite"` or `aria-live="assertive"` (rarely).
- Decorative images: `alt=""`. Informative images: meaningful `alt`.
- Don't repeat `alt` text in adjacent visible text — that's "Project icon" said twice.

## Colour & contrast

| Surface | Minimum contrast |
|---|---|
| Normal text (< 18 px or < 14 px bold) | 4.5 : 1 |
| Large text | 3 : 1 |
| Non-text UI (icons, borders that convey state, form input borders) | 3 : 1 |
| Focus indicator vs adjacent surface | 3 : 1 |

- Never rely on colour alone. Pair with icon, label, or shape.
- Use semantic tokens (`text-fg`, `text-fg-muted`) — primitives are vetted to meet contrast.

## Motion

- Respect `prefers-reduced-motion`. Disable parallax, decorative auto-play, large transitions.
- No flashing > 3 Hz.
- Auto-playing media has a pause control.

## Forms

- Labels are visible. Placeholder text is NOT a label.
- Required marked with `required` and visually (the `*` is helpful but not sufficient).
- Errors:
  - Programmatically associated (`aria-describedby` linking the input to the error message id).
  - Describe the fix ("Email must include @"), not just "Invalid".
  - Live region announces errors when they appear server-side.
- Group related fields: `<fieldset>` + `<legend>`.
- Autofill hints (`autocomplete` attribute) on personal-info fields.

## Modals / dialogs

- Use `<dialog>` element, or a vetted primitive (Radix Dialog).
- Focus moves into the dialog on open, returns to the trigger on close.
- `Escape` closes (unless destructive).
- Background content is `aria-hidden` and inert (`inert` attribute).
- The dialog has an accessible name (`aria-labelledby` referencing the title).

## Tables (data)

- `<thead>`, `<tbody>`, `<th scope="col">` / `<th scope="row">`.
- `<caption>` describing the table's purpose.
- Sortable column headers use `aria-sort`.
- Selectable rows use `aria-selected`.

## Tabs / tablists

- Use the ARIA Authoring Practices pattern, or a vetted primitive.
- Arrow keys navigate; `Tab` enters the active panel.
- Active tab has `aria-selected="true"` and `tabindex="0"`; inactive tabs `tabindex="-1"`.

## Links

- Link text describes the destination ("Read the design tokens guide", not "click here").
- External links: indicate target = `_blank` with an icon and `aria-label` ("opens in new tab").
- `<a href="#">` is never correct — use `<button>`.

## Error pages

- 404 / 403 / 500 pages have headings, descriptive text, and a link back to safety.
- Don't render only an icon.

## Testing

- Linter: `eslint-plugin-jsx-a11y` (configured in `eslint.config.mjs`).
- Automated runtime: `@axe-core/playwright` in e2e tests.
- Manual:
  - Keyboard-only walkthrough of every new feature.
  - Screen reader test (NVDA on Windows or VoiceOver on macOS) for any new widget.
  - Zoom to 200% — layout doesn't break; no horizontal scrolling on body content.

## Anti-patterns

| Don't | Do |
|---|---|
| `outline: none` for "design" | Custom `:focus-visible` ring with ≥ 3:1 contrast |
| Tooltip as the only label | Visible label or `aria-label` |
| Placeholder as the only label | Real `<label>` |
| `tabindex="5"` to control order | Source order matches visual order |
| `<div role="button">` | `<button>` |
| Modal that doesn't trap focus | Use a vetted primitive |
| Colour-only state ("red row = error") | Add icon or text |
| Auto-play with no pause | Pause control + reduced-motion respected |

## Review checklist

- [ ] All interactive elements keyboard-reachable
- [ ] Focus indicator visible everywhere (≥ 3:1 contrast)
- [ ] Logical tab order
- [ ] All inputs labelled programmatically
- [ ] Modals trap focus + restore on close
- [ ] Errors associated via `aria-describedby` and describe the fix
- [ ] No colour-alone state
- [ ] Reduced-motion respected
- [ ] axe-core has zero violations on changed pages
