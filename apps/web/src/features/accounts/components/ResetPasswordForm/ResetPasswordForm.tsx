"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { confirmPasswordReset } from "../../api";
import {
  resetPasswordSchema,
  type ResetPasswordInput,
} from "../../lib/schemas";

interface ResetPasswordFormProps {
  readonly uid: string;
  readonly token: string;
}

export function ResetPasswordForm({
  uid,
  token,
}: ResetPasswordFormProps): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordInput>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { uid, token, password: "" },
  });

  const onSubmit = async (input: ResetPasswordInput): Promise<void> => {
    setSubmitError(null);
    try {
      await confirmPasswordReset(input);
      router.push("/sign-in?reset=success");
      router.refresh();
    } catch (err) {
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
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="reset-password-title"
      className="space-y-6"
    >
      <h1 id="reset-password-title" className="text-2xl font-semibold text-fg">
        Set a new password
      </h1>

      {submitError !== null && (
        <p
          role="alert"
          className="rounded-md border border-danger-fg px-3 py-2 text-sm text-danger-fg"
        >
          {submitError}
        </p>
      )}

      <input type="hidden" {...register("uid")} />
      <input type="hidden" {...register("token")} />

      <div className="space-y-1">
        <label htmlFor="password" className="block text-sm font-medium text-fg">
          New password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          required
          aria-invalid={errors.password ? "true" : "false"}
          aria-describedby={
            errors.password ? "password-error" : "password-help"
          }
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.password ? "border-danger-fg" : "border-border",
          )}
          {...register("password")}
        />
        {errors.password ? (
          <p id="password-error" className="text-sm text-danger-fg">
            {errors.password.message}
          </p>
        ) : (
          <p id="password-help" className="text-sm text-fg-muted">
            Use at least 12 characters. Avoid common passwords.
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
        {isSubmitting ? "Saving…" : "Save new password"}
      </button>

      <p className="text-sm text-fg-muted">
        <Link
          href="/forgot-password"
          className="text-accent hover:underline focus-visible:underline"
        >
          Request a new reset link
        </Link>
      </p>
    </form>
  );
}
