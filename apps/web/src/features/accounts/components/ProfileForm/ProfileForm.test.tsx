import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { updateMe } from "../../api";
import type { User } from "../../types";

import { ProfileForm } from "./ProfileForm";

const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  updateMe: vi.fn(),
}));

const BASE_USER: User = {
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
  created_at: "2026-04-25T00:00:00Z",
};

describe("ProfileForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("hydrates from initial values", () => {
    render(
      <ProfileForm
        initial={{ ...BASE_USER, first_name: "Alice", last_name: "Anderson" }}
      />,
    );

    expect(screen.getByLabelText(/first name/i)).toHaveValue("Alice");
    expect(screen.getByLabelText(/last name/i)).toHaveValue("Anderson");
  });

  it("submits the trimmed values via updateMe", async () => {
    const user = userEvent.setup();
    vi.mocked(updateMe).mockResolvedValueOnce({
      ...BASE_USER,
      first_name: "Alice",
      last_name: "Anderson",
      display_name: "Alice Anderson",
    });

    render(<ProfileForm initial={BASE_USER} />);

    await user.type(screen.getByLabelText(/first name/i), "Alice");
    await user.type(screen.getByLabelText(/last name/i), "Anderson");
    await user.click(screen.getByRole("button", { name: /save profile/i }));

    expect(updateMe).toHaveBeenCalledWith({
      firstName: "Alice",
      lastName: "Anderson",
    });
    expect(refreshMock).toHaveBeenCalled();
  });

  it("disables the submit button until the form is dirty", () => {
    render(<ProfileForm initial={BASE_USER} />);

    expect(
      screen.getByRole("button", { name: /save profile/i }),
    ).toBeDisabled();
  });

  it("shows a client-side error when first name exceeds 150 chars", async () => {
    const user = userEvent.setup();
    render(<ProfileForm initial={BASE_USER} />);

    const overLength = 151;
    await user.type(screen.getByLabelText(/first name/i), "a".repeat(overLength));
    await user.click(screen.getByRole("button", { name: /save profile/i }));

    expect(
      await screen.findByText(/first name must be 150 characters or fewer/i),
    ).toBeInTheDocument();
    expect(updateMe).not.toHaveBeenCalled();
  });

  it("surfaces a server validation error on a 400 response", async () => {
    const user = userEvent.setup();
    vi.mocked(updateMe).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#validation_error",
          title: "Validation",
          status: 400,
          detail: "Invalid input.",
          errors: { first_name: ["Server says this is invalid."] },
        },
        new Response(null, { status: 400 }),
      ),
    );

    render(<ProfileForm initial={BASE_USER} />);
    await user.type(screen.getByLabelText(/first name/i), "X");
    await user.click(screen.getByRole("button", { name: /save profile/i }));

    expect(
      await screen.findByText(/server says this is invalid/i),
    ).toBeInTheDocument();
    expect(refreshMock).not.toHaveBeenCalled();
  });
});
