---
name: diagram-generate
description: Generate pictures, charts, and diagrams via code. Use when user asks for picture, diagram, chart, graph, flowchart, architecture sketch, or illustration.
license: MIT
compatibility: opencode
---

# Diagram Generate (no heavy AI model)

Stack verified 2026-09-17: `matplotlib 3.11.2` + `PIL 10.1.0` + Mermaid 11 + raw SVG. No GPU, no GB model download — smooth and offline-safe (SVG + PIL work fully offline; Mermaid CDN optional with text fallback).

## Pick method (chart chooser)

- Compare categories → bar (matplotlib). Trend over time → line (+markers). Parts of whole (≤5) → pie with patterns/hatch, else bar. Distribution → histogram. Flow/process/architecture/sequence → Mermaid (LR pipeline, TD hierarchy, <15 nodes per view; split if bigger).
- Crisp web icon/logo/simple illustration → raw SVG (no lib, `max-width:100%`, explicit `width/height`, `<title>` + text alternative). Matches website-build cards.
- Spot icons → `docs/assets/icons/*.svg` (29 Lucide, ISC, 24px stroke, use `stroke="currentColor"`); QR codes (e.g. feedback forms) → `qrcode` lib + PIL.
- Photo-like thumbnail/banner/edit/resize → PIL. Rounded cards `#f5f5f7` + hairline `#d2d2d7` to match website-build.

## Context first (from beauty-creative)

State Theme/Situation/Human in 1 line (e.g. guidebook bar for VN first-years on phones). This sets palette + density: print/B&W → patterns only; phone → big fonts ≥14px, few labels; formal → muted viridis/cividis.

## Flow

1. Ask type + data/labels + context (max 2 questions) unless given.
2. Generate to Temp, then quality check: `Read` PNG/SVG visually; title + axes labels present; fonts ≥14px body; contrast 4.5:1; legend uses shape/linestyle/pattern not color alone.
3. Copy final to `docs/` or `guidebook/` only on confirm; never overwrite originals.

## References (load only when needed)

- `references/mermaid-software.md` (228 lines, source: apexnova-dev/opencode) — class/sequence/ERD/C4/state/git/gantt details. Load for software architecture, DB schema, API flows.
- `references/matplotlib-deep.md` (366 lines, source: FrancoStino/opencode-skills-collection, risk:critical→ static Agg only) — subplots/mosaic/GridSpec, OO API, export PDF/SVG. Load for multi-panel or publication figures. Ignore its interactive/animation/GUI/3D sections.
- Note: refs are upstream excerpts — ignore their inner links to `references/*` / `scripts/*` (not installed here).

## Rules

- Mermaid: IDs unique, no reserved word `end`; quote labels with `()`/special chars; close all `subgraph…end`; direction LR pipeline / TD hierarchy.
- Matplotlib: `matplotlib.use('Agg')` first, one chart per file, no `plt.show()`; `style.use('tableau-colorblind10')`, colormap `viridis`/`cividis`, never `jet`; add markers + linestyles + hatch; describe series by shape ("dashed squares") not color alone (CTAO 2025).
- SVG: valid XML, `<title>`, text alternative nearby, no fixed pixel width in page CSS.
- No Stable Diffusion / torch download here — too heavy for scheduler box, breaks stdlib-only `brief.py`.
- Test files in `C:\Users\ADMIN\AppData\Local\Temp\opencode\`: `test-chart.png` (7108B) + `test-picture.png` (1884B) + `test-icon.svg` (317B) prove stack works.
