"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

import type { Account } from "../types";

export async function getAccount(): Promise<Account> {
  const response = await apiFetch("/api/v1/account/");
  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
  return (await response.json()) as Account;
}
