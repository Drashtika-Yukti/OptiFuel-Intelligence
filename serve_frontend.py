import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.join(os.path.dirname(__file__), "frontend")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"--- OptiFuel Intelligence Dashboard ---")
    print(f"Frontend is running at: http://localhost:{PORT}")
    print(f"Press CTRL+C to stop.")
    httpd.serve_forever()
