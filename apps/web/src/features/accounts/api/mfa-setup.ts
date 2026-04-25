"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { MfaSetupPayload } from "../types";

export async function startMfaSetup(): Promise<MfaSetupPayload> {
  const response = await apiFetch("/api/v1/auth/mfa/setup/", { method: "POST" });
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  return (await response.json()) as MfaSetupPayload;
}

export async function confirmMfaSetup(code: string): Promise<readonly string[]> {
  const response = await apiFetch("/api/v1/auth/mfa/setup/confirm/", {
    method: "POST",
    json: { code },
  });
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  const body = (await response.json()) as { recovery_codes: readonly string[] };
  return body.recovery_codes;
}
