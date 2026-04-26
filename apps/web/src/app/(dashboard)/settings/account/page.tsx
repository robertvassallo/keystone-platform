import Link from "next/link";
import type { JSX } from "react";

import { AccountEditPanel } from "@/features/accounts";
import { getAccountServer } from "@/features/accounts/api/get-account-server";
import { getMeServer } from "@/features/accounts/api/me-server";

export default async function AccountSettingsPage(): Promise<JSX.Element> {
  const [result, me] = await Promise.all([
    getAccountServer(),
    getMeServer(),
  ]);

  if (result.kind === "forbidden") {
    return (
      <main className="mx-auto max-w-md space-y-4 px-6 py-12">
        <h1 className="text-2xl font-semibold text-fg">Account unavailable</h1>
        <p className="text-sm text-fg-muted">
          We couldn&rsquo;t load your tenant. Try signing in again.
        </p>
        <p className="text-sm">
          <Link
            href="/sign-in"
            className="text-accent hover:underline focus-visible:underline"
          >
            Back to sign in
          </Link>
        </p>
      </main>
    );
  }

  const canEdit = me !== null && (me.is_tenant_owner || me.is_staff);

  return (
    <main className="mx-auto max-w-2xl space-y-6 px-6 py-12">
      <p className="text-sm">
        <Link
          href="/"
          className="text-accent hover:underline focus-visible:underline"
        >
          ← Back to dashboard
        </Link>
      </p>

      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-fg">Account</h1>
        <p className="text-sm text-fg-muted">
          The tenant your sign-in belongs to.
        </p>
      </header>

      <AccountEditPanel account={result.account} canEdit={canEdit} />
    </main>
  );
}
