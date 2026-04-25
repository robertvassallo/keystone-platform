"use client";

import { apiFetch, ApiError, readProblem } from "@/shared/lib/api-client";

import type { SignInInput } from "../lib/schemas";
import type { User } from "../types";

export async function signIn(input: SignInInput): Promise<User> {
  const response = await apiFetch("/api/v1/auth/sign-in/", {
    method: "POST",
    json: {
      email: input.email,
      password: input.password,
      remember_me: input.rememberMe,
    },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as User;
}
