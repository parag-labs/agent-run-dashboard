import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { Run, Stats } from "../src/api.js";
import { StatsBar } from "../src/components/StatsBar.js";
import { RunTable } from "../src/components/RunTable.js";
import { RunForm } from "../src/components/RunForm.js";

const stats: Stats = {
  runs: 3,
  total_tokens: 1234,
  total_cost: 1.75,
  by_status: { success: 2, error: 1 },
  by_model: { "gpt-4o": 3 },
};

const runs: Run[] = [
  { id: 1, name: "nightly", model: "gpt-4o", status: "success", tokens: 100, cost: 0.5, latency_ms: 800 },
  { id: 2, name: "adhoc", model: "o3-mini", status: "error", tokens: 50, cost: 0.25, latency_ms: 400 },
];

describe("StatsBar", () => {
  it("shows the aggregate numbers", () => {
    render(<StatsBar stats={stats} />);
    expect(screen.getByTestId("stat-cost").textContent).toBe("$1.7500");
    expect(screen.getByTestId("stat-errors").textContent).toBe("1");
  });
});

describe("RunTable", () => {
  it("renders a row per run", () => {
    render(<RunTable runs={runs} onDelete={() => {}} />);
    expect(screen.getAllByTestId("run-row")).toHaveLength(2);
    expect(screen.getByText("nightly")).toBeInTheDocument();
  });

  it("shows an empty state with no runs", () => {
    render(<RunTable runs={[]} onDelete={() => {}} />);
    expect(screen.getByTestId("empty")).toBeInTheDocument();
  });

  it("calls onDelete with the run id", async () => {
    const onDelete = vi.fn();
    render(<RunTable runs={runs} onDelete={onDelete} />);
    await userEvent.click(screen.getByLabelText("delete nightly"));
    expect(onDelete).toHaveBeenCalledWith(1);
  });
});

describe("RunForm", () => {
  it("submits a new run and clears the name", async () => {
    const onCreate = vi.fn();
    render(<RunForm onCreate={onCreate} />);
    await userEvent.type(screen.getByLabelText("run name"), "my-run");
    await userEvent.type(screen.getByLabelText("tokens"), "500");
    await userEvent.click(screen.getByText("record run"));
    expect(onCreate).toHaveBeenCalledTimes(1);
    expect(onCreate.mock.calls[0][0]).toMatchObject({ name: "my-run", tokens: 500 });
  });

  it("does not submit an empty run name", async () => {
    const onCreate = vi.fn();
    render(<RunForm onCreate={onCreate} />);
    await userEvent.click(screen.getByText("record run"));
    expect(onCreate).not.toHaveBeenCalled();
  });
});
