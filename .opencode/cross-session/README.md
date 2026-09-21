# Cross-Session Bus — new session feature

File-based inbox so any OpenCode sessions sharing this folder can talk.

## Join as a new session

```powershell
python .opencode/cross-session/bus.py new-session --name left
python .opencode/cross-session/bus.py sessions --list
```

## Send / receive

```powershell
# left -> right
python .opencode/cross-session/bus.py send --from left --to right --msg "Part A done, your turn" --type task

# right checks
python .opencode/cross-session/bus.py inbox --for right --unread-only
python .opencode/cross-session/bus.py read --for right --id <id> --mark-read

# announce to all
python .opencode/cross-session/bus.py broadcast --from left --msg "merge ready"
```

## OpenCode wiring

- Agent: `.opencode/agent/cross-session.md` — `@cross-session relay this to right`
- Commands: `/xsend right <msg>`, `/xinbox <my-session>`
- Works from TUI, `opencode serve` sessions, and `parallel-dashboard` panes (same disk = same bus).

## New-session template

New sessions copy this intro into their first message:

> I am session `<name>`. I joined via `bus.py new-session --name <name>`.
> I check `bus.py inbox --for <name>` before starting work.
> I send updates via `bus.py send --from <name> --to <other>`.

## Limits

- Local only (same machine / shared folder). No network.
- Bodies are plain text, truncated to 500 chars in inbox preview — use `read` for full.
- Inbox files live in `inbox/*.jsonl` (gitignored via `inbox/.gitignore`, ephemeral).
- Concurrent `read --mark-read` + `send` can race (read-modify-write). For parallel-dashboard use: send freely, mark-read from one side at a time.
