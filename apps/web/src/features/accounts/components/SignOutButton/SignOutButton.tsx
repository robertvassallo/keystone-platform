"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import type { JSX } from "react";

import { cn } from "@/shared/lib/cn";

import { signOut } from "../../api";

export function SignOutButton(): JSX.Element {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  const onClick = async (): Promise<void> => {
    setPending(true);
    try {
      await signOut();
      router.push("/sign-in");
      router.refresh();
    } finally {
      setPending(false);
    }
  };

  return (
    <button
      type="button"
      onClick={() => {
        void onClick();
      }}
      disabled={pending}
      className={cn(
        "rounded-md border border-border bg-bg-surface px-4 py-2 text-sm font-medium text-fg",
        "hover:bg-bg-canvas",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
        "disabled:cursor-not-allowed disabled:opacity-60",
      )}
    >
      {pending ? "Signing out…" : "Sign out"}
    </button>
  );
}
