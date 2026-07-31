# Mess Meal Management System — Requirements

## 1. Overview
A web application for managing a shared living "mess" (dormitory/hostel-style
food system). It tracks who ate which meals, how much money each member has
deposited, grocery spending, and fixed monthly bills — then (later) computes
each member's due/refund for the month.

Two roles:
- **Manager** — logs in, has full create/edit/delete access.
- **Member** — no login; views the mess dashboard via a shared/public link,
  read-only.

The system runs on a **monthly cycle**. At the end of each month the manager
closes the cycle, dues are calculated, balances settle to zero, and a new
cycle starts.

---

## 2. Core Entities (plain description, schema comes separately)

### 2.1 Member
- Name
- Join date (for prorating if they join mid-cycle)
- Leave date (optional — for prorating if they leave mid-cycle)
- Active/inactive flag
- Running deposit amount for the current cycle ("money given for meals")

### 2.2 Daily Meal Entry
- Member
- Date
- Breakfast: 0, 0.5, or 1 (manager enters 0.5 or 1; 0 = skipped)
- Lunch: 0 or 1
- Dinner: 0 or 1

> Only the manager can create/edit/delete these. Members only view.

### 2.3 Grocery Bill (main list)
- Date
- Purchased by (member reference)
- Total amount
- Optional itemized breakdown (item name, quantity, unit price) — manager can
  choose to just log a total, or expand into line items when they want more
  detail.

### 2.4 Extra Grocery (off-list purchases)
Separate from the main grocery list — e.g. a one-off item not part of routine
shopping.
- Product name
- Quantity
- Price
- Date
- Purchased by (member reference)

### 2.5 Fixed / Non-Meal Bills
Recurring costs that are **not** part of the grocery/meal cost pool directly
(rice, electricity, chef salary, wifi, and an open "other" category).
- Bill type (rice / electricity / chef / wifi / other — extensible list)
- Amount
- Date
- Note/description
- (How this gets divided among members is **explicitly deferred** — manager
  will supply the formula later. The system should store these bills now and
  allow the calculation logic to be plugged in afterward.)

---

## 3. Key Behaviors

### 3.1 Meal display counts (breakfast doubling rule)
Breakfast is valued at 0.5 per member (half meal), but the **member headcount**
should be shown, not the raw sum.

**Example:** On 5 members ate breakfast → each entry stored as `0.5` → sum =
`2.5` → displayed breakfast count = `2.5 × 2 = 5`. Lunch and dinner are shown
as-is (raw sum), since they're full meals.

Daily dashboard example:
| Meal | Raw sum (entries) | Displayed count |
|------|-------------------|------------------|
| Breakfast | 15.0 (30 halves) | 30 |
| Lunch | 31 | 31 |
| Dinner | 31 | 31 |

### 3.2 Mid-cycle join/leave (proration)
Members may be added or removed mid-month. Example: a member joins on 15
August. The system must:
- Only allow meal entries for that member from the join date onward
- Exclude them from any per-day averages/shared-bill logic for days before
  they joined (exact formula TBD, but the **join/leave date must be stored**
  so any formula can reference it later)
- Similarly, a member leaving on, say, 20 August should have no meal entries
  possible after that date, and should be excluded from cost-sharing for the
  remaining days.

### 3.3 Monthly cycle close-out
- Manager triggers "close month" (or it auto-closes on month-end, TBD in
  architecture doc).
- At close-out: dues/refunds are computed (formula supplied later), each
  member's balance settles to **zero** (any leftover deposit or due is
  considered settled outside the app — manually paid/collected).
- The closed month's data (meals, bills, groceries, computed dues) is
  archived/read-only. A new cycle starts with all deposits reset to 0 unless
  the manager re-enters an opening deposit for the new month.

### 3.4 Access control
- Manager: username/password login (or similar), full CRUD everywhere.
- Members: shared read-only link, no login, no write access anywhere,
  including no ability to edit their own meal entries.

---

## 4. Pages / Views (functional, not visual design)

1. **Dashboard (main mess page)**
   - Table: Member | Deposit given | Breakfast | Lunch | Dinner (per member,
     for the current cycle, likely with a date selector or "today" default)
   - Today's totals: Breakfast count / Lunch count / Dinner count (per §3.1)
   - Manager-only controls to add/edit/remove meal entries and deposits

2. **Grocery Bills page**
   - List/table of grocery bills by date, with purchaser and amount
   - Add/edit/delete (manager only)
   - Optional itemized view per bill

3. **Extra Grocery page**
   - List of off-list purchases: product, quantity, price, date, buyer
   - Add/edit/delete (manager only)

4. **Fixed Bills page**
   - List of rice / electricity / chef / wifi / other bills by date and amount
   - Add/edit/delete (manager only)

5. **Month-End Summary page** *(placeholder until formula is supplied)*
   - Per-member computed due/refund
   - "Close month" action (manager only)
   - Read-only view of past closed months

6. **Members page**
   - List of members, join/leave dates, active status
   - Add/edit/deactivate member (manager only)

---

## 5. Explicitly Deferred (to be specified later by you)
- Exact meal-rate formula (total expense ÷ total meals, or otherwise)
- How fixed bills (chef/wifi/electricity/rice) are split among members
- Whether "total expense" includes grocery only, or grocery + fixed bills
- Proration formula details for mid-month joiners/leavers

The system will be built so these can be added as a calculation module
without changing the data model.

---

## 6. Non-Functional Notes
- Free-tier deployment target: Render (web service) — see architecture.md
- Data must **persist reliably** across the month (grocery/meal history is
  financial-record-like; do not use a database that force-expires/deletes
  data, e.g. avoid Render's own free Postgres which auto-deletes after 30
  days)
- Mobile-friendly view expected, since members will likely check on phones
