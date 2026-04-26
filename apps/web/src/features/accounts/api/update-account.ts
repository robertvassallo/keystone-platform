"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { Account } from "../types";

export interface UpdateAccountInput {
  readonly name?: string;
  readonly slug?: string;
}

export async function updateAccount(input: UpdateAccountInput): Promise<Account> {
  const body: Record<string, string> = {};
  if (input.name !== undefined) body.name = input.name;
  if (input.slug !== undefined) body.slug = input.slug;

  const response = await apiFetch("/api/v1/account/", {
    method: "PATCH",
    json: body,
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }

  return (await response.json()) as Account;
}
