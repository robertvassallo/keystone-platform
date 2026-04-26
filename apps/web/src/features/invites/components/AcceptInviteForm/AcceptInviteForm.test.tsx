import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { acceptInvite } from "../../api";

import { AcceptInviteForm } from "./AcceptInviteForm";

const pushMock = vi.fn();
const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  acceptInvite: vi.fn(),
}));

describe("AcceptInviteForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the tenant name and email", () => {
    render(
      <AcceptInviteForm
        uid="UID"
        token="TOKEN"
        tenantName="Acme Co"
        email="alice@example.com"
      />,
    );

    expect(
      screen.getByRole("heading", { name: /join acme co/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/alice@example.com/)).toBeInTheDocument();
  });

  it("submits and pushes to the dashboard on success", async () => {
    const user = userEvent.setup();
    vi.mocked(acceptInvite).mockResolvedValueOnce({
      id: "01HXYZ",
      email: "alice@example.com",
      first_name: "",
      last_name: "",
      display_name: "alice",
      is_active: true,
      is_staff: false,
        is_tenant_owner: false,
      tenant: null,
      email_verified_at: null,
      created_at: "2026-04-26T00:00:00Z",
    });

    render(
      <AcceptInviteForm
        uid="UID"
        token="TOKEN"
        tenantName="Acme"
        email="alice@example.com"
      />,
    );

    await user.type(screen.getByLabelText(/^password$/i), "Strong-Password-7531");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(acceptInvite).toHaveBeenCalledWith({
      uid: "UID",
      token: "TOKEN",
      password: "Strong-Password-7531",
    });
    expect(pushMock).toHaveBeenCalledWith("/");
  });

  it("shows the server detail when the token is rejected", async () => {
    const user = userEvent.setup();
    vi.mocked(acceptInvite).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#invalid_invite_token",
          title: "Invalid",
          status: 422,
          detail: "This invite link is invalid or has expired.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(
      <AcceptInviteForm
        uid="UID"
        token="TOKEN"
        tenantName="Acme"
        email="alice@example.com"
      />,
    );

    await user.type(screen.getByLabelText(/^password$/i), "Strong-Password-7531");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent(/invalid or has expired/i);
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("rejects a too-short password client-side", async () => {
    const user = userEvent.setup();
    render(
      <AcceptInviteForm
        uid="UID"
        token="TOKEN"
        tenantName="Acme"
        email="alice@example.com"
      />,
    );

    await user.type(screen.getByLabelText(/^password$/i), "short");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    expect(
      await screen.findByText(/use at least 12 characters/i),
    ).toBeInTheDocument();
    expect(acceptInvite).not.toHaveBeenCalled();
  });
});
