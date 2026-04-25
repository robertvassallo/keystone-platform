# CSS / SASS

Tailwind handles most utility-level styling (see `tailwind.md`). SASS is for **component-level styles**, **design-token files**, and **complex selectors** Tailwind can't express cleanly.

## Why

- Tokens centralised in SASS source compile to CSS custom properties → consistent, themable.
- BEM-style class names communicate intent without coupling to DOM structure.
- Limited nesting and specificity keep CSS predictable across components.

## File layout

```
packages/ui/src/
├── styles/
│   ├── tokens/
│   │   ├── _color.scss
│   │   ├── _space.scss
│   │   ├── _type.scss
│   │   ├── _shadow.scss
│   │   ├── _radius.scss
│   │   └── _index.scss        # @forward all
│   ├── globals.scss            # resets, base, custom-property emission
│   └── mixins/
│       ├── _media.scss
│       └── _focus.scss
└── components/
    └── DataTable/
        ├── DataTable.tsx
        └── DataTable.module.scss   # CSS Modules; class names locally scoped
```

## Naming — BEM

```scss
// Block
.card { }

// Element (child of block)
.card__header { }
.card__body { }

// Modifier (variant of block or element)
.card--featured { }
.card__header--compact { }
```

- All class names: kebab-case.
- BEM lexical depth max **3** (`block__element--modifier`).
- Don't BEM utility classes — Tailwind covers utilities.

## Tokens

```scss
// _color.scss
:root {
  --color-bg-canvas: #{$gray-50};
  --color-bg-surface: #{$white};
  --color-fg-default: #{$gray-900};
  --color-fg-muted: #{$gray-600};
  --color-border-subtle: #{$gray-200};
  --color-accent-fg: #{$indigo-600};
  --color-accent-emphasis: #{$indigo-700};
  --color-danger-fg: #{$red-600};
  // ... etc.
}

[data-theme="dark"] {
  --color-bg-canvas: #{$gray-950};
  // ...
}
```

- Components reference the **semantic** custom property (`--color-fg-muted`), never the primitive (`#6b7280`).
- The Tailwind preset reads these tokens via `var(--color-...)`.

## Rules

- **Specificity**: max one class per simple selector. No `#id` selectors. No qualifying types (`div.card`).
- **Nesting depth**: max 3.
- **No `!important`** — refactor specificity instead. (Tailwind utilities themselves are fine.)
- **No raw colours** — use tokens. Hex / rgb literals fail stylelint.
- **No magic numbers in spacing** — use spacing tokens (`var(--space-3)`).
- **Logical properties** for inline-direction-aware layout (`margin-inline-start`, not `margin-left`).
- **Container queries** preferred over media queries when the rule is about a component's own size.

## Mixins / functions

- Use sparingly. A mixin that's used once is a function call where a few CSS lines would do.
- Place shared mixins in `styles/mixins/` and `@use` them by namespace.

## Anti-patterns

| Don't | Do |
|---|---|
| `color: #1f2937;` | `color: var(--color-fg-default);` |
| `.card .card-header .card-header-title` | `.card__header__title` (BEM, max depth 3) |
| `!important` to override | Increase the source class's specificity by structure |
| Deep nesting via SASS `&` | Flatten the rule set |
| Element selectors (`div`, `span`) for non-base styles | Use a class |
| Same token defined in two files | Single source in `tokens/` |

## Review checklist

- [ ] No raw colour values; all colours via custom properties
- [ ] No `!important`
- [ ] No `#id` selectors
- [ ] Class names follow BEM (kebab-case, max 3-part)
- [ ] Nesting ≤ 3 levels
- [ ] Tokens consumed via CSS custom properties, not SASS vars at use site
- [ ] Logical properties for inline-direction layout
- [ ] No duplicate token definitions
