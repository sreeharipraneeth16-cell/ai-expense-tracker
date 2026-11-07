#!/usr/bin/env python3
"""
AI Expense Tracker - local companion server
===========================================

What this does
--------------
1. Serves the tracker page, so you still open
   http://localhost:8000/ai-expense-tracker.html
2. Accepts bank SMS text from your phone at POST /api/sms
   and stores it in a small inbox file.
3. Lets the tracker page poll GET /api/sms?after=<id>, so new
   messages appear automatically (the page then asks Claude to
   categorize them and adds them to your list).

Nothing leaves your computer except the Claude API call that the
page already makes. Messages are stored in your temp folder:
    %TEMP%\\expense-tracker-inbox.json

Run it:
    python expense-server.py

Then configure an SMS-forwarding app on your Android phone to POST
to http://<this-PC-LAN-IP>:8000/api/sms with body {"message":"..."}.

Only use this on a trusted home Wi-Fi network.
"""

import json
import os
import socket
import sys
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = 8000
ROOT = os.path.dirname(os.path.abspath(__file__))

# Messages live OUTSIDE the folder that is served, so nobody on the
# network can download your SMS history by guessing a file name.
INBOX = os.path.join(tempfile.gettempdir(), "expense-tracker-inbox.json")

# One lock so two requests can't write the file at the same time.
LOCK = threading.Lock()

# Browser origins allowed to read the SMS inbox. Localhost/file use are
# allowed; any other website is refused by not setting a readable CORS header.
ALLOWED_ORIGINS = {
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null",
}

# Max size of an SMS posting: ~64 KB is far more than a bank message needs.
MAX_POST_BYTES = 64 * 1024


def load_inbox():
    """Return the stored messages (a list). Never raises."""
    try:
        with open(INBOX, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except Exception:
        # A corrupt file shouldn't crash the server.
        return []


def save_inbox(items):
    """Write atomically: temp file first, then rename."""
    temp_path = INBOX + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(items, handle, ensure_ascii=False, indent=1)
    os.replace(temp_path, INBOX)


def lan_ip():
    """Best guess at this computer's address on the local network."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connecting a UDP socket doesn't send anything; it just tells us
        # which local address the OS would use.
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        sock.close()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def send_response(self, code, message=None):
        super().send_response(code, message)
        # Basic hardening headers on every response.
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")

    # ---- small helpers -------------------------------------------------

    def log_message(self, fmt, *args):
        # Polling every few seconds would flood the console; hide those.
        if self.command == "GET" and self.path.startswith("/api/sms"):
            return
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_cors_headers(self):
        # Lets the page work even if it's opened as a local file, but only
        # for loopback origins: no random website on the internet can read
        # (or write) this inbox through the browser.
        origin = self.headers.get("Origin")
        allowed = origin is None or origin in ALLOWED_ORIGINS
        if allowed:
            self.send_header("Access-Control-Allow-Origin", origin or "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    # ---- HTTP verbs ----------------------------------------------------

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/health":
            with LOCK:
                items = load_inbox()
            self.send_json({
                "ok": True,
                "count": len(items),
                "lastId": items[-1]["id"] if items else 0,
            })
            return

        if parsed.path == "/api/sms":
            try:
                after = int(parse_qs(parsed.query).get("after", ["0"])[0])
            except ValueError:
                after = 0
            with LOCK:
                items = load_inbox()
            new = [m for m in items if int(m.get("id", 0)) > after]
            self.send_json({
                "messages": new,
                "lastId": items[-1]["id"] if items else 0,
            })
            return

        # Never serve the inbox file itself.
        if parsed.path == "/sms-inbox.json" or parsed.path == "/expense-tracker-inbox.json":
            self.send_json({"error": "Not found"}, 404)
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/sms":
            self.handle_new_sms()
            return

        if parsed.path == "/api/sms/clear":
            with LOCK:
                save_inbox([])
            self.send_json({"ok": True})
            return

        self.send_json({"error": "Not found"}, 404)

    # ---- /api/sms ------------------------------------------------------

    def handle_new_sms(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_POST_BYTES:
            # Refuse huge payloads before reading them into memory.
            self.send_json({"ok": False, "error": "Message too large for the tracker."}, 413)
            return
        raw = self.rfile.read(length) if length else b""
        text = raw.decode("utf-8", "replace").strip()
        content_type = (self.headers.get("Content-Type") or "").lower()

        # Some forwarding apps send a normal web form (message=...), others
        # send JSON, others just dump the raw text. Support all three.
        if "application/x-www-form-urlencoded" in content_type:
            form = parse_qs(text)
            messages = []
            for key in ("message", "messages", "text", "sms", "content", "body"):
                if key in form:
                    messages = form[key]
                    break
        else:
            messages = self.extract_messages(text)

        messages = [m.strip() for m in messages if m and m.strip()]
        if not messages:
            self.send_json({
                "ok": False,
                "error": "No message text received. Send JSON like {\"message\":\"Rs.450 debited...\"}.",
            }, 400)
            return

        with LOCK:
            items = load_inbox()
            next_id = (int(items[-1]["id"]) + 1) if items else 1
            for message in messages:
                items.append({
                    "id": next_id,
                    "message": message[:4000],
                    "receivedAt": time.strftime("%Y-%m-%dT%H:%M:%S"),
                })
                next_id += 1
            # Keep the file small: only the newest 500 messages.
            if len(items) > 500:
                items = items[-500:]
            save_inbox(items)

        print("  + SMS received: %d message(s), total stored %d" % (len(messages), len(items)))
        self.send_json({
            "ok": True,
            "added": len(messages),
            "lastId": items[-1]["id"] if items else 0,
        })

    @staticmethod
    def extract_messages(text):
        """Accept JSON {message}, JSON {messages:[...]}, a JSON list, or plain text."""
        if not text:
            return []

        candidates = []
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                if isinstance(data.get("messages"), list):
                    candidates = [str(x) for x in data["messages"]]
                elif data.get("message") is not None:
                    candidates = [str(data["message"])]
                elif data.get("text") is not None:
                    candidates = [str(data["text"])]
            elif isinstance(data, list):
                candidates = [str(x) for x in data]
            elif isinstance(data, str):
                candidates = [data]
        except Exception:
            # Not JSON: treat the raw body as one message.
            candidates = [text]

        # One message per line also works for batch pasting.
        cleaned = []
        for item in candidates:
            for line in str(item).replace("\r", "\n").split("\n"):
                line = line.strip()
                if line:
                    cleaned.append(line)
        return cleaned


def main():
    os.chdir(ROOT)
    ThreadingHTTPServer.allow_reuse_address = True
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

    print("")
    print("  AI Expense Tracker server is running")
    print("  ----------------------------------------------")
    print("  Open on this PC:  http://localhost:%d/ai-expense-tracker.html" % PORT)
    print("  Phone (same Wi-Fi) should POST to:")
    print("      http://%s:%d/api/sms" % (lan_ip(), PORT))
    print("")
    print("  Inbox file: %s" % INBOX)
    print("  Security: CORS is limited to local hosts, responses are no-store,")
    print("  and postings are limited in size. Use only on trusted Wi-Fi.")
    print("  Keep this window open. Press Ctrl+C to stop.")
    print("")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
