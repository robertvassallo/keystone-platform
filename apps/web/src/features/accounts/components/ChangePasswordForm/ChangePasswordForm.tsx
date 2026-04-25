"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { changePassword } from "../../api";
import {
  changePasswordSchema,
  type ChangePasswordInput,
} from "../../lib/schemas";

const WRONG_CURRENT_PASSWORD = "wrong_current_password";

export function ChangePasswordForm(): JSX.Element {
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ChangePasswordInput>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: { currentPassword: "", newPassword: "" },
  });

  const onSubmit = async (input: ChangePasswordInput): Promise<void> => {
    setSubmitError(null);
    try {
      await changePassword(input);
      setSubmitted(true);
      reset({ currentPassword: "", newPassword: "" });
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.problem.type.endsWith(WRONG_CURRENT_PASSWORD)) {
          setError("currentPassword", { message: err.problem.detail });
          return;
        }
        const newPasswordErrors = err.problem.errors?.new_password;
        if (newPasswordErrors) {
          setError("newPassword", {
            message: newPasswordErrors[0] ?? err.problem.detail,
          });
          return;
        }
        setSubmitError(err.problem.detail);
        return;
      }
      setSubmitError("We couldn't reach the server. Please try again.");
    }
  };

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="change-password-title"
      className="space-y-6"
    >
      <h1
        id="change-password-title"
        className="text-2xl font-semibold text-fg"
      >
        Change password
      </h1>

      <p className="text-sm text-fg-muted">
        Saving will keep this device signed in and sign you out everywhere
        else.
      </p>

      {submitted && (
        <p
          role="status"
          className="rounded-md border border-success-fg px-3 py-2 text-sm text-success-fg"
        >
          Password changed. Other sessions have been signed out.
        </p>
      )}

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

      <div className="space-y-1">
        <label
          htmlFor="newPassword"
          className="block text-sm font-medium text-fg"
        >
          New password
        </label>
        <input
          id="newPassword"
          type="password"
          autoComplete="new-password"
          required
          aria-invalid={errors.newPassword ? "true" : "false"}
          aria-describedby={
            errors.newPassword ? "newPassword-error" : "newPassword-help"
          }
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.newPassword ? "border-danger-fg" : "border-border",
          )}
          {...register("newPassword")}
        />
        {errors.newPassword ? (
          <p id="newPassword-error" className="text-sm text-danger-fg">
            {errors.newPassword.message}
          </p>
        ) : (
          <p id="newPassword-help" className="text-sm text-fg-muted">
            Use at least 12 characters. Different from your current password.
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
    </form>
  );
}
