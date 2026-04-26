import { redirect } from "next/navigation";
import type { JSX, ReactNode } from "react";

import { EmailVerificationBanner } from "@/features/accounts";
import { getMeServer } from "@/features/accounts/api/me-server";

interface DashboardLayoutProps {
  readonly children: ReactNode;
}

export default async function DashboardLayout({
  children,
}: DashboardLayoutProps): Promise<JSX.Element> {
  const me = await getMeServer();
  if (me === null) {
    redirect("/sign-in");
  }
  return (
    <>
      {me.email_verified_at === null ? <EmailVerificationBanner /> : null}
      {children}
    </>
  );
}
