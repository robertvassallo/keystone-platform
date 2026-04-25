import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { verifyMfaChallenge } from "../../api";

import { MfaChallengeForm } from "./MfaChallengeForm";

vi.mock("../../api", () => ({
  verifyMfaChallenge: vi.fn(),
}));

const FAKE_USER = {
  id: "1",
  email: "user@example.com",
  is_active: true,
  is_staff: false,
  tenant_id: null,
  created_at: "2026-04-25T00:00:00Z",
};

describe("MfaChallengeForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("submits a valid TOTP code and notifies the parent", async () => {
    const user = userEvent.setup();
    const onAuthenticated = vi.fn();
    vi.mocked(verifyMfaChallenge).mockResolvedValueOnce(FAKE_USER);

    render(
      <MfaChallengeForm
        onAuthenticated={onAuthenticated}
        onChallengeExpired={vi.fn()}
      />,
    );
    await user.type(screen.getByLabelText(/authenticator code/i), "123456");
    await user.click(screen.getByRole("button", { name: /verify/i }));

    expect(verifyMfaChallenge).toHaveBeenCalledWith("123456");
    expect(onAuthenticated).toHaveBeenCalledWith(FAKE_USER);
  });

  it("rejects non-6-digit TOTP at the client", async () => {
    const user = userEvent.setup();

    render(
      <MfaChallengeForm
        onAuthenticated={vi.fn()}
        onChallengeExpired={vi.fn()}
      />,
    );
    await user.type(screen.getByLabelText(/authenticator code/i), "abc123");
    await user.click(screen.getByRole("button", { name: /verify/i }));

    expect(
      await screen.findByText(/enter the 6-digit code from your authenticator/i),
    ).toBeInTheDocument();
    expect(verifyMfaChallenge).not.toHaveBeenCalled();
  });

  it("toggles to recovery mode and submits an 8-char code", async () => {
    const user = userEvent.setup();
    const onAuthenticated = vi.fn();
    vi.mocked(verifyMfaChallenge).mockResolvedValueOnce(FAKE_USER);

    render(
      <MfaChallengeForm
        onAuthenticated={onAuthenticated}
        onChallengeExpired={vi.fn()}
      />,
    );
    await user.click(
      screen.getByRole("button", { name: /use a recovery code/i }),
    );
    await user.type(screen.getByLabelText(/recovery code/i), "AAAA1111");
    await user.click(screen.getByRole("button", { name: /verify/i }));

    expect(verifyMfaChallenge).toHaveBeenCalledWith("AAAA1111");
    expect(onAuthenticated).toHaveBeenCalled();
  });

  it("shows an inline error on invalid_mfa_code", async () => {
    const user = userEvent.setup();
    vi.mocked(verifyMfaChallenge).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#invalid_mfa_code",
          title: "Invalid",
          status: 422,
          detail: "Invalid authentication code.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(
      <MfaChallengeForm
        onAuthenticated={vi.fn()}
        onChallengeExpired={vi.fn()}
      />,
    );
    await user.type(screen.getByLabelText(/authenticator code/i), "999999");
    await user.click(screen.getByRole("button", { name: /verify/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /invalid authentication code/i,
    );
  });

  it("calls onChallengeExpired when the API returns mfa_challenge_expired", async () => {
    const user = userEvent.setup();
    const onChallengeExpired = vi.fn();
    vi.mocked(verifyMfaChallenge).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#mfa_challenge_expired",
          title: "Expired",
          status: 422,
          detail: "Your sign-in session expired.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(
      <MfaChallengeForm
        onAuthenticated={vi.fn()}
        onChallengeExpired={onChallengeExpired}
      />,
    );
    await user.type(screen.getByLabelText(/authenticator code/i), "123456");
    await user.click(screen.getByRole("button", { name: /verify/i }));

    expect(onChallengeExpired).toHaveBeenCalledTimes(1);
  });
});
