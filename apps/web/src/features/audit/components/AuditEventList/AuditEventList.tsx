import type { JSX } from "react";

import type { AuditEvent } from "../../types";

interface AuditEventListProps {
  readonly events: readonly AuditEvent[];
}

const ACTION_LABELS: Readonly<Record<string, string>> = {
  "auth.sign_in": "Sign-in",
  "auth.password_change": "Password changed",
  "mfa.enrolled": "MFA enabled",
  "mfa.disabled": "MFA disabled",
  "mfa.recovery_codes_regenerated": "Recovery codes regenerated",
  "invite.sent": "Invite sent",
  "invite.revoked": "Invite revoked",
  "invite.accepted": "Invite accepted",
  "tenant.renamed": "Tenant renamed",
};

const ISO_MINUTE_LENGTH = 16;

export function AuditEventList({ events }: AuditEventListProps): JSX.Element {
  if (events.length === 0) {
    return (
      <div
        role="status"
        className="rounded-md border border-border-subtle bg-bg-surface p-8 text-center"
      >
        <h2 className="text-base font-semibold text-fg">No events yet</h2>
        <p className="mt-1 text-sm text-fg-muted">
          Sensitive actions (sign-ins, password changes, invites, tenant
          edits) will appear here as they happen.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-md border border-border-subtle">
      <table className="w-full border-collapse text-left text-sm">
        <caption className="sr-only">Audit log entries</caption>
        <thead className="bg-bg-canvas text-fg-muted">
          <tr>
            {["Action", "Actor", "Target", "When", "IP"].map((heading) => (
              <th
                key={heading}
                scope="col"
                className="px-4 py-2 text-xs font-semibold uppercase tracking-wide"
              >
                {heading}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id} className="border-t border-border-subtle">
              <th
                scope="row"
                className="px-4 py-3 font-medium text-fg"
              >
                {ACTION_LABELS[event.action] ?? event.action}
              </th>
              <td className="px-4 py-3 text-fg-muted">
                {event.actor_email || (
                  <span aria-label="System actor">system</span>
                )}
              </td>
              <td className="px-4 py-3 text-fg-muted">
                {event.target_label || (
                  <span aria-label="No target">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-fg-muted">
                <Timestamp iso={event.created_at} />
              </td>
              <td className="px-4 py-3 font-mono text-xs text-fg-muted">
                {event.ip ?? <span aria-label="No IP">—</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Timestamp({ iso }: { readonly iso: string }): JSX.Element {
  const date = new Date(iso);
  const absolute =
    date.toISOString().slice(0, ISO_MINUTE_LENGTH).replace("T", " ") + " UTC";
  return (
    <time dateTime={iso} title={absolute}>
      {absolute}
    </time>
  );
}
