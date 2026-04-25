"use client";

import { apiFetch, ApiError, readProblem } from "@/shared/lib/api-client";

import type { SignUpInput } from "../lib/schemas";
import type { User } from "../types";

export async function signUp(input: SignUpInput): Promise<User> {
  const response = await apiFetch("/api/v1/auth/sign-up/", {
    method: "POST",
    json: { email: input.email, password: input.password },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as User;
}
