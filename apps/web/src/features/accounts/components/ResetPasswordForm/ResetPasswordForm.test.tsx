import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { confirmPasswordReset } from "../../api";

import { ResetPasswordForm } from "./ResetPasswordForm";

const pushMock = vi.fn();
const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  confirmPasswordReset: vi.fn(),
}));

describe("ResetPasswordForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("submits with the uid, token, and new password and redirects", async () => {
    const user = userEvent.setup();
    vi.mocked(confirmPasswordReset).mockResolvedValueOnce(undefined);

    render(<ResetPasswordForm uid="abc-uid" token="zzz-token" />);
    await user.type(
      screen.getByLabelText(/^new password$/i),
      "Brand-New-Password-2026",
    );
    await user.click(screen.getByRole("button", { name: /save new password/i }));

    expect(confirmPasswordReset).toHaveBeenCalledWith({
      uid: "abc-uid",
      token: "zzz-token",
      password: "Brand-New-Password-2026",
    });
    expect(pushMock).toHaveBeenCalledWith("/sign-in?reset=success");
  });

  it("renders an alert when the API rejects the token", async () => {
    const user = userEvent.setup();
    vi.mocked(confirmPasswordReset).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#invalid_reset_token",
          title: "Invalid",
          status: 422,
          detail: "This password-reset link is invalid or has expired.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(<ResetPasswordForm uid="abc" token="bad" />);
    await user.type(
      screen.getByLabelText(/^new password$/i),
      "Brand-New-Password-2026",
    );
    await user.click(screen.getByRole("button", { name: /save new password/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /invalid or has expired/i,
    );
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("rejects passwords shorter than 12 characters at the client", async () => {
    const user = userEvent.setup();

    render(<ResetPasswordForm uid="abc" token="zzz" />);
    await user.type(screen.getByLabelText(/^new password$/i), "short");
    await user.click(screen.getByRole("button", { name: /save new password/i }));

    expect(
      await screen.findByText(/use at least 12 characters/i),
    ).toBeInTheDocument();
    expect(confirmPasswordReset).not.toHaveBeenCalled();
  });
});
