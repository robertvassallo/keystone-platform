"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { disableMfa, regenerateRecoveryCodes } from "../../api";
import {
  mfaPasswordConfirmSchema,
  type MfaPasswordConfirmInput,
} from "../../lib/schemas";
import type { MfaStatus } from "../../types";
import { MfaRecoveryCodesDisplay } from "../MfaRecoveryCodesDisplay";

interface MfaManagementPanelProps {
  readonly status: MfaStatus;
}

type View =
  | { kind: "idle" }
  | { kind: "disabling" }
  | { kind: "regenerating" }
  | { kind: "showing_new_codes"; codes: readonly string[] };

export function MfaManagementPanel({
  status,
}: MfaManagementPanelProps): JSX.Element {
  const router = useRouter();
  const [view, setView] = useState<View>({ kind: "idle" });

  if (view.kind === "showing_new_codes") {
    return (
      <MfaRecoveryCodesDisplay
        codes={view.codes}
        onAcknowledge={() => {
          setView({ kind: "idle" });
          router.refresh();
        }}
      />
    );
  }

  if (view.kind === "disabling") {
    return (
      <PasswordConfirmForm
        title="Disable two-factor authentication"
        description="Enter your password to remove your authenticator and recovery codes."
        submitLabel="Disable"
        onSubmit={async ({ currentPassword }) => {
          await disableMfa(currentPassword);
          router.refresh();
        }}
        onCancel={() => {
          setView({ kind: "idle" });
        }}
      />
    );
  }

  if (view.kind === "regenerating") {
    return (
      <PasswordConfirmForm
        title="Regenerate recovery codes"
        description="Enter your password to invalidate the old codes and get a new set."
        submitLabel="Generate new codes"
        onSubmit={async ({ currentPassword }) => {
          const codes = await regenerateRecoveryCodes(currentPassword);
          setView({ kind: "showing_new_codes", codes });
        }}
        onCancel={() => {
          setView({ kind: "idle" });
        }}
      />
    );
  }

  return (
    <section
      aria-labelledby="mfa-status-title"
      className="space-y-4 rounded-md border border-border-subtle bg-bg-surface p-4"
    >
      <header className="space-y-1">
        <h2 id="mfa-status-title" className="text-lg font-semibold text-fg">
          Two-factor authentication is on
        </h2>
        <p className="text-sm text-fg-muted">
          {status.recovery_codes_remaining} recovery code
          {status.recovery_codes_remaining === 1 ? "" : "s"} remaining.
        </p>
      </header>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => {
            setView({ kind: "regenerating" });
          }}
          className={cn(
            "rounded-md border border-border bg-bg-surface px-4 py-2 text-sm font-medium text-fg",
            "hover:bg-bg-canvas",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          Regenerate recovery codes
        </button>
        <button
          type="button"
          onClick={() => {
            setView({ kind: "disabling" });
          }}
          className={cn(
            "rounded-md border border-danger-fg px-4 py-2 text-sm font-medium text-danger-fg",
            "hover:bg-bg-canvas",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          Disable
        </button>
      </div>
    </section>
  );
}

interface PasswordConfirmFormProps {
  readonly title: string;
  readonly description: string;
  readonly submitLabel: string;
  readonly onSubmit: (input: MfaPasswordConfirmInput) => Promise<void>;
  readonly onCancel: () => void;
}

function PasswordConfirmForm({
  title,
  description,
  submitLabel,
  onSubmit,
  onCancel,
}: PasswordConfirmFormProps): JSX.Element {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<MfaPasswordConfirmInput>({
    resolver: zodResolver(mfaPasswordConfirmSchema),
    defaultValues: { currentPassword: "" },
  });

  const handler = async (input: MfaPasswordConfirmInput): Promise<void> => {
    setSubmitError(null);
    try {
      await onSubmit(input);
    } catch (err) {
      if (
        err instanceof ApiError &&
        err.problem.type.endsWith("wrong_current_password")
      ) {
        setError("currentPassword", { message: err.problem.detail });
        return;
      }
      const message =
        err instanceof ApiError
          ? err.problem.detail
          : "We couldn't reach the server. Please try again.";
      setSubmitError(message);
    }
  };

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(handler)(e);
      }}
      aria-labelledby="confirm-title"
      className="space-y-6 rounded-md border border-border-subtle bg-bg-surface p-4"
    >
      <header className="space-y-1">
        <h2 id="confirm-title" className="text-lg font-semibold text-fg">
          {title}
        </h2>
        <p className="text-sm text-fg-muted">{description}</p>
      </header>

      {submitError !== null && (
        <p
          role="alert"
          className="rounded-md border border-danger-fg px-3 py-2 text-sm text-danger-fg"
        >
          {submitError}
        </p>
      )}

      <div className="space-y-1">
        <label
          htmlFor="currentPassword"
          className="block text-sm font-medium text-fg"
        >
          Current password
        </label>
        <input
          id="currentPassword"
          type="password"
          autoComplete="current-password"
          required
          aria-invalid={errors.currentPassword ? "true" : "false"}
          aria-describedby={
            errors.currentPassword ? "currentPassword-error" : undefined
          }
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.currentPassword ? "border-danger-fg" : "border-border",
          )}
          {...register("currentPassword")}
        />
        {errors.currentPassword && (
          <p id="currentPassword-error" className="text-sm text-danger-fg">
            {errors.currentPassword.message}
          </p>
        )}
      </div>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onCancel}
          className={cn(
            "rounded-md border border-border bg-bg-surface px-4 py-2 text-sm font-medium text-fg",
            "hover:bg-bg-canvas",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className={cn(
            "rounded-md bg-accent px-4 py-2 text-sm font-medium text-fg-on-accent",
            "hover:bg-accent-emphasis",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            "disabled:cursor-not-allowed disabled:opacity-60",
          )}
        >
          {isSubmitting ? "Working…" : submitLabel}
        </button>
      </div>
    </form>
  );
}
