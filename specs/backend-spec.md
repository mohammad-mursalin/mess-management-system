# Backend Behavior Specification

This defines exact backend rules so Kilo isn't left to guess validation,
permissions, or edge-case behavior. Read alongside schema.md (data shapes)
and requirements.md (feature scope).

---

## 1. Permissions (enforced at the view level, every request)

| Route group | Who | Enforcement |
|---|---|---|
| `dashboard/*` | Anyone, no login | No write views exist in this app at all — nothing to enforce beyond "don't add any" |
| everything else (`meals`, `members`, `groceries`, `bills`, `cycles` admin/views) | Manager only | Django `@login_required` on every view; Django admin already enforces staff/superuser login |

There is no member-level authentication. Do not build a member login system
even if it seems convenient later — it's explicitly out of scope per
requirements.md.

---

## 2. Cycles

- Exactly one cycle has `status = 'open'` at any time. Creating a new cycle
  while one is open should be blocked (error: "Close the current cycle
  before starting a new one").
- **Closing a cycle** (`cycles/services.py: close_month()`):
  1. Set `status = 'closed'`, `end_date = today` (or last day of month)
  2. For every `member_cycle` row in this cycle: if `computed_due` formula is
     available, calculate and store it; otherwise leave null and show the
     placeholder banner (per ui-spec.md §3.7)
  3. Mark every `member_cycle.settled = True` (balances settle to zero per
     requirements.md §3.3 — no partial/manual settlement tracking in v1)
  4. This is irreversible in the UI — no "reopen cycle" button. (If a mistake
     is made, that's a manual DB fix by the developer, not a feature to build.)
- **Opening a new cycle**: manager explicitly triggers it (no auto-create on
  month boundary — avoids surprise behavior). New cycle's `start_date`
  defaults to today. All *active* members from the previous cycle get a new
  `member_cycle` row with `deposit_amount = 0` (manager re-enters deposits
  for the new month) and `join_date = new cycle's start_date`.

---

## 3. Members & Proration

- `Member.is_active` controls whether they appear in "Add Member to this
  cycle" type flows; it does not delete history.
- A member can only have meal entries within `[join_date, leave_date or
  cycle end]` for their `member_cycle` row. Attempting to create a
  `MealEntry` outside that range must be rejected with a clear error (e.g.
  "Member joined on 2026-08-15; cannot log meals before that date").
- Editing `join_date`/`leave_date` after meal entries already exist in the
  now-excluded range does **not** auto-delete those entries — show the
  warning from ui-spec.md §3.4 and leave existing data untouched. Deleting
  conflicting entries, if ever needed, is a separate explicit manager action.
- Proration math itself (how join/leave date affects bill-splitting) is
  deferred per requirements.md §5 — the *data* (join_date, leave_date) must
  be correctly enforced now; the *formula* that consumes it comes later.

---

## 4. Meal Entries

- Valid values: `breakfast ∈ {0, 0.5, 1}`, `lunch ∈ {0, 1}`, `dinner ∈ {0, 1}`.
  Reject anything else at the model/form level (`choices=` constraint, not
  just UI-level buttons — never trust the client).
- One entry per `(member_cycle, entry_date)` — enforced by DB unique
  constraint (schema.md). Submitting again for the same day updates the
  existing row, doesn't create a duplicate.
- `entry_date` must fall within the entry's cycle's `[start_date, end_date or
  today if still open]` — reject entries for dates in a closed cycle.
- **Daily count calculation** (`meals/selectors.py`):
  ```
  breakfast_count(date) = SUM(breakfast for that date across all entries) * 2
  lunch_count(date) = SUM(lunch for that date)
  dinner_count(date) = SUM(dinner for that date)
  ```
  This is the only place this formula should live — both the public
  dashboard and the manager grid call this same selector function, never
  duplicate the calculation in a template or view.

---

## 5. Grocery Bills

- `total_amount` is always required and always authoritative, even if line
  items are added.
- If line items are added, their `line_total` sum **does not need to equal**
  `total_amount` automatically — don't auto-validate/block on mismatch (real
  receipts have taxes/discounts not worth modeling). Optionally show a
  soft note if they differ by more than a trivial rounding amount, but never
  block saving.
- `purchased_by` must be an active member in the current cycle.

## 6. Extra Grocery
- Same `purchased_by` constraint as above.
- No relationship to `grocery_bills` — fully separate table/list per
  requirements.md §2.4.

## 7. Fixed Bills
- `bill_type = 'other'` requires a non-empty `description`. All other types,
  description is optional.
- No `purchased_by` field — these are mess-level bills, not attributed to a
  specific member's purchase.

---

## 8. HTMX Response Conventions

- Every HTMX-triggered endpoint (meal cell update, etc.) returns a small
  HTML fragment matching the relevant `partials/*.html` template — never a
  full page, never raw JSON (this app doesn't need a JSON API layer at all,
  keep it server-rendered throughout).
- On validation failure from an HTMX request, return the same partial with
  an inline error message rendered in it (HTTP 200 or 422, not a redirect) —
  the swap should show the error in place, not lose the user's context.

---

## 9. Things to explicitly NOT build in v1
- No member login/auth
- No email/SMS notifications
- No file uploads (no receipt photo attachments — out of scope unless you
  ask for it later)
- No multi-mess/multi-tenant support — this is a single mess, single deployment
- No automated recurring fixed-bill entry (manager enters each bill manually
  each month, even if amount is usually similar)
- No "reopen a closed cycle" feature
