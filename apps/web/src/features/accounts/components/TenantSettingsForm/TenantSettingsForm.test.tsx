import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/shared/lib/api-client";

import { updateAccount } from "../../api";
import type { Account } from "../../types";

import { TenantSettingsForm } from "./TenantSettingsForm";

const refreshMock = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: refreshMock }),
}));

vi.mock("../../api", () => ({
  updateAccount: vi.fn(),
}));

const ACCOUNT: Account = {
  id: "01HXYZ-acct",
  name: "Acme",
  slug: "acme",
  owner_email: "owner@example.com",
  created_at: "2026-04-26T00:00:00Z",
};

describe("TenantSettingsForm", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("hydrates from initial values", () => {
    render(<TenantSettingsForm initial={ACCOUNT} />);

    expect(screen.getByLabelText(/^name$/i)).toHaveValue("Acme");
    expect(screen.getByLabelText(/url slug/i)).toHaveValue("acme");
  });

  it("submits and refreshes the page tree on success", async () => {
    const user = userEvent.setup();
    vi.mocked(updateAccount).mockResolvedValueOnce({
      ...ACCOUNT,
      name: "New Co",
      slug: "new-co",
    });

    render(<TenantSettingsForm initial={ACCOUNT} />);

    const name = screen.getByLabelText(/^name$/i);
    await user.clear(name);
    await user.type(name, "New Co");
    const slug = screen.getByLabelText(/url slug/i);
    await user.clear(slug);
    await user.type(slug, "new-co");
    await user.click(screen.getByRole("button", { name: /save tenant/i }));

    expect(updateAccount).toHaveBeenCalledWith({
      name: "New Co",
      slug: "new-co",
    });
    expect(refreshMock).toHaveBeenCalled();
  });

  it("disables submit until the form is dirty", () => {
    render(<TenantSettingsForm initial={ACCOUNT} />);

    expect(
      screen.getByRole("button", { name: /save tenant/i }),
    ).toBeDisabled();
  });

  it("shows a client-side error on a slug with an underscore", async () => {
    const user = userEvent.setup();
    render(<TenantSettingsForm initial={ACCOUNT} />);

    const slug = screen.getByLabelText(/url slug/i);
    await user.clear(slug);
    await user.type(slug, "bad_slug");
    await user.click(screen.getByRole("button", { name: /save tenant/i }));

    expect(
      await screen.findByText(/lowercase letters, digits, and hyphens/i),
    ).toBeInTheDocument();
    expect(updateAccount).not.toHaveBeenCalled();
  });

  it("surfaces duplicate_slug as an inline slug error", async () => {
    const user = userEvent.setup();
    vi.mocked(updateAccount).mockRejectedValueOnce(
      new ApiError(
        {
          type: "about:blank#duplicate_slug",
          title: "Duplicate",
          status: 422,
          detail: "That URL slug is already taken.",
        },
        new Response(null, { status: 422 }),
      ),
    );

    render(<TenantSettingsForm initial={ACCOUNT} />);
    const slug = screen.getByLabelText(/url slug/i);
    await user.clear(slug);
    await user.type(slug, "taken");
    await user.click(screen.getByRole("button", { name: /save tenant/i }));

    expect(
      await screen.findByText(/url slug is already taken/i),
    ).toBeInTheDocument();
    expect(refreshMock).not.toHaveBeenCalled();
  });

  it("calls onCancel when the cancel button is clicked", async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    render(<TenantSettingsForm initial={ACCOUNT} onCancel={onCancel} />);

    await user.click(screen.getByRole("button", { name: /cancel/i }));

    expect(onCancel).toHaveBeenCalled();
  });
});
