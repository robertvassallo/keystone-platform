/** Semantic colour mappings — dark theme. */

import { gray, indigo, red, white, green, amber, black } from "../primitive/color.js";

export const darkSemantic = {
  "color-bg-canvas": gray[950],
  "color-bg-surface": gray[900],
  "color-bg-overlay": "rgb(0 0 0 / 0.6)",

  "color-fg-default": gray[50],
  "color-fg-muted": gray[400],
  "color-fg-subtle": gray[500],
  "color-fg-on-accent": white,

  "color-border-subtle": gray[800],
  "color-border-default": gray[700],
  "color-border-emphasis": gray[600],

  "color-accent-fg": indigo[400],
  "color-accent-emphasis": indigo[300],
  "color-accent-bg-subtle": indigo[900],

  "color-success-fg": green[500],
  "color-warning-fg": amber[500],
  "color-danger-fg": red[500],

  "color-shadow-rgb": "0 0 0",
  "color-black": black,
} as const;
