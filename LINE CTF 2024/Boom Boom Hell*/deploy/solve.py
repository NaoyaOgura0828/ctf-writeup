from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello from GET!')

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        self.send_response(200)
        self.end_headers()
        response = "Received POST request: " + str(params)
        self.wfile.write(response.encode())


if __name__ == '__main__':
    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()
