import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { disableMfa, regenerateRecoveryCodes } from "../../api";

import { MfaManagementPanel } from "./MfaManagementPanel";

const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  disableMfa: vi.fn(),
  regenerateRecoveryCodes: vi.fn(),
}));

const ENABLED_STATUS = { enabled: true, recovery_codes_remaining: 7 };

describe("MfaManagementPanel", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("shows the enabled status with the count of remaining recovery codes", () => {
    render(<MfaManagementPanel status={ENABLED_STATUS} />);

    expect(
      screen.getByRole("heading", { name: /two-factor authentication is on/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/7 recovery codes remaining/i)).toBeInTheDocument();
  });

  it("disables MFA after the user confirms with their password", async () => {
    const user = userEvent.setup();
    vi.mocked(disableMfa).mockResolvedValueOnce(undefined);

    render(<MfaManagementPanel status={ENABLED_STATUS} />);
    await user.click(screen.getByRole("button", { name: /^disable$/i }));
    await user.type(
      screen.getByLabelText(/current password/i),
      "Existing-Password-1234",
    );
    await user.click(screen.getByRole("button", { name: /^disable$/i }));

    expect(disableMfa).toHaveBeenCalledWith("Existing-Password-1234");
    expect(refreshMock).toHaveBeenCalled();
  });

  it("surfaces a wrong-password error inline on the disable form", async () => {
    const user = userEvent.setup();
    vi.mocked(disableMfa).mockRejectedValueOnce(
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

    render(<MfaManagementPanel status={ENABLED_STATUS} />);
    await user.click(screen.getByRole("button", { name: /^disable$/i }));
    await user.type(
      screen.getByLabelText(/current password/i),
      "wrong-password-12345",
    );
    await user.click(screen.getByRole("button", { name: /^disable$/i }));

    expect(
      await screen.findByText(/current password is incorrect/i),
    ).toBeInTheDocument();
    expect(refreshMock).not.toHaveBeenCalled();
  });

  it("regenerates recovery codes and shows the new set", async () => {
    const user = userEvent.setup();
    vi.mocked(regenerateRecoveryCodes).mockResolvedValueOnce([
      "AAAA1111",
      "BBBB2222",
    ]);

    render(<MfaManagementPanel status={ENABLED_STATUS} />);
    await user.click(
      screen.getByRole("button", { name: /regenerate recovery codes/i }),
    );
    await user.type(
      screen.getByLabelText(/current password/i),
      "Existing-Password-1234",
    );
    await user.click(
      screen.getByRole("button", { name: /generate new codes/i }),
    );

    expect(regenerateRecoveryCodes).toHaveBeenCalledWith(
      "Existing-Password-1234",
    );
    expect(
      await screen.findByRole("heading", { name: /save your recovery codes/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("AAAA1111")).toBeInTheDocument();
  });
});
