/**
 * Primitive colour palette — raw scales. Components must not consume these
 * directly; semantic tokens map them to roles in `semantic/`.
 */

export const gray = {
  50: "#f9fafb",
  100: "#f3f4f6",
  200: "#e5e7eb",
  300: "#d1d5db",
  400: "#9ca3af",
  500: "#6b7280",
  600: "#4b5563",
  700: "#374151",
  800: "#1f2937",
  900: "#111827",
  950: "#030712",
} as const;

export const indigo = {
  50: "#eef2ff",
  100: "#e0e7ff",
  200: "#c7d2fe",
  300: "#a5b4fc",
  400: "#818cf8",
  500: "#6366f1",
  600: "#4f46e5",
  700: "#4338ca",
  800: "#3730a3",
  900: "#312e81",
  950: "#1e1b4b",
} as const;

export const red = {
  500: "#ef4444",
  600: "#dc2626",
  700: "#b91c1c",
} as const;

export const amber = {
  500: "#f59e0b",
  600: "#d97706",
  700: "#b45309",
} as const;

export const green = {
  500: "#22c55e",
  600: "#16a34a",
  700: "#15803d",
} as const;

export const black = "#000000";
export const white = "#ffffff";
