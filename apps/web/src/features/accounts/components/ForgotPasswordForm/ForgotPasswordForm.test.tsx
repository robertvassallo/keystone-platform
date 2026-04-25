import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { requestPasswordReset } from "../../api";

import { ForgotPasswordForm } from "./ForgotPasswordForm";

vi.mock("../../api", () => ({
  requestPasswordReset: vi.fn(),
}));

describe("ForgotPasswordForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the heading and email field", () => {
    render(<ForgotPasswordForm />);

    expect(
      screen.getByRole("heading", { name: /forgot your password/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it("submits the email and shows the confirmation state", async () => {
    const user = userEvent.setup();
    vi.mocked(requestPasswordReset).mockResolvedValueOnce(undefined);

    render(<ForgotPasswordForm />);
    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.click(screen.getByRole("button", { name: /send reset link/i }));

    expect(requestPasswordReset).toHaveBeenCalledWith({
      email: "user@example.com",
    });
    expect(
      await screen.findByRole("heading", { name: /check your email/i }),
    ).toBeInTheDocument();
  });

  it("rejects invalid emails at the client", async () => {
    const user = userEvent.setup();
    render(<ForgotPasswordForm />);

    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.click(screen.getByRole("button", { name: /send reset link/i }));

    expect(
      await screen.findByText(/email must include @/i),
    ).toBeInTheDocument();
    expect(requestPasswordReset).not.toHaveBeenCalled();
  });
});
