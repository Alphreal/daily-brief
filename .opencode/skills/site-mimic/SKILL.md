---
name: site-mimic
description: Mimic a real website's layout and vibe for learning. Triggers on mimic website, clone homepage, recreate site, copy the vibe, learn from real site.
license: MIT
compatibility: opencode
---

# Site Mimic (learn-by-rebuilding, closest-legal)

Rebuild a real site's structure + feel with original assets and copy. Never hotlink or reproduce their images, text, or logos verbatim.

## Flow (one slice at a time, verify each)

1. Observe: browser `observe` + screenshots at desktop and 375px mobile + console check. Inventory: nav pattern, hero, cards, motion, backend shape (APIs, fragments, personalization).
2. Scaffold: `index.html` + `css/tokens.css|layout.css|components.css` + `js/app.js` + `data/*.json` + `FILEMAP.md` (token map: read map first, then only the file each task names).
3. Mimic order: structure → glass → motion → merch-backend (`data-*` slots filled from JSON, fallback text inline for offline).
4. Motion budget: transform/opacity only, 150–400ms, stagger via `--rd` custom property, parallax rAF-throttled and capped, `prefers-reduced-motion` off-switch, `@supports` fallback for `backdrop-filter`.
5. Harden: exactly one `h1`, aria state synced in every state function, zero inline handlers (delegate via `data-act`), breakpoints at 1020px and 640px, assert `scrollWidth == innerWidth` at 375px with JS evaluate (don't eyeball widths).
6. Evidence: verification screenshots go to `docs/evidence/`, never repo root. Serve over localhost, confirm 200s + clean console, then open.

## Don'ts

- No pixel-exact copy of copyrighted assets or copy. No new library for what ~15 lines do. No blur on large surfaces (GPU cost). No morphology claims without measurement. No full-folder reads when FILEMAP answers it.
