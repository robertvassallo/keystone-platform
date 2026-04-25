/**
 * Browser-side API client.
 *
 * In dev, requests go to ``/api/...`` and Next.js rewrites proxy them to
 * the Django backend so the browser sees same-origin (and the session
 * cookie travels). Writes carry the CSRF token from the ``csrftoken``
 * cookie as ``X-CSRFToken`` per Django's CSRF protocol.
 */

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS", "TRACE"]);

export const HTTP_NO_CONTENT = 204;
export const HTTP_UNAUTHORIZED = 401;

export function getCsrfToken(): string {
  if (typeof document === "undefined") return "";
  const match = /(?:^|;\s*)csrftoken=([^;]+)/.exec(document.cookie);
  return match?.[1] ? decodeURIComponent(match[1]) : "";
}

export interface ApiFetchOptions extends RequestInit {
  readonly json?: unknown;
}

export async function apiFetch(
  path: string,
  { json, ...init }: ApiFetchOptions = {},
): Promise<Response> {
  const headers = new Headers(init.headers);
  let body = init.body;

  if (json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(json);
  }

  const method = (init.method ?? "GET").toUpperCase();
  if (!SAFE_METHODS.has(method)) {
    const csrf = getCsrfToken();
    if (csrf) headers.set("X-CSRFToken", csrf);
  }

  const finalInit: RequestInit = {
    ...init,
    method,
    headers,
    credentials: "include",
  };
  if (body !== undefined && body !== null) {
    finalInit.body = body;
  }
  return fetch(path, finalInit);
}

export interface ProblemDetails {
  readonly type: string;
  readonly title: string;
  readonly status: number;
  readonly detail: string;
  readonly instance?: string;
  readonly request_id?: string;
  readonly errors?: Readonly<Record<string, readonly string[]>>;
}

export class ApiError extends Error {
  constructor(
    readonly problem: ProblemDetails,
    readonly response: Response,
  ) {
    super(problem.detail || problem.title);
    this.name = "ApiError";
  }
}

export async function readProblem(response: Response): Promise<ProblemDetails> {
  try {
    return (await response.json()) as ProblemDetails;
  } catch {
    return {
      type: "about:blank#unknown",
      title: response.statusText,
      status: response.status,
      detail: response.statusText,
    };
  }
}
