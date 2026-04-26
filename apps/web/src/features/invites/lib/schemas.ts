/**
 * Zod schemas for the invites forms.
 */

import { z } from "zod";

const MAX_EMAIL_LENGTH = 254;
const MIN_PASSWORD_LENGTH = 12;
const MAX_PASSWORD_LENGTH = 128;

export const sendInviteSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required.")
    .email("Email must include @ and a domain.")
    .max(MAX_EMAIL_LENGTH),
});

export type SendInviteInput = z.infer<typeof sendInviteSchema>;

export const acceptInviteSchema = z.object({
  uid: z.string().min(1),
  token: z.string().min(1),
  password: z
    .string()
    .min(
      MIN_PASSWORD_LENGTH,
      `Use at least ${String(MIN_PASSWORD_LENGTH)} characters.`,
    )
    .max(MAX_PASSWORD_LENGTH),
});

export type AcceptInviteInput = z.infer<typeof acceptInviteSchema>;
