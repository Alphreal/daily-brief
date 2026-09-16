# Project: Daily Brief Website UI

## Overview
Stop reading brief inside Gmail. Same brief content as static public website, check regularly. Style like OpenCode light, attractive cards, keep all info.

## Architecture Decisions
- Decision 1: Static HTML alongside .md in same OUT_DIR, plus docs/ export for GitHub Pages (no backend, no DB)
- Decision 2: OpenCode light minimal (not dark glass example) - white/gray, single action box pattern, TL;DR on top, bento cards
- Decision 3: Stdlib only, Tailwind CDN with inline CSS fallback. Keep Gmail draft as backup.

## Implementation Phases
### Phase 1: Daily HTML
- Files: brief.py render_daily_html()
- Input: same feeds dict as render_daily_md (HackerNews/NASA/SciTechDaily, title/link/summary/takeaway)
- Status: Done 2026-09-16 (verified 18/18 titles in html, bottom line identical)

### Phase 2: Monday HTML
- Files: brief.py render_monday_html()
- Input: same weekly + new_hot as render_monday_md (repo/gained/total/desc/verdict/url)
- Status: Done 2026-09-16 (real fetch 10019 bytes, bottom line identical incl Star spikes)

### Phase 3: Index + Publish
- Files: brief.py render_index_html(), docs/ export, --no-html flag
- Output: brief-YYYY-MM-DD-daily.html, brief-YYYY-MM-DD-monday.html, index.html
- Status: Done 2026-09-16 (docs/ html-only, index rebuilt from docs dir, supervisor PASS)

## Scope
- In: 3 render functions, save alongside .md, docs/ copy for Pages, keep .md + Gmail
- Out: No change to RSS/trending fetch, no backend/auth/DB, no auto-deploy secrets

## Acceptance
- python brief.py --mode daily produces .md + .html identical info, double-click works
- index.html lists daily+monday, works locally + when docs/ pushed to Pages
- Gmail draft still works

## Risks
- Tailwind CDN offline -> inline CSS fallback, semantic HTML
- token.json leak -> only copy *.html to docs/, never token/credentials
- Public URL = public data only (brief is public RSS, safe)
