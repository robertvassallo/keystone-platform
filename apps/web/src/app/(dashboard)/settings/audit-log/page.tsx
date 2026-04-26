import Link from "next/link";
import type { JSX } from "react";

import { AuditEventList } from "@/features/audit";
import { listAuditEventsServer } from "@/features/audit/api/list-audit-events-server";

interface AuditLogPageProps {
  readonly searchParams: Promise<{ readonly page?: string }>;
}

const FIRST_PAGE = 1;
const PAGE_SIZE = 25;

function parsePage(raw: string | undefined): number {
  if (raw === undefined) return FIRST_PAGE;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= FIRST_PAGE ? parsed : FIRST_PAGE;
}

export default async function AuditLogPage({
  searchParams,
}: AuditLogPageProps): Promise<JSX.Element> {
  const params = await searchParams;
  const page = parsePage(params.page);
  const result = await listAuditEventsServer({ page, pageSize: PAGE_SIZE });

  if (result.kind === "forbidden") {
    return (
      <main className="mx-auto max-w-md space-y-4 px-6 py-12">
        <h1 className="text-2xl font-semibold text-fg">Access required</h1>
        <p className="text-sm text-fg-muted">
          The audit log is available to tenant owners and platform staff. If
          you think you should have access, ask your tenant&rsquo;s owner.
        </p>
        <p className="text-sm">
          <Link
            href="/"
            className="text-accent hover:underline focus-visible:underline"
          >
            Back to dashboard
          </Link>
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl space-y-6 px-6 py-12">
      <p className="text-sm">
        <Link
          href="/"
          className="text-accent hover:underline focus-visible:underline"
        >
          ← Back to dashboard
        </Link>
      </p>

      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-fg">Audit log</h1>
        <p className="text-sm text-fg-muted">
          Sensitive actions in your tenant. Newest first.
        </p>
      </header>

      <AuditEventList events={result.data} />

      <Pagination page={result.page.page} total={result.page.total} pageSize={result.page.page_size} />
    </main>
  );
}

interface PaginationProps {
  readonly page: number;
  readonly total: number;
  readonly pageSize: number;
}

function Pagination({ page, total, pageSize }: PaginationProps): JSX.Element | null {
  if (total === 0) return null;

  const lastPage = Math.max(FIRST_PAGE, Math.ceil(total / pageSize));
  const start = (page - FIRST_PAGE) * pageSize + FIRST_PAGE;
  const end = Math.min(page * pageSize, total);
  const hasPrev = page > FIRST_PAGE;
  const hasNext = page < lastPage;

  return (
    <nav
      aria-label="Audit log pagination"
      className="flex items-center justify-between gap-3 pt-3 text-sm"
    >
      <p className="text-fg-muted">
        {start}&ndash;{end} of {total}
      </p>
      <div className="flex items-center gap-2">
        <PageLink href={hasPrev ? `?page=${String(page - 1)}` : null} label="Previous page">
          Previous
        </PageLink>
        <PageLink href={hasNext ? `?page=${String(page + 1)}` : null} label="Next page">
          Next
        </PageLink>
      </div>
    </nav>
  );
}

interface PageLinkProps {
  readonly href: string | null;
  readonly label: string;
  readonly children: string;
}

function PageLink({ href, label, children }: PageLinkProps): JSX.Element {
  const className =
    "rounded-md border px-3 py-1.5 text-sm font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent " +
    (href === null
      ? "cursor-not-allowed border-border-subtle text-fg-subtle"
      : "border-border bg-bg-surface text-fg hover:bg-bg-canvas");

  if (href === null) {
    return (
      <span aria-disabled="true" aria-label={`${label} (unavailable)`} className={className}>
        {children}
      </span>
    );
  }
  return (
    <Link href={href} aria-label={label} className={className}>
      {children}
    </Link>
  );
}
