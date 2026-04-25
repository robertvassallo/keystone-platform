import { cache } from "react";

import { HTTP_UNAUTHORIZED } from "@/shared/lib/api-client";
import { apiFetchServer } from "@/shared/lib/api-server";

import type { User } from "../types";

/**
 * Server-side ``/api/v1/auth/me/`` — used by route layouts that gate on
 * authentication. Returns ``null`` for anonymous sessions; throws on any
 * other non-OK response so transient backend failures surface as a 500
 * rather than silently logging the user out.
 *
 * Wrapped in React's ``cache`` so layout + page calls within a single
 * render hit the API only once.
 */
export const getMeServer = cache(async (): Promise<User | null> => {
  const response = await apiFetchServer("/api/v1/auth/me/");
  if (response.status === HTTP_UNAUTHORIZED) return null;
  if (!response.ok) {
    throw new Error(`me-server failed: ${String(response.status)}`);
  }
  return (await response.json()) as User;
});
