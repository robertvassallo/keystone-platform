import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { requestEmailVerification } from "../../api/request-email-verification";

import { EmailVerificationBanner } from "./EmailVerificationBanner";

vi.mock("../../api/request-email-verification", () => ({
  requestEmailVerification: vi.fn(),
}));

describe("EmailVerificationBanner", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the heading and description", () => {
    render(<EmailVerificationBanner />);

    expect(
      screen.getByRole("heading", { name: /verify your email/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/check your inbox/i)).toBeInTheDocument();
  });

  it("calls the request endpoint when the resend button is clicked", async () => {
    const user = userEvent.setup();
    vi.mocked(requestEmailVerification).mockResolvedValueOnce(undefined);

    render(<EmailVerificationBanner />);

    await user.click(
      screen.getByRole("button", { name: /resend verification email/i }),
    );

    expect(requestEmailVerification).toHaveBeenCalledTimes(1);
    expect(
      await screen.findByRole("button", { name: /email sent/i }),
    ).toBeDisabled();
  });

  it("shows the throttled message on a 429 response", async () => {
    const user = userEvent.setup();
    vi.mocked(requestEmailVerification).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#throttled",
          title: "Throttled",
          status: 429,
          detail: "Too many requests.",
        },
        new Response(null, { status: 429 }),
      ),
    );

    render(<EmailVerificationBanner />);
    await user.click(
      screen.getByRole("button", { name: /resend verification email/i }),
    );

    expect(
      await screen.findByText(/slow down a moment/i),
    ).toBeInTheDocument();
  });

  it("shows a generic error on an unexpected failure", async () => {
    const user = userEvent.setup();
    vi.mocked(requestEmailVerification).mockRejectedValueOnce(
      new Error("network exploded"),
    );

    render(<EmailVerificationBanner />);
    await user.click(
      screen.getByRole("button", { name: /resend verification email/i }),
    );

    expect(
      await screen.findByRole("alert"),
    ).toHaveTextContent(/couldn't send the verification email/i);
  });
});
