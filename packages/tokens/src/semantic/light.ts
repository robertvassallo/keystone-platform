/**
 * Semantic colour mappings — light theme.
 *
 * Components consume these; primitives are not used directly. The mapping
 * here mirrors the table in `docs/03_ux/design-tokens.md`.
 */

import { black, gray, green, indigo, red, white, amber } from "../primitive/color.js";

export const lightSemantic = {
  "color-bg-canvas": gray[50],
  "color-bg-surface": white,
  "color-bg-overlay": "rgb(17 24 39 / 0.5)",

  "color-fg-default": gray[900],
  "color-fg-muted": gray[600],
  "color-fg-subtle": gray[500],
  "color-fg-on-accent": white,

  "color-border-subtle": gray[200],
  "color-border-default": gray[300],
  "color-border-emphasis": gray[400],

  "color-accent-fg": indigo[600],
  "color-accent-emphasis": indigo[700],
  "color-accent-bg-subtle": indigo[50],

  "color-success-fg": green[600],
  "color-warning-fg": amber[600],
  "color-danger-fg": red[600],

  "color-shadow-rgb": "0 0 0",
  "color-black": black,
} as const;

export type SemanticToken = keyof typeof lightSemantic;
