/** Public types for the accounts feature. */

export interface TenantSummary {
  readonly id: string;
  readonly name: string;
  readonly slug: string;
}

export interface Account {
  readonly id: string;
  readonly name: string;
  readonly slug: string;
  readonly owner_email: string | null;
  readonly created_at: string;
}

export interface User {
  readonly id: string;
  readonly email: string;
  readonly is_active: boolean;
  readonly is_staff: boolean;
  readonly tenant: TenantSummary | null;
  readonly email_verified_at: string | null;
  readonly created_at: string;
}

export interface MfaStatus {
  readonly enabled: boolean;
  readonly recovery_codes_remaining: number;
}

export interface MfaSetupPayload {
  readonly secret: string;
  readonly provisioning_uri: string;
  readonly qr_data_url: string;
}

export type AccountResult =
  | { readonly kind: "ok"; readonly account: Account }
  | { readonly kind: "forbidden" };
