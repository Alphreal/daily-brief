# skills-index.md - tiny index, this is what main agent loads instead of full memory
# Call skill-keeper subagent to fetch details only when trigger matches.
# AUTO-RULE: after every edit/write/bash, auto-call supervisor subagent. No user prompt needed.

- auto-supervise | trigger: always after file change | call supervisor, PASS or FIX, max 1 re-check

- briefing-style | trigger: brief, monday trending, coffee brief | see upgrades.md 2026-09-15
- (add more: trigger keywords + pointer)
