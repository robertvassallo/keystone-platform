import type { JSX } from "react";

const SKELETON_ROW_COUNT = 6;

export function UsersListSkeleton(): JSX.Element {
  return (
    <div
      role="status"
      aria-label="Loading users"
      className="overflow-x-auto rounded-md border border-border-subtle"
    >
      <table className="w-full border-collapse text-left text-sm">
        <caption className="sr-only">Loading users</caption>
        <thead className="bg-bg-canvas text-fg-muted">
          <tr>
            <th scope="col" className="px-4 py-2 text-xs uppercase tracking-wide">
              Email
            </th>
            <th scope="col" className="px-4 py-2 text-xs uppercase tracking-wide">
              Status
            </th>
            <th scope="col" className="px-4 py-2 text-xs uppercase tracking-wide">
              Created
            </th>
            <th scope="col" className="px-4 py-2 text-xs uppercase tracking-wide">
              Last sign-in
            </th>
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: SKELETON_ROW_COUNT }, (_, idx) => (
            <tr
              key={`skeleton-${String(idx)}`}
              className="border-t border-border-subtle"
            >
              <td className="px-4 py-3">
                <SkeletonCell width="w-48" />
              </td>
              <td className="px-4 py-3">
                <SkeletonCell width="w-20" />
              </td>
              <td className="px-4 py-3">
                <SkeletonCell width="w-16" />
              </td>
              <td className="px-4 py-3">
                <SkeletonCell width="w-16" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SkeletonCell({ width }: { readonly width: string }): JSX.Element {
  return (
    <span
      aria-hidden
      className={`block h-4 ${width} animate-pulse rounded-sm bg-border-subtle`}
    />
  );
}
