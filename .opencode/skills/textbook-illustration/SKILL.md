---
name: textbook-illustration
description: Step-by-step textbook diagrams that teach, not decorate. Use when illustrating study guides, routines, or processes where the picture must show HOW in ordered steps at balanced scale.
license: MIT
compatibility: opencode
---

# Textbook Illustration (steps teach, decoration doesn't)

Complements `diagram-generate` (methods: matplotlib/PIL/Mermaid/SVG) + `beauty-creative` (judgment). This owns the step-by-step standard.

## Panel grammar (numbered steps, not scenes)

- One action per panel, max 4 panels, ordered left→right (phone: stack vertically, numbers preserved).
- Number badges 1-2-3-4 + 3–6 word caption per panel. If a panel needs a paragraph, it is two panels.
- Before/after pairs (phone in drawer vs on desk) count as steps 1→2, never side-by-side without order.
- Text inside figures is labels only (≤5 words); explanation lives in the caption/body.

## Scale vs text (the balance rule)

- Figure width ≤60% of column on desktop (float or constrained), full-width on phone.
- If the figure is taller than the paragraph it explains, split it or cut panels.
- Caption always: what to notice, not what it is ("Notice the phone stays shut away" beats "A phone in a drawer").
- Never upscale small SVGs past authored size (blur); author at 2x, display at 1x.

## Effort checklist (childish = inconsistent)

- One stroke width for all outlines in a figure; one corner radius; palette ≤4 (site bg + ink + accent + muted).
- Human figures: same proportions across panels (head = fixed unit), simple geometric bodies, no clip-art hands.
- Arrows always labeled (50 cm, next, 25 min). Unlabeled arrows are decoration — delete them.
- White breathing room ≥15% of viewBox; align elements to a grid, center optically.
- Title per figure (`<title>` + nearby text alternative); body text ≥14px equivalent.

## Method pick (from diagram-generate stack)

- Data with real numbers → matplotlib Agg (`tableau-colorblind10`, hatch + labels, never color-alone), export SVG/PNG.
- Ordered process/scene → raw SVG panels (this skill's grammar above).
- Photo-like scene → PIL composite, never AI-generated faces for class materials.
- Flow/architecture → Mermaid (<15 nodes/view).

## Don'ts

- No text-only "illustrations" (a labeled box is a caption, not a picture). No fake data in charts (unmapped slots stay honest placeholders). No effort-free single-shape figures. No faces/names of real students.
