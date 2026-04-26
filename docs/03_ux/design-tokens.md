# Design Tokens

Tokens are the source of truth for every visible decision: colour, spacing, type, radius, shadow, motion. Components consume tokens; tokens are defined in one place.

## Tier model

```
primitive  →  palette  →  semantic  →  component
```

| Tier | Example | Used by |
|---|---|---|
| **Primitive** | `gray-50`, `gray-100`, … `indigo-600` — the raw colour ramps | Only the next tier |
| **Palette** | A curated palette (`indigo`, `slate`, `emerald`) or a tenant-created **brand theme** (`brand-<uuid>`) — a named set of mappings to semantic tokens, in `light` and `dark` flavours | Theme system; emitted into `[data-palette="…"][data-theme="…"]` selectors |
| **Semantic** | `bg-canvas`, `bg-surface`, `fg-default`, `fg-muted`, `accent-fg` | Components, Tailwind theme |
| **Component** | `button-primary-bg`, `card-shadow` | A single component (rare; only when reuse warrants) |

Components reference **semantic** tokens. They never reference primitives or palettes directly. The active palette and mode determine which primitive values back the semantic tokens at runtime.

Curated palettes ship in `packages/tokens/src/palettes/` and bake into `tokens.css`. **Brand themes** are tenant-created palettes stored in the DB and rendered into a tenant-scoped `<style>` block at first paint. Both produce the same `[data-palette="…"][data-theme="…"]` selector shape — the rest of the system can't tell them apart.

User-facing copy says "theme" (the picker shows themes); the architecture says "palette" (the data structure is a palette). See `theming.md` for how palettes, modes, and surface overrides compose, and for the brand-theme builder + lifecycle.

## Files

```
packages/tokens/
├── src/
│   ├── primitive/
│   │   ├── color.ts
│   │   ├── space.ts
│   │   ├── type.ts
│   │   └── radius.ts
│   ├── palettes/                  # one file per registered palette
│   │   ├── indigo.ts              # exports { light, dark }
│   │   ├── slate.ts
│   │   ├── emerald.ts
│   │   └── index.ts               # registry consumed by build + UI pickers
│   ├── semantic/
│   │   ├── light.ts               # default-palette mapping (kept for back-compat / SSR baseline)
│   │   └── dark.ts
│   └── index.ts
├── build.ts        # generate tokens.css + tailwind.preset.ts + tokens.d.ts
└── package.json
```

Build outputs:
- `dist/tokens.css` — CSS custom properties for every (curated palette × mode) combination, plus a surface-override block for region-local theming. Brand-theme CSS is *not* in `tokens.css` — it's emitted at request time, scoped to the active tenant.
- `dist/tailwind.preset.ts` — Tailwind theme extension.
- `dist/tokens.d.ts` — typed constants for TS code (semantic token names, curated palette ids, modes).

## Colour

### Primitive scales

`gray`, `red`, `amber`, `green`, `blue`, `indigo`, `purple` — each with stops `50`, `100`, …, `950`. Tailwind defaults are fine; pin in `primitive/color.ts`.

### Semantic mappings (default palette `indigo`, light)

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

Dark mode remaps the **same** semantic tokens to different primitives — components don't change.

Each theme (curated palette or tenant brand theme) ships its own `light` and `dark` mapping with the same key set. Switching themes never adds or removes a semantic token; it only changes the value each token points at. See `theming.md` for the theme registry and the (theme × mode) selector matrix.

### Platform-locked semantic subset

A subset of the semantic tokens is platform-locked: brand themes cannot override them. They convey **meaning**, not style.

| Locked token | Why |
|---|---|
| `success-fg`, `success-bg-subtle` | Green semantics — repurposing breaks "everything's fine" recognition |
| `warning-fg`, `warning-bg-subtle` | Amber semantics |
| `danger-fg`, `danger-bg-subtle` | Red semantics |
| `fg-on-accent` | Auto-derived as black or white per accent's luminance — picked for the tenant by the builder |

These keys are present in every theme (curated and brand) but the brand-theme serializer rejects writes to them. Curated palettes can deviate from the default green/amber/red only with a decisions-log entry — the colour-encodes-meaning convention is a platform contract.

`focus-ring` derives from `accent-fg` automatically with a min-contrast clamp against `bg-surface`. No theme overrides it directly.

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

- Two attributes on `<html>`: `data-theme="light" | "dark" | "mixed"` and `data-palette="<curated-id | brand-<uuid>>"`.
- A region-local subtree may carry `data-surface-theme="dark"` to opt into dark tokens locally (this is how `mixed` paints the sidebar).
- Persistence, resolution (user pick → tenant default → platform default, with `lock_level` of `none` / `allowlist` / `strict`), the cookie mirror used for FOUC-free first paint, the brand-theme builder, and the admin surfaces all live in `theming.md`. This doc is the vocabulary; that doc is the grammar.

## Adding a new token

1. Justify it (component reuse ≥ 3, or a meaningful new semantic role).
2. Add the primitive (if needed) → add the semantic key to **every curated palette**, in both `light` and `dark` → Tailwind preset.
3. Decide whether it's overrideable by brand themes or platform-locked. Update the brand-theme serializer's allowlist accordingly.
4. Update `docs/03_ux/design-tokens.md` (this file).
5. Open a PR; design review before merge.

For adding a new curated **palette** (rather than a new token), see `theming.md` → "Adding a curated palette". Tenant-created **brand themes** don't go through this process — they're created at runtime via the builder.

## Anti-patterns

- Raw hex / rgb in component code.
- Tailwind's primitive utilities (`bg-indigo-600`) used directly — use the semantic `bg-accent`.
- A component defining its own colour outside the token system.
- Two tokens with overlapping meaning (`fg-secondary` + `fg-muted`).

## Review checklist

- [ ] No raw colour / spacing / radius values in components
- [ ] Tokens flow through CSS custom properties, consumed by Tailwind theme
- [ ] Light + dark mapping in place for every curated palette for every new semantic token
- [ ] Platform-locked subset (`success-*`, `warning-*`, `danger-*`, `fg-on-accent`) decided and reflected in the brand-theme serializer
- [ ] Motion respects reduced-motion preference
- [ ] Tier respected: components → semantic → palette → primitive
- [ ] No component reads `data-theme` / `data-palette` to branch styles
