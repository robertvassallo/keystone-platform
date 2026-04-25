import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { changePassword } from "../../api";

import { ChangePasswordForm } from "./ChangePasswordForm";

vi.mock("../../api", () => ({
  changePassword: vi.fn(),
}));

describe("ChangePasswordForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("submits and shows the success state", async () => {
    const user = userEvent.setup();
    vi.mocked(changePassword).mockResolvedValueOnce(undefined);

    render(<ChangePasswordForm />);
    await user.type(
      screen.getByLabelText(/current password/i),
      "Existing-Password-1234",
    );
    await user.type(
      screen.getByLabelText(/^new password$/i),
      "Even-Stronger-Password-2026",
    );
    await user.click(screen.getByRole("button", { name: /save new password/i }));

    expect(changePassword).toHaveBeenCalledWith({
      currentPassword: "Existing-Password-1234",
      newPassword: "Even-Stronger-Password-2026",
    });
    expect(await screen.findByRole("status")).toHaveTextContent(
      /password changed/i,
    );
  });

  it("surfaces wrong-current-password as a field error", async () => {
    const user = userEvent.setup();
    vi.mocked(changePassword).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#wrong_current_password",
          title: "Wrong",
          status: 422,
          detail: "Current password is incorrect.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(<ChangePasswordForm />);
    await user.type(
      screen.getByLabelText(/current password/i),
      "Wrong-Password-1234567",
    );
    await user.type(
      screen.getByLabelText(/^new password$/i),
      "Even-Stronger-Password-2026",
    );
    await user.click(screen.getByRole("button", { name: /save new password/i }));

    expect(
      await screen.findByText(/current password is incorrect/i),
    ).toBeInTheDocument();
  });

  it("rejects matching current and new passwords at the client", async () => {
    const user = userEvent.setup();

    render(<ChangePasswordForm />);
    await user.type(
      screen.getByLabelText(/current password/i),
      "Same-Password-1234567",
    );
    await user.type(
      screen.getByLabelText(/^new password$/i),
      "Same-Password-1234567",
    );
    await user.click(screen.getByRole("button", { name: /save new password/i }));

    expect(
      await screen.findByText(/different from the current password/i),
    ).toBeInTheDocument();
    expect(changePassword).not.toHaveBeenCalled();
  });
});
