import type { JSX } from "react";

export function UsersListEmpty(): JSX.Element {
  return (
    <div
      role="status"
      className="rounded-md border border-border-subtle bg-bg-surface p-8 text-center"
    >
      <h2 className="text-base font-semibold text-fg">No users yet</h2>
      <p className="mt-1 text-sm text-fg-muted">
        Once people sign up, they&rsquo;ll show up here.
      </p>
    </div>
  );
}
