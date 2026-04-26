"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

export async function requestEmailVerification(): Promise<void> {
  const response = await apiFetch("/api/v1/auth/email-verification/request/", {
    method: "POST",
    json: {},
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
}
