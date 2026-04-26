import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { Account } from "../../types";

import { AccountEditPanel } from "./AccountEditPanel";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn() }),
}));

vi.mock("../../api", () => ({
  updateAccount: vi.fn(),
}));

const ACCOUNT: Account = {
  id: "01HXYZ-acct",
  name: "Acme",
  slug: "acme",
  owner_email: "owner@example.com",
  created_at: "2026-04-26T00:00:00Z",
};

describe("AccountEditPanel", () => {
  it("renders the read-only card with no edit button when canEdit is false", () => {
    render(<AccountEditPanel account={ACCOUNT} canEdit={false} />);

    expect(
      screen.getByRole("heading", { name: /acme/i, level: 2 }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /edit tenant/i }),
    ).not.toBeInTheDocument();
  });

  it("renders the read-only card with an edit button when canEdit is true", () => {
    render(<AccountEditPanel account={ACCOUNT} canEdit />);

    expect(
      screen.getByRole("button", { name: /edit tenant/i }),
    ).toBeInTheDocument();
  });

  it("clicking edit swaps the card for the form", async () => {
    const user = userEvent.setup();
    render(<AccountEditPanel account={ACCOUNT} canEdit />);

    await user.click(screen.getByRole("button", { name: /edit tenant/i }));

    expect(screen.getByLabelText(/url slug/i)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /edit tenant/i }),
    ).not.toBeInTheDocument();
  });

  it("clicking cancel swaps the form back to the card", async () => {
    const user = userEvent.setup();
    render(<AccountEditPanel account={ACCOUNT} canEdit />);

    await user.click(screen.getByRole("button", { name: /edit tenant/i }));
    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(
      screen.getByRole("heading", { name: /acme/i, level: 2 }),
    ).toBeInTheDocument();
    expect(
      screen.queryByLabelText(/url slug/i),
    ).not.toBeInTheDocument();
  });
});
