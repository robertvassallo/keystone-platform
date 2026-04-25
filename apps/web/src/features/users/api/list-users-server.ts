import "server-only";

import { apiFetchServer } from "@/shared/lib/api-server";

import type { UsersListResponse, UsersListResult, UserStatus } from "../types";

const HTTP_FORBIDDEN = 403;

export interface ListUsersServerInput {
  readonly page?: number;
  readonly pageSize?: number;
  readonly q?: string | null;
  readonly status?: UserStatus | null;
}

function buildQuery(input: ListUsersServerInput): string {
  const params = new URLSearchParams();
  if (input.page !== undefined) params.set("page", String(input.page));
  if (input.pageSize !== undefined) {
    params.set("page_size", String(input.pageSize));
  }
  if (input.q !== undefined && input.q !== null && input.q !== "") {
    params.set("q", input.q);
  }
  if (input.status !== undefined && input.status !== null) {
    params.set("status", input.status);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

/**
 * Server-side users-list fetch. Discriminates 403 (non-staff) from
 * generic backend failures so the page can render a friendly
 * "access required" panel instead of throwing.
 */
export async function listUsersServer(
  input: ListUsersServerInput = {},
): Promise<UsersListResult> {
  const response = await apiFetchServer(`/api/v1/users/${buildQuery(input)}`);

  if (response.status === HTTP_FORBIDDEN) {
    return { kind: "forbidden" };
  }

  if (!response.ok) {
    throw new Error(`users-list failed: ${String(response.status)}`);
  }

  const body = (await response.json()) as UsersListResponse;
  return { kind: "ok", ...body };
}
