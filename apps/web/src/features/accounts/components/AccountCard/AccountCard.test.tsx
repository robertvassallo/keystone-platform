import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { Account } from "../../types";

import { AccountCard } from "./AccountCard";

const ACCOUNT: Account = {
  id: "01HXYZ-acct-uuid",
  name: "Acme",
  slug: "acme",
  owner_email: "owner@example.com",
  created_at: "2026-04-25T10:00:00Z",
};

describe("AccountCard", () => {
  it("renders the name as the heading and the slug below it", () => {
    render(<AccountCard account={ACCOUNT} />);

    expect(
      screen.getByRole("heading", { name: "Acme", level: 2 }),
    ).toBeInTheDocument();
    expect(screen.getByText("acme")).toBeInTheDocument();
  });

  it("renders id, owner email, and created date in the definition list", () => {
    render(<AccountCard account={ACCOUNT} />);

    expect(screen.getByText("01HXYZ-acct-uuid")).toBeInTheDocument();
    expect(screen.getByText("owner@example.com")).toBeInTheDocument();
    expect(screen.getByText(/2026-04-25 10:00 UTC/)).toBeInTheDocument();
  });

  it("renders an em-dash for accounts with no owner_email", () => {
    render(
      <AccountCard account={{ ...ACCOUNT, owner_email: null }} />,
    );

    expect(screen.getByLabelText(/no owner/i)).toBeInTheDocument();
  });
});
