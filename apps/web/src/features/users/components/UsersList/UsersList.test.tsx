import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { UserListItem } from "../../types";

import { UsersList } from "./UsersList";

const ROW: UserListItem = {
  id: "01HXYZ",
  email: "alice@example.com",
  is_active: true,
  is_staff: false,
  created_at: "2026-04-25T10:00:00Z",
  last_login: null,
};

describe("UsersList", () => {
  it("renders the column headers", () => {
    render(<UsersList users={[ROW]} />);

    expect(
      screen.getByRole("columnheader", { name: /email/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /status/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /created/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /last sign-in/i }),
    ).toBeInTheDocument();
  });

  it("renders one row per user with the email as the row header", () => {
    render(
      <UsersList
        users={[
          ROW,
          { ...ROW, id: "01HXYZ2", email: "bob@example.com", is_staff: true },
        ]}
      />,
    );

    expect(
      screen.getByRole("rowheader", { name: "alice@example.com" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("rowheader", { name: "bob@example.com" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Staff role")).toBeInTheDocument();
  });

  it("falls back to the empty state when there are no users", () => {
    render(<UsersList users={[]} />);

    expect(
      screen.getByRole("heading", { name: /no users yet/i }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows a placeholder for users who have never signed in", () => {
    render(<UsersList users={[ROW]} />);

    expect(screen.getByLabelText(/never signed in/i)).toBeInTheDocument();
  });
});
