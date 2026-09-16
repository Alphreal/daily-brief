# Parallel Dashboard — Option A prototype

Side-by-side UI for 2 OpenCode chats sharing one screen. Uses free space instead of one narrow column.

## What it is
- `index.html` — static page, no build. Left + right panes, each bound to an `opencode serve` session.
- Top fan-out box sends one prompt to **both** sessions in parallel.
- `Mark winner` = your "box for choices" — highlights the pane you keep.

## Run (live — currently working on this machine)
1. Backend (opencode 1.18 `serve` requires a password; localhost-only):
   `$env:OPENCODE_SERVER_PASSWORD='parallel-local-01'; opencode serve --port 4097 --cors http://localhost:8000`
2. Serve the page (new terminal, in this folder):
   `python -m http.server 8000`
3. Open `http://localhost:8000`, uncheck **demo mode**, Connect, `+ New` on each side.
   Server URL, user `opencode` and password are prefilled in the header.
4. Type in fan-out → `Send to both`, compare, `⤺ Combine` into Merge, `Mark winner`.

API spec lives at `http://localhost:4097/doc` (`GET /global/health`, `GET /session`, `POST /session`, `GET/POST /session/:id/message`, `POST /session/:id/prompt_async`, `POST /session/:id/abort`).

## Notes / limits vs Option B
- This does not modify the TUI. It is a second client to the same server.
- Parallel edits to the same files can conflict — use separate `git worktree`s for real parallel coding.
- Demo mode (default ON) lets you test layout with no server.
