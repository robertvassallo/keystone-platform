"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { User } from "../types";

export async function verifyMfaChallenge(code: string): Promise<User> {
  const response = await apiFetch("/api/v1/auth/mfa/verify/", {
    method: "POST",
    json: { code },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as User;
}
