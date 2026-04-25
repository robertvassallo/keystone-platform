/** Public types for the accounts feature. */

export interface User {
  readonly id: string;
  readonly email: string;
  readonly is_active: boolean;
  readonly is_staff: boolean;
  readonly tenant_id: string | null;
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
