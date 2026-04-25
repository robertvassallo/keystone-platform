/** Public types for the users feature. */

export interface UserListItem {
  readonly id: string;
  readonly email: string;
  readonly is_active: boolean;
  readonly is_staff: boolean;
  readonly created_at: string;
  readonly last_login: string | null;
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
