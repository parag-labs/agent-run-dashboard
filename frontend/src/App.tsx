import { useCallback, useEffect, useState } from "react";
import type { Run, Stats } from "./api.js";
import { api } from "./api.js";
import { LoginForm } from "./components/LoginForm.js";
import { StatsBar } from "./components/StatsBar.js";
import { RunForm } from "./components/RunForm.js";
import { RunTable } from "./components/RunTable.js";

const TOKEN_KEY = "agent-ops-token";

export function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [runs, setRuns] = useState<Run[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);

  const refresh = useCallback(async () => {
    if (!token) return;
    const [r, s] = await Promise.all([api.listRuns(token), api.stats(token)]);
    setRuns(r);
    setStats(s);
  }, [token]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  function onAuthed(t: string) {
    localStorage.setItem(TOKEN_KEY, t);
    setToken(t);
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setRuns([]);
    setStats(null);
  }

  async function createRun(run: Partial<Run>) {
    if (!token) return;
    await api.createRun(token, run);
    await refresh();
  }

  async function deleteRun(id: number) {
    if (!token) return;
    await api.deleteRun(token, id);
    await refresh();
  }

  if (!token) {
    return (
      <div className="shell centered">
        <LoginForm onAuthed={onAuthed} />
      </div>
    );
  }

  return (
    <div className="shell">
      <header>
        <h1>agent-ops</h1>
        <button className="link" onClick={logout}>
          log out
        </button>
      </header>
      {stats && <StatsBar stats={stats} />}
      <RunForm onCreate={createRun} />
      <RunTable runs={runs} onDelete={deleteRun} />
    </div>
  );
}
