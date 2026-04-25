"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { requestPasswordReset } from "../../api";
import {
  forgotPasswordSchema,
  type ForgotPasswordInput,
} from "../../lib/schemas";

export function ForgotPasswordForm(): JSX.Element {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordInput>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: "" },
  });

  const onSubmit = async (input: ForgotPasswordInput): Promise<void> => {
    setSubmitError(null);
    try {
      await requestPasswordReset(input);
      setSubmitted(true);
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.problem.detail
          : "We couldn't reach the server. Please try again.";
      setSubmitError(message);
    }
  };

  if (submitted) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-semibold text-fg">Check your email</h1>
        <p className="text-sm text-fg-muted">
          If that address is registered, we&rsquo;ve sent a password-reset link
          that expires in one hour.
        </p>
        <p className="text-sm">
          <Link
            href="/sign-in"
            className="text-accent hover:underline focus-visible:underline"
          >
            Back to sign in
          </Link>
        </p>
      </div>
    );
  }

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="forgot-password-title"
      className="space-y-6"
    >
      <h1 id="forgot-password-title" className="text-2xl font-semibold text-fg">
        Forgot your password?
      </h1>

      <p className="text-sm text-fg-muted">
        Enter your email and we&rsquo;ll send a reset link.
      </p>

      {submitError !== null && (
        <p
          role="alert"
          className="rounded-md border border-danger-fg px-3 py-2 text-sm text-danger-fg"
        >
          {submitError}
        </p>
      )}

      <div className="space-y-1">
        <label htmlFor="email" className="block text-sm font-medium text-fg">
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          aria-invalid={errors.email ? "true" : "false"}
          aria-describedby={errors.email ? "email-error" : undefined}
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.email ? "border-danger-fg" : "border-border",
          )}
          {...register("email")}
        />
        {errors.email && (
          <p id="email-error" className="text-sm text-danger-fg">
            {errors.email.message}
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
        {isSubmitting ? "Sending…" : "Send reset link"}
      </button>

      <p className="text-sm text-fg-muted">
        <Link
          href="/sign-in"
          className="text-accent hover:underline focus-visible:underline"
        >
          Back to sign in
        </Link>
      </p>
    </form>
  );
}
