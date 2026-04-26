import Link from "next/link";
import type { JSX } from "react";

import { SignOutButton } from "@/features/accounts";
import { getMeServer } from "@/features/accounts/api/me-server";

export default async function DashboardPage(): Promise<JSX.Element> {
  // The (dashboard) layout guard guarantees ``me`` is non-null here.
  const me = await getMeServer();
  if (me === null) {
    throw new Error("Dashboard rendered without an authenticated user.");
  }

  return (
    <main className="mx-auto max-w-2xl space-y-8 px-6 py-12">
      <header className="space-y-2">
        {me.tenant !== null && (
          <p className="text-xs font-semibold uppercase tracking-wider text-fg-muted">
            {me.tenant.name}
          </p>
        )}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-fg">Dashboard</h1>
          <SignOutButton />
        </div>
      </header>

      <p className="text-fg-muted">
        Signed in as{" "}
        <span className="font-medium text-fg">{me.display_name}</span>
        {me.display_name !== me.email ? (
          <span className="text-fg-subtle"> ({me.email})</span>
        ) : null}
        .
      </p>

      <section
        aria-labelledby="account-widget-title"
        className="space-y-3 rounded-md border border-border-subtle bg-bg-surface p-4"
      >
        <h2 id="account-widget-title" className="text-sm font-semibold text-fg">
          Account
        </h2>
        <ul className="space-y-1 text-sm">
          <li>
            <Link
              href="/settings/profile"
              className="text-accent hover:underline focus-visible:underline"
            >
              Profile
            </Link>
          </li>
          <li>
            <Link
              href="/settings/account"
              className="text-accent hover:underline focus-visible:underline"
            >
              Tenant
            </Link>
          </li>
          <li>
            <Link
              href="/change-password"
              className="text-accent hover:underline focus-visible:underline"
            >
              Change password
            </Link>
          </li>
          <li>
            <Link
              href="/mfa"
              className="text-accent hover:underline focus-visible:underline"
            >
              Two-factor authentication
            </Link>
          </li>
          {(me.is_staff || me.is_tenant_owner) && (
            <>
              <li>
                <Link
                  href="/users"
                  className="text-accent hover:underline focus-visible:underline"
                >
                  Users
                </Link>
              </li>
              <li>
                <Link
                  href="/settings/audit-log"
                  className="text-accent hover:underline focus-visible:underline"
                >
                  Audit log
                </Link>
              </li>
            </>
          )}
        </ul>
      </section>
    </main>
  );
}
