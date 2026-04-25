import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { signIn } from "../../api";

import { SignInForm } from "./SignInForm";

const pushMock = vi.fn();
const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock, refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  signIn: vi.fn(),
}));

describe("SignInForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the sign-in heading and form fields", () => {
    render(<SignInForm />);

    expect(
      screen.getByRole("heading", { name: /sign in/i, level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(
      screen.getByLabelText(/remember me for 30 days/i),
    ).toBeInTheDocument();
  });

  it("submits and calls signIn with the form values", async () => {
    const user = userEvent.setup();
    vi.mocked(signIn).mockResolvedValueOnce({
      id: "1",
      email: "user@example.com",
      is_active: true,
      is_staff: false,
      tenant_id: null,
      created_at: "2026-04-25T00:00:00Z",
    });

    render(<SignInForm nextPath="/dashboard" />);

    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.type(
      screen.getByLabelText(/^password$/i),
      "VeryStrongPassword-7531",
    );
    await user.click(screen.getByLabelText(/remember me/i));
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(signIn).toHaveBeenCalledWith({
      email: "user@example.com",
      password: "VeryStrongPassword-7531",
      rememberMe: true,
    });
    expect(pushMock).toHaveBeenCalledWith("/dashboard");
  });

  it("shows the server error when the API rejects the credentials", async () => {
    const user = userEvent.setup();
    vi.mocked(signIn).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#invalid_credentials",
          title: "AuthenticationFailed",
          status: 401,
          detail: "Email or password is incorrect.",
        },
        new Response(null, { status: 401 }),
      ),
    );

    render(<SignInForm />);
    await user.type(screen.getByLabelText(/email/i), "user@example.com");
    await user.type(
      screen.getByLabelText(/^password$/i),
      "WrongPassword-12345",
    );
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByRole("alert", { name: "" }),
    ).toHaveTextContent("Email or password is incorrect.");
    expect(pushMock).not.toHaveBeenCalled();
  });

  it("shows a client-side validation error when email is invalid", async () => {
    const user = userEvent.setup();
    render(<SignInForm />);

    await user.type(screen.getByLabelText(/email/i), "not-an-email");
    await user.type(
      screen.getByLabelText(/^password$/i),
      "anything-not-empty-12",
    );
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      await screen.findByText(/email must include @/i),
    ).toBeInTheDocument();
    expect(signIn).not.toHaveBeenCalled();
  });
});
