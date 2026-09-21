---
name: skill-improvement-development
description: Create new skills and improve skill system for reuse across projects. Use when creating a new skill, improving skill setup, promoting skill to global, or needing a skill template.
license: MIT
compatibility: opencode
---

# Skill Improvement and Development

General system for making skills better and making new skills that work in any project.

Use with `self-improve` (auto-supervise + DONE review) and `skill-keeper` (memory owner). Precedence: this skill overrides self-improve steps 2-4 for skill tasks; self-improve auto-supervise still applies.

## Where skills live

- Project-local: `.opencode/skills/<skill-name>/SKILL.md` — only this project.
- Project memory: `.opencode/memory/skills-index.md` (tiny index), `upgrades.md`, `mistakes.md`.
- Global (all projects): `~/.config/opencode/skills/<skill-name>/SKILL.md` = `C:\Users\ADMIN\.config\opencode\skills\<skill-name>\SKILL.md`.
- Project agents: `.opencode/agent/supervisor.md`, `skill-keeper.md`, `cross-session.md`.

Rule: build local first, prove on 1 real task, then promote to global or copy to next project.

## A) Improve an existing skill

1. Read `.opencode/memory/skills-index.md` only. If trigger matches, read that skill's `SKILL.md` + relevant `upgrades.md` section. Never load full memory.
2. Run supervisor review on last use: what broke, what was verbose, what tool was wasted. Return PASS or 1-3 concrete fixes with file:line.
3. Propose 1-3 rules in format `YYYY-MM-DD | trigger | rule | example`. Keep tiny, prune duplicates.
4. Only on user confirm (DONE review), call skill-keeper to append to `upgrades.md` / `mistakes.md` and update `skills-index.md`.
5. Never invent rules. If no evidence, say PASS.

## B) Create a new skill

1. Interview (max 4 questions): goal, trigger phrases, input/output, scope + out-of-scope.
2. Draft from template below. One skill = one job. Description must contain trigger keywords so opencode can auto-load it.
3. Validate: `name` matches folder, description has triggers, body < 80 lines, no project-specific paths except as examples.
4. Register: add one line to `.opencode/memory/skills-index.md`: `- <name> | trigger: <keywords> | see .opencode/skills/<name>/SKILL.md`.
5. Test on 1 real task before promoting.

Template for `.opencode/skills/<name>/SKILL.md`:

```md
---
name: <name>
description: What it does. Triggers on <keyword1>, <keyword2>, <keyword3>.
---

# <Title>

When to use + when NOT to use.

## Flow
1. Step with tool + file:line output.
2. Validate / supervisor check.
3. DONE handoff to skill-keeper.

## Template / Checklist
- Copy-paste block user can run.
```

## C) Reuse in many projects

Pick one per case (replace `<name>` / `<new-project>` before running):
- Same fix needed in 2+ projects → promote to global. PowerShell:
  `New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\opencode\skills\<name>" | Out-Null; Copy-Item -Recurse ".opencode\skills\<name>\*" "$env:USERPROFILE\.config\opencode\skills\<name>\" -Force`
- New project needs current system → copy starter kit:
  `New-Item -ItemType Directory -Force "<new-project>\.opencode" | Out-Null; Copy-Item -Recurse ".opencode\memory", ".opencode\skills\self-improve", ".opencode\skills\skill-improvement-development", ".opencode\agent" "<new-project>\.opencode\" -Force`
- One-off project quirk → keep project-local, do NOT promote.

After copy/promote: test with `skill <name>` load + 1 task, then DONE review.

## Don'ts

- No global edits without local proof.
- No memory bloat: index stays tiny, details in skill folder or upgrades.md section.
- No silent renames: old trigger stays in index for 1 week or breaks auto-load.
- No single-project domain rules in generic skills — keep examples generic, project details in memory only.
