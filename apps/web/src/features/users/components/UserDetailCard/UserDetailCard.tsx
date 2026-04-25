import type { JSX } from "react";

import { cn } from "@/shared/lib/cn";

import type { UserDetail } from "../../types";

const ISO_MINUTE_LENGTH = 16;

interface UserDetailCardProps {
  readonly user: UserDetail;
}

export function UserDetailCard({ user }: UserDetailCardProps): JSX.Element {
  return (
    <section
      aria-labelledby="user-detail-title"
      className="space-y-6 rounded-md border border-border-subtle bg-bg-surface p-6"
    >
      <header className="flex items-center justify-between gap-3">
        <h2
          id="user-detail-title"
          className="break-all text-xl font-semibold text-fg"
        >
          {user.email}
        </h2>
        <StatusBadges
          isActive={user.is_active}
          isStaff={user.is_staff}
          isSuperuser={user.is_superuser}
        />
      </header>

      <dl className="grid grid-cols-1 gap-x-6 gap-y-4 text-sm sm:grid-cols-[max-content,1fr]">
        <DetailRow label="ID">
          <code className="break-all font-mono text-xs text-fg-muted">
            {user.id}
          </code>
        </DetailRow>
        <DetailRow label="Tenant">
          {user.tenant_id ? (
            <code className="break-all font-mono text-xs text-fg-muted">
              {user.tenant_id}
            </code>
          ) : (
            <span className="text-fg-muted" aria-label="No tenant assigned">
              —
            </span>
          )}
        </DetailRow>
        <DetailRow label="Created">
          <AbsoluteDate iso={user.created_at} />
        </DetailRow>
        <DetailRow label="Updated">
          <AbsoluteDate iso={user.updated_at} />
        </DetailRow>
        <DetailRow label="Last sign-in">
          {user.last_login ? (
            <AbsoluteDate iso={user.last_login} />
          ) : (
            <span className="text-fg-muted" aria-label="Never signed in">
              Never
            </span>
          )}
        </DetailRow>
      </dl>
    </section>
  );
}

interface DetailRowProps {
  readonly label: string;
  readonly children: JSX.Element | string;
}

function DetailRow({ label, children }: DetailRowProps): JSX.Element {
  return (
    <>
      <dt className="text-fg-muted">{label}</dt>
      <dd className="text-fg">{children}</dd>
    </>
  );
}

interface StatusBadgesProps {
  readonly isActive: boolean;
  readonly isStaff: boolean;
  readonly isSuperuser: boolean;
}

function StatusBadges({
  isActive,
  isStaff,
  isSuperuser,
}: StatusBadgesProps): JSX.Element {
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
      {isSuperuser && (
        <Badge tone="accent" label="Superuser role">
          Superuser
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

function AbsoluteDate({ iso }: { readonly iso: string }): JSX.Element {
  const date = new Date(iso);
  const display =
    date.toISOString().slice(0, ISO_MINUTE_LENGTH).replace("T", " ") + " UTC";
  return (
    <time dateTime={iso} className="text-fg">
      {display}
    </time>
  );
}
