import type { Stats } from "../api.js";
import { formatCost } from "../api.js";

/** The headline stat cards across the top of the dashboard. */
export function StatsBar({ stats }: { stats: Stats }) {
  return (
    <div className="stats" data-testid="stats-bar">
      <Card label="runs" value={String(stats.runs)} />
      <Card label="tokens" value={stats.total_tokens.toLocaleString()} />
      <Card label="total cost" value={formatCost(stats.total_cost)} testId="stat-cost" />
      <Card label="errors" value={String(stats.by_status.error ?? 0)} testId="stat-errors" />
    </div>
  );
}

function Card({ label, value, testId }: { label: string; value: string; testId?: string }) {
  return (
    <div className="card">
      <b data-testid={testId}>{value}</b>
      <span>{label}</span>
    </div>
  );
}
