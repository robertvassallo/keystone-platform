"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

export async function disableMfa(currentPassword: string): Promise<void> {
  const response = await apiFetch("/api/v1/auth/mfa/disable/", {
    method: "POST",
    json: { current_password: currentPassword },
  });
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
}

export async function regenerateRecoveryCodes(
  currentPassword: string,
): Promise<readonly string[]> {
  const response = await apiFetch(
    "/api/v1/auth/mfa/recovery-codes/regenerate/",
    {
      method: "POST",
      json: { current_password: currentPassword },
    },
  );
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  const body = (await response.json()) as { recovery_codes: readonly string[] };
  return body.recovery_codes;
}
