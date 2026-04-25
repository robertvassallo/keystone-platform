"use client";

import { usePathname, useRouter } from "next/navigation";
import {
  useId,
  useState,
  type ChangeEvent,
  type JSX,
  type SyntheticEvent,
} from "react";

import { cn } from "@/shared/lib/cn";

import type { UsersListFilters as UsersListFiltersValue, UserStatus } from "../../types";
import { USER_STATUS_VALUES } from "../../types";

interface UsersListFiltersProps {
  readonly filters: UsersListFiltersValue;
}

const STATUS_LABELS: Readonly<Record<UserStatus, string>> = {
  active: "Active",
  inactive: "Inactive",
  staff: "Staff",
};

function buildHref(
  pathname: string,
  filters: UsersListFiltersValue,
): string {
  const params = new URLSearchParams();
  if (filters.q !== null && filters.q !== "") params.set("q", filters.q);
  if (filters.status !== null) params.set("status", filters.status);
  const query = params.toString();
  return query ? `${pathname}?${query}` : pathname;
}

function isUserStatus(value: string): value is UserStatus {
  return (USER_STATUS_VALUES as readonly string[]).includes(value);
}

export function UsersListFilters({
  filters,
}: UsersListFiltersProps): JSX.Element {
  const router = useRouter();
  const pathname = usePathname();
  const searchInputId = useId();
  const statusSelectId = useId();
  const [draftQ, setDraftQ] = useState(filters.q ?? "");

  const hasFilters = filters.q !== null || filters.status !== null;

  const submit = (next: UsersListFiltersValue): void => {
    router.push(buildHref(pathname, next));
  };

  const onSubmit = (event: SyntheticEvent<HTMLFormElement>): void => {
    event.preventDefault();
    const trimmed = draftQ.trim();
    submit({ q: trimmed === "" ? null : trimmed, status: filters.status });
  };

  const onStatusChange = (event: ChangeEvent<HTMLSelectElement>): void => {
    const raw = event.target.value;
    const nextStatus: UserStatus | null = isUserStatus(raw) ? raw : null;
    submit({ q: filters.q, status: nextStatus });
  };

  const clearQ = (): void => {
    setDraftQ("");
    submit({ q: null, status: filters.status });
  };

  const clearStatus = (): void => {
    submit({ q: filters.q, status: null });
  };

  const clearAll = (): void => {
    setDraftQ("");
    submit({ q: null, status: null });
  };

  return (
    <section aria-labelledby="users-filters-heading" className="space-y-3">
      <h2 id="users-filters-heading" className="sr-only">
        Filter users
      </h2>
      <form
        onSubmit={onSubmit}
        className="flex flex-wrap items-end gap-3"
        role="search"
        aria-label="Search and filter users"
      >
        <div className="flex flex-col gap-1">
          <label
            htmlFor={searchInputId}
            className="text-xs font-medium text-fg-muted"
          >
            Search by email
          </label>
          <input
            id={searchInputId}
            type="search"
            name="q"
            value={draftQ}
            onChange={(event) => {
              setDraftQ(event.target.value);
            }}
            placeholder="alice@example.com"
            autoComplete="off"
            className={cn(
              "h-9 w-64 rounded-md border border-border bg-bg-surface px-3 text-sm text-fg",
              "placeholder:text-fg-subtle",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            )}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label
            htmlFor={statusSelectId}
            className="text-xs font-medium text-fg-muted"
          >
            Status
          </label>
          <select
            id={statusSelectId}
            name="status"
            value={filters.status ?? ""}
            onChange={onStatusChange}
            className={cn(
              "h-9 rounded-md border border-border bg-bg-surface px-3 text-sm text-fg",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            )}
          >
            <option value="">All</option>
            {USER_STATUS_VALUES.map((value) => (
              <option key={value} value={value}>
                {STATUS_LABELS[value]}
              </option>
            ))}
          </select>
        </div>

        <button
          type="submit"
          className={cn(
            "h-9 rounded-md border border-border bg-bg-surface px-4 text-sm font-medium text-fg",
            "hover:bg-bg-canvas",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          Apply
        </button>
      </form>

      {hasFilters ? (
        <div className="flex flex-wrap items-center gap-2 text-sm">
          <span className="text-fg-muted">Active filters:</span>
          {filters.q !== null ? (
            <FilterChip
              label={`Search: ${filters.q}`}
              clearLabel={`Clear search filter ${filters.q}`}
              onClear={clearQ}
            />
          ) : null}
          {filters.status !== null ? (
            <FilterChip
              label={`Status: ${STATUS_LABELS[filters.status]}`}
              clearLabel={`Clear status filter ${STATUS_LABELS[filters.status]}`}
              onClear={clearStatus}
            />
          ) : null}
          <button
            type="button"
            onClick={clearAll}
            className={cn(
              "rounded-md border border-transparent px-2 py-1 text-xs font-medium text-accent",
              "hover:underline",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            )}
          >
            Clear all
          </button>
        </div>
      ) : null}
    </section>
  );
}

interface FilterChipProps {
  readonly label: string;
  readonly clearLabel: string;
  readonly onClear: () => void;
}

function FilterChip({
  label,
  clearLabel,
  onClear,
}: FilterChipProps): JSX.Element {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border border-border bg-bg-surface",
        "px-2 py-0.5 text-xs font-medium text-fg",
      )}
    >
      <span>{label}</span>
      <button
        type="button"
        onClick={onClear}
        aria-label={clearLabel}
        className={cn(
          "inline-flex h-5 w-5 items-center justify-center rounded-full",
          "text-fg-muted hover:bg-bg-canvas hover:text-fg",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
        )}
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </span>
  );
}
