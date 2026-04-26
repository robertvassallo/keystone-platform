# Theming

> **Status:** design / not yet implemented. See decisions-log entry of the same date.

How the platform paints itself. The token system in `design-tokens.md` is the *vocabulary*; this doc is the *grammar* — how a user's choice of light / dark / mixed and a palette (curated or tenant-created) resolves into the CSS custom properties components consume.

## Vocabulary

- **Palette** — a complete set of semantic-token mappings (light + dark variants). Two kinds:
  - **Curated palette** — ships with the platform (`indigo`, `slate`, `emerald`, …). CI-contrast-checked.
  - **Brand theme** — a tenant-created palette stored in the DB. Built in the in-app builder.
- **Theme** — user-facing label for "the palette you picked." The picker calls them themes; the architecture calls them palettes.
- **Mode** — `light` / `dark` / `mixed` / `system`.

## Goals

1. Three user-visible knobs: **mode**, **theme**, **density**. Density already lives in `dashboard-layout.md`.
2. Tenants get real brand expression — owners can build **brand themes** that become first-class alongside the curated set.
3. Users keep autonomy by default — they pick any allowed theme; brand themes are *invitation*, not *imposition*. Owners may opt into stricter locking when brand consistency truly matters.
4. Switching is instant, no flash of unstyled content, no layout shift.
5. Curated palettes meet WCAG 2.2 AA at build time. Brand themes are warned-not-blocked while users keep the escape hatch; locking removes the escape and re-imposes AA at publish time.
6. Component code never branches on theme. All variation flows through token custom properties.

## Three orthogonal axes

| Axis | Values | What it controls |
|---|---|---|
| **Mode** | `light`, `dark`, `mixed`, `system` | Which token block applies to the canvas. `system` follows `prefers-color-scheme`. `mixed` = light canvas, dark sidebar. |
| **Palette** | A curated palette id (`indigo`, `slate`, …) or a brand-theme id (`brand-<uuid>`) | Which set of token values backs the semantic layer. Each palette ships a `light` and a `dark` mapping. |
| **Surface** | per-region override | A subtree can opt into a different mode locally — e.g. a dark sidebar inside a light canvas. Surface override is what makes `mixed` possible. |

The three are independent. Any (mode, palette) combination is valid; surface is set per region by the layout components.

## Token layering

```
primitive  →  palette  →  semantic  →  component
```

The `palette` tier covers both curated and brand-theme palettes. Components consume **semantic** tokens only — they don't know which palette is active.

```ts
// packages/tokens/src/palettes/indigo.ts (curated example)
import { gray, indigo } from "../primitive/color.js";

export const indigoLight = {
  "color-bg-canvas":      gray[50],
  "color-fg-default":     gray[900],
  "color-accent-fg":      indigo[600],
  "color-accent-emphasis":indigo[700],
  // ...full semantic set (minus the platform-locked subset)
};
export const indigoDark = { /* same keys, dark values */ };
```

The build emits, for every (curated palette × mode) pair, one CSS block:

```css
[data-palette="indigo"][data-theme="light"]  { --color-bg-canvas: #f9fafb; … }
[data-palette="indigo"][data-theme="dark"]   { --color-bg-canvas: #030712; … }
[data-palette="emerald"][data-theme="light"] { … }
[data-palette="emerald"][data-theme="dark"]  { … }

/* surface override — re-applies the dark block to a local subtree */
[data-surface-theme="dark"] { --color-bg-canvas: #030712; … }
```

Brand themes ship their CSS the same way, but server-rendered for the active tenant only — see "Brand themes" below.

### Why custom properties (not CSS classes per palette)

Cascade. A surface override (`data-surface-theme="dark"` on `<aside>`) re-declares the token custom properties for the subtree. Components inside the sidebar paint with the dark values without knowing they're in a sidebar — they just read `var(--color-bg-canvas)` and the cascaded value is dark. This is the only thing that makes `mixed` possible without forking every component.

## Selectors

Set on `<html>`:

```html
<html data-theme="light" data-palette="indigo">
```

| Attribute | Values | Default |
|---|---|---|
| `data-theme` | `light` \| `dark` \| `mixed` | `light` |
| `data-palette` | a curated palette id (`indigo`, `slate`, …) or a brand-theme id (`brand-<uuid>`) | `indigo` |

`mixed` is implemented as `data-theme="light"` *plus* the navigation surface carrying `data-surface-theme="dark"`. The runtime resolves user preference into this combination.

`system` is resolved client-side at first paint into `light` or `dark` based on `prefers-color-scheme`, then re-resolved on `change`. It never reaches `data-theme="system"`.

