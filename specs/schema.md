# Database Schema (Draft)

Relational design (Postgres-flavored). Tables grouped by domain. This is
storage-layer only — calculation logic (meal rate, bill splitting) is
intentionally NOT baked into the schema yet, per requirements.md §5.

---

## cycles
Represents a monthly period.

| Column | Type | Notes |
|---|---|---|
| id | uuid/serial PK | |
| label | text | e.g. "2026-08" |
| start_date | date | |
| end_date | date | nullable until closed |
| status | enum('open','closed') | |
| created_at | timestamp | |

---

## members
| Column | Type | Notes |
|---|---|---|
| id | uuid/serial PK | |
| name | text | |
| is_active | boolean | |
| created_at | timestamp | |

## member_cycle
One row per member per cycle — handles mid-cycle join/leave and per-cycle
deposit, without polluting the base `members` table.

| Column | Type | Notes |
|---|---|---|
| id | PK | |
| member_id | FK -> members | |
| cycle_id | FK -> cycles | |
| join_date | date | defaults to cycle start_date |
| leave_date | date | nullable |
| deposit_amount | numeric | "money given for meals" this cycle |
| computed_due | numeric | nullable, filled at month-end close |
| settled | boolean | true once manually settled to zero |

> Meal entries reference `member_cycle_id`, not `member_id` directly, so a
> given member's history stays cleanly separated cycle by cycle.

---

## meal_entries
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| member_cycle_id | FK -> member_cycle | |
| entry_date | date | |
| breakfast | numeric(3,1) | 0, 0.5, or 1 |
| lunch | numeric(3,1) | 0 or 1 |
| dinner | numeric(3,1) | 0 or 1 |
| updated_by | FK -> manager/user | audit trail |
| updated_at | timestamp | |

Unique constraint: (member_cycle_id, entry_date) — one row per member per day.

**Derived, not stored:** daily displayed breakfast count =
`SUM(breakfast for that date) * 2`. Lunch/dinner displayed count =
`SUM(lunch/dinner for that date)`. Computed at query time or cached in a
`daily_meal_summary` view/materialized table if performance matters later.

---

## grocery_bills
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| cycle_id | FK -> cycles | |
| bill_date | date | |
| purchased_by | FK -> members | |
| total_amount | numeric | required |
| note | text | optional |

## grocery_bill_items
Optional itemization, 0..N rows per grocery_bills row.

| Column | Type | Notes |
|---|---|---|
| id | PK | |
| grocery_bill_id | FK -> grocery_bills | |
| item_name | text | |
| quantity | numeric | |
| unit_price | numeric | |
| line_total | numeric | quantity * unit_price (stored or computed) |

> If the manager just logs a total, `grocery_bill_items` stays empty for
> that bill — `total_amount` on the parent row is still authoritative.

---

## extra_grocery
Off-list one-off purchases — kept separate from the main grocery bills.

| Column | Type | Notes |
|---|---|---|
| id | PK | |
| cycle_id | FK -> cycles | |
| purchased_by | FK -> members | |
| product_name | text | |
| quantity | numeric | |
| price | numeric | |
| purchase_date | date | |

---

## fixed_bills
Rice / electricity / chef / wifi / other — not part of the meal grocery pool.

| Column | Type | Notes |
|---|---|---|
| id | PK | |
| cycle_id | FK -> cycles | |
| bill_type | enum('rice','electricity','chef','wifi','other') | extensible |
| amount | numeric | |
| bill_date | date | |
| description | text | optional, esp. useful when bill_type = 'other' |

---

## managers (auth)
| Column | Type | Notes |
|---|---|---|
| id | PK | |
| username | text unique | |
| password_hash | text | |
| created_at | timestamp | |

> Members do not get rows here — they access via a public read-only route
> (optionally protected by a single shared view-only passcode, per your
> earlier answer: "manager login, members view via shared link, no login").

---

## Entity Relationship Summary

```
cycles ──< member_cycle >── members
                │
                ├──< meal_entries
                │
cycles ──< grocery_bills ──< grocery_bill_items
cycles ──< extra_grocery
cycles ──< fixed_bills
managers (standalone, auth only)
```

## Indexing notes
- `meal_entries (member_cycle_id, entry_date)` — unique + primary lookup path
- `grocery_bills (cycle_id, bill_date)`
- `fixed_bills (cycle_id, bill_type)`
- `member_cycle (cycle_id)` — for building the dashboard table per cycle
