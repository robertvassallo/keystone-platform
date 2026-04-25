/** Public types for the accounts feature. */

export interface User {
  readonly id: string;
  readonly email: string;
  readonly is_active: boolean;
  readonly is_staff: boolean;
  readonly tenant_id: string | null;
  readonly created_at: string;
}
