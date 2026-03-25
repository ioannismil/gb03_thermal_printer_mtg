import http.server
import socketserver
import urllib.request
from urllib.parse import urlparse, parse_qs
import os

PORT = 8080

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/proxy?url='):
            qs = parse_qs(urlparse(self.path).query)
            target_url = qs.get('url', [''])[0]
            if not target_url:
                self.send_error(400, "Missing url parameter")
                return
            
            try:
                # Add a reasonable User-Agent so Scryfall's CDN doesn't block the request
                req = urllib.request.Request(
                    target_url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req) as response:
                    self.send_response(response.status)
                    self.send_header('Content-type', response.headers.get('Content-type', 'image/jpeg'))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.read())
            except Exception as e:
                self.send_error(500, str(e))
        else:
            # Serve the static files (index.html, etc.) from this directory normally
            super().do_GET()

if __name__ == '__main__':
    # Ensure serving from the directory where this script lives
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
        print(f"Starting local server and proxy at http://localhost:{PORT}")
        print("Open this URL in Chrome on this PC, or use your local IP on your phone's Chrome")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
