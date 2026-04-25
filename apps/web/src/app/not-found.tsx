import type { JSX } from "react";

export default function NotFound(): JSX.Element {
  return (
    <main className="flex min-h-screen items-center justify-center p-8">
      <p className="text-lg text-fg-muted">Not found.</p>
    </main>
  );
}
