---
name: website-build
description: Build and publish simple static websites with clean UI and auto-update. Use when building website UI, cards, layout, responsive pages, or publishing via docs and scheduler.
license: MIT
compatibility: opencode
---

# Website Build (merged: ui-simplicity + website-delivery + 2026 a11y/perf)

One flow: Build → Check → Deliver. Replaces separate ui-simplicity + website-delivery lookups.

## Build (mandatory core)

- Simplest code, OpenCode light minimal. One primary action per screen, one action box (never two for same action).
- TL;DR first, details via disclosure (accordion/load-more). One card = one question; same padding/CTA spot; title 20-28px, body >=14px, gutter >=12px.
- Semantic shell every page: `<header>/<nav>/<main>/<footer>`, one H1, `<meta name=description>`, footer repeats nav + contact.
- F-pattern for text-heavy, Z for single-CTA. Max-width 980px dense / 1440px grids; whitespace separates blocks.

## Check (before done)

- Desktop 1920px AND phone 390px — wide must not feel empty (bento: one card dominates).
- Contrast 4.5:1 text / 3:1 large; keyboard tab order + `:focus-visible`; images sized + alt (no keyword stuffing); LCP target <2.5s, no heavy CDN as single point of failure.
- Audit per element: "can I remove this?" Errors in plain language with a fix + next step.

## Deliver

- Ask once: "Want this to update itself, or is manual publish OK?" If auto: docs/ export (html only, never token/credentials) + push + scheduler/cron.
- Static/build-time render default; test double-click locally + Pages URL.

## Optional style (pick one, never mix)

- Apple variant only if asked: canvas #ffffff/#f5f5f7, text #1d1d1f, ONE accent #0071e3, hairlines only, radius 8-11px, system stack. See upgrades.md 2026-09-17 apple-* for values.

## Don'ts

- No Tailwind-only layout (keep inline CSS fallback). No overlay-widget accessibility shortcuts. No manual-only publish by default.
