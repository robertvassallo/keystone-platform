import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { confirmMfaSetup, startMfaSetup } from "../../api";

import { MfaEnrolFlow } from "./MfaEnrolFlow";

const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  startMfaSetup: vi.fn(),
  confirmMfaSetup: vi.fn(),
}));

const SETUP_PAYLOAD = {
  secret: "JBSWY3DPEHPK3PXP",
  provisioning_uri:
    "otpauth://totp/Keystone:test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Keystone",
  qr_data_url: "data:image/png;base64,FAKEQRCODEDATA",
};

describe("MfaEnrolFlow", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the set-up button before the user starts", () => {
    render(<MfaEnrolFlow />);

    expect(
      screen.getByRole("button", { name: /set up two-factor/i }),
    ).toBeInTheDocument();
  });

  it("starts setup and reveals the QR + code form", async () => {
    const user = userEvent.setup();
    vi.mocked(startMfaSetup).mockResolvedValueOnce(SETUP_PAYLOAD);

    render(<MfaEnrolFlow />);
    await user.click(
      screen.getByRole("button", { name: /set up two-factor/i }),
    );

    expect(startMfaSetup).toHaveBeenCalledTimes(1);
    expect(
      await screen.findByRole("img", {
        name: /qr code for setting up two-factor/i,
      }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/6-digit code/i)).toBeInTheDocument();
    expect(screen.getByText(SETUP_PAYLOAD.secret)).toBeInTheDocument();
  });

  it("confirms and shows the recovery codes", async () => {
    const user = userEvent.setup();
    vi.mocked(startMfaSetup).mockResolvedValueOnce(SETUP_PAYLOAD);
    vi.mocked(confirmMfaSetup).mockResolvedValueOnce([
      "AAAA1111",
      "BBBB2222",
      "CCCC3333",
    ]);

    render(<MfaEnrolFlow />);
    await user.click(
      screen.getByRole("button", { name: /set up two-factor/i }),
    );
    await user.type(
      await screen.findByLabelText(/6-digit code/i),
      "123456",
    );
    await user.click(
      screen.getByRole("button", { name: /confirm and enable/i }),
    );

    expect(confirmMfaSetup).toHaveBeenCalledWith("123456");
    expect(
      await screen.findByRole("heading", { name: /save your recovery codes/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("AAAA1111")).toBeInTheDocument();
  });
});
