import Link from "next/link";
import type { JSX } from "react";

import { confirmEmailVerificationServer } from "@/features/accounts/api/confirm-email-verification-server";

interface VerifyEmailPageProps {
  readonly searchParams: Promise<{
    readonly uid?: string;
    readonly token?: string;
  }>;
}

export default async function VerifyEmailPage({
  searchParams,
}: VerifyEmailPageProps): Promise<JSX.Element> {
  const { uid, token } = await searchParams;

  if (!uid || !token) {
    return (
      <Panel
        heading="Verification link looks broken"
        body={
          <>
            This page needs both a <code>uid</code> and a <code>token</code> in
            the URL. Open the most recent verification email and try the link
            again, or request a new one from the dashboard.
          </>
        }
        action={
          <Link
            href="/"
            className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
          >
            Back to dashboard
          </Link>
        }
      />
    );
  }

  const result = await confirmEmailVerificationServer({ uid, token });

  if (result.kind === "ok") {
    return (
      <Panel
        heading="Email verified"
        body="Thanks — your email is confirmed. You can keep using Keystone as usual."
        action={
          <Link
            href="/"
            className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
          >
            Continue to dashboard
          </Link>
        }
      />
    );
  }

  return (
    <Panel
      heading="Link is invalid or expired"
      body="Verification links work for 24 hours from the time we send them. Sign in and request a new one from your dashboard."
      action={
        <Link
          href="/sign-in"
          className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
        >
          Sign in to request a new link
        </Link>
      }
    />
  );
}

interface PanelProps {
  readonly heading: string;
  readonly body: React.ReactNode;
  readonly action: React.ReactNode;
}

function Panel({ heading, body, action }: PanelProps): JSX.Element {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <section
        aria-labelledby="verify-email-heading"
        className="w-full max-w-sm space-y-4 rounded-lg border border-border-subtle bg-bg-surface p-8 shadow-md"
      >
        <h1
          id="verify-email-heading"
          className="text-2xl font-semibold text-fg"
        >
          {heading}
        </h1>
        <p className="text-sm text-fg-muted">{body}</p>
        <p className="text-sm">{action}</p>
      </section>
    </main>
  );
}
