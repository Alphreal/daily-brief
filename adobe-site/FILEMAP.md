# FILEMAP — read this instead of all files (token saver)

Agent rule: for any task, read this file first, then open ONLY the listed file(s). Never glob+read everything.

- `index.html` — MAIN. Page shell + all sections + IDs. Read when: structure, copy, IDs, wiring (`<link>`/`<script>`).
- `css/tokens.css` — variables + reset + focus. Read when: colors, fonts, global restyle. ~25 lines.
- `css/layout.css` — positions: header, hero grid, bento, split, footer, breakpoints. Read when: layout broken, responsive.
- `css/components.css` — skins: .btn, .card, .pill, .tool, details animation, blobs. Read when: button/card looks wrong.
- `js/app.js` — behavior: go()/step(), pills filter, bill(), filterTools(), reveal. All clicks/input delegate via `data-act`/`data-filter` (zero inline handlers). Read when: interaction broken.
- `docs/evidence/` — verification screenshots (browser captures). Never read for code tasks.
- `js/backend-mimic.js` — backend SHAPE: loads `data/merch.json` into `[data-merch]` slots (mimics MAS/AEM). Read when: prices/fragments.
- `data/merch.json` — mock MAS prices/CTAs per card. Edit prices here, never in HTML.
- `STRUCTURE.md` — naming + org core (kebab-case, one-axis, shared-rule). Read when: creating files.

## What is MAIN?
`index.html` + `css/tokens.css` + `js/app.js`. Change tokens once → whole site updates. Break index wiring → nothing loads.

## Known PROBLEMS (watch)
1. Carousel timer leak: `restart()` must clearInterval before set — else multiple timers after fast clicks.
2. Filter coupling: pills use `data-cat`, tools use `data-n` — renaming one without the other silently breaks filter.
3. CSS bleed: `.bcard p` gray also hits dark cards — override inline or scope `.big p`.
4. file:// vs http://: `js/app.js defer` works on both; ES `import` would break on file:// — kept global functions on purpose.
5. Cache: browsers cache .css/.js — bump query `?v=2` if edits don't show.
6. Glass cost: `backdrop-filter` is GPU-heavy — only header/mega/tabs/arrows/search use it. Never put blur on large cards or body. `@supports` fallback keeps old browsers solid.
7. Motion set (mimics Adobe): floating pill nav, tabs overlapping hero, mega fade+rise, stagger cascade via `data-stagger`+`--rd`, hero parallax (rAF, capped 120px), card-zoom hover. All transform/opacity, 150–400ms, `prefers-reduced-motion` kills parallax (CSS kills the rest).

## Future OPTIMIZE (do NOT build now)
- Images: replace gradient `.art` divs with sized webp + `loading="lazy"` + alt.
- Split `app.js` → carousel.js/filter.js/reveal.js only when >200 lines.
- Critical CSS inline, rest deferred; minify for ship.
- Add `CONSTRAINTS.md` (contrast 4.5:1, LCP <2.5s) before adding libs.
