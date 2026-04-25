/** Public types for the users feature. */

import type { TenantSummary } from "@/features/accounts";

export interface UserListItem {
  readonly id: string;
  readonly email: string;
  readonly is_active: boolean;
  readonly is_staff: boolean;
  readonly created_at: string;
  readonly last_login: string | null;
}

export interface UserDetail extends UserListItem {
  readonly is_superuser: boolean;
  readonly tenant: TenantSummary;
  readonly updated_at: string;
}

export interface UsersListResponse {
  readonly data: readonly UserListItem[];
  readonly page: {
    readonly page: number;
    readonly page_size: number;
    readonly total: number;
  };
}

export interface UsersListAccessDenied {
  readonly kind: "forbidden";
}

export interface UsersListOk extends UsersListResponse {
  readonly kind: "ok";
}

export type UsersListResult = UsersListOk | UsersListAccessDenied;

export type UserDetailResult =
  | { readonly kind: "ok"; readonly user: UserDetail }
  | { readonly kind: "forbidden" }
  | { readonly kind: "not_found" };
