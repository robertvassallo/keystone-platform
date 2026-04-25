/**
 * Zod schemas for the auth forms. The same schemas are the source of
 * truth for both the form types (via ``z.infer``) and the resolver
 * passed to React Hook Form.
 */

import { z } from "zod";

const MIN_PASSWORD_LENGTH = 12;
const MAX_PASSWORD_LENGTH = 128;
const MAX_EMAIL_LENGTH = 254;

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
