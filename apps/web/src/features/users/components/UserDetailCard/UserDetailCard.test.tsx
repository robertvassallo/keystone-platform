import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { UserDetail } from "../../types";

import { UserDetailCard } from "./UserDetailCard";

const BASE: UserDetail = {
  id: "01HXYZ-id-uuid",
  email: "alice@example.com",
  is_active: true,
  is_staff: false,
  is_superuser: false,
  tenant: {
    id: "01HXYZ-tenant-uuid",
    name: "Acme",
    slug: "acme",
  },
  created_at: "2026-04-25T10:00:00Z",
  updated_at: "2026-04-25T11:00:00Z",
  last_login: null,
};

describe("UserDetailCard", () => {
  it("renders the email as the section heading and the id row", () => {
    render(<UserDetailCard user={BASE} />);

    expect(
      screen.getByRole("heading", { name: "alice@example.com", level: 2 }),
    ).toBeInTheDocument();
    expect(screen.getByText("01HXYZ-id-uuid")).toBeInTheDocument();
  });

  it("renders the tenant name and shows 'Never' when last_login is null", () => {
    render(<UserDetailCard user={BASE} />);

    expect(screen.getByText("Acme")).toBeInTheDocument();
    expect(screen.getByLabelText(/never signed in/i)).toBeInTheDocument();
  });

  it("renders the staff and superuser badges when both flags are true", () => {
    render(
      <UserDetailCard
        user={{ ...BASE, is_staff: true, is_superuser: true }}
      />,
    );

    expect(screen.getByLabelText(/staff role/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/superuser role/i)).toBeInTheDocument();
  });

  it("renders the inactive badge instead of active when is_active is false", () => {
    render(<UserDetailCard user={{ ...BASE, is_active: false }} />);

    expect(screen.getByLabelText(/inactive/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/^active$/i)).not.toBeInTheDocument();
  });
});
