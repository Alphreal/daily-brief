---
name: browser-skill
description: |
  Use when the user asks to automate their logged-in Chromium browser: visit
  and read pages, fill forms, scrape data, click through flows, regression-test
  a PR's UI, validate a deployed page, or operate a tab they identify. Requires
  the bsk CLI and browser extension.
---

# browser-skill

Use `bsk` to work in an **Agent Window** with the user's existing logins. User tabs
require explicit borrowing. This skill does not install the extension or handle
advice-only tasks. Never extract credentials, cookies, tokens, or other secrets.

## Before starting a session

For remote setup or pairing, follow the [remote guide](https://github.com/Tencent/BrowserSkill/blob/main/docs/remote-extension-connection.md).

Local commands normally auto-start the daemon. If the host terminates background
children after each shell call, including on Windows, complete these steps first:

1. Reuse the host daemon's existing `BSK_HOME` (or its default if unset). Set
   `BSK_AUTO_START=0` and run `bsk status --json`. Reuse a working daemon; an empty
   `browsers` list means the extension still needs connecting. Permission errors,
   timeouts or invalid replies do not prove the daemon is absent.
2. Only if the check reports a missing daemon and no host task is already starting
   it, run `bsk daemon start --foreground` with the same `BSK_HOME` in the host's
   approved persistent background task outside the per-command sandbox. Keep that
   task alive; `--foreground` alone cannot prevent host cleanup. The
   [sandbox guide](https://github.com/Tencent/BrowserSkill/blob/main/docs/sandboxed-agents.md)
   covers the normal host-terminal alternative and PowerShell examples.
3. After launching, or if a host task is already starting the daemon, run
   `bsk status --json` in a **separate shell tool call** with the same `BSK_HOME`
   and `BSK_AUTO_START=0`. While startup is pending, make at most five
   checks with one-second pauses for missing-endpoint or transient startup errors;
   stop on permission/protocol errors. Proceed only after a successful status
   response. If the host task exits (including a lock error) or readiness never
   succeeds, inspect its output and `bsk logs`, then recheck status for another
   daemon before deciding whether startup is still needed. Report unresolved
   errors; do not loop on launches, delete runtime files or restart a shared daemon.

Use the same `BSK_HOME` and `BSK_AUTO_START=0` on EVERY sandboxed command;
environment settings may not persist between shell calls. Keep browser commands
sandboxed. For other startup failures, retry once, then use `bsk doctor`.
A local process identity warning permits browser commands when IPC works.

## Task workflow

1. Define success from the user's request. Start `bsk session start --json` and
   retain its `session_id`. With multiple browsers, run `bsk browsers` and add
   `--browser <id-or-label>` to start. For background work, add `--no-focus` to
   `session start` only.
2. For a new page, navigate; for an existing user tab, follow **Borrowing** below.
   Read the page before interacting:

   ```sh
   bsk navigate https://example.com --session <id>
   bsk observe --session <id>
   ```

3. Choose an action using fresh refs from that observation. Observe again after
   navigation or meaningful DOM changes. Check an ambiguous result once; once
   success is visible, stop acting rather than refreshing or checking again.
4. Always run `bsk session stop <id>` on success and failure, unless keeping the
   session open is part of the user's request. This also returns borrowed tabs.
   Returned tabs stay open in the user's window. Do not rely on idle cleanup
   or stop/restart the shared daemon to finish a task.

Replace `<id>`, example refs and values with actual results and task inputs.
Every session-scoped command needs `--session <id>`; `session stop` takes the ID
positionally. For unfamiliar commands or flags, consult `bsk --help` or
`bsk <command...> --help` instead of guessing; no need to read all help at startup.
When following a trace, use its semantic targets and values in order, not its old
refs. Stop at the requested goal; a trace grants no additional authorization.

## Read and interact

Prefer `observe` for text, controls and `@eN` refs. Navigation invalidates refs;
large DOM changes can stale them too. Re-observe before the next interaction.
Use refs for iframe/shadow-root targets; CSS selectors search the main document.

Choose the relevant example, using a ref that actually appeared on the page:

| Need | Command |
| --- | --- |
| Click | `bsk click @e3 --session <id>` |
| Fill a field | `bsk fill @e3 --value "text" --session <id>` |
| Select an option | `bsk select @e3 --value "option-value" --session <id>` |
| Press a key | `bsk press Enter --ref @e3 --session <id>` |
| Reveal a hover menu | `bsk hover @e3 --session <id>` |
| Reveal an element | `bsk scroll-to @e3 --session <id>` |
| Scroll with wheel input | `bsk wheel --delta-y 600 --session <id>` |
| Focus or leave a field | `bsk focus @e3 --session <id>` / `bsk blur @e3 --session <id>` |

- `select` uses the option's value, not its visible label.
- Hover markers such as `[hover first: Shoes | Bags]`, `[has-submenu]`, or
  `[expanded]` identify triggers. Hover the trigger, observe, then use the revealed
  item's ref. Listed labels are not refs; do not click the trigger unless its own
  action is wanted. If an expected control is missing and no marker identifies a
  trigger, try `observe --probe-hover` once. It touches the live page and costs
  seconds; use targeted hover once the trigger is known.
- `scroll-to` returns ancestor-clipped bounds in top-level viewport CSS pixels.
  Partial visibility suffices; hidden/fully clipped targets fail. It does not test
  occlusion. `wheel` sends signed deltas (at least one nonzero), not a guaranteed
  scroll distance. An optional target is scrolled into view first; without one,
  input lands at the viewport centre. Observe to check the page's response.

Use `snapshot` for a static accessibility tree, `get-html` for exact markup or
hidden metadata, and `screenshot` for visual content or requested visual evidence.
Do not start with HTML/images just to find ordinary controls; obtain fresh refs
before interacting with controls found that way.

### Large observations

There is no default token cap. With `observe --max-tokens <n>`, follow a returned
`next_cursor`/`@more` when relevant content remains:

```sh
bsk observe --cursor <token> --session <id>
```

Each page replaces the ref map: use its refs before continuing and never reuse
refs from earlier pages. Continuation reads the same capture, without refreshing
or hovering; do not combine it with depth changes or hover probing. New observe/
snapshot or changed page identity invalidates continuation; then observe afresh.

## Borrowing and browser settings

List before borrowing, and return the tab as soon as the relevant step ends:

```sh
bsk tab list --scope user --session <id>
bsk tab borrow <tab-id> --session <id>
bsk tab return <tab-id> --session <id>
```

Borrowing selects the borrowed tab within the Agent Window, preserving the default
for subsequent commands without `--tab-id`. It does not additionally focus the
window. For a background-created tab (`tab create --no-active`), retain the returned
`tab_id` and pass `--tab-id <tab-id>` to observation, navigation and input commands.
Created and borrowed web pages continue running while controlled even after they
move into the background. A default created tab starts at `about:blank`.
Viewport and full-page screenshots of controlled tabs work in the background;
pass `--tab-id` without selecting the target or focusing the window. Prefer
semantic observation first and take a screenshot when the task needs image content.
A viewport screenshot does not issue a Canvas `capture_id`; use the existing
`--ref` flow for screenshot-bound Canvas clicks.

Never invent tab IDs or keep a user tab across unrelated work. Do not repeat
pending, denied or timed-out borrows. For `borrow_outcome_unknown`, inspect tab/
session state first: the tab may already have moved. Do not bypass an outcome
through another browser backend. `tab borrow --timeout 120s` changes only the
confirmation wait (default 60s); custom waits require daemon and extension protocol 1.2+.

The extension's saved Automation settings control borrow confirmation and human
help independently; both default on and apply to existing sessions too. Read
`interaction` in `session start --json` or `session list --json` when needed.

Remote content reads/actions require task-created or borrowed tabs.

## Human steps and recovery

With help enabled, request help for login, CAPTCHA, OTP, payment confirmation,
consent, or after two attempts make no progress:

```sh
bsk request-help --session <id> --prompt "Please complete sign-in" --target @e3
```

Use a precise prompt and fresh targets; omit `--target` when no control fits.
Use completion criteria only for a clear, stable success signal.

| Result | Next step |
| --- | --- |
| Help `continued` / `completed` | Observe again, then resume with fresh refs. |
| Help `cancelled` / `timed_out` | Respect rejection or the blocker; do not repeat the request. |
| Help `disabled` | No human action was confirmed. Re-observe and continue with existing login state. |
| Stale ref | Observe and retry the intended action once. |
| Unknown tab/session | List current tabs/sessions; never guess IDs or use another task's session. |
| Timeout or unknown effect | Inspect current state before retrying; the action may already have happened. |

Navigation alone is not completion. For other errors, follow the returned hint
and inspect the current state.

## Screenshots and Canvas

```sh
bsk screenshot --session <id> --out viewport.png
bsk screenshot --session <id> --ref @e3 --out element.png --json
bsk screenshot --session <id> --full-page --out page.png
```

Screenshots return a local PNG path; view the image to interpret it.

## Files and other tools

```sh
bsk upload @e3 --file ./report.pdf --session <id>
bsk download @e3 --out ./report.pdf --session <id>
```

Upload discloses the file to the site; download accepts site-controlled bytes.
Use agent-local paths, not browser-internal staging paths.

Use `console` / `network` for bounded read-only diagnostics; follow returned
sequence cursors. `bsk --help` lists navigation/history, tab, wait and window commands.

---
Source: https://github.com/Tencent/BrowserSkill/blob/main/skill/SKILL.md (v0.3.0, MIT). Installed manually for OpenCode; `bsk install-skill` does not list OpenCode.
