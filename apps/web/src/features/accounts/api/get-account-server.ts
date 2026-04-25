import { cache } from "react";

import { HTTP_UNAUTHORIZED } from "@/shared/lib/api-client";
import { apiFetchServer } from "@/shared/lib/api-server";

import type { Account, AccountResult } from "../types";

const HTTP_FORBIDDEN = 403;

/**
 * Server-side ``/api/v1/account/`` fetch.
 *
 * The (dashboard) layout already redirects anonymous requests, so the
 * 401 case is mostly defensive — we surface "forbidden" for both 401
 * and 403 so the caller renders a single panel.
 */
export const getAccountServer = cache(async (): Promise<AccountResult> => {
  const response = await apiFetchServer("/api/v1/account/");

  if (
    response.status === HTTP_UNAUTHORIZED ||
    response.status === HTTP_FORBIDDEN
  ) {
    return { kind: "forbidden" };
  }

  if (!response.ok) {
    throw new Error(`account-server failed: ${String(response.status)}`);
  }

  const account = (await response.json()) as Account;
  return { kind: "ok", account };
});
