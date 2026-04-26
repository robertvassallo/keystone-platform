import "server-only";

import { apiFetchServer } from "@/shared/lib/api-server";

export type ConfirmEmailVerificationResult =
  | { readonly kind: "ok" }
  | { readonly kind: "invalid" };

const HTTP_NO_CONTENT = 204;
const HTTP_UNPROCESSABLE = 422;

export interface ConfirmEmailVerificationServerInput {
  readonly uid: string;
  readonly token: string;
}

/**
 * Server-side confirm of an email-verification token. Discriminates
 * 422 invalid_verification_token from generic backend failures so the
 * verify-email page can render an "expired" panel instead of throwing.
 */
export async function confirmEmailVerificationServer(
  input: ConfirmEmailVerificationServerInput,
): Promise<ConfirmEmailVerificationResult> {
  const response = await apiFetchServer(
    "/api/v1/auth/email-verification/confirm/",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ uid: input.uid, token: input.token }),
    },
  );

  if (response.status === HTTP_NO_CONTENT) {
    return { kind: "ok" };
  }

  if (response.status === HTTP_UNPROCESSABLE) {
    return { kind: "invalid" };
  }

  throw new Error(`email-verification confirm failed: ${String(response.status)}`);
}
