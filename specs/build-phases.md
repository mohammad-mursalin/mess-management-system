# Build Phases

Work through these in order. **Stop after each phase and wait for review**
before starting the next one — don't run ahead. Each phase lists what "done"
means so it's reviewable as a discrete chunk.

Reference docs for every phase: requirements.md, schema.md, ui-spec.md,
backend-spec.md, project-structure.md. If something needed to complete a
phase isn't covered in those docs, stop and ask rather than deciding.

---

## Phase 0 — Project Scaffold
- Django project (`config/`) + all five apps created (`cycles`, `members`,
  `meals`, `groceries`, `bills`, `dashboard`) per project-structure.md
- `requirements.txt`, `.env.example`, `.gitignore`, `runtime.txt`, `Procfile`
- Settings configured to read `DATABASE_URL` from env (Neon connection
  string goes here later), `DEBUG` from env, static files configured
- **Done when:** `python manage.py runserver` boots with no errors, admin
  site loads at `/admin`, no models yet.

## Phase 1 — Cycles & Members
- `Cycle`, `Member`, `MemberCycle` models + migrations (schema.md §cycles,
  members, member_cycle)
- Django admin registered for all three with sensible `list_display`
- Manager auth working (`registration/login.html` per ui-spec.md §3.2,
  `@login_required` on non-admin manager views)
- `cycles/services.py`: `close_month()` and `open_new_cycle()` implemented
  per backend-spec.md §2, even though there's nothing to close yet
- **Done when:** manager can log in, create a cycle, add members with
  join/leave dates and a deposit amount, all via admin or a basic form.

## Phase 2 — Meal Entries
- `MealEntry` model + migration, unique constraint on `(member_cycle,
  entry_date)`
- `meals/selectors.py` with the breakfast-doubling calculation
  (backend-spec.md §4)
- `meals/entry_grid.html` — full HTMX-driven grid per ui-spec.md §3.3
- Validation: reject entries outside a member's join/leave window, reject
  entries in a closed cycle, reject invalid meal values
- **Done when:** manager can enter/edit meals for any active member on any
  valid date via the grid, invalid attempts show clear errors, and the
  today's-counts summary updates live.

## Phase 3 — Public Dashboard
- `dashboard/home.html` per ui-spec.md §3.1 — today's counts + members table
- Confirm: zero write routes anywhere in the `dashboard` app
- **Done when:** the public page is reachable with no login, shows live data
  matching what phase 2 entered, and has no edit controls anywhere.

## Phase 4 — Groceries & Extra Grocery
- `GroceryBill`, `GroceryBillItem`, `ExtraGrocery` models + migrations
- Admin + `groceries/bill_list.html`, `extra_list.html` per ui-spec.md §3.5
- Itemization toggle working, `total_amount` remains authoritative
  (backend-spec.md §5)
- **Done when:** manager can log a simple total-only bill, a fully itemized
  bill, and separate extra-grocery entries.

## Phase 5 — Fixed Bills
- `FixedBill` model + migration
- Admin + `bills/bill_list.html` per ui-spec.md §3.6, type badges colored
  per spec, `other` type requires description (backend-spec.md §7)
- **Done when:** manager can log rice/electricity/chef/wifi/other bills and
  see them listed with correct badges.

## Phase 6 — Month Summary (placeholder version)
- `dashboard/month_summary.html` showing raw totals only, with the "not yet
  configured" banner per ui-spec.md §3.7 — no invented formula
- **Done when:** totals (grocery, extra grocery, fixed bills, meals per
  member) display correctly for the current open cycle; no due/refund
  numbers shown yet.

## Phase 7 — Styling Pass
- Apply ui-spec.md tokens (colors, spacing, typography) consistently across
  every template built in phases 0–6 — this is a dedicated pass, not
  something to half-do inline per phase, so it's reviewable as one unit
- **Done when:** every page matches ui-spec.md's component/layout rules, on
  both desktop and the `768px` mobile breakpoint.

## Phase 8 — Deployment
- `render.yaml` / Render dashboard config, Neon `DATABASE_URL` wired in,
  static files served correctly in production (e.g. WhiteNoise), manager
  superuser created on the deployed instance
- **Done when:** the live Render URL shows a working public dashboard, and
  manager login works on the deployed instance.

---

## Phase 9 — Deferred, do not start until formula is supplied
- Due/refund formula in `cycles/services.py`
- Wiring that formula into `close_month()` and `month_summary.html`'s real
  numbers
- Bill-splitting-by-proration logic

This phase is intentionally last and separate — everything through Phase 8
should be fully usable (manager logging data, members viewing it) without it.
