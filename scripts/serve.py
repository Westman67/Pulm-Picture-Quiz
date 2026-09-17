#!/usr/bin/env python3
"""Serve dist/ with correct MIME types (older Python mimetypes DBs omit .webp)."""
import http.server
import mimetypes
import sys
from pathlib import Path

mimetypes.add_type("image/webp", ".webp")

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
DIRECTORY = sys.argv[2] if len(sys.argv) > 2 else "dist"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


if __name__ == "__main__":
    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        print(f"Serving {Path(DIRECTORY).resolve()} at http://localhost:{PORT}")
        httpd.serve_forever()
