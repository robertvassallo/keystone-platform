"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { Invite } from "../types";

export async function sendInvite(input: {
  readonly email: string;
}): Promise<Invite> {
  const response = await apiFetch("/api/v1/invites/", {
    method: "POST",
    json: { email: input.email },
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as Invite;
}
