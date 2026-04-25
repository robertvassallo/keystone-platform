import Link from "next/link";
import type { JSX } from "react";

export function UsersListNoMatches(): JSX.Element {
  return (
    <div
      role="status"
      className="rounded-md border border-border-subtle bg-bg-surface p-8 text-center"
    >
      <h2 className="text-base font-semibold text-fg">No matches</h2>
      <p className="mt-1 text-sm text-fg-muted">
        No users match the current filters.
      </p>
      <p className="mt-3 text-sm">
        <Link
          href="/users"
          className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
        >
          Clear filters
        </Link>
      </p>
    </div>
  );
}
