---
name: self-improve
description: Supervise current task after every edit, write, bash, and on DONE with review and mistake/upgrade memory. Use when supervising current work, not creating new skills.
license: MIT
compatibility: opencode
---

# Self-Improve

Always apply. No need for user to say supervise. Trigger on file changes + DONE.

## Flow
1. **Auto-supervise (no user call needed):** after every edit, write, or bash that changes files, main agent MUST auto-call `supervisor` subagent via Task tool with goal + diff + file:line list. Skip only for read-only answers. If PASS, continue. If FIX, apply fix then re-check once.
2. **DONE:** when user types `DONE` or `/done`, run:
   - call `supervisor` to summarize what was done + self-critique
   - ask user 3 questions: what worked? what was wrong? what to keep?
   - on user confirm, call `skill-keeper` to append to `.opencode/memory/mistakes.md` / `upgrades.md` and update `skills-index.md`
3. **Reuse:** on new task, read ONLY `.opencode/memory/skills-index.md` (tiny). If trigger matches, call `skill-keeper` to fetch the detail. Never load full memory. For skill creation/improvement tasks, load `skill-improvement-development` instead.
4. **Other projects:** copy `.opencode/memory/` + `.opencode/skills/self-improve/` + `.opencode/skills/skill-improvement-development/` to new project, or to `~/.config/opencode/skills/` for global use. See skill-improvement-development C) for copy commands.

Memory lives in `.opencode/memory/`, separate from chat history, so long context is not re-read each time.
