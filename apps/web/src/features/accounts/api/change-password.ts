"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { ChangePasswordInput } from "../lib/schemas";

export async function changePassword(
  input: ChangePasswordInput,
): Promise<void> {
  const response = await apiFetch("/api/v1/auth/password/change/", {
    method: "POST",
    json: {
      current_password: input.currentPassword,
      new_password: input.newPassword,
    },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
}
