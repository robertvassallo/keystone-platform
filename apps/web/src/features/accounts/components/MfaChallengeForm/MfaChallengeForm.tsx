"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState, type JSX } from "react";
import { type Resolver, useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { verifyMfaChallenge } from "../../api";
import {
  mfaChallengeRecoverySchema,
  mfaChallengeTotpSchema,
} from "../../lib/schemas";
import type { User } from "../../types";

const MFA_CHALLENGE_EXPIRED = "mfa_challenge_expired";
const TOTP_CODE_LENGTH = 6;
const RECOVERY_CODE_LENGTH = 8;

type Mode = "totp" | "recovery";

interface FormValues {
  code: string;
}

interface MfaChallengeFormProps {
  readonly onAuthenticated: (user: User) => void;
  readonly onChallengeExpired: () => void;
}

export function MfaChallengeForm({
  onAuthenticated,
  onChallengeExpired,
}: MfaChallengeFormProps): JSX.Element {
  const [mode, setMode] = useState<Mode>("totp");

  return (
    <ChallengeFields
      key={mode}
      mode={mode}
      onAuthenticated={onAuthenticated}
      onChallengeExpired={onChallengeExpired}
      onSwitchMode={() => {
        setMode((prev) => (prev === "totp" ? "recovery" : "totp"));
      }}
    />
  );
}

interface ChallengeFieldsProps {
  readonly mode: Mode;
  readonly onAuthenticated: (user: User) => void;
  readonly onChallengeExpired: () => void;
  readonly onSwitchMode: () => void;
}

function ChallengeFields({
  mode,
  onAuthenticated,
  onChallengeExpired,
  onSwitchMode,
}: ChallengeFieldsProps): JSX.Element {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const schema =
    mode === "totp" ? mfaChallengeTotpSchema : mfaChallengeRecoverySchema;
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema) as Resolver<FormValues>,
    defaultValues: { code: "" },
  });

  const onSubmit = async (input: FormValues): Promise<void> => {
    setSubmitError(null);
    try {
      const user = await verifyMfaChallenge(input.code);
      onAuthenticated(user);
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.problem.type.endsWith(MFA_CHALLENGE_EXPIRED)) {
          onChallengeExpired();
          return;
        }
        setSubmitError(err.problem.detail);
        return;
      }
      setSubmitError("We couldn't reach the server. Please try again.");
    }
  };

  const isTotp = mode === "totp";

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="mfa-challenge-title"
      className="space-y-6"
    >
      <header className="space-y-2">
        <h1
          id="mfa-challenge-title"
          className="text-2xl font-semibold text-fg"
        >
          Verify it&rsquo;s you
        </h1>
        <p className="text-sm text-fg-muted">
          {isTotp
            ? "Open your authenticator app and enter the 6-digit code."
            : "Enter one of the recovery codes you saved when MFA was enabled."}
        </p>
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
        <label htmlFor="code" className="block text-sm font-medium text-fg">
          {isTotp ? "Authenticator code" : "Recovery code"}
        </label>
        <input
          id="code"
          type="text"
          inputMode={isTotp ? "numeric" : "text"}
          autoComplete="one-time-code"
          maxLength={isTotp ? TOTP_CODE_LENGTH : RECOVERY_CODE_LENGTH}
          required
          aria-invalid={errors.code ? "true" : "false"}
          aria-describedby={errors.code ? "code-error" : undefined}
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 font-mono text-lg tracking-widest text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.code ? "border-danger-fg" : "border-border",
          )}
          {...register("code")}
        />
        {errors.code && (
          <p id="code-error" className="text-sm text-danger-fg">
            {errors.code.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className={cn(
          "w-full rounded-md bg-accent px-4 py-2 text-sm font-medium text-fg-on-accent",
          "hover:bg-accent-emphasis",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          "disabled:cursor-not-allowed disabled:opacity-60",
        )}
      >
        {isSubmitting ? "Verifying…" : "Verify"}
      </button>

      <p className="text-sm">
        <button
          type="button"
          onClick={onSwitchMode}
          className="text-accent hover:underline focus-visible:underline focus-visible:outline-none"
        >
          {isTotp
            ? "Use a recovery code instead"
            : "Use authenticator code instead"}
        </button>
      </p>
    </form>
  );
}
