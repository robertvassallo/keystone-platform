import { cache } from "react";

import { HTTP_UNAUTHORIZED } from "@/shared/lib/api-client";
import { apiFetchServer } from "@/shared/lib/api-server";

import type { MfaStatus } from "../types";

/**
 * Server-side ``/api/v1/auth/mfa/status/`` — used by the ``/mfa`` route's
 * Server Component to branch between enrolment and management UI.
 *
 * Returns ``null`` if the user isn't authenticated; the dashboard layout
 * has already redirected anonymous requests, so this is mostly defensive.
 */
export const getMfaStatusServer = cache(
  async (): Promise<MfaStatus | null> => {
    const response = await apiFetchServer("/api/v1/auth/mfa/status/");
    if (response.status === HTTP_UNAUTHORIZED) return null;
    if (!response.ok) {
      throw new Error(`mfa-status-server failed: ${String(response.status)}`);
    }
    return (await response.json()) as MfaStatus;
  },
);
