import { redirect } from "next/navigation";
import type { JSX, ReactNode } from "react";

import { getMeServer } from "@/features/accounts/api/me-server";

interface AuthLayoutProps {
  readonly children: ReactNode;
}

export default async function AuthLayout({
  children,
}: AuthLayoutProps): Promise<JSX.Element> {
  const me = await getMeServer();
  if (me !== null) {
    redirect("/");
  }
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm rounded-lg border border-border-subtle bg-bg-surface p-8 shadow-md">
        {children}
      </div>
    </main>
  );
}
