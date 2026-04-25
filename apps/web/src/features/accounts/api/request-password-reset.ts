"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { ForgotPasswordInput } from "../lib/schemas";

export async function requestPasswordReset(
  input: ForgotPasswordInput,
): Promise<void> {
  const response = await apiFetch("/api/v1/auth/password-reset/request/", {
    method: "POST",
    json: { email: input.email },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
}
