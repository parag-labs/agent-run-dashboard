import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, api, formatCost } from "../src/api.js";

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    statusText: "",
    json: async () => body,
  });
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("sends credentials on register and returns the token", async () => {
    const fetchMock = mockFetch(201, { access_token: "abc" });
    vi.stubGlobal("fetch", fetchMock);

    const out = await api.register("alice", "pw");
    expect(out.access_token).toBe("abc");
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/auth/register");
    expect(JSON.parse(init.body)).toEqual({ username: "alice", password: "pw" });
  });

  it("attaches the bearer token on authenticated calls", async () => {
    const fetchMock = mockFetch(200, []);
    vi.stubGlobal("fetch", fetchMock);

    await api.listRuns("my-token");
    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer my-token");
  });

  it("throws ApiError carrying the server detail", async () => {
    vi.stubGlobal("fetch", mockFetch(401, { detail: "bad credentials" }));
    await expect(api.login("x", "y")).rejects.toMatchObject({ status: 401, message: "bad credentials" });
    await expect(api.login("x", "y")).rejects.toBeInstanceOf(ApiError);
  });

  it("treats 204 as an empty success", async () => {
    vi.stubGlobal("fetch", mockFetch(204, null));
    await expect(api.deleteRun("t", 1)).resolves.toBeUndefined();
  });
});

describe("formatCost", () => {
  it("formats to four decimals with a dollar sign", () => {
    expect(formatCost(1.2)).toBe("$1.2000");
    expect(formatCost(0)).toBe("$0.0000");
  });
});
