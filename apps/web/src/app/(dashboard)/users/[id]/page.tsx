import Link from "next/link";
import type { JSX } from "react";

import { UserDetailCard } from "@/features/users";
import { getUserServer } from "@/features/users/api/get-user-server";

interface UserDetailPageProps {
  readonly params: Promise<{ readonly id: string }>;
}

export default async function UserDetailPage({
  params,
}: UserDetailPageProps): Promise<JSX.Element> {
  const { id } = await params;
  const result = await getUserServer(id);

  if (result.kind === "forbidden") {
    return <AccessRequired />;
  }
  if (result.kind === "not_found") {
    return <NotFoundPanel />;
  }

  return (
    <main className="mx-auto max-w-3xl space-y-6 px-6 py-12">
      <p className="text-sm">
        <Link
          href="/users"
          className="text-accent hover:underline focus-visible:underline"
        >
          ← Back to users
        </Link>
      </p>
      <UserDetailCard user={result.user} />
    </main>
  );
}

function AccessRequired(): JSX.Element {
  return (
    <main className="mx-auto max-w-md space-y-4 px-6 py-12">
      <h1 className="text-2xl font-semibold text-fg">Access required</h1>
      <p className="text-sm text-fg-muted">
        This area is staff-only. If you think you should have access, ask an
        administrator.
      </p>
      <p className="text-sm">
        <Link
          href="/"
          className="text-accent hover:underline focus-visible:underline"
        >
          Back to dashboard
        </Link>
      </p>
    </main>
  );
}

function NotFoundPanel(): JSX.Element {
  return (
    <main className="mx-auto max-w-md space-y-4 px-6 py-12">
      <h1 className="text-2xl font-semibold text-fg">User not found</h1>
      <p className="text-sm text-fg-muted">
        We couldn&rsquo;t find a user with that id. It may have been removed.
      </p>
      <p className="text-sm">
        <Link
          href="/users"
          className="text-accent hover:underline focus-visible:underline"
        >
          Back to users
        </Link>
      </p>
    </main>
  );
}
