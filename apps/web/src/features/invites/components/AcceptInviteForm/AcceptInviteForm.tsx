"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { acceptInvite } from "../../api";
import {
  acceptInviteSchema,
  type AcceptInviteInput,
} from "../../lib/schemas";

const INVALID_INVITE_TOKEN = "invalid_invite_token";
const DUPLICATE_MEMBER = "duplicate_member";

interface AcceptInviteFormProps {
  readonly uid: string;
  readonly token: string;
  readonly tenantName: string;
  readonly email: string;
}

export function AcceptInviteForm({
  uid,
  token,
  tenantName,
  email,
}: AcceptInviteFormProps): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<AcceptInviteInput>({
    resolver: zodResolver(acceptInviteSchema),
    defaultValues: { uid, token, password: "" },
  });

  const onSubmit = async (input: AcceptInviteInput): Promise<void> => {
    setSubmitError(null);
    try {
      await acceptInvite(input);
      router.push("/");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.problem.type.endsWith(INVALID_INVITE_TOKEN)) {
          setSubmitError(err.problem.detail);
          return;
        }
        if (err.problem.type.endsWith(DUPLICATE_MEMBER)) {
          setSubmitError(err.problem.detail);
          return;
        }
        const passwordMessage = err.problem.errors?.password?.[0];
        if (passwordMessage) {
          setError("password", { message: passwordMessage });
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
      aria-labelledby="accept-invite-title"
      className="space-y-6"
    >
      <h1 id="accept-invite-title" className="text-2xl font-semibold text-fg">
        Join {tenantName}
      </h1>

      <p className="text-sm text-fg-muted">
        Set a password to finish creating your account at{" "}
        <span className="font-medium text-fg">{email}</span>.
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
            Use at least 12 characters.
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
    </form>
  );
}
