import type { JSX } from "react";

import { ChangePasswordForm } from "@/features/accounts";

export default function ChangePasswordPage(): JSX.Element {
  return (
    <main className="mx-auto max-w-md px-6 py-12">
      <ChangePasswordForm />
    </main>
  );
}
