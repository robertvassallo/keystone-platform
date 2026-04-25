"use client";

import { apiFetch, HTTP_UNAUTHORIZED } from "@/shared/lib/api-client";

import type { User } from "../types";

export async function getMe(): Promise<User | null> {
  const response = await apiFetch("/api/v1/auth/me/");
  if (response.status === HTTP_UNAUTHORIZED) return null;
  if (!response.ok) throw new Error(`me failed: ${String(response.status)}`);
  return (await response.json()) as User;
}
