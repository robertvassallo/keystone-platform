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
    <main className="mx-auto max-w-2xl px-6 py-12">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-fg">Dashboard</h1>
        <SignOutButton />
      </header>
      <p className="text-fg-muted">
        Signed in as{" "}
        <span className="font-medium text-fg">{me.email}</span>.
      </p>
    </main>
  );
}
