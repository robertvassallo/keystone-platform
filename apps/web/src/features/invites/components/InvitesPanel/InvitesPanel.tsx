"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, useTransition, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { revokeInvite, sendInvite } from "../../api";
import { sendInviteSchema, type SendInviteInput } from "../../lib/schemas";
import type { Invite } from "../../types";

const DUPLICATE_INVITE = "duplicate_invite";
const DUPLICATE_MEMBER = "duplicate_member";

interface InvitesPanelProps {
  readonly invites: readonly Invite[];
}

export function InvitesPanel({ invites }: InvitesPanelProps): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState<string | null>(null);
  const [, startTransition] = useTransition();
  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SendInviteInput>({
    resolver: zodResolver(sendInviteSchema),
    defaultValues: { email: "" },
  });

  const onSubmit = async (input: SendInviteInput): Promise<void> => {
    setSubmitError(null);
    try {
      await sendInvite({ email: input.email });
      setSubmitted(input.email);
      reset({ email: "" });
      startTransition(() => {
        router.refresh();
      });
    } catch (err) {
      if (err instanceof ApiError) {
        if (
          err.problem.type.endsWith(DUPLICATE_MEMBER)
          || err.problem.type.endsWith(DUPLICATE_INVITE)
        ) {
          setError("email", { message: err.problem.detail });
          return;
        }
        const emailMessage = err.problem.errors?.email?.[0];
        if (emailMessage) {
          setError("email", { message: emailMessage });
          return;
        }
        setSubmitError(err.problem.detail);
        return;
      }
      setSubmitError("We couldn't reach the server. Please try again.");
    }
  };

  const onRevoke = (id: string): void => {
    void (async () => {
      try {
        await revokeInvite({ id });
        startTransition(() => {
          router.refresh();
        });
      } catch (err) {
        if (err instanceof ApiError) {
          setSubmitError(err.problem.detail);
        } else {
          setSubmitError("We couldn't revoke that invite.");
        }
      }
    })();
  };

  const pending = invites.filter((invite) => invite.status === "pending");

  return (
    <section
      aria-labelledby="invites-panel-title"
      className="space-y-4 rounded-md border border-border-subtle bg-bg-surface p-4"
    >
      <header className="flex items-center justify-between">
        <h2
          id="invites-panel-title"
          className="text-sm font-semibold text-fg"
        >
          Invite a user
        </h2>
        {pending.length > 0 ? (
          <p className="text-xs text-fg-muted">
            {pending.length} pending
          </p>
        ) : null}
      </header>

      <form
        noValidate
        onSubmit={(e) => {
          void handleSubmit(onSubmit)(e);
        }}
        aria-label="Invite a user by email"
        className="flex flex-col gap-2 sm:flex-row sm:items-start"
      >
        <div className="flex-1 space-y-1">
          <label htmlFor="invite-email" className="sr-only">
            Email
          </label>
          <input
            id="invite-email"
            type="email"
            autoComplete="off"
            placeholder="newhire@example.com"
            aria-invalid={errors.email ? "true" : "false"}
            aria-describedby={
              errors.email ? "invite-email-error" : undefined
            }
            className={cn(
              "h-9 w-full rounded-md border bg-bg-surface px-3 text-sm text-fg",
              "placeholder:text-fg-subtle",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
              errors.email ? "border-danger-fg" : "border-border",
            )}
            {...register("email")}
          />
          {errors.email && (
            <p id="invite-email-error" className="text-sm text-danger-fg">
              {errors.email.message}
            </p>
          )}
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          className={cn(
            "h-9 rounded-md bg-accent px-4 text-sm font-medium text-fg-on-accent",
            "hover:bg-accent-emphasis",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            "disabled:cursor-not-allowed disabled:opacity-60",
          )}
        >
          {isSubmitting ? "Sending…" : "Send invite"}
        </button>
      </form>

      {submitted !== null && (
        <p role="status" className="text-sm text-success-fg">
          Invite sent to {submitted}.
        </p>
      )}

      {submitError !== null && (
        <p role="alert" className="text-sm text-danger-fg">
          {submitError}
        </p>
      )}

      {pending.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-fg-muted">
            Pending invites
          </h3>
          <ul className="divide-y divide-border-subtle text-sm">
            {pending.map((invite) => (
              <li
                key={invite.id}
                className="flex items-center justify-between gap-2 py-2"
              >
                <div>
                  <p className="font-medium text-fg">{invite.email}</p>
                  <p className="text-xs text-fg-muted">
                    Invited by {invite.invited_by_email}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    onRevoke(invite.id);
                  }}
                  aria-label={`Revoke invite for ${invite.email}`}
                  className={cn(
                    "rounded-md border border-border bg-bg-surface px-2 py-1 text-xs font-medium text-fg",
                    "hover:bg-bg-canvas",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
                  )}
                >
                  Revoke
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
