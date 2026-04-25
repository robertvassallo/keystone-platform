/**
 * Shared Tailwind preset.
 *
 * Maps Tailwind theme keys to the CSS custom properties emitted by
 * `@keystone/tokens` (see `dist/tokens.css`). Apps consume this via:
 *
 *     import preset from "@keystone/config/tailwind.preset";
 */

import type { Config } from "tailwindcss";

const preset: Partial<Config> = {
  darkMode: ["class", '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        bg: {
          canvas: "var(--color-bg-canvas)",
          surface: "var(--color-bg-surface)",
          overlay: "var(--color-bg-overlay)",
        },
        fg: {
          DEFAULT: "var(--color-fg-default)",
          muted: "var(--color-fg-muted)",
          subtle: "var(--color-fg-subtle)",
          "on-accent": "var(--color-fg-on-accent)",
        },
        border: {
          subtle: "var(--color-border-subtle)",
          DEFAULT: "var(--color-border-default)",
          emphasis: "var(--color-border-emphasis)",
        },
        accent: {
          DEFAULT: "var(--color-accent-fg)",
          fg: "var(--color-accent-fg)",
          emphasis: "var(--color-accent-emphasis)",
          "bg-subtle": "var(--color-accent-bg-subtle)",
        },
        success: { fg: "var(--color-success-fg)" },
        warning: { fg: "var(--color-warning-fg)" },
        danger: { fg: "var(--color-danger-fg)" },
      },
      borderRadius: {
        none: "0",
        sm: "4px",
        md: "6px",
        lg: "8px",
        xl: "12px",
        "2xl": "16px",
        full: "9999px",
      },
      fontFamily: {
        sans: [
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
      transitionDuration: {
        instant: "75ms",
        fast: "150ms",
        DEFAULT: "200ms",
        slow: "300ms",
      },
      transitionTimingFunction: {
        DEFAULT: "cubic-bezier(0.4, 0, 0.2, 1)",
        out: "cubic-bezier(0, 0, 0.2, 1)",
        in: "cubic-bezier(0.4, 0, 1, 1)",
      },
    },
  },
};

export default preset;
