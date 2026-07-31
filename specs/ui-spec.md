# UI Specification

This is the source of truth for all visual and interaction decisions.
Kilo should not invent colors, spacing, or layout choices not covered here —
if something genuinely isn't specified (e.g. an exact border-radius on a
minor element), pick a value consistent with the tokens below and move on;
don't stop and ask for trivia like that.

---

## 1. Design Tokens

### Colors
A calm, utilitarian palette. Manager side needs to feel like a clean data
tool (lots of tables); public side needs to feel simple and trustworthy on a
phone screen.

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `#F7F8FA` | page background |
| `--color-surface` | `#FFFFFF` | cards, tables, panels |
| `--color-border` | `#E2E5E9` | table borders, dividers |
| `--color-text-primary` | `#1F2430` | main text |
| `--color-text-muted` | `#6B7280` | secondary text, labels |
| `--color-primary` | `#2E6F5E` | primary buttons, links, active nav (muted teal-green — calm, not corporate-blue-cliché) |
| `--color-primary-hover` | `#255A4C` | hover state on primary |
| `--color-accent` | `#C97B2E` | warnings, "due" amounts, attention badges (warm amber) |
| `--color-danger` | `#B3413B` | delete actions, errors, over-budget states |
| `--color-success` | `#3E8E5A` | confirmations, "settled"/"paid" states |

