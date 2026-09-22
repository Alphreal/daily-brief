# Constraints

Last reviewed: 2026-09-22

## Floor (always enforced, no setup required)

- No new suppression comments: `# noqa`, `# type: ignore`, `eslint-disable`, `biome-ignore`
- No unimplemented stubs: `throw new Error("Not implemented")`, empty `catch {}`, `pass  # stub`
- No skipped or deleted tests without a reason in the commit message
- No secrets in source (`credentials.json`, `token.json` never committed/copied to `docs/`)
- This file does not get weakened to make a change pass

## Enforced with numbers — file length (clean code)

| Ext | Optimal | Warn | Block | Checked by | Runs at |
|-----|---------|------|-------|------------|---------|
| `.py` `.html` `.js` `.css` | ≤300 lines | >300 split soon | >500 must split | `python check_lengths.py` | every edit, task end |
| `.json` `.md` | n/a | — | — | excluded | — |
| Python lint | Zero `ruff check` errors (E,F,B,I; E501 off — layout is the formatter's job) | `ruff check .` | every edit, pre-commit |
| Python format | Zero `ruff format --check` diffs | `ruff format .` | pre-commit |
| Whitespace | No trailing space, files end with newline (vendor + `.opencode/` excluded) | pre-commit hooks | every commit |

Why: ESLint `max-lines` default 300 (range 100-500), Biome `noExcessiveLinesPerFile` default 300, Oracle Java `>2000 cumbersome`, Uncle Bob FitNesse avg 77 / max 498. 300 warn / 500 block is met by this repo except warn-listed files (see Exceptions).
Rule: 1 file = 1 responsibility. Split by function, never `part1/part2`. Total lines (`wc -l`), blanks included — simplest count that can't be gamed.

## Measured, not yet enforced

| Metric | Today | Direction |
|--------|-------|-----------|
| Max code file | 452 (`tiktok_github_v2.py`) | must not grow |
| Files >300 | 7 warns, 0 fail (`python check_lengths.py`) | must not grow |

## Exceptions (grandfathered, split on next touch)

| ID | Rule | Path | Reason | Owner | Expires |
|----|------|------|--------|-------|---------|
| W1 | warn-300 | `adobe-clone.html` (424) | single-file prototype | @admin | 2026-12-22 |
| W2 | warn-300 | `tiktok_github_v2.py` (452) | shared base lib for v3/v4/mimic, split risks 3 importers | @admin | 2026-12-22 |
| W3 | warn-300 | `zoom_fatigue.py` (425) | one-off generator | @admin | 2026-12-22 |
| W4 | warn-300 | `brief.py` (355) | `ruff format` vertical style vs data-heavy scheduler; split again on next touch | @admin | 2026-12-22 |
| W5 | warn-300 | `brief_render.py` (350) | template-heavy render module | @admin | 2026-12-22 |
| W6 | warn-300 | `mimic_retainpdf.py` (418) | SCENES data + video pipeline; formatter-inflated | @admin | 2026-12-22 |
| W7 | warn-300 | `mimic_draw.py` (417) | draw primitives, formatter-inflated | @admin | 2026-12-22 |

Resolved 2026-09-22: `brief.py` 518 → `brief.py` 295 + `brief_render.py` 229; `mimic_retainpdf.py` 573 → 279 + `mimic_draw.py` 279 (also fixed missing `pill` def, dropped unused `gradient_text` + dead Tahoma font block).
