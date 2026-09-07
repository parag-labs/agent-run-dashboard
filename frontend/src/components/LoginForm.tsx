import { useState } from "react";
import { api, ApiError } from "../api.js";

interface Props {
  onAuthed: (token: string) => void;
}

/** Login / register form. Toggles between the two modes and surfaces API errors. */
export function LoginForm({ onAuthed }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const fn = mode === "login" ? api.login : api.register;
      const { access_token } = await fn(username, password);
      onAuthed(access_token);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "something went wrong");
    }
  }

  return (
    <form className="auth" onSubmit={submit} data-testid="login-form">
      <h1>agent-ops</h1>
      <p className="muted">Record agent runs and watch cost, tokens, and failures.</p>
      <input
        placeholder="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        aria-label="username"
      />
      <input
        type="password"
        placeholder="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        aria-label="password"
      />
      <button type="submit" className="btn primary">
        {mode === "login" ? "log in" : "create account"}
      </button>
      {error && (
        <p className="error" data-testid="auth-error">
          {error}
        </p>
      )}
      <button
        type="button"
        className="link"
        onClick={() => {
          setMode(mode === "login" ? "register" : "login");
          setError(null);
        }}
      >
        {mode === "login" ? "need an account? register" : "have an account? log in"}
      </button>
    </form>
  );
}
