"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { updateMe } from "../../api";
import { profileSchema, type ProfileInput } from "../../lib/schemas";
import type { User } from "../../types";

interface ProfileFormProps {
  readonly initial: User;
}

export function ProfileForm({ initial }: ProfileFormProps): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<ProfileInput>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      firstName: initial.first_name,
      lastName: initial.last_name,
    },
  });

  const onSubmit = async (input: ProfileInput): Promise<void> => {
    setSubmitError(null);
    try {
      await updateMe({
        firstName: input.firstName,
        lastName: input.lastName,
      });
      setSubmitted(true);
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        const firstNameMessage = err.problem.errors?.first_name?.[0];
        if (firstNameMessage) {
          setError("firstName", { message: firstNameMessage });
          return;
        }
        const lastNameMessage = err.problem.errors?.last_name?.[0];
        if (lastNameMessage) {
          setError("lastName", { message: lastNameMessage });
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
      aria-labelledby="profile-form-title"
      className="space-y-6"
    >
      <h1
        id="profile-form-title"
        className="text-2xl font-semibold text-fg"
      >
        Profile
      </h1>

      <p className="text-sm text-fg-muted">
        These names appear on your dashboard and on email invitations you send.
      </p>

      {submitted && !isDirty && (
        <p
          role="status"
          className="rounded-md border border-success-fg px-3 py-2 text-sm text-success-fg"
        >
          Profile saved.
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
          htmlFor="firstName"
          className="block text-sm font-medium text-fg"
        >
          First name
        </label>
        <input
          id="firstName"
          type="text"
          autoComplete="given-name"
          aria-invalid={errors.firstName ? "true" : "false"}
          aria-describedby={
            errors.firstName ? "firstName-error" : undefined
          }
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.firstName ? "border-danger-fg" : "border-border",
          )}
          {...register("firstName")}
        />
        {errors.firstName && (
          <p id="firstName-error" className="text-sm text-danger-fg">
            {errors.firstName.message}
          </p>
        )}
      </div>

      <div className="space-y-1">
        <label
          htmlFor="lastName"
          className="block text-sm font-medium text-fg"
        >
          Last name
        </label>
        <input
          id="lastName"
          type="text"
          autoComplete="family-name"
          aria-invalid={errors.lastName ? "true" : "false"}
          aria-describedby={
            errors.lastName ? "lastName-error" : undefined
          }
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.lastName ? "border-danger-fg" : "border-border",
          )}
          {...register("lastName")}
        />
        {errors.lastName && (
          <p id="lastName-error" className="text-sm text-danger-fg">
            {errors.lastName.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !isDirty}
        className={cn(
          "w-full rounded-md bg-accent px-4 py-2 text-sm font-medium text-fg-on-accent",
          "hover:bg-accent-emphasis",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
          "disabled:cursor-not-allowed disabled:opacity-60",
        )}
      >
        {isSubmitting ? "Saving…" : "Save profile"}
      </button>
    </form>
  );
}
