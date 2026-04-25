"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { UserDetail } from "../types";

export async function getUser(id: string): Promise<UserDetail> {
  const response = await apiFetch(`/api/v1/users/${id}/`);
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  return (await response.json()) as UserDetail;
}
