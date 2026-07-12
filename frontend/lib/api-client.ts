// Typed client for the backend's versioned API (backend/app/api/v1).
//
// - Browser requests: same-origin `/api/v1/...`, proxied to the backend
//   by the rewrite in next.config.ts.
// - Server-side requests (SSR, build-time prerender): Node's fetch has
//   no browser origin to resolve a relative URL against, so this must
//   be an absolute URL — NEXT_PUBLIC_API_URL in production, or the
//   local backend directly in dev/build.
const API_BASE =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_API_URL ?? "/api/v1")
    : (process.env.NEXT_PUBLIC_API_URL ?? process.env.INTERNAL_API_URL ?? "http://localhost:8000/api/v1");

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions extends RequestInit {
  token?: string;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, headers, ...rest } = options;

  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, token?: string) => request<T>(path, { method: "GET", token }),
  post: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body), token }),
  patch: <T>(path: string, body: unknown, token?: string) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body), token }),
};
