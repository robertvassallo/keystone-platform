import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { AuditEvent } from "../../types";

import { AuditEventList } from "./AuditEventList";

const ROW: AuditEvent = {
  id: "01HXYZ",
  action: "tenant.renamed",
  actor_email: "owner@example.com",
  target_type: "account",
  target_label: "Acme Co",
  ip: "10.0.0.1",
  created_at: "2026-04-26T10:00:00Z",
};

describe("AuditEventList", () => {
  it("renders the column headers", () => {
    render(<AuditEventList events={[ROW]} />);

    expect(
      screen.getByRole("columnheader", { name: /action/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /actor/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /target/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /when/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("columnheader", { name: /ip/i }),
    ).toBeInTheDocument();
  });

  it("renders one row per event with the human action label", () => {
    render(
      <AuditEventList
        events={[
          ROW,
          { ...ROW, id: "01HXYZ2", action: "auth.sign_in" },
          { ...ROW, id: "01HXYZ3", action: "invite.sent" },
        ]}
      />,
    );

    expect(
      screen.getByRole("rowheader", { name: /tenant renamed/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("rowheader", { name: /sign-in/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("rowheader", { name: /invite sent/i }),
    ).toBeInTheDocument();
  });

  it("falls back to the raw action code for unknown actions", () => {
    render(
      <AuditEventList events={[{ ...ROW, action: "feature.unknown" }]} />,
    );

    expect(
      screen.getByRole("rowheader", { name: "feature.unknown" }),
    ).toBeInTheDocument();
  });

  it("shows a 'system' label when the actor email is empty", () => {
    render(<AuditEventList events={[{ ...ROW, actor_email: "" }]} />);

    expect(screen.getByLabelText(/system actor/i)).toBeInTheDocument();
  });

  it("renders the empty state when there are no events", () => {
    render(<AuditEventList events={[]} />);

    expect(
      screen.getByRole("heading", { name: /no events yet/i }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });
});
