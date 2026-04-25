"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { UsersListResponse } from "../types";

export interface ListUsersInput {
  readonly page?: number;
  readonly pageSize?: number;
}

function buildQuery(input: ListUsersInput): string {
  const params = new URLSearchParams();
  if (input.page !== undefined) params.set("page", String(input.page));
  if (input.pageSize !== undefined) {
    params.set("page_size", String(input.pageSize));
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

export async function listUsers(
  input: ListUsersInput = {},
): Promise<UsersListResponse> {
  const response = await apiFetch(`/api/v1/users/${buildQuery(input)}`);
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  return (await response.json()) as UsersListResponse;
}
