import "server-only";

import { apiFetchServer } from "@/shared/lib/api-server";

import type {
  AuditEventListResponse,
  AuditEventListResult,
} from "../types";

const HTTP_FORBIDDEN = 403;

export interface ListAuditEventsServerInput {
  readonly page?: number;
  readonly pageSize?: number;
}

function buildQuery(input: ListAuditEventsServerInput): string {
  const params = new URLSearchParams();
  if (input.page !== undefined) params.set("page", String(input.page));
  if (input.pageSize !== undefined) {
    params.set("page_size", String(input.pageSize));
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

export async function listAuditEventsServer(
  input: ListAuditEventsServerInput = {},
): Promise<AuditEventListResult> {
  const response = await apiFetchServer(
    `/api/v1/audit/${buildQuery(input)}`,
  );

  if (response.status === HTTP_FORBIDDEN) {
    return { kind: "forbidden" };
  }

  if (!response.ok) {
    throw new Error(`audit-list failed: ${String(response.status)}`);
  }

  const body = (await response.json()) as AuditEventListResponse;
  return { kind: "ok", data: body.data, page: body.page };
}
