# STRUCTURE — the core of how pros name + organize (distilled from 2026 sources)

## 1. Names are API
- Web files: `kebab-case` — `tokens.css`, `backend-mimic.js`, `hero-image.webp`. Survives URLs, shells, all OSes.
- File = primary export: `carousel.js` exports carousel, not `helpers.js` with 15 things.
- Role not method: `price-loader.js` not `fetch-wrapper.js`. Never `utils-2.js`, never `final-v2`.
- Tests mirror source: `app.js` → `app.test.js`, side by side.

## 2. One axis per level (golden rule)
- Small (<50 files): layer axis OK — `css/`, `js/`, `data/`, `assets/` (what we use here).
- Large: feature axis — `features/auth/`, `features/checkout/`, each with own api/ui/types. Never mix `components/` + `features/` + `domain/` at the same level.
- `shared/` = only code used by 2+ features. Used once? Lives in the feature.

## 3. Boundaries
- One `index` per feature = public API. Others import the barrel, never deep internals.
- Depth ≤ 4 from root. Deeper = split the feature.
- Root is signage: `README`, manifest, config only. Scripts → `scripts/`, docs → `docs/`, output (`dist/`) gitignored always.

## 4. How pros USE files
- Colocation: files that change together live together (card + its test + its style).
- Thin routes: page = composition glue; logic lives in feature/lib.
- Transport split: one boring HTTP client in `shared/api`, endpoints live in each feature.
- Enforce with lint/aliases (`#/` imports), not tribal knowledge. Document in 15 lines (this file + FILEMAP).
