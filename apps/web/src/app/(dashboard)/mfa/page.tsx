import type { JSX } from "react";

import { MfaEnrolFlow, MfaManagementPanel } from "@/features/accounts";
import { getMfaStatusServer } from "@/features/accounts/api/mfa-status-server";

export default async function MFAPage(): Promise<JSX.Element> {
  // The (dashboard) layout guard already ensured an authenticated user;
  // ``getMfaStatusServer`` returning null here would be a backend hiccup.
  const status = await getMfaStatusServer();
  if (status === null) {
    throw new Error("MFA page rendered without an authenticated user.");
  }

  return (
    <main className="mx-auto max-w-md space-y-6 px-6 py-12">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold text-fg">
          Two-factor authentication
        </h1>
        <p className="text-sm text-fg-muted">
          Add a second step at sign-in using a TOTP authenticator app.
        </p>
      </header>

      {status.enabled ? (
        <MfaManagementPanel status={status} />
      ) : (
        <MfaEnrolFlow />
      )}
    </main>
  );
}
