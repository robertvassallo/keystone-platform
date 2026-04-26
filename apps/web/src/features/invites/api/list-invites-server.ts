import "server-only";

import { apiFetchServer } from "@/shared/lib/api-server";

import type {
  Invite,
  InvitesListResponse,
  InvitesListResult,
} from "../types";

const HTTP_FORBIDDEN = 403;

export interface ListInvitesServerInput {
  readonly status?: "pending" | "accepted" | "revoked" | "expired";
}

function buildQuery(input: ListInvitesServerInput): string {
  if (input.status === undefined) return "";
  const params = new URLSearchParams({ status: input.status });
  return `?${params.toString()}`;
}

export async function listInvitesServer(
  input: ListInvitesServerInput = {},
): Promise<InvitesListResult> {
  const response = await apiFetchServer(`/api/v1/invites/${buildQuery(input)}`);

  if (response.status === HTTP_FORBIDDEN) {
    return { kind: "forbidden" };
  }

  if (!response.ok) {
    throw new Error(`invites-list failed: ${String(response.status)}`);
  }

  const body = (await response.json()) as InvitesListResponse;
  const data: readonly Invite[] = body.data;
  return { kind: "ok", data };
}
