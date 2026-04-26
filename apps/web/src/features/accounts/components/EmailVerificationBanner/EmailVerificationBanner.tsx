"use client";

import { useState, type JSX } from "react";

import { ApiError } from "@/shared/lib/api-client";

import { requestEmailVerification } from "../../api/request-email-verification";

const HTTP_TOO_MANY_REQUESTS = 429;

type Status =
  | { readonly kind: "idle" }
  | { readonly kind: "pending" }
  | { readonly kind: "sent" }
  | { readonly kind: "throttled" }
  | { readonly kind: "error"; readonly message: string };

export function EmailVerificationBanner(): JSX.Element {
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  const onResend = async (): Promise<void> => {
    setStatus({ kind: "pending" });
    try {
      await requestEmailVerification();
      setStatus({ kind: "sent" });
    } catch (error) {
      if (error instanceof ApiError && error.response.status === HTTP_TOO_MANY_REQUESTS) {
        setStatus({ kind: "throttled" });
      } else {
        setStatus({
          kind: "error",
          message: "Couldn't send the verification email. Try again in a moment.",
        });
      }
    }
  };

  return (
    <aside
      role="region"
      aria-labelledby="email-verification-heading"
      className="border-b border-warning-fg/30 bg-warning-bg/40 px-6 py-3 text-sm"
    >
      <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-3">
        <div>
          <h2
            id="email-verification-heading"
            className="font-semibold text-fg"
          >
            Verify your email
          </h2>
          <p className="text-fg-muted">
            We sent a confirmation link when you signed up. Check your inbox to
            keep your account secure.
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <button
            type="button"
            onClick={() => {
              void onResend();
            }}
            disabled={status.kind === "pending" || status.kind === "sent"}
            className="rounded-md border border-border bg-bg-surface px-3 py-1.5 text-sm font-medium text-fg hover:bg-bg-canvas focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent disabled:cursor-not-allowed disabled:opacity-60"
          >
            {status.kind === "pending"
              ? "Sending…"
              : status.kind === "sent"
                ? "Email sent"
                : "Resend verification email"}
          </button>
          {status.kind === "throttled" ? (
            <p role="status" className="text-xs text-fg-muted">
              Slow down a moment before requesting another link.
            </p>
          ) : null}
          {status.kind === "error" ? (
            <p role="alert" className="text-xs text-error-fg">
              {status.message}
            </p>
          ) : null}
        </div>
      </div>
    </aside>
  );
}
