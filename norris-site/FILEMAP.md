# FILEMAP — read this instead of all files (token saver)

Agent rule: read this first, then open ONLY the listed file(s).

- `index.html` — MAIN shell + all sections. Structure/copy/IDs.
- `css/tokens.css` — LN4 theme (paper/papaya/lime). Colors/fonts.
- `css/layout.css` — topbar, hero, bands, grids, footer, breakpoints.
- `css/components.css` — buttons, cards, helmet hover-swap, marquee items.
- `js/app.js` — reveal, countdown, drawer, count-up stats.
- `data/race.json` — next GP + lights-out UTC. Update after each race.
- `assets/ln4-loader.riv` — REAL Rive animation, authored as text in `scene.rml` (see Temp/ln4-loader), compiled with the Rive CLI. Player: `vendor/rive/` (vendored runtime + wasm, no CDN).- `assets/` photos (hero + gallery) CC-licensed, credited in footer.
- `docs/evidence/` — reference screenshots. Never read for code tasks.

## Note (original-assets rule)
All art is CSS gradients. No hotlinked photos, no copied copy — structure and vibe only.
