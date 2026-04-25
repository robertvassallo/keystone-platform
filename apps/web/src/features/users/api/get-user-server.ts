import "server-only";

import { apiFetchServer } from "@/shared/lib/api-server";

import type { UserDetail, UserDetailResult } from "../types";

const HTTP_FORBIDDEN = 403;
const HTTP_NOT_FOUND = 404;

/**
 * Server-side user detail fetch. Discriminates the three "non-throw"
 * outcomes (ok / forbidden / not_found) so the page can render the
 * right panel without try/catch.
 */
export async function getUserServer(id: string): Promise<UserDetailResult> {
  const response = await apiFetchServer(`/api/v1/users/${id}/`);

  if (response.status === HTTP_FORBIDDEN) return { kind: "forbidden" };
  if (response.status === HTTP_NOT_FOUND) return { kind: "not_found" };

  if (!response.ok) {
    throw new Error(`user-detail-server failed: ${String(response.status)}`);
  }

  const user = (await response.json()) as UserDetail;
  return { kind: "ok", user };
}
