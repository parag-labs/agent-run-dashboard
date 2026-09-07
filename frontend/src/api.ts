// A tiny typed API client. Kept dependency-free (just fetch) and separate from the
// components so the request/format logic can be unit-tested on its own.

export interface Run {
  id: number;
  name: string;
  model: string;
  status: string;
  tokens: number;
  cost: number;
  latency_ms: number;
}

export interface Stats {
  runs: number;
  total_tokens: number;
  total_cost: number;
  by_status: Record<string, number>;
  by_model: Record<string, number>;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, token: string | null, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const resp = await fetch(path, { ...init, headers: { ...headers, ...(init.headers ?? {}) } });
  if (!resp.ok) {
    let detail = resp.statusText;
    try {
      detail = (await resp.json()).detail ?? detail;
    } catch {
      // response wasn't JSON; keep the status text
    }
    throw new ApiError(resp.status, detail);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export const api = {
  register: (username: string, password: string) =>
    request<{ access_token: string }>("/api/auth/register", null, {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  login: (username: string, password: string) =>
    request<{ access_token: string }>("/api/auth/login", null, {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  listRuns: (token: string) => request<Run[]>("/api/runs", token),
  createRun: (token: string, run: Partial<Run>) =>
    request<Run>("/api/runs", token, { method: "POST", body: JSON.stringify(run) }),
  deleteRun: (token: string, id: number) =>
    request<void>(`/api/runs/${id}`, token, { method: "DELETE" }),
  stats: (token: string) => request<Stats>("/api/stats", token),
};

export function formatCost(cost: number): string {
  return `$${cost.toFixed(4)}`;
}
