"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { User } from "../types";

export interface UpdateMeInput {
  readonly firstName?: string;
  readonly lastName?: string;
}

export async function updateMe(input: UpdateMeInput): Promise<User> {
  const body: Record<string, string> = {};
  if (input.firstName !== undefined) body.first_name = input.firstName;
  if (input.lastName !== undefined) body.last_name = input.lastName;

  const response = await apiFetch("/api/v1/auth/me/", {
    method: "PATCH",
    json: body,
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as User;
}
