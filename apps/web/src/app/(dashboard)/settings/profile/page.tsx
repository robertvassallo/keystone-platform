import type { JSX } from "react";

import { ProfileForm } from "@/features/accounts";
import { getMeServer } from "@/features/accounts/api/me-server";

export default async function ProfilePage(): Promise<JSX.Element> {
  // The (dashboard) layout guard guarantees ``me`` is non-null here.
  const me = await getMeServer();
  if (me === null) {
    throw new Error("Profile rendered without an authenticated user.");
  }

  return (
    <main className="mx-auto max-w-md space-y-6 px-6 py-12">
      <ProfileForm initial={me} />
    </main>
  );
}
