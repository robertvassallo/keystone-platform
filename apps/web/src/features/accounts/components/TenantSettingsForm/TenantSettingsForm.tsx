"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState, type JSX } from "react";
import { useForm } from "react-hook-form";

import { ApiError } from "@/shared/lib/api-client";
import { cn } from "@/shared/lib/cn";

import { updateAccount } from "../../api";
import {
  tenantSettingsSchema,
  type TenantSettingsInput,
} from "../../lib/schemas";
import type { Account } from "../../types";

const DUPLICATE_SLUG = "duplicate_slug";

interface TenantSettingsFormProps {
  readonly initial: Account;
  readonly onCancel?: () => void;
}

export function TenantSettingsForm({
  initial,
  onCancel,
}: TenantSettingsFormProps): JSX.Element {
  const router = useRouter();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<TenantSettingsInput>({
    resolver: zodResolver(tenantSettingsSchema),
    defaultValues: { name: initial.name, slug: initial.slug },
  });

  const onSubmit = async (input: TenantSettingsInput): Promise<void> => {
    setSubmitError(null);
    try {
      await updateAccount({ name: input.name, slug: input.slug });
      setSubmitted(true);
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.problem.type.endsWith(DUPLICATE_SLUG)) {
          setError("slug", { message: err.problem.detail });
          return;
        }
        const slugMessage = err.problem.errors?.slug?.[0];
        if (slugMessage) {
          setError("slug", { message: slugMessage });
          return;
        }
        const nameMessage = err.problem.errors?.name?.[0];
        if (nameMessage) {
          setError("name", { message: nameMessage });
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
      aria-labelledby="tenant-settings-title"
      className="space-y-6"
    >
      <h2
        id="tenant-settings-title"
        className="text-base font-semibold text-fg"
      >
        Tenant settings
      </h2>

      {submitted && !isDirty && (
        <p
          role="status"
          className="rounded-md border border-success-fg px-3 py-2 text-sm text-success-fg"
        >
          Tenant saved.
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
        <label htmlFor="tenant-name" className="block text-sm font-medium text-fg">
          Name
        </label>
        <input
          id="tenant-name"
          type="text"
          autoComplete="organization"
          aria-invalid={errors.name ? "true" : "false"}
          aria-describedby={errors.name ? "tenant-name-error" : undefined}
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.name ? "border-danger-fg" : "border-border",
          )}
          {...register("name")}
        />
        {errors.name && (
          <p id="tenant-name-error" className="text-sm text-danger-fg">
            {errors.name.message}
          </p>
        )}
      </div>

      <div className="space-y-1">
        <label htmlFor="tenant-slug" className="block text-sm font-medium text-fg">
          URL slug
        </label>
        <input
          id="tenant-slug"
          type="text"
          autoComplete="off"
          autoCapitalize="off"
          spellCheck={false}
          aria-invalid={errors.slug ? "true" : "false"}
          aria-describedby={errors.slug ? "tenant-slug-error" : "tenant-slug-help"}
          className={cn(
            "w-full rounded-md border bg-bg-surface px-3 py-2 font-mono text-fg",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            errors.slug ? "border-danger-fg" : "border-border",
          )}
          {...register("slug")}
        />
        {errors.slug ? (
          <p id="tenant-slug-error" className="text-sm text-danger-fg">
            {errors.slug.message}
          </p>
        ) : (
          <p id="tenant-slug-help" className="text-sm text-fg-muted">
            Lowercase letters, digits, hyphens. Used as the tenant&rsquo;s URL identifier.
          </p>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={isSubmitting || !isDirty}
          className={cn(
            "rounded-md bg-accent px-4 py-2 text-sm font-medium text-fg-on-accent",
            "hover:bg-accent-emphasis",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            "disabled:cursor-not-allowed disabled:opacity-60",
          )}
        >
          {isSubmitting ? "Saving…" : "Save tenant"}
        </button>
        {onCancel !== undefined && (
          <button
            type="button"
            onClick={onCancel}
            className={cn(
              "rounded-md border border-border px-4 py-2 text-sm font-medium text-fg",
              "hover:bg-bg-canvas",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            )}
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
