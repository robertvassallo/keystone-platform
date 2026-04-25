import Link from "next/link";
import type { JSX } from "react";

import {
  USER_STATUS_VALUES,
  UsersList,
  UsersListFilters,
  UsersListPagination,
} from "@/features/users";
import type {
  UsersListFiltersValue,
  UserStatus,
} from "@/features/users";
import { listUsersServer } from "@/features/users/api/list-users-server";

interface UsersPageProps {
  readonly searchParams: Promise<{
    readonly page?: string;
    readonly q?: string;
    readonly status?: string;
  }>;
}

const FIRST_PAGE = 1;
const PAGE_SIZE = 25;

function parsePage(raw: string | undefined): number {
  if (raw === undefined) return FIRST_PAGE;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= FIRST_PAGE ? parsed : FIRST_PAGE;
}

function parseStatus(raw: string | undefined): UserStatus | null {
  if (raw === undefined) return null;
  return (USER_STATUS_VALUES as readonly string[]).includes(raw)
    ? (raw as UserStatus)
    : null;
}

function parseQuery(raw: string | undefined): string | null {
  if (raw === undefined) return null;
  const trimmed = raw.trim();
  return trimmed === "" ? null : trimmed;
}

export default async function UsersPage({
  searchParams,
}: UsersPageProps): Promise<JSX.Element> {
  const params = await searchParams;
  const page = parsePage(params.page);
  const filters: UsersListFiltersValue = {
    q: parseQuery(params.q),
    status: parseStatus(params.status),
  };
  const isFiltered = filters.q !== null || filters.status !== null;

  const result = await listUsersServer({
    page,
    pageSize: PAGE_SIZE,
    q: filters.q,
    status: filters.status,
  });

  if (result.kind === "forbidden") {
    return (
      <main className="mx-auto max-w-md space-y-4 px-6 py-12">
        <h1 className="text-2xl font-semibold text-fg">Access required</h1>
        <p className="text-sm text-fg-muted">
          This area is staff-only. If you think you should have access, ask an
          administrator.
        </p>
        <p className="text-sm">
          <Link
            href="/"
            className="text-accent hover:underline focus-visible:underline"
          >
            Back to dashboard
          </Link>
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl space-y-6 px-6 py-12">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-fg">Users</h1>
        <p className="text-sm text-fg-muted">
          {result.page.total} {isFiltered ? "match" : "total"}
        </p>
      </header>

      <UsersListFilters filters={filters} />
      <UsersList users={result.data} isFiltered={isFiltered} />
      <UsersListPagination
        page={result.page.page}
        pageSize={result.page.page_size}
        total={result.page.total}
        filters={filters}
      />
    </main>
  );
}
