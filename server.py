"""Minimal web server for reviewing git diffs of sibling repositories on a phone."""

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPOS_DIR = Path(os.environ.get("REPOS_DIR", "/repos"))
PORT = int(os.environ.get("PORT", "8043"))
STATIC_DIR = Path(__file__).parent / "static"


def list_repos():
    """Return the names of all git repositories directly inside REPOS_DIR."""
    return sorted(
        (p.name for p in REPOS_DIR.iterdir() if p.is_dir() and (p / ".git").exists()),
        key=str.lower,
    )


def git_diff(repo):
    result = subprocess.run(
        # --no-optional-locks: the repos are mounted read-only, so never try to write the index
        ["git", "--no-optional-locks", "diff"],
        cwd=REPOS_DIR / repo,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return result.stdout


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/repos":
            self.send_json({"repos": list_repos()})
        elif url.path == "/api/diff":
            repo = parse_qs(url.query).get("repo", [""])[0]
            # Only accept names from the repo listing, which rules out path traversal
            if repo not in list_repos():
                self.send_json({"error": "Unknown repository"}, status=404)
                return
            try:
                self.send_json({"repo": repo, "diff": git_diff(repo)})
            except RuntimeError as e:
                self.send_json({"error": str(e)}, status=500)
        elif url.path == "/":
            self.send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def send_json(self, data, status=200):
        self.send_body(json.dumps(data).encode(), "application/json", status)

    def send_file(self, path, content_type):
        self.send_body(path.read_bytes(), content_type)

    def send_body(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Serving repositories from {REPOS_DIR} on port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
