"""
agent-os Live Dashboard Server

Serves the Kanban dashboard and the real-time status JSON.
Run this in one terminal, run team_coordinator in another.

Usage:
    python lib/dashboard_server.py
    # Then open http://localhost:7777 in your browser
"""

import http.server
import json
import os
from pathlib import Path

STATUS_FILE = Path.home() / ".agent-os" / "live_status.json"
DASHBOARD_FILE = Path(__file__).parent.parent / "agent-os-dashboard.html"
PORT = 7777


class DashboardHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_file(DASHBOARD_FILE, "text/html")
        elif self.path == "/status":
            self._serve_status()
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_file(self, path: Path, content_type: str):
        if not path.exists():
            self.send_response(404)
            self.end_headers()
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(content))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def _serve_status(self):
        if STATUS_FILE.exists():
            data = STATUS_FILE.read_bytes()
        else:
            data = json.dumps({"status": "idle", "agents": [], "task": ""}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass  # suppress access logs


def write_idle_status():
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps({
        "status": "idle",
        "task": "",
        "session_id": "",
        "started_at": "",
        "agents": [],
        "elapsed_s": 0,
    }, indent=2))


if __name__ == "__main__":
    write_idle_status()
    print(f"\nagent-os Live Dashboard")
    print(f"Open: http://localhost:{PORT}")
    print(f"Waiting for team sessions...\n")
    with http.server.HTTPServer(("", PORT), DashboardHandler) as server:
        server.serve_forever()
