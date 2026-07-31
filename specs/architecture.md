# Architecture & Deployment (Draft — stack to be finalized separately)

This is a starting point for the stack conversation, not a final decision.

## Deployment targets (confirmed)
- **App hosting:** Render (free web service tier)
- **Database:** NOT Render's free Postgres (auto-deletes after 30 days —
  unacceptable for financial/meal records). Use a provider with a
  non-expiring free tier instead — leading candidates: **Supabase** or
  **Neon** (both Postgres-compatible, both have durable free tiers).
- **Coding tool:** Kilo CLI

## Known constraints from Render's free tier
- Free web services spin down after ~15 min of inactivity; first request
  after idle takes ~30–60s to wake up
- 750 free instance-hours/month per workspace (plenty for a single small app)
- No persistent disk on free web services — confirms the DB must be external
  (Supabase/Neon), not local SQLite on the Render instance itself

## Access model (confirmed)
- Manager: authenticated (username/password) session, full read/write
- Members: unauthenticated, read-only view via a shared link (no per-member
  accounts)

## Open questions for next discussion
- Backend language/framework (e.g. Node/Express, Python/FastAPI, Django,
  etc.) — should match what Kilo CLI works best with and your comfort level
- Frontend approach — server-rendered pages vs. a separate frontend (React/
  Vue) calling an API
- ORM/query layer for Postgres (e.g. Prisma, Drizzle, SQLAlchemy)
- Whether the "shared link" for members needs a passcode or is fully public
- Exact meal-rate/bill-splitting formula (affects whether calculations run
  in the backend at close-out, or are computed live on each page load)

This document will be superseded once the stack and project structure are
finalized in the next step.
