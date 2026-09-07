import type { Run } from "../api.js";
import { formatCost } from "../api.js";

interface Props {
  runs: Run[];
  onDelete: (id: number) => void;
}

/** The table of recorded runs, newest first. */
export function RunTable({ runs, onDelete }: Props) {
  if (runs.length === 0) {
    return (
      <p className="muted" data-testid="empty">
        No runs yet. Record one above to see it here.
      </p>
    );
  }
  return (
    <table className="runs" data-testid="run-table">
      <thead>
        <tr>
          <th>name</th>
          <th>model</th>
          <th>status</th>
          <th className="right">tokens</th>
          <th className="right">cost</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {runs.map((r) => (
          <tr key={r.id} data-testid="run-row">
            <td>{r.name}</td>
            <td className="mono">{r.model}</td>
            <td>
              <span className={`pill ${r.status}`}>{r.status}</span>
            </td>
            <td className="right mono">{r.tokens.toLocaleString()}</td>
            <td className="right mono">{formatCost(r.cost)}</td>
            <td className="right">
              <button className="link" onClick={() => onDelete(r.id)} aria-label={`delete ${r.name}`}>
                delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
