"use client";

import {
  ApiError,
  apiFetch,
  HTTP_NO_CONTENT,
  readProblem,
} from "@/shared/lib/api-client";

export async function signOut(): Promise<void> {
  const response = await apiFetch("/api/v1/auth/sign-out/", { method: "POST" });
  if (!response.ok && response.status !== HTTP_NO_CONTENT) {
    throw new ApiError(await readProblem(response), response);
  }
}
