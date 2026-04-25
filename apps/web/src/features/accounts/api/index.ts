/** Public API surface for the accounts feature — client-safe.
 *
 * Server-only modules (``./me-server``, ``./mfa-status-server``) live in
 * their own files and must not be re-exported here, otherwise Next.js
 * will pull ``next/headers`` into the client bundle.
 */

export { changePassword } from "./change-password";
export { confirmPasswordReset } from "./confirm-password-reset";
export { getMe } from "./me";
export {
  disableMfa,
  regenerateRecoveryCodes,
} from "./mfa-disable";
export { confirmMfaSetup, startMfaSetup } from "./mfa-setup";
export { getMfaStatus } from "./mfa-status";
export { verifyMfaChallenge } from "./mfa-verify";
export { requestPasswordReset } from "./request-password-reset";
export { signIn, type SignInResult } from "./sign-in";
export { signOut } from "./sign-out";
export { signUp } from "./sign-up";
