# Project Structure — Django + HTMX + Neon (Postgres) + Render

Stack locked in: **Django + HTMX**, DB on **Neon**, hosted on **Render**.

Django apps are split by domain so each maps cleanly to a table group from
schema.md. `dashboard` is the only app members ever touch (public, read-only).
Everything else lives behind the manager login, largely via Django admin.

```
mess-manager/
├── manage.py
├── requirements.txt
├── runtime.txt                  # python version pin, e.g. python-3.12.x
├── Procfile                     # for Render: web: gunicorn config.wsgi
├── render.yaml                  # optional: infra-as-code for Render deploy
├── .env.example                 # DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS
├── .gitignore
│
├── config/                      # Django project package (settings/urls root)
│   ├── __init__.py
│   ├── settings.py               # or settings/ split into base.py, prod.py, dev.py
│   ├── urls.py                   # root urlconf, includes each app's urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── cycles/                   # monthly cycle open/close logic
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py             # Cycle
│   │   ├── admin.py
│   │   ├── migrations/
│   │   └── services.py           # close_month(), open_new_cycle() — logic hooks
│   │
│   ├── members/                  # Member, MemberCycle (join/leave, deposit)
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py              # Member, MemberCycle
│   │   ├── admin.py               # manager CRUD via Django admin
│   │   ├── migrations/
│   │   └── forms.py               # add/edit member forms (if not pure admin)
│   │
│   ├── meals/                    # daily breakfast/lunch/dinner entries
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py               # MealEntry
│   │   ├── admin.py
│   │   ├── views.py                # manager entry grid (HTMX partial updates)
│   │   ├── urls.py
│   │   ├── selectors.py            # daily_meal_counts(), breakfast doubling logic
│   │   ├── migrations/
│   │   └── templates/meals/
│   │       ├── entry_grid.html       # full page: table of members x days
│   │       └── partials/
│   │           └── meal_cell.html    # single editable cell, swapped via HTMX
│   │
│   ├── groceries/                # grocery_bills, grocery_bill_items, extra_grocery
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py               # GroceryBill, GroceryBillItem, ExtraGrocery
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── migrations/
│   │   └── templates/groceries/
│   │       ├── bill_list.html
│   │       ├── bill_form.html
│   │       └── extra_list.html
│   │
│   ├── bills/                    # fixed bills: rice/electricity/chef/wifi/other
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py               # FixedBill
│   │   ├── admin.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── migrations/
│   │   └── templates/bills/
│   │       └── bill_list.html
│   │
│   └── dashboard/                # PUBLIC read-only views — this is what members see
│       ├── __init__.py
│       ├── apps.py
│       ├── views.py               # no login required, read-only querysets only
│       ├── urls.py
│       ├── migrations/            # (likely empty, no models of its own)
│       └── templates/dashboard/
│           ├── home.html            # main mess page: members table + today's counts
│           ├── month_summary.html   # per-member due/refund (once formula exists)
│           └── partials/
│               └── today_counts.html # HTMX-refreshable "today's meal totals" widget
│
├── templates/                    # shared/global templates
│   ├── base.html                  # base layout, nav differs for manager vs public
│   ├── base_manager.html          # extends base.html, adds manager nav + login-required
│   ├── base_public.html           # extends base.html, public nav, no write controls
│   └── registration/
│       └── login.html             # manager login page (Django auth)
│
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       └── htmx.min.js            # or loaded via CDN in base.html
│
└── tests/
    ├── test_meals.py               # breakfast doubling, proration edge cases
    ├── test_cycles.py              # month close-out behavior
    └── test_dashboard.py           # public view returns read-only, no write routes
```

## Notes on structure decisions

- **`apps/` folder** groups all Django apps together instead of scattering
  them at project root — keeps `config/` (settings) visually separate from
  domain code.
- **`selectors.py` / `services.py` pattern** (seen in `meals/` and `cycles/`):
  keeps calculation logic (breakfast doubling, month-close, future
  due-formula) out of models and views, so it's easy to swap/extend once you
  supply the actual meal-rate formula — matches the "pluggable calculation
  layer" decision from requirements.md.
- **`dashboard` app has no write views at all** — this is the enforcement
  point for "members are read-only." If a route isn't in `dashboard/urls.py`,
  a member never sees it.
- **Django admin is the primary manager CRUD surface** for `members`,
  `groceries`, `bills` — customized via each app's `admin.py`
  (`list_display`, `list_filter`, inline editing for `GroceryBillItem`).
  `meals/views.py` gets a custom HTMX grid instead of plain admin, since
  entering 30+ members × 3 meals daily is painful in default Django admin
  list-edit — a dedicated grid view is worth the extra code there.

## Deployment file notes

- **`Procfile`**: `web: gunicorn config.wsgi --log-file -`
- **`render.yaml`**: defines the web service + env vars (`DATABASE_URL`
  pointing to your Neon connection string, `SECRET_KEY`, `DEBUG=False`)
- **`.env.example`**: documents required env vars without committing secrets
  — actual `.env` stays gitignored, Render env vars set via its dashboard

## Suggested build order
1. `config/` + `cycles` + `members` (get auth + base models running)
2. `meals` (core daily entry grid + breakfast doubling logic)
3. `dashboard` home page (public view, read-only)
4. `groceries` + `bills`
5. Month-close flow in `cycles/services.py` (once you supply the formula)
6. `dashboard/month_summary.html`
