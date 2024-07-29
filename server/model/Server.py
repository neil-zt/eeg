from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import multiprocessing
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "active"})
            self.wfile.write(response.encode())
        else:
            self.send_error(404, "Not Found")

class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.httpd = None
        self.output_destination = None
        self.server_process = None

    def run_server(self):
        self.httpd = HTTPServer((self.host, self.port), SimpleHTTPRequestHandler)
        print(f"Server running on http://{self.host}:{self.port}")
        self.httpd.serve_forever()

    def run(self):
        self.server_process = multiprocessing.Process(target=self.run_server)
        self.server_process.start()

    def stop(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join()
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()

    def inject_output_destination_name(self, output_destination):
        self.output_destination = output_destination