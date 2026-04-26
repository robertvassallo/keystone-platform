"use client";

import { useState, type JSX } from "react";

import { cn } from "@/shared/lib/cn";

import type { Account } from "../../types";
import { AccountCard } from "../AccountCard";
import { TenantSettingsForm } from "../TenantSettingsForm";

interface AccountEditPanelProps {
  readonly account: Account;
  readonly canEdit: boolean;
}

export function AccountEditPanel({
  account,
  canEdit,
}: AccountEditPanelProps): JSX.Element {
  const [editing, setEditing] = useState(false);

  if (editing) {
    return (
      <div className="rounded-md border border-border-subtle bg-bg-surface p-6">
        <TenantSettingsForm
          initial={account}
          onCancel={() => {
            setEditing(false);
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <AccountCard account={account} />
      {canEdit && (
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => {
              setEditing(true);
            }}
            className={cn(
              "rounded-md border border-border bg-bg-surface px-3 py-1.5 text-sm font-medium text-fg",
              "hover:bg-bg-canvas",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent",
            )}
          >
            Edit tenant
          </button>
        </div>
      )}
    </div>
  );
}
