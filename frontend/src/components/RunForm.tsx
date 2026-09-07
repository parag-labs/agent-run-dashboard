import { useState } from "react";
import type { Run } from "../api.js";

interface Props {
  onCreate: (run: Partial<Run>) => void;
}

/** Inline form to record a new run. */
export function RunForm({ onCreate }: Props) {
  const [name, setName] = useState("");
  const [model, setModel] = useState("gpt-4o");
  const [status, setStatus] = useState("success");
  const [tokens, setTokens] = useState("0");
  const [cost, setCost] = useState("0");

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    onCreate({
      name: name.trim(),
      model,
      status,
      tokens: Number(tokens) || 0,
      cost: Number(cost) || 0,
    });
    setName("");
    setTokens("0");
    setCost("0");
  }

  return (
    <form className="runform" onSubmit={submit} data-testid="run-form">
      <input placeholder="run name" value={name} onChange={(e) => setName(e.target.value)} aria-label="run name" />
      <input placeholder="model" value={model} onChange={(e) => setModel(e.target.value)} aria-label="model" />
      <select value={status} onChange={(e) => setStatus(e.target.value)} aria-label="status">
        <option value="success">success</option>
        <option value="error">error</option>
        <option value="running">running</option>
      </select>
      <input
        type="number"
        placeholder="tokens"
        value={tokens}
        onChange={(e) => setTokens(e.target.value)}
        aria-label="tokens"
      />
      <input
        type="number"
        step="0.0001"
        placeholder="cost"
        value={cost}
        onChange={(e) => setCost(e.target.value)}
        aria-label="cost"
      />
      <button type="submit" className="btn">
        record run
      </button>
    </form>
  );
}
