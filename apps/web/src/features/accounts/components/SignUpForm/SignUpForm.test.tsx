import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { signUp } from "../../api";

import { SignUpForm } from "./SignUpForm";

const pushMock = vi.fn();
const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  signUp: vi.fn(),
}));

describe("SignUpForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the sign-up heading and form fields", () => {
    render(<SignUpForm />);

    expect(
      screen.getByRole("heading", { name: /create your account/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
  });

  it("submits and calls signUp with the form values", async () => {
    const user = userEvent.setup();
    vi.mocked(signUp).mockResolvedValueOnce({
      id: "1",
      email: "new@example.com",
      is_active: true,
      is_staff: false,
      tenant: null,
        email_verified_at: null,
      created_at: "2026-04-25T00:00:00Z",
    });

    render(<SignUpForm />);
    await user.type(screen.getByLabelText(/email/i), "new@example.com");
    await user.type(
      screen.getByLabelText(/^password$/i),
      "StrongPassword-7531-xy",
    );
    await user.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    expect(signUp).toHaveBeenCalledWith({
      email: "new@example.com",
      password: "StrongPassword-7531-xy",
    });
    expect(pushMock).toHaveBeenCalledWith("/");
  });

  it("rejects passwords shorter than 12 characters at the client", async () => {
    const user = userEvent.setup();
    render(<SignUpForm />);

    await user.type(screen.getByLabelText(/email/i), "new@example.com");
    await user.type(screen.getByLabelText(/^password$/i), "short");
    await user.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    expect(
      await screen.findByText(/use at least 12 characters/i),
    ).toBeInTheDocument();
    expect(signUp).not.toHaveBeenCalled();
  });

  it("surfaces server-side per-field errors from a 400 response", async () => {
    const user = userEvent.setup();
    vi.mocked(signUp).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#validationerror",
          title: "ValidationError",
          status: 400,
          detail: "Invalid input.",
          errors: { password: ["This password is too common."] },
        },
        new Response(null, { status: 400 }),
      ),
    );

    render(<SignUpForm />);
    await user.type(screen.getByLabelText(/email/i), "new@example.com");
    await user.type(
      screen.getByLabelText(/^password$/i),
      "Password1234567890",
    );
    await user.click(
      screen.getByRole("button", { name: /create account/i }),
    );

    expect(
      await screen.findByText(/this password is too common/i),
    ).toBeInTheDocument();
  });
});
