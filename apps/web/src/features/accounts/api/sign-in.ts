"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { SignInInput } from "../lib/schemas";
import type { User } from "../types";

export type SignInResult =
  | { readonly kind: "signed_in"; readonly user: User }
  | { readonly kind: "mfa_required" };

const HTTP_OK = 200;
const HTTP_ACCEPTED = 202;

export async function signIn(input: SignInInput): Promise<SignInResult> {
  const response = await apiFetch("/api/v1/auth/sign-in/", {
    method: "POST",
    json: {
      email: input.email,
      password: input.password,
      remember_me: input.rememberMe,
    },
  });

  if (response.status === HTTP_OK) {
    return { kind: "signed_in", user: (await response.json()) as User };
  }
  if (response.status === HTTP_ACCEPTED) {
    return { kind: "mfa_required" };
  }

  throw new ApiError(await readProblem(response), response);
}
