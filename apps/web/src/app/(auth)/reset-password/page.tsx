import Link from "next/link";
import type { JSX } from "react";

import { ResetPasswordForm } from "@/features/accounts";

interface ResetPasswordPageProps {
  readonly searchParams: Promise<{
    readonly uid?: string;
    readonly token?: string;
  }>;
}

export default async function ResetPasswordPage({
  searchParams,
}: ResetPasswordPageProps): Promise<JSX.Element> {
  const { uid, token } = await searchParams;

  if (!uid || !token) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold text-fg">Reset link looks broken</h1>
        <p className="text-sm text-fg-muted">
          This page needs both a <code>uid</code> and a <code>token</code> in
          the URL. Request a new reset link to continue.
        </p>
        <p className="text-sm">
          <Link
            href="/forgot-password"
            className="text-accent hover:underline focus-visible:underline"
          >
            Request a new link
          </Link>
        </p>
      </div>
    );
  }

  return <ResetPasswordForm uid={uid} token={token} />;
}
