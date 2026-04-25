import Link from "next/link";
import type { JSX } from "react";

import { cn } from "@/shared/lib/cn";

import type { UserListItem } from "../../types";

import { UsersListEmpty } from "./UsersListEmpty";

interface UsersListProps {
  readonly users: readonly UserListItem[];
}

export function UsersList({ users }: UsersListProps): JSX.Element {
  if (users.length === 0) {
    return <UsersListEmpty />;
  }

  return (
    <div className="overflow-x-auto rounded-md border border-border-subtle">
      <table className="w-full border-collapse text-left text-sm">
        <caption className="sr-only">All users on the platform</caption>
        <thead className="bg-bg-canvas text-fg-muted">
          <tr>
            <th
              scope="col"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wide"
            >
              Email
            </th>
            <th
              scope="col"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wide"
            >
              Status
            </th>
            <th
              scope="col"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wide"
            >
              Created
            </th>
            <th
              scope="col"
              className="px-4 py-2 text-xs font-semibold uppercase tracking-wide"
            >
              Last sign-in
            </th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr
              key={user.id}
              className="border-t border-border-subtle"
            >
              <th
                scope="row"
                className="px-4 py-3 font-medium text-fg"
              >
                <Link
                  href={`/users/${user.id}`}
                  className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
                >
                  {user.email}
                </Link>
              </th>
              <td className="px-4 py-3">
                <StatusBadges
                  isActive={user.is_active}
                  isStaff={user.is_staff}
                />
              </td>
              <td className="px-4 py-3 text-fg-muted">
                <RelativeDate iso={user.created_at} />
              </td>
              <td className="px-4 py-3 text-fg-muted">
                {user.last_login ? (
                  <RelativeDate iso={user.last_login} />
                ) : (
                  <span aria-label="Never signed in">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface StatusBadgesProps {
  readonly isActive: boolean;
  readonly isStaff: boolean;
}

function StatusBadges({ isActive, isStaff }: StatusBadgesProps): JSX.Element {
  return (
    <span className="flex flex-wrap gap-1">
      {isActive ? (
        <Badge tone="success" label="Active">
          Active
        </Badge>
      ) : (
        <Badge tone="muted" label="Inactive">
          Inactive
        </Badge>
      )}
      {isStaff && (
        <Badge tone="accent" label="Staff role">
          Staff
        </Badge>
      )}
    </span>
  );
}

interface BadgeProps {
  readonly tone: "success" | "muted" | "accent";
  readonly label: string;
  readonly children: string;
}

function Badge({ tone, label, children }: BadgeProps): JSX.Element {
  return (
    <span
      aria-label={label}
      className={cn(
        "inline-flex items-center rounded-sm px-2 py-0.5 text-xs font-medium",
        tone === "success" && "border border-success-fg text-success-fg",
        tone === "muted" && "border border-border text-fg-muted",
        tone === "accent" && "border border-accent text-accent",
      )}
    >
      {children}
    </span>
  );
}

interface RelativeDateProps {
  readonly iso: string;
}

// "YYYY-MM-DD HH:MM" — slicing the ISO string at this index drops seconds + ms.
const ISO_MINUTE_LENGTH = 16;

function RelativeDate({ iso }: RelativeDateProps): JSX.Element {
  const date = new Date(iso);
  const absolute =
    date.toISOString().slice(0, ISO_MINUTE_LENGTH).replace("T", " ") + " UTC";
  const relative = formatRelative(date);
  return (
    <time dateTime={iso} title={absolute}>
      {relative}
    </time>
  );
}

const MS_PER_SECOND = 1000;
const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;
const HOURS_PER_DAY = 24;
const MINUTE_MS = SECONDS_PER_MINUTE * MS_PER_SECOND;
const HOUR_MS = MINUTES_PER_HOUR * MINUTE_MS;
const DAY_MS = HOURS_PER_DAY * HOUR_MS;

function formatRelative(date: Date): string {
  const diff = Date.now() - date.getTime();
  if (diff < MINUTE_MS) return "just now";
  if (diff < HOUR_MS) return `${String(Math.floor(diff / MINUTE_MS))}m ago`;
  if (diff < DAY_MS) return `${String(Math.floor(diff / HOUR_MS))}h ago`;
  return `${String(Math.floor(diff / DAY_MS))}d ago`;
}
