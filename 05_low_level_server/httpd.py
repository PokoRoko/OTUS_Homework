import argparse
import logging
import mimetypes
import os
import socket
import urllib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum

DOCUMENT_ROOT = "./"
TIME_OUT_SERVER = 10
VALID_METHODS = ["GET", "HEAD"]


class HTTPStatus(Enum):
    OK = 200
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500


class Server:
    def __init__(self, host, port, server_name, max_workers, document_root):
        self.host = host
        self.port = port
        self.server_name = server_name
        self.max_workers = max_workers
        self.document_root = document_root

    def run_server_forever(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((self.host, self.port))
            server.listen(self.max_workers)
            logging.info(f'Listening on {self.host}:{self.port}')
            executor = ThreadPoolExecutor(max_workers=self.max_workers)
            while True:
                client_sock, address = server.accept()
                client_sock.settimeout(TIME_OUT_SERVER)
                executor.submit(ConnectHandler, client_sock, self.document_root, self.server_name)
        finally:
            server.close()


class ConnectHandler:
    def __init__(self, conn, document_root, server_name):
        self.conn = conn
        self.document_root = document_root
        self.server_name = server_name
        self.request = self.get_request(self.conn)

        self.response_status = None
        self.response_data = None
        self.response_header = {
            'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Server': self.server_name,
        }

        self.method, self.uri, self.http_ver = self.parse_request()
        self.method_handler()

    @staticmethod
    def get_request(conn):
        request = b''
        while b"\r\n\r\n" not in request:
            chunk = conn.recv(1024)
            request += chunk
            if not chunk:
                raise ConnectionError
        return request.rstrip()

    def parse_request(self):
        lines = self.request.decode().split("\r\n")
        method, url, http_ver = lines[0].split(" ")
        url = urllib.parse.unquote(url, encoding='utf-8', errors='replace')
        clear_url = urllib.parse.urlparse(url).path
        return method, clear_url, http_ver

    def method_handler(self):
        is_send_data = True
        if self.method in VALID_METHODS:
            self.request_method()
            if self.method == "HEAD":
                is_send_data = False
        else:
            self.response_status = HTTPStatus.METHOD_NOT_ALLOWED

        response = self.create_response(is_send_data)
        self.send_response(response)

    def request_method(self):
        path = os.path.abspath(self.document_root + self.uri)
        if os.path.exists(path) and "../" not in self.uri:
            if os.path.isfile(path) and not self.uri.endswith("/"):
                with open(path, 'rb') as data:
                    self.response_data = data.read()
                    self.response_status = HTTPStatus.OK
                    self.response_header["Content-Type"] = self.define_content_type(path)

            elif self.check_index_file(path):
                self.response_status = HTTPStatus.OK
                self.response_header["Content-Type"] = "text/html"
                self.response_data = b"<html>Directory index file</html>\n"

            elif os.path.isfile(path) and self.uri.endswith("/"):
                self.response_status = HTTPStatus.NOT_FOUND

            else:
                self.response_status = HTTPStatus.NOT_FOUND
        else:
            self.response_status = HTTPStatus.NOT_FOUND

    def send_response(self, response):
        self.conn.sendall(response)
        self.conn.close()

    @staticmethod
    def check_index_file(path):
        if os.path.isdir(path):
            list_files = os.listdir(path)
            return 'index.html' in list_files
        else:
            return False

    @staticmethod
    def define_content_type(file_path: str) -> str:
        _, file_extension = os.path.splitext(file_path)
        return mimetypes.types_map[file_extension]

    @staticmethod
    def create_status_line(http_status: HTTPStatus):
        return f"HTTP/1.1 {http_status.value} {http_status.name}".encode()

    def create_header(self):
        headers = ""
        if self.response_data:
            self.response_header["Content-Length"] = len(self.response_data)

        for key, value in self.response_header.items():
            headers += f"{key}: {value}\r\n"
        return headers.encode()

    def create_response(self, is_send_data=True):
        status_line = self.create_status_line(self.response_status)
        headers = self.create_header()
        response = status_line + b"\r\n" + headers + b"\r\n"

        if self.response_data and is_send_data:
            response += self.response_data + b"\r\n"
        return response


if __name__ == "__main__":
    arg_pars = argparse.ArgumentParser()
    arg_pars.add_argument('--host', default="127.0.0.1")
    arg_pars.add_argument('-p', '--port', default=8080, type=int)
    arg_pars.add_argument('-s', '--server_name', default="OTUServer", help="Name server")
    arg_pars.add_argument('-w', '--workers', default=1, type=int, help="Count workers")
    arg_pars.add_argument('-r', '--document-root', default=DOCUMENT_ROOT, help='Document root folder')
    args = arg_pars.parse_args()

    logging.basicConfig(level=logging.DEBUG,
                        datefmt='%Y.%m.%d %H:%M:%S',
                        format='[%(asctime)s] %(threadName)s %(levelname)s %(message)s',
                        )

    server = Server(host=args.host,
                    port=args.port,
                    server_name=args.server_name,
                    max_workers=args.workers,
                    document_root=args.document_root,
                    )

    server.run_server_forever()
