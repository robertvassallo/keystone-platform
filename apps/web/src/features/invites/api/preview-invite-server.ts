import "server-only";

import { apiFetchServer } from "@/shared/lib/api-server";

import type { InvitePreview, InvitePreviewResult } from "../types";

const HTTP_OK = 200;
const HTTP_UNPROCESSABLE = 422;

export interface PreviewInviteServerInput {
  readonly uid: string;
  readonly token: string;
}

export async function previewInviteServer(
  input: PreviewInviteServerInput,
): Promise<InvitePreviewResult> {
  const params = new URLSearchParams({ uid: input.uid, token: input.token });
  const response = await apiFetchServer(
    `/api/v1/auth/invite/preview/?${params.toString()}`,
  );

  if (response.status === HTTP_OK) {
    const preview = (await response.json()) as InvitePreview;
    return { kind: "ok", preview };
  }

  if (response.status === HTTP_UNPROCESSABLE) {
    return { kind: "invalid" };
  }

  throw new Error(`invite-preview failed: ${String(response.status)}`);
}
