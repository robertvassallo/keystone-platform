/** Public types for the audit-log feature. */

export interface AuditEvent {
  readonly id: string;
  readonly action: string;
  readonly actor_email: string;
  readonly target_type: string;
  readonly target_label: string;
  readonly ip: string | null;
  readonly created_at: string;
}

export interface AuditEventListResponse {
  readonly data: readonly AuditEvent[];
  readonly page: {
    readonly page: number;
    readonly page_size: number;
    readonly total: number;
  };
}

export type AuditEventListResult =
  | {
      readonly kind: "ok";
      readonly data: readonly AuditEvent[];
      readonly page: AuditEventListResponse["page"];
    }
  | { readonly kind: "forbidden" };
