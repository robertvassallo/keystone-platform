"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { signIn } from "../../api";
import { signInSchema, type SignInInput } from "../../lib/schemas";

interface SignInFormProps {
  readonly nextPath?: string;
}

export function SignInForm({ nextPath = "/" }: SignInFormProps): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SignInInput>({
    resolver: zodResolver(signInSchema),
    defaultValues: { email: "", password: "", rememberMe: false },
  });

  const onSubmit = async (input: SignInInput): Promise<void> => {
    setSubmitError(null);
    try {
      await signIn(input);
      router.push(nextPath);
      router.refresh();
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.problem.detail
          : "Sign-in failed. Try again.";
      setSubmitError(message);
    }
  };

  return (
    <form
      noValidate
      onSubmit={(e) => {
        void handleSubmit(onSubmit)(e);
      }}
      aria-labelledby="sign-in-title"
      className="space-y-6"
    >
      <h1 id="sign-in-title" className="text-2xl font-semibold text-fg">
        Sign in
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
          autoComplete="current-password"
          required
          aria-invalid={errors.password ? "true" : "false"}
          aria-describedby={errors.password ? "password-error" : undefined}
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.password ? "border-danger-fg" : "border-border",
          )}
          {...register("password")}
        />
        {errors.password && (
          <p id="password-error" className="text-sm text-danger-fg">
            {errors.password.message}
          </p>
        )}
      </div>

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <input
            id="remember-me"
            type="checkbox"
            className="h-4 w-4 rounded border-border text-accent focus-visible:ring-2 focus-visible:ring-accent"
            {...register("rememberMe")}
          />
          <label htmlFor="remember-me" className="text-sm text-fg">
            Remember me for 30 days
          </label>
        </div>
        <Link
          href="/forgot-password"
          className="text-sm text-accent hover:underline focus-visible:underline"
        >
          Forgot password?
        </Link>
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
        {isSubmitting ? "Signing in…" : "Sign in"}
      </button>

      <p className="text-sm text-fg-muted">
        New here?{" "}
        <Link
          href="/sign-up"
          className="text-accent hover:underline focus-visible:underline"
        >
          Create an account
        </Link>
      </p>
    </form>
  );
}
