import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { UsersListPagination } from "./UsersListPagination";

describe("UsersListPagination", () => {
  it("renders the range and total count", () => {
    render(<UsersListPagination page={1} pageSize={25} total={142} />);

    expect(screen.getByText(/1–25 of 142/)).toBeInTheDocument();
  });

  it("disables the previous link on the first page", () => {
    render(<UsersListPagination page={1} pageSize={25} total={142} />);

    const previous = screen.getByLabelText(/previous page \(unavailable\)/i);
    expect(previous).toHaveAttribute("aria-disabled", "true");
  });

  it("disables the next link on the last page", () => {
    render(<UsersListPagination page={6} pageSize={25} total={142} />);

    const next = screen.getByLabelText(/next page \(unavailable\)/i);
    expect(next).toHaveAttribute("aria-disabled", "true");
  });

  it("links to adjacent pages in the middle of the range", () => {
    render(<UsersListPagination page={3} pageSize={25} total={142} />);

    expect(screen.getByRole("link", { name: /previous page$/i })).toHaveAttribute(
      "href",
      "?page=2",
    );
    expect(screen.getByRole("link", { name: /next page$/i })).toHaveAttribute(
      "href",
      "?page=4",
    );
  });

  it("renders nothing when there are zero rows", () => {
    const { container } = render(
      <UsersListPagination page={1} pageSize={25} total={0} />,
    );

    expect(container.firstChild).toBeNull();
  });
});
