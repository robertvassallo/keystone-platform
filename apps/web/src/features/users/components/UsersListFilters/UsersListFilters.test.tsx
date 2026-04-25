import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { UsersListFilters } from "./UsersListFilters";

const pushMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
  usePathname: () => "/users",
}));

describe("UsersListFilters", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders empty inputs and no chips when no filters are active", () => {
    render(<UsersListFilters filters={{ q: null, status: null }} />);

    expect(screen.getByLabelText(/search by email/i)).toHaveValue("");
    expect(screen.getByLabelText(/^status$/i)).toHaveValue("");
    expect(screen.queryByText(/active filters:/i)).not.toBeInTheDocument();
  });

  it("hydrates inputs from current filter values and renders chips", () => {
    render(
      <UsersListFilters filters={{ q: "alice", status: "staff" }} />,
    );

    expect(screen.getByLabelText(/search by email/i)).toHaveValue("alice");
    expect(screen.getByLabelText(/^status$/i)).toHaveValue("staff");
    expect(screen.getByText(/search: alice/i)).toBeInTheDocument();
    expect(screen.getByText(/status: staff/i)).toBeInTheDocument();
  });

  it("submitting the form pushes the trimmed query to the URL", async () => {
    const user = userEvent.setup();
    render(<UsersListFilters filters={{ q: null, status: null }} />);

    await user.type(screen.getByLabelText(/search by email/i), "  alice  ");
    await user.click(screen.getByRole("button", { name: /apply/i }));

    expect(pushMock).toHaveBeenCalledWith("/users?q=alice");
  });

  it("changing the status select pushes the new status immediately", async () => {
    const user = userEvent.setup();
    render(<UsersListFilters filters={{ q: null, status: null }} />);

    await user.selectOptions(screen.getByLabelText(/^status$/i), "staff");

    expect(pushMock).toHaveBeenCalledWith("/users?status=staff");
  });

  it("selecting 'All' clears the status param", async () => {
    const user = userEvent.setup();
    render(
      <UsersListFilters filters={{ q: null, status: "active" }} />,
    );

    await user.selectOptions(screen.getByLabelText(/^status$/i), "");

    expect(pushMock).toHaveBeenCalledWith("/users");
  });

  it("preserves the other filter when clearing one chip", async () => {
    const user = userEvent.setup();
    render(
      <UsersListFilters filters={{ q: "alice", status: "staff" }} />,
    );

    await user.click(
      screen.getByRole("button", { name: /clear search filter alice/i }),
    );

    expect(pushMock).toHaveBeenCalledWith("/users?status=staff");
  });

  it("clear all removes both filters", async () => {
    const user = userEvent.setup();
    render(
      <UsersListFilters filters={{ q: "alice", status: "staff" }} />,
    );

    await user.click(screen.getByRole("button", { name: /clear all/i }));

    expect(pushMock).toHaveBeenCalledWith("/users");
  });

  it("submitting an empty query clears the q param", async () => {
    const user = userEvent.setup();
    render(
      <UsersListFilters filters={{ q: "alice", status: null }} />,
    );

    await user.clear(screen.getByLabelText(/search by email/i));
    await user.click(screen.getByRole("button", { name: /apply/i }));

    expect(pushMock).toHaveBeenCalledWith("/users");
  });
});