The Tailwind preset's `darkMode: ["class", '[data-theme="dark"]']` (already configured) continues to work — the dark variant fires for the whole document under `dark`. Surface overrides do *not* trigger Tailwind's `dark:` modifier; they re-cascade the custom properties, which is enough because components consume tokens, not `dark:` utilities.

## Mixed mode

```
┌──────────────┬───────────────────────────────────┐
│   sidebar    │           main content            │
│ (dark tokens)│         (light tokens)            │
│              │                                   │
└──────────────┴───────────────────────────────────┘
```

Implementation:

```tsx
// apps/web/src/components/layout/AppShell.tsx
const mode = useResolvedTheme();           // 'light' | 'dark' | 'mixed'
const sidebarSurface = mode === 'mixed' ? 'dark' : undefined;

return (
  <div className="flex">
    <aside data-surface-theme={sidebarSurface} className="bg-bg-surface text-fg">
      <Nav />
    </aside>
    <main className="bg-bg-canvas text-fg">{children}</main>
  </div>
);
```

The reverse (`light sidebar, dark content`) is intentionally not offered. One mixed combination keeps the design language consistent and the contrast story tractable.

When the active palette is a brand theme, mixed mode pulls the sidebar's tokens from the *brand theme's `dark` variant* and the content from its `light` variant. The mechanism doesn't care whether tokens come from a curated palette or a brand theme — both ship both modes.

The seam between the two surfaces is a `1px` `--color-border-emphasis` line. No drop-shadow, no gradient — the dark→light contrast is itself the strongest cue and shadow on a vertical seam reads as an accident.

## Resolution order

A user's effective palette is computed as:

```
effective = userPick   if userPick is in the tenant's allowlist (or no allowlist) and lock_level != strict
          | tenantDefault   otherwise
          | platformDefault   if tenant has no default
```

Sources, in precedence order:

1. **User preference** — what the signed-in user picked. Unauthenticated visitors only have steps 2–3.
2. **Tenant default** — what the owner picked for the tenant. Subject to the lock level (below).
3. **Platform default** — `light` / `indigo`. Hardcoded fallback.

### Lock levels

`Account.theme_lock_level` — three values, self-explaining:

| Lock | Meaning | When to use |
|---|---|---|
| `none` | User picks anything available (curated + tenant brand themes). Allowlist still applies if set. | Default. |
| `allowlist` | User picks only from the tenant's allowlist (e.g. only the brand themes). | Nudge users to the brand without forbidding personal preference within an approved set. |
| `strict` | User can't change palette — only `mode` and `density`. Tenant default is binding. | Brand-strict environments (regulated, customer-facing kiosks, white-label installs). |

Mode is **always** user-controlled. Lock applies to palette only — light vs dark is a personal accessibility / preference choice that owners shouldn't override.

Examples:

| Scenario | Effective |
|---|---|
| New user, no tenant default | platform default — light, indigo |
| User picks dark + emerald, tenant default light/slate, lock=none | dark, emerald |
| Tenant publishes "Acme primary" brand theme, sets it as default, lock=allowlist with `[Acme primary, Acme dark]` | user picks within the two brand themes; mode free |
| Tenant locks=strict on Acme primary, user picks emerald | user's mode kept, palette = Acme primary |
| User picked a curated palette that the tenant later removed from allowlist | user's mode kept, palette falls back to tenant default |

The fallback never throws. An unknown palette id in the user record (e.g. brand theme deleted, palette removed) silently degrades to tenant default, then platform default.

## Persistence

### Database

```python
# apps/api/apps/accounts/models/user.py
theme_mode = models.CharField(max_length=16, choices=ThemeMode.choices, default=ThemeMode.SYSTEM)
theme_palette = models.CharField(max_length=64, default="")  # "" means inherit; "indigo" / "brand-<uuid>" otherwise

# apps/api/apps/accounts/models/account.py
theme_default_mode = models.CharField(max_length=16, choices=ThemeMode.choices, default=ThemeMode.LIGHT)
theme_default_palette = models.CharField(max_length=64, default="indigo")
theme_lock_level = models.CharField(max_length=16, choices=ThemeLockLevel.choices, default=ThemeLockLevel.NONE)
theme_allowlist = models.JSONField(default=list)  # [] = all allowed; otherwise list of palette ids

# apps/api/apps/accounts/models/brand_theme.py — new
class BrandTheme(models.Model):
    id = models.UUIDField(primary_key=True, ...)
    tenant = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="brand_themes")
    name = models.CharField(max_length=80)              # "Acme primary"
    tokens_light = models.JSONField()                   # { "color-accent-fg": "#7B2CBF", ... }
    tokens_dark = models.JSONField()                    # same key set
    is_published = models.BooleanField(default=False)
    contrast_audit = models.JSONField(default=dict)     # last AA check, per-pair
    created_at, updated_at, deleted_at, created_by, ...
```

