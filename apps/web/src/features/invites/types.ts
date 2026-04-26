/** Public types for the invites feature. */

export type InviteStatus = "pending" | "accepted" | "revoked" | "expired";

export interface Invite {
  readonly id: string;
  readonly email: string;
  readonly invited_by_email: string;
  readonly status: InviteStatus;
  readonly expires_at: string;
  readonly accepted_at: string | null;
  readonly revoked_at: string | null;
  readonly created_at: string;
}

export interface InvitePreview {
  readonly tenant_name: string;
  readonly email: string;
  readonly expires_at: string;
}

export interface InvitesListResponse {
  readonly data: readonly Invite[];
}

export type InvitesListResult =
  | { readonly kind: "ok"; readonly data: readonly Invite[] }
  | { readonly kind: "forbidden" };

export type InvitePreviewResult =
  | { readonly kind: "ok"; readonly preview: InvitePreview }
  | { readonly kind: "invalid" };
