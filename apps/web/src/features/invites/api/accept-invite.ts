"use client";

import type { User } from "@/features/accounts";
import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

export interface AcceptInviteInput {
  readonly uid: string;
  readonly token: string;
  readonly password: string;
}

export async function acceptInvite(input: AcceptInviteInput): Promise<User> {
  const response = await apiFetch("/api/v1/auth/invite/accept/", {
    method: "POST",
    json: input,
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as User;
}
