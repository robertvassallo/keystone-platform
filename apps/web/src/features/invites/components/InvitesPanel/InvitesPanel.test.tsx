import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { revokeInvite, sendInvite } from "../../api";
import type { Invite } from "../../types";

import { InvitesPanel } from "./InvitesPanel";

const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  sendInvite: vi.fn(),
  revokeInvite: vi.fn(),
}));

const PENDING: Invite = {
  id: "01HABC",
  email: "alice@example.com",
  invited_by_email: "admin@example.com",
  status: "pending",
  expires_at: "2026-05-03T00:00:00Z",
  accepted_at: null,
  revoked_at: null,
  created_at: "2026-04-26T00:00:00Z",
};

describe("InvitesPanel", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the form heading", () => {
    render(<InvitesPanel invites={[]} />);

    expect(
      screen.getByRole("heading", { name: /invite a user/i }),
    ).toBeInTheDocument();
  });

  it("submits and shows a success message", async () => {
    const user = userEvent.setup();
    vi.mocked(sendInvite).mockResolvedValueOnce({
      ...PENDING,
      email: "newhire@example.com",
    });

    render(<InvitesPanel invites={[]} />);

    await user.type(
      screen.getByRole("textbox"),
      "newhire@example.com",
    );
    await user.click(screen.getByRole("button", { name: /send invite/i }));

    expect(sendInvite).toHaveBeenCalledWith({
      email: "newhire@example.com",
    });
    expect(
      await screen.findByText(/invite sent to newhire@example.com/i),
    ).toBeInTheDocument();
    expect(refreshMock).toHaveBeenCalled();
  });

  it("shows duplicate-member error inline on the email field", async () => {
    const user = userEvent.setup();
    vi.mocked(sendInvite).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#duplicate_member",
          title: "Duplicate",
          status: 422,
          detail: "A user with this email already exists.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(<InvitesPanel invites={[]} />);

    await user.type(screen.getByRole("textbox"), "taken@example.com");
    await user.click(screen.getByRole("button", { name: /send invite/i }));

    expect(
      await screen.findByText(/user with this email already exists/i),
    ).toBeInTheDocument();
  });

  it("renders pending invites with a revoke button", () => {
    render(<InvitesPanel invites={[PENDING]} />);

    expect(screen.getByText("alice@example.com")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /revoke invite for alice@example.com/i }),
    ).toBeInTheDocument();
  });

  it("calls revoke when the revoke button is clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(revokeInvite).mockResolvedValueOnce(undefined);
    render(<InvitesPanel invites={[PENDING]} />);

    await user.click(
      screen.getByRole("button", { name: /revoke invite for alice@example.com/i }),
    );

    expect(revokeInvite).toHaveBeenCalledWith({ id: "01HABC" });
  });
});
