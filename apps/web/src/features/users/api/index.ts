/** Public API surface for the users feature — client-safe.
 *
 * Server-only modules (``./list-users-server``, ``./get-user-server``)
 * deliberately aren't re-exported so ``next/headers`` stays out of the
 * client bundle.
 */

export { getUser } from "./get-user";
export { listUsers, type ListUsersInput } from "./list-users";
