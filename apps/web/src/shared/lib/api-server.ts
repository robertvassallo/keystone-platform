/**
 * Server-side API client used by Server Components.
 *
 * Server-side requests can't rely on Next.js rewrites, so they hit the
 * absolute internal API URL and forward the browser's cookies (taken
 * from ``next/headers``) to keep the session intact.
 */

import "server-only";

import { cookies } from "next/headers";

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL ?? "http://localhost:8000";

export async function apiFetchServer(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const cookieHeader = (await cookies()).toString();
  const headers = new Headers(init.headers);
  if (cookieHeader) headers.set("cookie", cookieHeader);

  return fetch(`${INTERNAL_API_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
}
