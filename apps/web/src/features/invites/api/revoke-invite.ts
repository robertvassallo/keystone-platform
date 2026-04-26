"use client";

import { ApiError, apiFetch, readProblem } from "@/shared/lib/api-client";

export async function revokeInvite(input: {
  readonly id: string;
}): Promise<void> {
  const response = await apiFetch(`/api/v1/invites/${input.id}/`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new ApiError(await readProblem(response), response);
  }
}
