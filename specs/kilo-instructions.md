# How to Brief Kilo CLI on This Project

## What to give it
Point Kilo at all six docs before it writes anything:
`requirements.md`, `schema.md`, `ui-spec.md`, `backend-spec.md`,
`project-structure.md`, `build-phases.md`.

## Suggested first message to Kilo
Something close to this, adjusted to Kilo's actual prompt conventions:

> Read requirements.md, schema.md, ui-spec.md, backend-spec.md,
> project-structure.md, and build-phases.md fully before writing any code.
> These documents are the complete source of truth for this project's
> features, data model, visual design, and backend rules. Do not invent
> features, validation rules, colors, layouts, or architectural choices that
> aren't in these docs. If something you need isn't covered, stop and ask me
> instead of assuming.
>
> Follow project-structure.md exactly for file/folder layout and
> build-phases.md for order of work. Complete one phase at a time, then stop
> and wait for my review before starting the next phase — do not continue to
> the next phase on your own even if the current one seems complete.
>
> Start with Phase 0.

## Ground rules to hold Kilo to throughout
- **One phase per session/approval.** Don't let it batch multiple phases
  into one giant diff — you lose the ability to catch a wrong turn early.
- **No silent scope changes.** If Kilo suggests a "better" approach mid-phase
  (different library, different folder layout, different validation
  behavior), that's a discussion to have with you first, not something to
  just do.
- **Ambiguity → question, not invented default**, except for genuinely
  trivial styling values not worth a round-trip (exact px on a minor
  border-radius, etc. — ui-spec.md already covers everything that matters).
- **Re-read the relevant doc section before each phase**, not just once at
  the start — details from backend-spec.md §4 (meal validation) matter most
  during Phase 2, ui-spec.md §3.5 matters most during Phase 4, etc.

## When you'll need to update the docs mid-build
A few things are explicitly deferred (requirements.md §5, backend-spec.md §9,
build-phases.md Phase 9) — the due/refund formula and bill-splitting logic.
When you're ready to supply that, write it up the same way these docs are
written (explicit rules + examples), rather than describing it conversationally
to Kilo directly — keeps the same "docs are the source of truth" discipline
for the trickiest part of the whole system.

## If something goes wrong mid-phase
Better to stop Kilo, fix or clarify the relevant .md file, and restart that
phase, than to patch the disagreement only in chat with Kilo — the docs
should stay the accurate record of what the system is supposed to do, not
just what happened to get typed into a terminal that day.
