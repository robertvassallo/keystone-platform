import type { JSX } from "react";

import type { Account } from "../../types";

const ISO_MINUTE_LENGTH = 16;

interface AccountCardProps {
  readonly account: Account;
}

export function AccountCard({ account }: AccountCardProps): JSX.Element {
  return (
    <section
      aria-labelledby="account-card-title"
      className="space-y-6 rounded-md border border-border-subtle bg-bg-surface p-6"
    >
      <header className="space-y-1">
        <h2 id="account-card-title" className="text-xl font-semibold text-fg">
          {account.name}
        </h2>
        <p className="font-mono text-xs text-fg-muted">{account.slug}</p>
      </header>

      <dl className="grid grid-cols-1 gap-x-6 gap-y-4 text-sm sm:grid-cols-[max-content,1fr]">
        <DetailRow label="ID">
          <code className="break-all font-mono text-xs text-fg-muted">
            {account.id}
          </code>
        </DetailRow>
        <DetailRow label="Owner">
          {account.owner_email !== null ? (
            <span className="text-fg">{account.owner_email}</span>
          ) : (
            <span className="text-fg-muted" aria-label="No owner">
              —
            </span>
          )}
        </DetailRow>
        <DetailRow label="Created">
          <AbsoluteDate iso={account.created_at} />
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