### Typography
- Font: system font stack — `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif` (no webfont load, keeps it fast and free-tier-friendly)
- Base size: `16px`, line-height `1.5`
- Scale: `12px` (small/meta) / `14px` (body/table) / `16px` (default) / `20px` (section headers) / `28px` (page title)
- Weight: `400` body, `600` headers/labels, `700` only for key numbers (today's meal counts, balances)

### Spacing
8px base unit: `4, 8, 12, 16, 24, 32, 48` — use these values only, no arbitrary spacing.

### Components
- **Buttons**: `--color-primary` background, white text, `6px` border-radius, `10px 16px` padding. Danger buttons use `--color-danger`, same shape. Disabled state: `--color-border` background, `--color-text-muted` text.
- **Tables**: white surface, `1px solid --color-border` row dividers, no vertical lines, `12px 16px` cell padding, header row `600` weight with `--color-text-muted` color, sticky header on scroll for the meal grid specifically.
- **Cards**: white surface, `1px solid --color-border`, `8px` border-radius, `16px` padding, subtle shadow (`0 1px 2px rgba(0,0,0,0.04)`).
- **Badges** (for settled/due/over-budget states): pill shape, `12px` text, colored background at 15% opacity of the relevant token color + full-opacity text of that color.
- **Forms**: labels above inputs (not inline), `--color-border` input borders, `--color-primary` focus ring, inline validation error text in `--color-danger` directly under the field.

### Layout
- Manager pages: max content width `1100px`, centered, left sidebar nav (collapses to top bar under `768px`)
- Public dashboard: max content width `720px`, centered, no sidebar — single column, mobile-first (most members will view on phone)
- Breakpoint: `768px` is the only breakpoint needed (desktop manager use vs. mobile member use covers the real usage split)

---

## 2. Global Layout

### `base_manager.html` (behind login)
- Left sidebar (top bar on mobile): links to Dashboard, Meal Entry, Members, Groceries, Bills, Month Summary, Logout
- Top-right: current cycle label (e.g. "August 2026") + status (Open/Closed)

### `base_public.html` (no login)
- Simple top bar: mess name (configurable) + current cycle label only. No nav links needed — it's a single scrolling page (see §3.1).

---

## 3. Page-by-Page Specification

### 3.1 Public Dashboard (`dashboard/home.html`)
This is the one page regular members actually use. Single scrolling page,
mobile-first, top to bottom:

1. **Header**: mess name, current cycle (e.g. "August 2026"), last-updated timestamp
2. **Today's meal counts** — three large number cards side by side (stack vertically under 480px): Breakfast / Lunch / Dinner, each showing the doubled/raw-as-appropriate count per requirements.md §3.1, with the meal name as a `12px` muted label above a `28px` bold number
3. **Members table** — columns: Name | Deposit Given | Breakfast (this month, sum) | Lunch (this month, sum) | Dinner (this month, sum). Sortable by column header click (client-side, no backend call needed). No edit controls anywhere on this page — purely read-only, enforced both by no write routes existing (per project-structure.md) and by no buttons rendered here.
4. **Footer note**: small muted text, "Data updated by mess manager. Contact [manager] for corrections." (static text, not built dynamically — just a placeholder string the manager can edit in settings later if needed)

### 3.2 Manager Login (`registration/login.html`)
- Centered card, max-width `360px`, vertically centered on screen
- Fields: username, password. Single primary button "Log in". No "remember me," no "forgot password" flow for v1 — single manager account, out of scope.

### 3.3 Meal Entry Grid (`meals/entry_grid.html`)
The highest-friction page — needs to be fast for daily data entry.
- Date selector at top (defaults to today), with prev/next day arrows
- Table: rows = active members for the current cycle (filtered by join/leave date automatically — a member who hasn't joined yet or already left doesn't appear as an editable row for that date), columns = Breakfast | Lunch | Dinner
- Each cell is an HTMX-driven inline control: three small toggle buttons per meal type — Breakfast shows `0 / ½ / 1`, Lunch and Dinner show `0 / 1`. Clicking a value submits via HTMX and swaps just that cell (`partials/meal_cell.html`), no full page reload.
- Active/selected value in each cell is highlighted with `--color-primary` background; others are plain outlined buttons.
- Top of page also shows the same "today's meal counts" summary as the public dashboard, so the manager sees the live effect of edits immediately.

### 3.4 Members Page (`members` — likely rendered via customized Django admin, but if a custom page is built instead, same spec applies)
- Table: Name | Status (Active/Inactive badge) | Join Date | Leave Date | Deposit (current cycle) | Actions (Edit/Deactivate)
- "Add Member" button top-right opens a form (modal or separate page — modal preferred for speed): Name, Join Date (defaults to today), Deposit Amount
- Editing join/leave dates on an existing member should show a confirmation note: "This affects which dates this member can have meal entries" — not a hard blocker, just a visible warning, since retroactive edits are a manager's call.

### 3.5 Groceries Page (`groceries/bill_list.html`, `extra_list.html`)
- Two tabs or two sections on one page: "Grocery Bills" and "Extra Grocery"
- Grocery Bills table: Date | Purchased By | Total Amount | Items (expandable row showing itemized list if present, else "—")
- "Add Bill" form: Date, Purchased By (dropdown of active members), Total Amount, then an optional "+ Add itemized breakdown" toggle that reveals repeatable rows (item name, quantity, unit price) — collapsed by default per requirements.md §2.3 ("manager can choose")
- Extra Grocery table: Date | Product | Quantity | Price | Purchased By — simpler, single-row-per-entry form, no itemization needed since each entry already is a single item

### 3.6 Fixed Bills Page (`bills/bill_list.html`)
- Table: Date | Bill Type (badge, one color per type — e.g. rice=amber, electricity=teal, chef=primary, wifi=muted, other=gray) | Amount | Description
- "Add Bill" form: dropdown for bill type (rice/electricity/chef/wifi/other), amount, date, optional description (required if type = "other")

### 3.7 Month Summary (`dashboard/month_summary.html`)
- Until the due/refund formula is supplied: this page shows raw totals only — total grocery spend, total extra grocery spend, total fixed bills, total meals eaten per member — with a visible placeholder banner: "Due/refund calculation not yet configured." No fake numbers, no guessed formula.
- Once the formula is added, this becomes: table of Member | Meals Eaten | Amount Due | Deposit Given | Balance, plus the manager-only "Close Month" button with a confirmation dialog ("This will archive August 2026 and settle all balances to zero. This cannot be undone.").

---

## 4. Interaction Conventions
- All destructive actions (delete a bill, deactivate a member, close a month) require a confirmation dialog — no silent deletes.
- All forms show inline validation errors next to the field, not a generic top-of-page error banner.
- Success actions (save, add) show a brief toast/inline confirmation, not a full page reload where avoidable (HTMX swap + a small confirmation message).
- No client-side framework beyond HTMX + vanilla JS for small things like the sortable table headers on the public dashboard — keep the stack as specified, no React introduced here.
