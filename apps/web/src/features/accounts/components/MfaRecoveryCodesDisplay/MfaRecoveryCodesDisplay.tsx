"use client";

import { useState, type JSX } from "react";

import { cn } from "@/shared/lib/cn";

interface MfaRecoveryCodesDisplayProps {
  readonly codes: readonly string[];
  readonly onAcknowledge: () => void;
}

export function MfaRecoveryCodesDisplay({
  codes,
  onAcknowledge,
}: MfaRecoveryCodesDisplayProps): JSX.Element {
  const [copied, setCopied] = useState(false);
  const allCodes = codes.join("\n");

  const handleCopy = async (): Promise<void> => {
    await navigator.clipboard.writeText(allCodes);
    setCopied(true);
  };

  return (
    <section
      aria-labelledby="recovery-codes-title"
      className="space-y-4 rounded-md border border-border-subtle bg-bg-surface p-4"
    >
      <header className="space-y-1">
        <h2 id="recovery-codes-title" className="text-lg font-semibold text-fg">
          Save your recovery codes
        </h2>
        <p className="text-sm text-fg-muted">
          Store these somewhere safe. Each code can be used once if you lose
          access to your authenticator. They will not be shown again.
        </p>
      </header>

      <ul
        className="grid grid-cols-2 gap-2 font-mono text-sm text-fg"
        aria-label="Recovery codes"
      >
        {codes.map((code) => (
          <li
            key={code}
            className="rounded-sm bg-bg-canvas px-3 py-2 tracking-wider"
          >
            {code}
          </li>
        ))}
      </ul>

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => {
            void handleCopy();
          }}
          className={cn(
            "rounded-md border border-border bg-bg-surface px-3 py-2 text-sm font-medium text-fg",
            "hover:bg-bg-canvas",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          {copied ? "Copied" : "Copy all"}
        </button>
        <button
          type="button"
          onClick={onAcknowledge}
          className={cn(
            "rounded-md bg-accent px-4 py-2 text-sm font-medium text-fg-on-accent",
            "hover:bg-accent-emphasis",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          I&rsquo;ve saved them
        </button>
      </div>
    </section>
  );
}
