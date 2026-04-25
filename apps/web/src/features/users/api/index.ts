/** Public API surface for the users feature — client-safe.
 *
 * The server-only ``listUsersServer`` deliberately isn't re-exported
 * here so ``next/headers`` stays out of the client bundle.
 */

export { listUsers, type ListUsersInput } from "./list-users";
