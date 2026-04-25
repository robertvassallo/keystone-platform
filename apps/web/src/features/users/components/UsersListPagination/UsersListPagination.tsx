import Link from "next/link";
import type { JSX } from "react";

import { cn } from "@/shared/lib/cn";

import type { UsersListFilters as UsersListFiltersValue } from "../../types";

interface UsersListPaginationProps {
  readonly page: number;
  readonly pageSize: number;
  readonly total: number;
  readonly filters?: UsersListFiltersValue;
}

const FIRST_PAGE = 1;

function buildHref(targetPage: number, filters?: UsersListFiltersValue): string {
  const params = new URLSearchParams();
  params.set("page", String(targetPage));
  if (filters !== undefined) {
    if (filters.q !== null && filters.q !== "") params.set("q", filters.q);
    if (filters.status !== null) params.set("status", filters.status);
  }
  return `?${params.toString()}`;
}

export function UsersListPagination({
  page,
  pageSize,
  total,
  filters,
}: UsersListPaginationProps): JSX.Element | null {
  if (total === 0) return null;

  const lastPage = Math.max(FIRST_PAGE, Math.ceil(total / pageSize));
  const start = (page - FIRST_PAGE) * pageSize + FIRST_PAGE;
  const end = Math.min(page * pageSize, total);

  const hasPrev = page > FIRST_PAGE;
  const hasNext = page < lastPage;

  return (
    <nav
      aria-label="Users list pagination"
      className="flex items-center justify-between gap-3 pt-3 text-sm"
    >
      <p className="text-fg-muted">
        {start}&ndash;{end} of {total}
      </p>
      <div className="flex items-center gap-2">
        <PageLink
          href={hasPrev ? buildHref(page - 1, filters) : null}
          label="Previous page"
        >
          Previous
        </PageLink>
        <PageLink
          href={hasNext ? buildHref(page + 1, filters) : null}
          label="Next page"
        >
          Next
        </PageLink>
      </div>
    </nav>
  );
}

interface PageLinkProps {
  readonly href: string | null;
  readonly label: string;
  readonly children: string;
}

function PageLink({ href, label, children }: PageLinkProps): JSX.Element {
  const className = cn(
    "rounded-md border px-3 py-1.5 text-sm font-medium",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
    href === null
      ? "cursor-not-allowed border-border-subtle text-fg-subtle"
      : "border-border bg-bg-surface text-fg hover:bg-bg-canvas",
  );

  if (href === null) {
    return (
      <span aria-disabled="true" aria-label={`${label} (unavailable)`} className={className}>
        {children}
      </span>
    );
  }

  return (
    <Link href={href} aria-label={label} className={className}>
      {children}
    </Link>
  );
}
