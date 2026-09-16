---
description: Finish a project with supervisor review and save improvements to memory.
---

Run the DONE review from the self-improve skill:

1. Summarize what was built in 3 bullets.
2. Call supervisor subagent for self-critique (PASS or fixes).
3. Ask user: what worked? what was wrong? what to keep as rule? $ARGUMENTS
4. On confirm, call skill-keeper subagent to save to .opencode/memory/mistakes.md, upgrades.md, skills-index.md.

Keep it short. Do not invent rules without user confirmation.
