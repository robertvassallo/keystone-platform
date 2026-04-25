import { redirect } from "next/navigation";
import type { JSX, ReactNode } from "react";

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
  return <>{children}</>;
}
