import Link from "next/link";
import type { JSX } from "react";

import { AcceptInviteForm } from "@/features/invites";
import { previewInviteServer } from "@/features/invites/api/preview-invite-server";

interface AcceptInvitePageProps {
  readonly searchParams: Promise<{
    readonly uid?: string;
    readonly token?: string;
  }>;
}

export default async function AcceptInvitePage({
  searchParams,
}: AcceptInvitePageProps): Promise<JSX.Element> {
  const { uid, token } = await searchParams;

  if (!uid || !token) {
    return (
      <Panel
        heading="Invitation link looks broken"
        body={
          <>
            This page needs both a <code>uid</code> and a <code>token</code> in
            the URL. Open the most recent invite email and try the link again.
          </>
        }
        action={
          <Link
            href="/sign-in"
            className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
          >
            Go to sign in
          </Link>
        }
      />
    );
  }

  const result = await previewInviteServer({ uid, token });

  if (result.kind === "invalid") {
    return (
      <Panel
        heading="Link is invalid or expired"
        body="Invitation links work for 7 days from the time we send them. Ask your inviter to send a new one."
        action={
          <Link
            href="/sign-in"
            className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
          >
            Go to sign in
          </Link>
        }
      />
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm rounded-lg border border-border-subtle bg-bg-surface p-8 shadow-md">
        <AcceptInviteForm
          uid={uid}
          token={token}
          tenantName={result.preview.tenant_name}
          email={result.preview.email}
        />
      </div>
    </main>
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
        aria-labelledby="accept-invite-heading"
        className="w-full max-w-sm space-y-4 rounded-lg border border-border-subtle bg-bg-surface p-8 shadow-md"
      >
        <h1
          id="accept-invite-heading"
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
