# SQL (Postgres)

For schema conventions see `docs/01_architecture/data-model.md`. This file is about **writing queries and migrations**.

## Why

- A bad query at scale is a production outage.
- A bad migration locks a hot table and takes the app down.
- Explicit SQL is debuggable; clever SQL is a future incident.

## Style

- Keywords UPPERCASE, identifiers lower_snake.
- Two-space indent.
- One column per line in `SELECT` lists; one join per line.
- Trailing commas not allowed in Postgres SQL (lint catches it).

```sql
SELECT
  p.id,
  p.name,
  p.created_at,
  a.name AS account_name
FROM projects AS p
INNER JOIN accounts AS a
  ON a.id = p.account_id
WHERE p.deleted_at IS NULL
  AND p.status = 'active'
ORDER BY p.created_at DESC
LIMIT 50;
```

## Query rules

### Never `SELECT *`

- Always list the columns you actually need.
- Adding a column should not silently change the result shape downstream.
- ORM equivalent: use `.only(...)` / `.values(...)`.

### Always `LIMIT` with `ORDER BY`

`LIMIT` without an order is non-deterministic. Pair them.

### Joins

- Explicit join type: `INNER JOIN`, `LEFT JOIN`. Never bare `JOIN`.
- Join on columns with indexes — usually foreign keys.
- Avoid more than 4 joins in one query — refactor or denormalise if hot.

### Filters

- Filter on indexed columns when possible.
- Avoid leading wildcards (`LIKE '%foo'`) — they can't use a btree index. Use trigram or full-text.
- For "exists" checks: `EXISTS (SELECT 1 FROM ...)` not `COUNT(*) > 0`.

### Aggregates

- `GROUP BY` lists every non-aggregated column. Postgres enforces this — Django ORM doesn't always.
- Window functions over self-joins where applicable.

### N+1

- Loops that issue one query per row are forbidden.
- Django: `select_related` for FK / 1-1; `prefetch_related` for reverse / m2m.
- Verify with `django-debug-toolbar` or `assertNumQueries` in tests.

### Pagination

- **Cursor pagination** for large lists (stable under inserts).
- Offset pagination only for small bounded sets (e.g. an admin list of < 10K items).
- Always paginated. No unbounded `.all()` returned to a view.

### Money / time

- `numeric(p, s)` — never `float`.
- `timestamptz` — never naive `timestamp`.
- Index on `(tenant_id, created_at DESC)` for time-series listings.

## Migration rules

### Reversibility

Every `up` has a `down`. CI runs `migrate` then `migrate <previous>` on a copy of the schema.

### Lock-aware operations

| Operation | Default lock | Safe variant |
|---|---|---|
| `CREATE INDEX` | ShareLock (blocks writes) | `CREATE INDEX CONCURRENTLY` |
| `ALTER TABLE … ADD COLUMN NOT NULL` | ACCESS EXCLUSIVE; rewrites table on populated tables | Add nullable → backfill → set NOT NULL |
| `ALTER COLUMN ... TYPE` | Often rewrites table | Add new column → dual-write → swap |
| Rename column | Cheap lock — but breaks deployed reader | Three-step migration |
| Drop column | Cheap lock — but breaks deployed reader | Stop reading deploy → drop in next release |
| `DELETE` of large set | Long-held row locks | Batched delete |

Add `--concurrent` indexes via `RunSQL(... atomic=False)` in Django migrations.

### Three-step renames

1. Add the new column / index, dual-write both old and new.
2. Read from the new in code; deploy.
3. Drop the old.

Same pattern for table renames, type changes, FK changes.

### Backfills

- Live in **data migrations**, not schema migrations.
- Batched (`UPDATE ... WHERE id IN (...)` in chunks of 1–10K).
- Idempotent — safe to run twice.

### Data integrity

- Foreign keys explicit `ON DELETE` action. `CASCADE` only when intentional and tested.
- `CHECK` constraints for invariants the database can enforce (`amount >= 0`).
- Use `EXCLUSION` constraints for "no two overlapping ranges" needs.

## Security

- **Never** interpolate user input into SQL strings. Use parameters.
- Avoid `RawSQL` / `cursor.execute()` with anything user-derived.
- Apply Row-Level Security policies for multi-tenant tables (see `data-model.md`).

## Performance investigation

- `EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <query>` — check planner's estimates vs actuals.
- Look for `Seq Scan` on large tables → missing index.
- Look for `Rows Removed by Filter` >> `Rows` returned → wrong index used.

## Anti-patterns

| Don't | Do |
|---|---|
| `SELECT *` | List columns |
| `LIMIT 50` without `ORDER BY` | Always paired |
| `COUNT(*) > 0` to check existence | `EXISTS (SELECT 1 FROM ...)` |
| `WHERE created_at::date = '2026-04-24'` | `WHERE created_at >= '...' AND created_at < '...'` (uses index) |
| `CREATE INDEX` in a busy migration | `CONCURRENTLY` |
| `ALTER TABLE … ADD COLUMN ... NOT NULL DEFAULT 'x'` on a hot table | 3-step migration |
| String-interpolated SQL | Parameterised |
| `float` for money | `numeric` |

## Review checklist

- [ ] No `SELECT *`
- [ ] Every `LIMIT` has an `ORDER BY`
- [ ] No N+1 (verified with query count)
- [ ] Indexes for `WHERE` / `JOIN` / `ORDER BY` columns
- [ ] No `CREATE INDEX` without `CONCURRENTLY` on tables > 100K rows
- [ ] Migrations reversible, tested both ways
- [ ] No raw SQL with string interpolation
- [ ] Pagination on every list endpoint
- [ ] Money via `numeric`, time via `timestamptz`

The `@sql-reviewer` agent enforces this checklist.
