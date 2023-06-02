from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
import threading
import json
from datetime import datetime
import os

# Конфигурация портов
HTTP_PORT = 3000
SOCKET_PORT = 5000

# Конфигурация путей к статическим файлам
STATIC_DIR = 'static'
CSS_FILE = 'style.css'
LOGO_FILE = 'logo.png'

# Конфигурация путей и файлов для сохранения данных
STORAGE_DIR = 'storage'
DATA_FILE = 'data.json'

# Класс HTTP обработчика



class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self._render_html('message.html')
        elif self.path == '/' + CSS_FILE:
            self._serve_static_file(CSS_FILE, 'text/css')
        elif self.path == '/' + LOGO_FILE:
            self._serve_static_file(LOGO_FILE, 'image/png')
        else:
            self._send_404_response()

    def do_POST(self):
        if self.path == '/':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data_dict = dict(param.split('=') for param in post_data.split('&'))
            self._send_data_to_socket_server(data_dict)
            self._render_html('thankyou.html')
        else:
            self._send_404_response()

    def _serve_static_file(self, filename, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        with open(os.path.join(STATIC_DIR, filename), 'rb') as file:
            self.wfile.write(file.read())

    def _send_404_response(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self._render_html('error.html')

    def _render_html(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())


    def _send_data_to_socket_server(self, data):
        save_data_to_file(data) # вызов функции сохрениния данных
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(json.dumps(data).encode(), ('localhost', SOCKET_PORT))
        sock.close()


# Класс Socket сервера
class SocketServerThread(threading.Thread):

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('localhost', SOCKET_PORT))
        os.makedirs(STORAGE_DIR, exist_ok=True)
        while True:
            data, addr = sock.recvfrom(1024)
            data_dict = json.loads(data.decode())
            data_dict['timestamp'] = str(datetime.now())
            with open(os.path.join(STORAGE_DIR, DATA_FILE), 'a') as file:
                json.dump(data_dict, file)
                file.write('\n')

# Запуск HTTP сервера
def run_http_server():
    server_address = ('', HTTP_PORT)
    http_server = HTTPServer(server_address, HTTPHandler)
    http_server.serve_forever()


# Запуск Socket сервера
def run_socket_server():
    socket_server = SocketServerThread()
    socket

# сохрание в data.json
def save_data_to_file(data):
    with open(os.path.join(STORAGE_DIR, DATA_FILE), 'w') as file:
        json.dump(data, file)

if __name__ == '__main__':
    # Запуск HTTP сервера в отдельном потоке
    http_server_thread = threading.Thread(target=run_http_server)
    http_server_thread.start()

    # Запуск Socket сервера в отдельном потоке
    socket_server_thread = threading.Thread(target=run_socket_server)
    socket_server_thread.start()