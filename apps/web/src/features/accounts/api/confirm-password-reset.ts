"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { ResetPasswordInput } from "../lib/schemas";

export async function confirmPasswordReset(
  input: ResetPasswordInput,
): Promise<void> {
  const response = await apiFetch("/api/v1/auth/password-reset/confirm/", {
    method: "POST",
    json: {
      uid: input.uid,
      token: input.token,
      password: input.password,
    },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
}
