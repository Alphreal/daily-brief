# upgrades.md - confirmed improvement rules, read on demand only
# Format: YYYY-MM-DD | trigger | rule

# Example (delete when you have real entries):
# 2026-09-15 | python brief | stdlib only, no pip, write to Temp\opencode\brief-out
2026-09-16 | ui build | keep UX smooth and connected; auto-chain multi-step flows instead of manual button-hopping
2026-09-16 | ui build | one action box with full features; never two boxes for same action with fewer features — check duplicates and missing features before shipping
2026-09-16 | code | simplest code possible; match OpenCode UI simplicity
2026-09-16 | planning | use plan mode when 3+ files or contract/schema/auth change or unfamiliar code / unclear cause; skip for 1-sentence change
2026-09-16 | planning | plan format: Context found / Questions (2-4) / Steps (Goal, Scope, Out-of-scope, Done-when) / Risks+mitigations; read-only until approved
2026-09-16 | planning | save complex plans to PLANS.md or spec/ or tasks.md; update when requirements change; implement only after approval
2026-09-16 | website/responsive UI | verify layout on desktop fullscreen AND phone widths before calling UI done; phone-fit alone is not enough, wide screens must not feel empty (constrain max-width / multi-column bento) | say: "Phone-fit isn't enough — check wide desktop too so it doesn't feel empty." e.g. 1920px + 390px
2026-09-16 | website/project delivery | always ask whether site/project needs auto-update or scheduled process (Pages push, scheduler, cron) before finishing; don't leave manual-only publish by default | say: "Want this to update itself, or is manual publish OK?" e.g. Pages push / cron
2026-09-16 | website UI text | cut unneeded explanatory text; repurpose leftover lines as descriptions, keep headlines clean (headline-as-link acceptable if rest is clean) | say: "Cut extra words — reuse leftovers as descriptions, keep headlines clean." e.g. headline-as-link OK
2026-09-17 | ui build | one primary action per screen; secondary actions lighter or after primary done (Joshua Porter)
2026-09-17 | ui build | TL;DR first, details via progressive disclosure (accordion/load-more); never dump all content at once
2026-09-17 | cards | one card answers one question; identical padding via 4/8pt grid, same CTA spot every card, title 20-28px, body >=14px, gutter >=12px
2026-09-17 | layout | F-pattern: most important top-left with biggest contrast/area; whitespace lifts comprehension ~20%
2026-09-17 | ui audit | end-of-build audit: ask "can I remove this?" per element; extra info competes with relevant info (Nielsen)
2026-09-17 | feedback | every action shows status + natural next step; errors in plain language with a fix, never codes alone
2026-09-17 | consistency | same behavior looks same, different looks different; reuse patterns across cards/screens
2026-09-17 | apple palette | canvas #ffffff/#f5f5f7, text #1d1d1f, ONE accent #0071e3 for actions/links only, hairlines #d2d2d7 [optional style]
2026-09-17 | apple type | system stack (-apple-system/Segoe UI/Roboto); display 40-56px/600, body 17px/400 with -0.016em tracking; small 12px; max semibold 600 for names [optional style]
2026-09-17 | apple spacing | 4px base [4,8,12,16,20,24,32,48,128]; card padding 24px, grid gutter 20-24px, section gap 64-128px, 64px air above headline [optional style]
2026-09-17 | apple shape | flat chrome, no shadows/gradients; radius 8-11px cards, 980px pills for buttons/tags; hairline borders only [optional style]
2026-09-17 | apple rhythm | full-width stacked hero (headline/tagline/1-2 CTAs) then alternate white and #f5f5f7 sections; max-width 980px dense, 1440px grids [optional style]
2026-09-17 | apple chunk | split long text into whitespace-separated blocks; alternate vertical/horizontal arrangement for balance; boring stuff (footers/meta) aligned at bottom [optional style]
2026-09-17 | grid | 12-col backbone: 4-col mobile, 8-col tablet, 12-col desktop; everything snaps to invisible guides or it reads as chaos
2026-09-17 | scan | F-pattern for text-heavy (headlines+CTA top/left), Z-pattern for sparse goal pages (logo top-left, CTA bottom-right), Gutenberg: primary top-left, terminal action bottom-right
2026-09-17 | bento | one card dominates or grid becomes noise; consistent padding/radii is what keeps bento from chaos
2026-09-17 | responsive | mobile-first, min-width breakpoints from content (where it breaks), not devices; NN/G start: 500/1200/1400; viewport meta + max-width:100% images
2026-09-17 | nav | show navigation if it fits (no hamburger on desktop); sticky top bar, collapse under hamburger on small, mirror links in footer
2026-09-17 | hero | first viewport = ONE idea (headline/sub/1 CTA); goal is not everything above the fold
2026-09-17 | match | match layout to page goal: SaaS explain+convert = hero-then-bento; single CTA = Z; dense browse = grid; story = magazine alternate sizes
2026-09-17 | shell | every page same order: header (logo+name) / nav (structure links) / main (text+media) / footer (copyright+contact)
2026-09-17 | shell | footer repeats nav links + contact info; nav labels mirror actual site structure
2026-09-17 | goals | judge every layout on 4: readability (hierarchy+spacing), usability (intuitive nav), engagement (visuals+CTA placement), conversions (guide to action)
2026-09-17 | precedence | universal core + simplicity are mandatory every UI build; Apple/named styles are optional variants to choose from
2026-09-17 | deliverable | ask deliverable format FIRST (Google Docs vs website vs other); never assume a website
2026-09-17 | interactivity | interactivity must add new value (schedules/marks/tools); never re-quiz existing content
2026-09-17 | TOC | TOC lists main chapters only; sub-items visually distinct
2026-09-17 | flow cycle | 4 stages: struggle (unpleasant loading, required) / release (mind off problem, walk/breathe, never TV) / flow / recovery (low, needs sleep+sunlight+nutrients; master struggle+recovery to get flow)
2026-09-17 | flow study | challenge ~4% above skill (flow channel); anxious = build skill or lower challenge; bored = raise challenge; both high = flow
2026-09-17 | flow triggers | clear immediate goal + instant feedback loop + no interruptions; phone out of room, 1 tab, notifications off
2026-09-17 | flow team | group flow needs familiarity (shared language), blended egos (no spotlight hog), control (choose own challenges), yes-and listening
2026-09-17 | flow measure | Flow Short Scale (Rheinberg): fluency + absorption; flow predicts performance mainly when activity feels important (achievement motive moderates)