Empty string on `User.theme_palette` means "inherit from tenant"; explicit value means "override". Same pattern as a typical preference column.

### Cookie mirror

On sign-in (and on any change to user / tenant theme settings), the server sets two cookies:

| Cookie | Value | Lifetime | Purpose |
|---|---|---|---|
| `theme_mode` | resolved mode (`light` / `dark` / `mixed`, never `system`) | 1 year, `SameSite=Lax` | First-paint attribute |
| `theme_palette` | resolved palette id | 1 year, `SameSite=Lax` | First-paint attribute |

Cookies are not the source of truth — they're a pre-paint cache. The DB is canonical. On sign-out, cookies are cleared.

### First paint

Server reads cookies in the App Router root layout, and (when the active palette is a brand theme) injects the tenant-scoped brand-theme CSS inline:

```tsx
// apps/web/src/app/layout.tsx
const cookies = (await import('next/headers')).cookies();
const mode = cookies.get('theme_mode')?.value ?? 'light';
const palette = cookies.get('theme_palette')?.value ?? 'indigo';

const brandStyles = palette.startsWith('brand-')
  ? await loadBrandThemeCss(palette)   // small <style> block; cached per (tenant, palette)
  : null;

return (
  <html lang="en" data-theme={mode === 'mixed' ? 'light' : mode} data-palette={palette}>
    <head>{brandStyles && <style>{brandStyles}</style>}</head>
    …
  </html>
);
```

Curated palettes are statically baked into `tokens.css` and ship for everyone. Brand-theme CSS is *only* injected for the tenant whose palette it is — no global cross-tenant leak.

For `system`, an inline pre-paint script runs before first paint to resolve `prefers-color-scheme` and patch the attribute if the cookie was stale.

## API contract

### Read

`GET /api/v1/me/` includes a resolved theme block:

```json
{
  "id": "…",
  "theme": {
    "mode": "dark",
    "palette": "brand-3f9e…",
    "palette_name": "Acme primary",
    "lock_level": "allowlist",
    "allowlist": ["indigo", "slate", "brand-3f9e…", "brand-7c2a…"]
  }
}
```

`mode` and `palette` are the *resolved* values (what the UI should paint). `lock_level` and `allowlist` are echoed so the user-settings UI can disable / filter the picker accordingly.

### List available palettes

`GET /api/v1/themes/` — returns the curated palettes plus the tenant's published brand themes (filtered by allowlist if `lock_level != none`). Used by the picker:

```json
{
  "items": [
    { "id": "indigo",       "name": "Indigo",       "kind": "curated" },
    { "id": "slate",        "name": "Slate",        "kind": "curated" },
    { "id": "brand-3f9e…",  "name": "Acme primary", "kind": "brand" }
  ]
}
```

### Write — user

`PATCH /api/v1/me/` accepts `theme_mode` and `theme_palette`. `theme_palette = ""` clears the override. Server-side validates against the tenant's allowlist + lock level; rejected picks return `422 theme_not_permitted`.

