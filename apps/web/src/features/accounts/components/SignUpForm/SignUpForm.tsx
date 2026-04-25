"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { signUp } from "../../api";
import { signUpSchema, type SignUpInput } from "../../lib/schemas";

export function SignUpForm(): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<SignUpInput>({
    resolver: zodResolver(signUpSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (input: SignUpInput): Promise<void> => {
    setSubmitError(null);
    try {
      await signUp(input);
      router.push("/");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.problem.errors) {
          for (const [field, messages] of Object.entries(err.problem.errors)) {
            if (field === "email" || field === "password") {
              setError(field, { message: messages[0] ?? err.problem.detail });
            }
          }
          return;
        }
        setSubmitError(err.problem.detail);
        return;
      }
      setSubmitError("Sign-up failed. Try again.");
    }
  };

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="sign-up-title"
      className="space-y-6"
    >
      <h1 id="sign-up-title" className="text-2xl font-semibold text-fg">
        Create your account
      </h1>

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

      <div className="space-y-1">
        <label htmlFor="password" className="block text-sm font-medium text-fg">
          Password
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
        {isSubmitting ? "Creating account…" : "Create account"}
      </button>

      <p className="text-sm text-fg-muted">
        Already have an account?{" "}
        <Link
          href="/sign-in"
          className="text-accent hover:underline focus-visible:underline"
        >
          Sign in
        </Link>
      </p>
    </form>
  );
}
