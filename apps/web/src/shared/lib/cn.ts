import clsx, { type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Compose Tailwind classNames safely.
 *
 * `clsx` handles conditional class composition; `twMerge` resolves conflicting
 * Tailwind utilities so the last value wins predictably.
 */
export function cn(...inputs: readonly ClassValue[]): string {
  return twMerge(clsx(inputs));
}