### Brand-theme management — tenant owner only (`IsTenantOwnerOrStaff`)

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/brand-themes/` | List the tenant's brand themes (drafts + published) |
| `POST /api/v1/brand-themes/` | Create a draft |
| `PATCH /api/v1/brand-themes/<id>/` | Edit (tokens, name, publish/unpublish) |
| `POST /api/v1/brand-themes/<id>/contrast-check/` | Re-run AA check; returns per-pair results |
| `DELETE /api/v1/brand-themes/<id>/` | Soft-delete (users on it fall back to tenant default) |

`PATCH /api/v1/account/` accepts `theme_default_mode`, `theme_default_palette`, `theme_lock_level`, `theme_allowlist`. Same per-method permission shape as tenant rename. Setting `theme_lock_level = "strict"` on a brand theme that fails AA returns `422 contrast_required_for_strict_lock`.

## Admin UI surfaces

| Page | Audience | Controls |
|---|---|---|
| `/settings/profile/appearance` | every user | mode picker, theme picker (curated + tenant brand themes, filtered by allowlist), density, preview |
| `/settings/account/branding` | tenant owner / staff | tenant default mode, tenant default palette, allowlist multi-select, lock level (`none` / `allowlist` / `strict`), preview |
| `/settings/account/branding/themes` | tenant owner / staff | list of brand themes (name, status, last-edited), "New brand theme" CTA |
| `/settings/account/branding/themes/<id>` | tenant owner / staff | the brand-theme builder (see below) |

All pages share the `<ThemePreview>` component — a small mock dashboard frame that re-paints under a local surface override so the user sees the effect without committing the change.

The dashboard widget gains a "Branding" link visible only when `me.is_tenant_owner || me.is_staff`, mirroring the existing "Audit log" pattern.

## Brand themes

A brand theme is a tenant-owned palette stored in the DB, sitting alongside the curated set in the picker.

### The builder — lite mode (the 95% case)

Three inputs:

1. **Accent hex** (required) — one colour. The system generates a 50→950 ramp algorithmically (CIE-Lab interpolation, same shape as the curated ramps).
2. **Neutral preset** (default `cool gray`) — `cool gray` / `true gray` / `warm gray` / `slate`. Drives canvas, surface, fg, and border tokens.
3. **Mode coverage** — light + dark previewed side-by-side. The dark variant auto-derives from light (accent desaturated 1–2 stops, canvas swapped to `gray-950`). Tenant can tweak the dark variant independently.

This produces a complete `{ tokens_light, tokens_dark }` blob. ~95% of tenants stop here.

### The builder — advanced mode

For tenants whose design team wants to tune individual surfaces. Exposes the full overrideable token set (see "Platform-locked semantic subset" below). Each token has a colour picker; the live preview re-paints on change. Reset-to-derived button per token.

### Live contrast feedback

The builder runs a real-time AA check on every token change and shows:

- **Per-pair results** — green / amber / red badges next to the affected pairs (e.g. "fg-default on bg-canvas: 12.4 : 1 ✓ AA-pass").
- **Sticky summary** — banner at the top: "All checks pass" / "3 pairs below AA — review before publish."
- **Non-blocking on draft / publish** — tenant can save and publish anyway, with a confirm dialog calling out the failing pairs.

### Platform-locked semantic subset

Brand themes can override the *neutral / accent / surface* tokens. They **cannot** override:

| Token | Reason |
|---|---|
| `color-success-fg`, `color-success-bg-subtle` | Green semantics — repurposing breaks "everything's fine" recognition |
| `color-warning-fg`, `color-warning-bg-subtle` | Amber semantics — same |
| `color-danger-fg`, `color-danger-bg-subtle` | Red semantics — same |
| `color-fg-on-accent` | Auto-derived as black or white per accent's luminance — the builder picks for you |

These are platform-locked because they convey **meaning**, not style. A "danger" message rendered in the tenant's pink because pink is their brand is a broken system, not a customised one. The builder UI doesn't surface controls for them; the API rejects writes to them with `422 platform_locked_token`.

`color-focus-ring` derives from `color-accent-fg` automatically with a min-contrast clamp — if a tenant's accent doesn't meet 3 : 1 against `bg-surface`, the ring darkens or lightens to clear the bar. This is invisible to the tenant; it just works.

### Lifecycle

```
draft  →  published  →  archived (soft-delete)
```

- **Draft** — visible only in the builder. Not in the user picker.
- **Published** — appears in the user picker (subject to allowlist). Editable; edits propagate live via re-emitted CSS on next request.
- **Archived** — soft-deleted. Users on the archived palette fall back to tenant default on next sign-in. Not restorable from the UI; admin-DB recovery only.

A tenant can have N brand themes (typical: 1–3). No hard cap; the `BrandTheme` table is small and per-tenant.

### Contrast posture — graduated, not binary

| Where | Posture |
|---|---|
| Curated palette | CI contrast check, **hard fail** on AA. Platform's promise. |
| Brand theme, draft | Live warnings in builder. **Doesn't block** save. |
| Brand theme, published, `lock_level != strict` | Live warnings; **doesn't block** publish. Users can escape to a curated palette → they keep readable UI. |
| Brand theme, published, `lock_level = strict` | **Hard-fails publish** if AA fails. Strict lock removes the user escape; the platform re-imposes AA in its place. |

The architecture *gets stricter* exactly where user choice goes away. Locking implies responsibility.

### Storage + injection

- `tokens_light` / `tokens_dark` are JSONB blobs. Values validated as `^#[0-9a-f]{6}$` or `rgb(... )` / `rgba(... )` strings only — never raw CSS.
- CSS for a published brand theme is rendered server-side by a small templater that emits a `<style>` block keyed `[data-palette="brand-<uuid>"][data-theme="light"] { … }`. No client-side string interpolation.
- Cached per (tenant, palette, last_modified). Cache busts on PATCH.
- Brand-theme CSS is injected only for the active tenant (and only for the active palette if the tenant has multiple, with a small additional block for the user's previous palette to keep cookie-stale paint usable).

### Adding a curated palette (still curated, not BYO)

1. Add `packages/tokens/src/palettes/<name>.ts` exporting `{ light, dark }` semantic mappings.
2. Register in `packages/tokens/src/palettes/index.ts`.
3. Run `pnpm --filter @keystone/tokens build` — emits CSS and updates `tokens.d.ts`.
4. Run `pnpm --filter @keystone/tokens check:contrast` — fails CI if any pair drops below WCAG AA.
5. Add the id to the `CuratedPalette` choices in the API and migrate.
6. Update this doc's "Curated palettes" table.

## Curated palettes

Initial set; expand cautiously — every new curated palette is a contrast-matrix expansion the platform owns.

| Id | Neutral ramp | Accent ramp | Use case |
|---|---|---|---|
| `indigo` | gray | indigo | Default |
| `slate` | slate | sky | Cool, professional |
| `emerald` | gray | emerald | Growth, finance |
| `rose` | gray | rose | Consumer, playful |
| `amber` | stone | amber | Warm, editorial |
| `mono` | gray | gray (darker step) | Brand-strict tenants who want UI to disappear; pairs cleanly with strong tenant chrome |

`mono` exists specifically for tenants whose brand colour doesn't fit any palette and who'd rather have a quiet UI behind their own chrome.

## Accessibility

- **Curated palette contrast**: every (palette × mode) must meet WCAG 2.2 AA. CI-enforced; new curated palettes can't merge if any pair drops below 4.5 : 1 for body text or 3 : 1 for UI.
- **Brand theme contrast**: warned in builder; required only when `lock_level = strict`. The user-escape-hatch carries the burden otherwise.
- **`prefers-color-scheme`**: honoured when mode = `system`. Re-resolved on OS theme change without a page reload.
- **`prefers-reduced-motion`**: theme-change transitions disabled when the user has reduced motion set.
- **`prefers-contrast`**: not implemented in v1 but the architecture leaves room — a future `high-contrast` mode adds a third value to the mode axis.
- **No information conveyed by colour alone**: theme choice never gates content. Status badges still pair colour with an icon and text. The platform-locked success/warning/danger tokens guarantee this stays true even when a tenant builds a brand theme.
- **Focus rings**: ring colour derives from `--color-accent-fg` with a min-contrast clamp against `--color-bg-surface`. Works for any palette automatically.

## Anti-patterns

| Don't | Do |
|---|---|
| Read `data-theme` / `data-palette` in component code to branch styles | Read tokens via Tailwind classes (`bg-bg-canvas`); they re-paint via cascade |
| Hardcode a palette's primitive (`bg-indigo-600`) anywhere outside `palettes/*.ts` | Use the semantic class (`bg-accent`) |
| Persist theme only in `localStorage` | Persist in DB, mirror to cookie for first paint |
| Set `data-surface-theme="light"` on a sub-region "to force light mode here" | Surface overrides exist for the navigation rail in mixed mode only. New uses require a decisions-log entry. |
| Add a curated palette without contrast check | Run the contrast check; failures block merge |
| Branch component code on `mode === 'mixed'` | Surface scope is set at the layout level; components stay agnostic |
| Let brand themes override `success-*` / `warning-*` / `danger-*` | Platform-locked. Builder doesn't surface these; API rejects them |
| Inject brand-theme CSS globally for every tenant | Inject only for the active tenant, server-side, scoped by `[data-palette="brand-<uuid>"]` |
| Use `lock_level = strict` to "save users from themselves" | Strict is for brand-strict environments. Default to `none`; the user escape hatch is what makes brand themes safe. |

## Review checklist

- [ ] No raw colour values in components — semantic tokens only
- [ ] No theme branching in component code (no `if (theme === 'dark')`)
- [ ] New curated palette added the file in `packages/tokens/src/palettes/` and ran the build
- [ ] Curated palette contrast check passes for every (palette × mode)
- [ ] Brand-theme tokens validated as colour strings only (no CSS injection)
- [ ] Brand-theme CSS scoped per tenant + palette; never global
- [ ] Platform-locked tokens (`success-*`, `warning-*`, `danger-*`, `fg-on-accent`) rejected by the brand-theme serializer
- [ ] `lock_level = strict` requires AA-passing contrast at publish time
- [ ] User preference round-trips: DB → cookie → first-paint attribute → resolved tokens
- [ ] Allowlist + lock level enforced server-side in `MeUpdateSerializer.validate_theme_palette`
- [ ] `prefers-color-scheme` and `prefers-reduced-motion` honoured
- [ ] `<ThemePreview>` reflects the user's pending choice without committing
