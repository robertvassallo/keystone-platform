# Data Model

Postgres conventions for any project built from this template.

## Naming

| Object | Convention | Example |
|---|---|---|
| Schema | `lower_snake` | `public`, `audit`, `analytics` |
| Table | `lower_snake`, plural | `user_accounts`, `project_milestones` |
| Column | `lower_snake` | `created_at`, `last_login_at` |
| Primary key | `id` (uuid v7) | |
| Foreign key | `<referenced_singular>_id` | `account_id`, `project_id` |
| Index | `ix_<table>_<col(s)>` | `ix_orders_account_id` |
| Unique constraint | `uq_<table>_<col(s)>` | `uq_users_email` |
| Check constraint | `chk_<table>_<rule>` | `chk_orders_total_nonneg` |
| Foreign-key constraint | `fk_<table>_<col>` | `fk_orders_account_id` |

## Audit columns (every table)

```sql
created_at  timestamptz NOT NULL DEFAULT now(),
updated_at  timestamptz NOT NULL DEFAULT now(),
created_by  uuid REFERENCES user_accounts(id),
updated_by  uuid REFERENCES user_accounts(id),
```

`updated_at` maintained by a trigger (`set_updated_at`) — applied via a migration template.

## Soft delete (when needed)

```sql
deleted_at  timestamptz NULL,
deleted_by  uuid NULL REFERENCES user_accounts(id),
```

- A row with `deleted_at IS NOT NULL` is invisible to default Django manager.
- Hard delete reserved for compliance erasure (GDPR) or test fixtures.
- Unique constraints that should ignore deleted rows use partial indexes:
  `CREATE UNIQUE INDEX uq_users_email ON users (email) WHERE deleted_at IS NULL;`

## Multi-tenancy options

Pick **one** per project; document the choice in `decisions-log.md`.

| Strategy | When to use |
|---|---|
| `tenant_id` column on every tenant-owned table + RLS | Default for SaaS dashboards. Clean isolation. |
| Schema-per-tenant | Strong isolation requirements; few tenants. |
| Database-per-tenant | Compliance / data residency requirements. |

If using `tenant_id` + RLS, every query goes through `set_config('app.current_tenant', '<id>')` in a request middleware.

## ID strategy

- **UUID v7** (time-ordered) for primary keys — sortable, no enumeration leakage.
- Generated client-side or via Postgres function `uuid_generate_v7()`.
- Never expose integer auto-increment IDs in URLs or APIs.

## Money & quantity

- Use `numeric(precision, scale)` — never `float` / `double`.
- Store currency code alongside amount: `amount_cents int`, `currency_code char(3)`.

## Time

- Always `timestamptz`. Never naive `timestamp`.
- Persist UTC; format to user timezone in the UI.

## Enums

- Prefer `text` + `CHECK` constraint — easy to ALTER, queryable.
- Use Postgres `ENUM` only when the values are very stable; add new values with `ALTER TYPE`.

## JSON

- `jsonb`, never `json`.
- Add a check or schema validation at the application layer; Postgres alone doesn't validate shape.
- Index specific paths used in `WHERE` clauses (`CREATE INDEX … ON … ((data->>'foo'))`).

## Migrations

- Reversible — every `up` has a corresponding `down`.
- Schema migrations and data migrations live in separate files.
- Long-running operations (`CREATE INDEX`, `ALTER TABLE`) use `CONCURRENTLY` / batched updates. See `docs/02_standards/sql.md`.

## Seed data

- Live in `infra/scripts/seed/` as idempotent SQL or Python functions.
- Never embedded in migrations — migrations apply to all environments; seeds are dev/test only.

## Review checklist

- [ ] All tables have audit columns
- [ ] Foreign keys have explicit `ON DELETE` action
- [ ] Multi-tenant tables enforce isolation (RLS or explicit `tenant_id` filter in default manager)
- [ ] Money columns use `numeric` + currency code
- [ ] Constraints are named per the table above
- [ ] Migrations reversible and tested both directions
