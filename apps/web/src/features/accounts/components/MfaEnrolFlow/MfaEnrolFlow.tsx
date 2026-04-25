"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { confirmMfaSetup, startMfaSetup } from "../../api";
import {
  mfaSetupConfirmSchema,
  type MfaSetupConfirmInput,
} from "../../lib/schemas";
import type { MfaSetupPayload } from "../../types";
import { MfaRecoveryCodesDisplay } from "../MfaRecoveryCodesDisplay";

type Stage =
  | { kind: "idle" }
  | { kind: "configuring"; setup: MfaSetupPayload }
  | { kind: "showing_codes"; codes: readonly string[] };

export function MfaEnrolFlow(): JSX.Element {
  const router = useRouter();
  const [stage, setStage] = useState<Stage>({ kind: "idle" });
  const [error, setError] = useState<string | null>(null);

  const handleStart = async (): Promise<void> => {
    setError(null);
    try {
      const setup = await startMfaSetup();
      setStage({ kind: "configuring", setup });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.problem.detail
          : "We couldn't start MFA setup. Please try again.";
      setError(message);
    }
  };

  if (stage.kind === "idle") {
    return (
      <div className="space-y-4">
        <p className="text-sm text-fg-muted">
          Two-factor authentication adds a second step at sign-in. You&rsquo;ll
          need an authenticator app such as 1Password, Authy, or Google
          Authenticator.
        </p>
        {error !== null && (
          <p
            role="alert"
            className="rounded-md border border-danger-fg px-3 py-2 text-sm text-danger-fg"
          >
            {error}
          </p>
        )}
        <button
          type="button"
          onClick={() => {
            void handleStart();
          }}
          className={cn(
            "rounded-md bg-accent px-4 py-2 text-sm font-medium text-fg-on-accent",
            "hover:bg-accent-emphasis",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          )}
        >
          Set up two-factor authentication
        </button>
      </div>
    );
  }

  if (stage.kind === "configuring") {
    return (
      <MFAConfigureForm
        setup={stage.setup}
        onConfirmed={(codes) => {
          setStage({ kind: "showing_codes", codes });
        }}
      />
    );
  }

  return (
    <MfaRecoveryCodesDisplay
      codes={stage.codes}
      onAcknowledge={() => {
        router.refresh();
      }}
    />
  );
}

interface MFAConfigureFormProps {
  readonly setup: MfaSetupPayload;
  readonly onConfirmed: (codes: readonly string[]) => void;
}

function MFAConfigureForm({
  setup,
  onConfirmed,
}: MFAConfigureFormProps): JSX.Element {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<MfaSetupConfirmInput>({
    resolver: zodResolver(mfaSetupConfirmSchema),
    defaultValues: { code: "" },
  });

  const onSubmit = async (input: MfaSetupConfirmInput): Promise<void> => {
    setSubmitError(null);
    try {
      const codes = await confirmMfaSetup(input.code);
      onConfirmed(codes);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.problem.detail
          : "We couldn't verify the code. Please try again.";
      setSubmitError(message);
    }
  };

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="mfa-configure-title"
      className="space-y-6"
    >
      <header className="space-y-2">
        <h2
          id="mfa-configure-title"
          className="text-lg font-semibold text-fg"
        >
          Scan the QR code
        </h2>
        <p className="text-sm text-fg-muted">
          Open your authenticator app and scan this code, or enter the secret
          manually. Then type the 6-digit code your app shows.
        </p>
      </header>

      <div className="flex flex-col items-center gap-3 rounded-md border border-border-subtle bg-bg-surface p-4">
        <Image
          src={setup.qr_data_url}
          alt="QR code for setting up two-factor authentication"
          width={192}
          height={192}
          unoptimized
        />
        <p className="break-all text-center font-mono text-xs text-fg-muted">
          {setup.secret}
        </p>
      </div>

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
          6-digit code
        </label>
        <input
          id="code"
          type="text"
          inputMode="numeric"
          autoComplete="one-time-code"
          maxLength={6}
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
        {isSubmitting ? "Verifying…" : "Confirm and enable"}
      </button>
    </form>
  );
}
