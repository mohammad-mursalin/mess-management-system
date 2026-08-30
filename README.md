# Mess Management System

[**Live Demo →**](https://mess-manager-7pu0.onrender.com/)

A Django-based web application for managing a shared "mess" (dormitory/hostel-style food system). It tracks who ate which meals, member deposits and balances, grocery spending, fixed monthly bills, and automates due/refund calculations at the end of each monthly cycle.

---

## Table of Contents

1. [What Is This Project?](#what-is-this-project)
2. [Why Does It Exist?](#why-does-it-exist)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Database Schema](#database-schema)
7. [Monthly Cycle Workflow](#monthly-cycle-workflow)
8. [How It Calculates Dues](#how-it-calculates-dues)
9. [Guest Meals](#guest-meals)
10. [Access Control](#access-control)
11. [Installation & Setup](#installation--setup)
12. [Running Tests](#running-tests)
13. [Deployment](#deployment)
14. [Configuration](#configuration)
15. [Extending the Project](#extending-the-project)
16. [License](#license)

---

## What Is This Project?

The Mess Management System is a web application built to solve the bookkeeping chaos of a shared mess — a group of people who eat together and share food expenses. Instead of spreadsheets, WhatsApp threads, and monthly arguments about who owes what, this system gives managers a clean, real-time dashboard and gives members a public read-only view of the mess's financial state.

The app lives on a **monthly cycle**. Every month the manager opens a new cycle, logs daily meals and expenses throughout the month, and then closes the cycle. On close, the system automatically computes each member's balance — how much they owe or are owed — based on every meal eaten, every grocery bill, and every fixed monthly expense.

It is built with **Django**, uses **HTMX** for dynamic interactions (no separate frontend framework needed), and is deployed on **Render** with a **Neon (PostgreSQL)** database.

---

## Why Does It Exists?

Managing a shared mess involves dozens of small, daily decisions:

- Who ate breakfast today?
- How much did groceries cost this week?
- Who bought them?
- What's the electricity bill?
- How much has each person deposited?
- At the end of the month, who owes money and who gets a refund?

Doing this by hand leads to errors, forgotten entries, and trust issues. The Mess Management System digitizes every step so that numbers are always current, every entry is traceable, and month-end settlements are computed automatically.

---

## Features

### Manager Features (authenticated)

| Feature | Description |
|---|---|
| **Meal Entry Grid** | HTMX-driven interactive grid to log breakfast, lunch, and dinner per member per day. Supports half-meals and guest meals with a stepper UI. |
| **Member Management** | Add, edit, deactivate, and reactivate members. Set join and leave dates for mid-cycle proration. Track deposit amounts. |
| **Grocery Bills** | Log grocery expenses with optional itemized breakdowns. Track extra off-list purchases. |
| **Fixed Bills** | Record recurring non-meal costs: electricity, chef salary, wifi, gas, garbage, and custom "other" bills. |
| **Month Summary** | Live estimated dues while the cycle is open; finalized numbers after the cycle closes. Editable per-member meal rate. |
| **Cycle Management** | Open a new monthly cycle or close the current one. Enforces one open cycle at a time. |
| **Meal History** | Day-by-day breakdown of any member's meal record for the current or previous cycle. |

### Public / Member Features (no login required)

| Feature | Description |
|---|---|
| **Public Dashboard** | Today's meal counts, per-member meal status for the day, and monthly totals. No account needed. |
| **Month Summary (Read-Only)** | Same detailed dues/refunds view as managers, but members can only view, not edit. |
| **Meal History** | Select a member and view their complete day-by-day meal record for the current or previous cycle. |

### Guest Meals

The system supports **guest meals** natively. Each meal type has a base unit:
- Breakfast = 0.5 (half-meal)
- Lunch = 1 (full meal)
- Dinner = 1 (full meal)

When a value exceeds the base unit, the extra portion is counted as a guest meal. For example, a breakfast entry of `1.5` means `0.5` member meal + `1.0` guest portion. Guest meals are displayed with a `👤+N` badge and factored into the meal rate calculation so that guests effectively subsidize the cost of the meals they eat.

### Mid-Cycle Joiners and Leavers

Members can join or leave mid-month. The system enforces:
- No meal entries allowed before a member's join date or after their leave date.
- Cost-sharing calculations respect the join/leave window so new and departing members are only charged for the days they were present.

### Breakfast Doubling Rule

Breakfast is valued at `0.5` per member per meal. The daily dashboard displays the **member headcount** (not the raw sum). For example, if 30 members each have a `0.5` breakfast entry, the raw sum is `15.0` but the displayed count is `30`.

---

## Technology Stack

| Category | Technology |
|---|---|
| **Backend Framework** | Django 5.0.1 |
| **Dynamic UI** | HTMX 2.0 (via `django-htmx` 1.5.0) |
| **Database (Production)** | PostgreSQL via Neon |
| **Database (Development)** | SQLite3 (local fallback) |
| **Configuration** | `django-environ` for environment variables |
| **Static Files** | WhiteNoise 6.7.0 |
| **WSGI Server** | Gunicorn 23.0.0 |
| **Deployment** | Render (web service + external Postgres) |
| **Containerization** | Docker Compose (local Postgres 16) |
| **Testing** | Django TestCase |

---

## Project Structure

```
mess-management-system/
├── manage.py                        # Django entry point
├── requirements.txt                  # Python dependencies
├── docker-compose.yml               # Local Postgres container
├── .env / .env.example              # Environment variables
├── Procfile                         # Render deployment config
├── config/                          # Django project configuration
│   ├── settings.py                  # Main settings (env-driven)
│   ├── urls.py                      # Root URL routing
│   ├── wsgi.py / asgi.py
│   ├── dev.py                       # Local dev overrides (SQLite)
│   ├── prod.py                      # Production overrides
│   └── context_processors.py        # Injects current_cycle into templates
├── apps/                            # Domain-driven Django apps
│   ├── cycles/                      # Monthly cycle open/close
│   │   ├── models.py                # Cycle model
│   │   ├── services.py              # close_month(), open_new_cycle(), compute_cycle_due()
│   │   ├── views.py / urls.py / admin.py
│   │   └── migrations/
│   ├── members/                     # Member & MemberCycle
│   │   ├── models.py                # Member, MemberCycle
│   │   ├── forms.py                 # AddMemberForm, EditMemberForm
│   │   ├── views.py                 # List, add, edit, toggle active
│   │   ├── management/commands/
│   │   │   └── seed_members.py      # Seeds predefined members
│   │   └── migrations/
│   ├── meals/                       # Daily meal entries
│   │   ├── models.py                # MealEntry
│   │   ├── selectors.py             # Breakfast doubling, member/guest unit math
│   │   ├── views.py                 # Entry grid + HTMX cell updates
│   │   ├── templatetags/
│   │   │   └── meal_extras.py       # format_meal_value, meal_guest_count, stepper_values
│   │   └── migrations/
│   ├── groceries/                   # Grocery bills & extras
│   │   ├── models.py                # GroceryBill, GroceryBillItem, ExtraGrocery
│   │   ├── forms.py                 # GroceryBillForm, ExtraGroceryForm
│   │   ├── views.py                 # CRUD for bills and extras
│   │   ├── utils.py                 # sync_bill_items, member_choices_json
│   │   └── migrations/
│   ├── bills/                       # Fixed/recurring bills
│   │   ├── models.py                # FixedBill (electricity, chef, wifi, gas, garbage, other)
│   │   ├── forms.py                 # FixedBillForm
│   │   ├── views.py / urls.py / admin.py
│   │   └── migrations/
│   └── dashboard/                   # Public read-only views
│       ├── views.py                 # home, month_summary, meal_history
│       ├── templatetags/
│       │   └── dashboard_extras.py  # format_meal_value filter
│       └── migrations/
├── templates/                       # Shared global templates
│   ├── base_manager.html            # Sidebar layout for authenticated managers
│   ├── base_public.html             # Public layout (sidebar if logged in, else public header)
│   └── registration/
│       └── login.html
├── static/                          # CSS, JavaScript, images
├── tests/                           # Django test suite
│   ├── test_due_calculation.py
│   ├── test_fixed_member_rate.py
│   └── test_ui_fixes.py
└── specs/                           # Comprehensive project documentation
    ├── requirements.md
    ├── schema.md
    ├── ui-spec.md
    ├── backend-spec.md
    ├── architecture.md
    ├── project-structure.md
    ├── build-phases.md
    ├── due-calculation-spec.md
    ├── guest-meals-spec.md
    ├── mobile-spec.md
    └── public-visibility-spec.md
```

---

## Database Schema

| Table | Purpose |
|---|---|
| `cycles` | Monthly periods (label, start/end dates, open/closed status, fixed_member_rate) |
| `members` | Member list (name, active/inactive status) |
| `member_cycle` | Member-to-cycle join table (join/leave dates, deposit, computed_due, settled status) |
| `meal_entries` | Daily meal records per member (breakfast, lunch, dinner as decimals) |
| `grocery_bills` | Main grocery shopping totals (date, purchaser, total, note) |
| `grocery_bill_items` | Optional itemization per grocery bill |
| `extra_grocery` | Off-list one-off grocery purchases |
| `fixed_bills` | Recurring non-meal costs (electricity, chef, wifi, gas, garbage, other) |
| `auth_user` | Django's built-in manager accounts |

---

## Monthly Cycle Workflow

1. **Open Cycle** — The manager opens a new monthly cycle. The system creates a `MemberCycle` row for every active member with deposits reset to zero.

2. **Daily Operations** — Throughout the month, the manager:
   - Logs daily meal entries via the HTMX-driven grid.
   - Records grocery bills (with optional itemized breakdowns).
   - Logs extra grocery purchases.
   - Adds fixed bills (electricity, chef, wifi, etc.).

3. **Live Estimates** — While the cycle is open, the Month Summary page shows estimated dues computed in real time so members can see where things stand.

4. **Close Cycle** — At month-end, the manager closes the cycle:
   - All calculations are finalized and stored as `computed_due` on each `MemberCycle`.
   - The cycle becomes read-only.
   - A new cycle can be opened.

---

## How It Calculates Dues

The core calculation in `cycles/services.py:compute_cycle_due()` works as follows:

```
Per-member meal expense  =  (member's total meals × fixed_member_rate)
                            + (member's guest meals × fixed_member_rate)

Total grocery expense    =  sum of all GroceryBill totals + ExtraGrocery totals
                            (split equally among active members for that cycle)

Total fixed bills        =  sum of all FixedBill amounts
                            (split equally among active members for that cycle)

Member's total expense   =  per-member meal expense
                            + member's share of grocery expense
                            + member's share of fixed bills

Member's balance/due     =  total expense − deposit
                            (positive = owes money, negative = gets refund)
```

The `fixed_member_rate` is editable by the manager and represents the per-meal cost. Guest meals are charged at the same rate as member meals. All fixed bills and grocery totals are split equally among active members for the cycle.

This formula is fully implemented, tested with a worked example in `tests/test_due_calculation.py`, and verified end-to-end.

---

## Guest Meals

The system handles guest meals through **unit math** rather than a separate "guest" flag:

- **Breakfast base unit:** `0.5`
- **Lunch base unit:** `1`
- **Dinner base unit:** `1`

When a manager enters a value above the base unit for a meal, the excess is treated as guest portions. The stepper UI in the meal grid makes this intuitive:
- Breakfast: `0` → `0.5` → `1` → `1.5` → `2` ...
- Lunch / Dinner: `0` → `1` → `2` → `3` ...

The UI displays guest counts with a `👤+N` badge so members can see at a glance how many guests were fed.

---

## Access Control

The system has two distinct access levels:

| Role | Access | Authentication |
|---|---|---|
| **Manager** | Full CRUD on meals, members, groceries, bills, cycles | Django login (`@login_required`) |
| **Member / Public** | Read-only dashboard, month summary, meal history | None (shared public link) |

Managers use Django's built-in authentication. Members and the general public access the app via a shared link with no login required. The public views are explicitly designed and tested for this use case.

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- pip
- Virtual environment tool (`venv`)
- (Optional) Docker & Docker Compose for local PostgreSQL

### Local Development

```bash
# 1. Clone the repository
git clone <repository-url>
cd mess-management-system

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, DEBUG, etc.

# 5. Start local PostgreSQL (optional, if not using SQLite)
docker-compose up -d

# 6. Run database migrations
python manage.py migrate

# 7. Create a superuser account
python manage.py createsuperuser

# 8. (Optional) Seed the open cycle with sample members
python manage.py seed_members

# 9. Run the development server
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## Running Tests

```bash
python manage.py test
```

The test suite includes:
- **`tests/test_due_calculation.py`** — Verifies the due calculation formula with a worked example.
- **`tests/test_fixed_member_rate.py`** — Tests rate recalculation when the fixed member rate changes.
- **`tests/test_ui_fixes.py`** — Tests public/member navigation, empty states, and duplicate cycle-open prevention.

---

## Deployment

The application is configured for deployment on **Render**.

### Render Configuration

- **Web Service:** Gunicorn serving the Django app
- **Database:** Neon (PostgreSQL) — external, non-expiring free tier
- **Procfile:** `web: gunicorn config.wsgi --log-file -`
- **Release Command:** `python manage.py migrate --noinput && python manage.py collectstatic --noinput`

### Required Environment Variables (Render Dashboard)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Set to `False` in production |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | Trusted origins for CSRF (e.g. `https://mess-management-system.onrender.com`) |

---

## Configuration

The project uses `django-environ` for environment-based configuration. Key settings live in `config/settings.py` with dev and prod overrides in `config/dev.py` and `config/prod.py`.

| Setting | Default (dev) | Production |
|---|---|---|
| Database | SQLite (`db.sqlite3`) | PostgreSQL via `DATABASE_URL` |
| Debug | `True` | `False` |
| Static files | Django dev server | WhiteNoise |
| Allowed hosts | `*` | Restricted via env var |

A `config/context_processors.py` module injects `current_cycle` (the open monthly cycle) into every template context, so all pages can reference the active cycle without additional queries.

---

## Extending the Project

The codebase is organized around **domain-driven Django apps**. To add new functionality:

1. **New domain entity?** Create a new app under `apps/` following the existing pattern (models, views, urls, templates).
2. **New business logic?** Add it to the relevant app's `services.py` or `selectors.py` to keep views thin.
3. **New public page?** Add a view in `apps/dashboard/views.py` and register the URL in `apps/dashboard/urls.py`.
4. **New fixed bill type?** Add a new choice to the `FixedBill.bill_type` field in `apps/bills/models.py`.

Extensive specifications live in the `specs/` directory for deeper understanding of the system's design decisions, formulas, and UI patterns.

---

## License

This project is provided as-is for managing shared mess expenses.

---

*Built with Django, HTMX, and PostgreSQL. Deployed on Render.*
