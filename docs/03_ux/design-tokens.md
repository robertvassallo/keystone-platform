# Design Tokens

Tokens are the source of truth for every visible decision: colour, spacing, type, radius, shadow, motion. Components consume tokens; tokens are defined in one place.

## Tier model

```
primitive  →  semantic  →  component
```

| Tier | Example | Used by |
|---|---|---|
| **Primitive** | `gray-50`, `gray-100`, … `indigo-600` — the raw palette | Only the next tier |
| **Semantic** | `bg-canvas`, `bg-surface`, `fg-default`, `fg-muted`, `accent-fg` | Components, Tailwind theme |
| **Component** | `button-primary-bg`, `card-shadow` | A single component (rare; only when reuse warrants) |

Components reference **semantic** tokens. They never reference primitives directly.

## Files

```
packages/tokens/
├── src/
│   ├── primitive/
│   │   ├── color.ts
│   │   ├── space.ts
│   │   ├── type.ts
│   │   └── radius.ts
│   ├── semantic/
│   │   ├── light.ts
│   │   └── dark.ts
│   └── index.ts
├── build.ts        # generate tokens.css + tailwind.preset.ts + tokens.d.ts
└── package.json
```

Build outputs:
- `dist/tokens.css` — all CSS custom properties for `:root` and `[data-theme="dark"]`.
- `dist/tailwind.preset.ts` — Tailwind theme extension.
- `dist/tokens.d.ts` — typed constants for TS code.

## Colour

### Primitive scales

`gray`, `red`, `amber`, `green`, `blue`, `indigo`, `purple` — each with stops `50`, `100`, …, `950`. Tailwind defaults are fine; pin in `primitive/color.ts`.

### Semantic mappings (light)

| Token | Primitive |
|---|---|
| `bg-canvas` | `gray-50` |
| `bg-surface` | `white` |
| `bg-overlay` | `gray-900 / 0.5` |
| `fg-default` | `gray-900` |
| `fg-muted` | `gray-600` |
| `fg-subtle` | `gray-500` |
| `fg-on-accent` | `white` |
| `border-subtle` | `gray-200` |
| `border-default` | `gray-300` |
| `border-emphasis` | `gray-400` |
| `accent-fg` | `indigo-600` |
| `accent-emphasis` | `indigo-700` |
| `accent-bg-subtle` | `indigo-50` |
| `success-fg` | `green-600` |
| `warning-fg` | `amber-600` |
| `danger-fg` | `red-600` |

Dark theme remaps the **same** semantic tokens to different primitives — components don't change.

## Spacing

Base unit `4 px`. Scale: `0`, `1` (4 px), `2` (8 px), `3` (12 px), `4` (16 px), `5` (20 px), `6` (24 px), `8` (32 px), `10` (40 px), `12` (48 px), `16` (64 px), `20` (80 px), `24` (96 px).

- All margins / paddings / gaps come from this scale.
- Don't introduce in-between values (`10 px`, `14 px`); pick the nearest token.

## Type

| Token | Use |
|---|---|
| `text-2xs` (10/14) | Tags, micro-labels |
| `text-xs` (12/16) | Caption, table cells dense |
| `text-sm` (14/20) | Body small, dense UI |
| `text-base` (16/24) | Body |
| `text-lg` (18/28) | Lead, large body |
| `text-xl` (20/28) | Section heading |
| `text-2xl` (24/32) | Page heading (`<h2>`) |
| `text-3xl` (30/36) | Page heading (`<h1>`) — small dashboards |
| `text-4xl` (36/40) | Marketing surfaces only |

Font stack: system-ui first, fall back to platform sans. One body font + one mono font (for code).

## Radius

`none` (0), `sm` (4), `md` (6), `lg` (8), `xl` (12), `2xl` (16), `full` (9999). Use `md` as the default for inputs, buttons, cards.

## Shadow

`xs`, `sm`, `md`, `lg`, `xl` — semantic levels of elevation. Don't author bespoke shadows in components.

## Motion

| Token | Value |
|---|---|
| `motion-duration-instant` | 75 ms |
| `motion-duration-fast` | 150 ms |
| `motion-duration-default` | 200 ms |
| `motion-duration-slow` | 300 ms |
| `motion-ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `motion-ease-out` | `cubic-bezier(0, 0, 0.2, 1)` |
| `motion-ease-in` | `cubic-bezier(0.4, 0, 1, 1)` |

All motion respects `prefers-reduced-motion: reduce` and falls back to `0 ms`.

## Theme switching

- Theme attribute on `<html>`: `data-theme="light" | "dark"`.
- Default to `prefers-color-scheme`; user preference persisted in `localStorage` and synced server-side once authenticated.
- Switch is instant — no flash of unstyled content (handled by an inline pre-paint script).

## Adding a new token

1. Justify it (component reuse ≥ 3, or a meaningful new semantic role).
2. Add the primitive (if needed) → semantic → Tailwind preset.
3. Update `docs/03_ux/design-tokens.md` (this file).
4. Open a PR; design review before merge.

## Anti-patterns

- Raw hex / rgb in component code.
- Tailwind's primitive utilities (`bg-indigo-600`) used directly — use the semantic `bg-accent`.
- A component defining its own colour outside the token system.
- Two tokens with overlapping meaning (`fg-secondary` + `fg-muted`).

## Review checklist

- [ ] No raw colour / spacing / radius values in components
- [ ] Tokens flow through CSS custom properties, consumed by Tailwind theme
- [ ] Dark theme mapping in place for every new semantic token
- [ ] Motion respects reduced-motion preference
- [ ] Tier respected: components → semantic → primitive
