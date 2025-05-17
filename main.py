from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import urllib.parse
import pathlib
import mimetypes
import os
import json

BASE_DIR = pathlib.Path(__file__).parent
STORAGE_DIR = BASE_DIR / 'storage'
DATA_FILE = STORAGE_DIR / 'data.json'
env = Environment(loader=FileSystemLoader('./'))

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.render_read_page()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        timestamp = datetime.now().isoformat()

        if not STORAGE_DIR.exists():
            os.makedirs(STORAGE_DIR)
        
        if not DATA_FILE.exists():
            with open(DATA_FILE, 'w') as f:
                json.dump({}, f)
        
        with open(DATA_FILE, 'r+') as file:
            content = json.load(file)
            content[timestamp] = data_dict
            file.seek(0)
            json.dump(content, file, indent=4)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def render_read_page(self):
        with open(DATA_FILE, 'r') as f:
            messages = json.load(f)
        template = env.get_template('read.html')
        rendered_content = template.render(messages=messages)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(rendered_content.encode())

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

if __name__ == '__main__':
    run()
