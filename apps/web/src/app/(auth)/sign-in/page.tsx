import type { JSX } from "react";

import { SignInForm } from "@/features/accounts";

interface SignInPageProps {
  readonly searchParams: Promise<{ readonly next?: string }>;
}

export default async function SignInPage({
  searchParams,
}: SignInPageProps): Promise<JSX.Element> {
  const params = await searchParams;
  return <SignInForm nextPath={params.next ?? "/"} />;
}
