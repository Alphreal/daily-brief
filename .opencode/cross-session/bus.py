#!/usr/bin/env python3
"""
Cross-Session bus for OpenCode. Stdlib only.
All sessions in this project share .opencode/cross-session/ on disk,
so they can send/inbox messages without a server.

Usage:
  python bus.py new-session --name left
  python bus.py send --from left --to right --msg "hello" --type task
  python bus.py broadcast --from left --msg "all read this"
  python bus.py inbox --for right --unread-only
  python bus.py read --for right --id <msg_id> --mark-read
  python bus.py sessions --list
"""
import argparse
import datetime
import json
import os
import sys
import uuid

BASE = os.path.dirname(os.path.abspath(__file__))
INBOX_DIR = os.path.join(BASE, "inbox")
SESSIONS_FILE = os.path.join(BASE, "sessions.json")


def ensure_dirs():
    os.makedirs(INBOX_DIR, exist_ok=True)
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def load_sessions():
    ensure_dirs()
    try:
        with open(SESSIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        # Don't silently clobber corrupt registry — back it up
        try:
            bad = SESSIONS_FILE + ".corrupt-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            os.replace(SESSIONS_FILE, bad)
            print(f"sessions.json corrupt, backed up to {os.path.basename(bad)}", file=sys.stderr)
        except Exception:
            pass
        return {}


def save_sessions(d):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)


def valid_name(name):
    return bool(name) and all(c.isalnum() or c in ("-", "_") for c in name)


def inbox_path(name):
    if not valid_name(name):
        print(f"invalid session name: {name!r} (use A-Z a-z 0-9 - _)", file=sys.stderr)
        sys.exit(1)
    return os.path.join(INBOX_DIR, name + ".jsonl")


def load_inbox(name):
    p = inbox_path(name)
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def save_inbox(name, msgs):
    p = inbox_path(name)
    with open(p, "w", encoding="utf-8") as f:
        for m in msgs:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")


def append_msg(to_name, msg):
    p = inbox_path(to_name)
    os.makedirs(INBOX_DIR, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg, ensure_ascii=False) + "\n")


def make_msg(from_name, to_name, body, mtype="text", thread=""):
    return {
        "id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6],
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "from": from_name,
        "to": to_name,
        "type": mtype,
        "thread": thread,
        "body": body,
        "read": False,
    }


def cmd_new_session(a):
    ensure_dirs()
    if not valid_name(a.name):
        print(f"invalid session name: {a.name!r}", file=sys.stderr)
        sys.exit(1)
    d = load_sessions()
    if a.name in d:
        print(f"session exists: {a.name} (use sessions --list)")
        return
    d[a.name] = {"created": datetime.date.today().isoformat(), "meta": a.meta or ""}
    save_sessions(d)
    # touch inbox
    if not os.path.exists(inbox_path(a.name)):
        open(inbox_path(a.name), "a").close()
    print(f"session ready: {a.name}")


def cmd_send(a):
    ensure_dirs()
    d = load_sessions()
    if a.to not in d:
        print(f"warn: target {a.to!r} not registered (typo?). Sending anyway.", file=sys.stderr)
    m = make_msg(a.frm, a.to, a.msg, a.type, a.thread or "")
    append_msg(a.to, m)
    print(f"sent {m['id']} {a.frm}->{a.to}")


def cmd_broadcast(a):
    ensure_dirs()
    d = load_sessions()
    targets = [k for k in d.keys() if k != a.frm]
    if not targets:
        targets = [t for t in ("left", "right", "merge") if t != a.frm]
    for t in targets:
        append_msg(t, make_msg(a.frm, t, a.msg, a.type, a.thread or ""))
    print(f"broadcast from {a.frm} to {len(targets)}: {', '.join(targets)}")


def cmd_inbox(a):
    target = a.for_session
    msgs = load_inbox(target)
    if a.unread_only:
        msgs = [m for m in msgs if not m.get("read")]
    msgs = msgs[-a.limit:]
    if not msgs:
        print(f"inbox {target}: empty")
        return
    for m in msgs:
        flag = "unread" if not m.get("read") else "read"
        print(f"[{flag}] {m['id']} from={m['from']} type={m.get('type','text')} ts={m.get('ts','')}")
        print(f"  {m.get('body','')[:500]}")
    # touch last_seen
    d = load_sessions()
    if target in d:
        d[target]["last_seen"] = datetime.datetime.now().isoformat(timespec="seconds")
        save_sessions(d)


def cmd_read(a):
    msgs = load_inbox(a.for_session)
    hit = [m for m in msgs if m.get("id", "").startswith(a.id)]
    if len(hit) != 1:
        print(f"not found/ambiguous: {a.id} in {a.for_session} ({len(hit)} hits)", file=sys.stderr)
        sys.exit(1)
    m = hit[0]
    print(json.dumps(m, indent=2, ensure_ascii=False))
    if a.mark_read:
        for x in msgs:
            if x.get("id") == m.get("id"):
                x["read"] = True
        save_inbox(a.for_session, msgs)
        print("marked read")


def cmd_sessions(a):
    d = load_sessions()
    if a.register:
        if not valid_name(a.register):
            print(f"invalid session name: {a.register!r}", file=sys.stderr)
            sys.exit(1)
        d[a.register] = {"created": datetime.date.today().isoformat(), "meta": a.meta or ""}
        save_sessions(d)
        print(f"registered: {a.register}")
        return
    if not d:
        print("no sessions yet. Use: bus.py new-session --name left")
        return
    for k, v in d.items():
        box = load_inbox(k)
        n = len(box)
        unread = len([m for m in box if not m.get("read")])
        print(f"{k}: {n} msgs ({unread} unread) meta={v.get('meta','')}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new-session"); p.add_argument("--name", required=True); p.add_argument("--meta", default=""); p.set_defaults(fn=cmd_new_session)
    p = sub.add_parser("send"); p.add_argument("--from", dest="frm", required=True); p.add_argument("--to", required=True); p.add_argument("--msg", required=True); p.add_argument("--type", default="text"); p.add_argument("--thread", default=""); p.set_defaults(fn=cmd_send)
    p = sub.add_parser("broadcast"); p.add_argument("--from", dest="frm", required=True); p.add_argument("--msg", required=True); p.add_argument("--type", default="text"); p.add_argument("--thread", default=""); p.set_defaults(fn=cmd_broadcast)
    p = sub.add_parser("inbox"); p.add_argument("--for", dest="for_session", required=True); p.add_argument("--unread-only", action="store_true"); p.add_argument("--limit", type=int, default=20); p.set_defaults(fn=cmd_inbox)
    p = sub.add_parser("read"); p.add_argument("--for", dest="for_session", required=True); p.add_argument("--id", required=True); p.add_argument("--mark-read", action="store_true"); p.set_defaults(fn=cmd_read)
    p = sub.add_parser("sessions"); p.add_argument("--list", action="store_true"); p.add_argument("--register", default=""); p.add_argument("--meta", default=""); p.set_defaults(fn=cmd_sessions)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
