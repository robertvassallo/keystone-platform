/**
 * Zod schemas for the auth forms. The same schemas are the source of
 * truth for both the form types (via ``z.infer``) and the resolver
 * passed to React Hook Form.
 */

import { z } from "zod";

const MIN_PASSWORD_LENGTH = 12;
const MAX_PASSWORD_LENGTH = 128;
const MAX_EMAIL_LENGTH = 254;
const MAX_NAME_LENGTH = 150;

export const signInSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required.")
    .email("Email must include @ and a domain.")
    .max(MAX_EMAIL_LENGTH),
  password: z
    .string()
    .min(1, "Password is required.")
    .max(MAX_PASSWORD_LENGTH),
  rememberMe: z.boolean().default(false),
});

export type SignInInput = z.infer<typeof signInSchema>;

export const signUpSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required.")
    .email("Email must include @ and a domain.")
    .max(MAX_EMAIL_LENGTH),
  password: z
    .string()
    .min(
      MIN_PASSWORD_LENGTH,
      `Use at least ${String(MIN_PASSWORD_LENGTH)} characters.`,
    )
    .max(MAX_PASSWORD_LENGTH),
});

export type SignUpInput = z.infer<typeof signUpSchema>;

export const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required.")
    .email("Email must include @ and a domain.")
    .max(MAX_EMAIL_LENGTH),
});

export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;

export const resetPasswordSchema = z.object({
  uid: z.string().min(1, "Reset link is missing its uid."),
  token: z.string().min(1, "Reset link is missing its token."),
  password: z
    .string()
    .min(
      MIN_PASSWORD_LENGTH,
      `Use at least ${String(MIN_PASSWORD_LENGTH)} characters.`,
    )
    .max(MAX_PASSWORD_LENGTH),
});

export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;

export const changePasswordSchema = z
  .object({
    currentPassword: z
      .string()
      .min(1, "Current password is required.")
      .max(MAX_PASSWORD_LENGTH),
    newPassword: z
      .string()
      .min(
        MIN_PASSWORD_LENGTH,
        `Use at least ${String(MIN_PASSWORD_LENGTH)} characters.`,
      )
      .max(MAX_PASSWORD_LENGTH),
  })
  .refine((data) => data.currentPassword !== data.newPassword, {
    message: "New password must be different from the current password.",
    path: ["newPassword"],
  });

export type ChangePasswordInput = z.infer<typeof changePasswordSchema>;

export const mfaSetupConfirmSchema = z.object({
  code: z
    .string()
    .regex(/^\d{6}$/, "Enter the 6-digit code from your authenticator app."),
});

export type MfaSetupConfirmInput = z.infer<typeof mfaSetupConfirmSchema>;

export const mfaPasswordConfirmSchema = z.object({
  currentPassword: z
    .string()
    .min(1, "Current password is required.")
    .max(MAX_PASSWORD_LENGTH),
});

export type MfaPasswordConfirmInput = z.infer<typeof mfaPasswordConfirmSchema>;

export const mfaChallengeTotpSchema = z.object({
  code: z
    .string()
    .regex(/^\d{6}$/, "Enter the 6-digit code from your authenticator app."),
});

export type MfaChallengeTotpInput = z.infer<typeof mfaChallengeTotpSchema>;

export const mfaChallengeRecoverySchema = z.object({
  code: z
    .string()
    .regex(
      /^[A-Za-z0-9]{8}$/,
      "Recovery codes are 8 letters and digits.",
    )
    .transform((value) => value.toUpperCase()),
});

export type MfaChallengeRecoveryInput = z.infer<
  typeof mfaChallengeRecoverySchema
>;

export const profileSchema = z.object({
  firstName: z
    .string()
    .max(
      MAX_NAME_LENGTH,
      `First name must be ${String(MAX_NAME_LENGTH)} characters or fewer.`,
    ),
  lastName: z
    .string()
    .max(
      MAX_NAME_LENGTH,
      `Last name must be ${String(MAX_NAME_LENGTH)} characters or fewer.`,
    ),
});

export type ProfileInput = z.infer<typeof profileSchema>;

const MAX_TENANT_NAME_LENGTH = 200;
const MAX_TENANT_SLUG_LENGTH = 100;
const SLUG_PATTERN = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/;

export const tenantSettingsSchema = z.object({
  name: z
    .string()
    .min(1, "Name is required.")
    .max(
      MAX_TENANT_NAME_LENGTH,
      `Name must be ${String(MAX_TENANT_NAME_LENGTH)} characters or fewer.`,
    ),
  slug: z
    .string()
    .min(1, "Slug is required.")
    .max(
      MAX_TENANT_SLUG_LENGTH,
      `Slug must be ${String(MAX_TENANT_SLUG_LENGTH)} characters or fewer.`,
    )
    .regex(
      SLUG_PATTERN,
      "Use lowercase letters, digits, and hyphens only. No leading or trailing hyphens.",
    ),
});

export type TenantSettingsInput = z.infer<typeof tenantSettingsSchema>;
