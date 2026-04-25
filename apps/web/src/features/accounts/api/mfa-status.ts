"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { MfaStatus } from "../types";

export async function getMfaStatus(): Promise<MfaStatus> {
  const response = await apiFetch("/api/v1/auth/mfa/status/");
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  return (await response.json()) as MfaStatus;
}
