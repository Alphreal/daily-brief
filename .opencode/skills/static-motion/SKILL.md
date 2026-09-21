---
name: static-motion
description: CSS/JS motion for static sites (hand CSS first, vendored libs allowed). Use when adding animation, transitions, hover/click feedback, scroll reveal, animated details, or smoothness to any static page.
license: MIT
compatibility: opencode
---

# Static Motion (offline-safe; hand CSS first, vendored libs allowed)

Complements `website-build` (structure) + `beauty-creative` (judgment). Prefer hand CSS + tiny vanilla JS; locally-vendored motion libs (e.g. AOS in `docs/assets/vendor`) allowed for scroll reveal. No motion/animation CDN dependency (Tailwind CDN for layout is separate, has inline fallback), print-safe.

## Principles

- Purposeful only: every animation answers "what changed / where am I". Decorative loops need user opt-in.
- 150–300ms, ease-out. Nothing linear except progress fills.
- Animate transform/opacity only (no layout thrash). Never animate width/height/margin.
- Kill-switch first: `@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important}}`.
- Print: freeze final states; open all `details` via `beforeprint`, restore via `afterprint`.

## Patterns (copy, don't invent)

- Smooth `details/summary`: wrapper `display:grid;grid-template-rows:0fr;transition:grid-template-rows .25s ease-out` → `[open]` gives `1fr`; inner `overflow:hidden`. (Height animation without JS.)
- Hover lift: `transition:transform .15s,box-shadow .15s` → `:hover{transform:translateY(-2px)}`. Cards/chips/buttons only.
- Active press: `:active{transform:scale(.98)}` on buttons.
- Scroll reveal: `IntersectionObserver`, one-shot, `opacity:0;translateY(12px)` → visible. Skip if <10 blocks.
- Progress/bar fill: animate `width` only for true progress (allowed exception), or SVG rect grow via CSS `transform:scaleX` with `transform-origin:left`.
- Chart hover: SVG `<title>` child (native tooltip, zero JS) + `:hover` opacity on bar group.
- Focus: `:focus-visible{outline:2px solid accent;outline-offset:2px}` on every interactive element.
- Sticky nav shadow: add shadow class when `scrollY>4` (one listener).

## Don'ts

- No motion/animation CDN (vendor motion libs locally so file:// + offline still work). Vendored libs must match spec: 150-300ms, transform/opacity only, reduced-motion off-switch, content visible if JS fails. No infinite motion by default. No motion that blocks input (`pointer-events` intact). No parallax on text-heavy study pages (vestibular risk + phone jank).
