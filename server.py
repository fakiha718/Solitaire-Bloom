"""
server.py - Local Web Server Launcher for Klondike Solitaire Web UI
===================================================================

Academic Data Structures & Algorithms Implementation
Zero external dependencies: uses Python standard library `http.server`
to host the modern Web Browser UI and auto-opens the default browser.
"""

import os
import sys
import webbrowser
import http.server
import socketserver

PORT = 8000
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def log_message(self, format, *args):
        # Mute noisy static request logs in console
        pass


def run_server(port=PORT):
    # Change current working directory to web/
    os.chdir(WEB_DIR)

    handler = CustomHTTPRequestHandler
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True

    # Try requested port or fallback to next available
    active_port = port
    httpd = None
    for p in range(port, port + 10):
        try:
            httpd = socketserver.TCPServer(("", p), handler)
            active_port = p
            break
        except OSError:
            continue

    if not httpd:
        print(f"Error: Could not bind to any port between {port} and {port+9}.")
        sys.exit(1)

    url = f"http://localhost:{active_port}/"
    print("=" * 70)
    print("      ♠ ♥ KLONDIKE SOLITAIRE - WEB BROWSER INTERFACE ♦ ♣")
    print("=" * 70)
    print(f" [✓] Local Server Active: {url}")
    print(f" [✓] Web Assets Root:     {WEB_DIR}")
    print(" [✓] Opening default browser automatically...")
    print("=" * 70)
    print(" Press Ctrl+C in this terminal to stop the server.\n")

    # Auto-open browser
    webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Shutting down Solitaire web server. Goodbye!")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
