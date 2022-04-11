import argparse
import logging
import os
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

DOCUMENT_ROOT = "./"
TIME_OUT_SERVER = 10
VALID_METHODS = ["GET", "HEAD"]


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
        logging.debug(f"Receive {self.request}")
        self.response_status = "HTTP/1.1 200 OK"
        self.response_header = {
            'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Server': self.server_name,
        }
        self.response_data = None

        self.method, self.uri, self.http_ver = self.parse_request()
        self.method_handler = self.method_handler()
        #self.get_path()

        self.response_code = 200

        logging.debug("_________________________________________")




    def get_request(self, conn):
        logging.debug("Got request")
        request = b''
        while b"\r\n\r\n" not in request:
            chunk = conn.recv(1024)
            request += chunk
            if not chunk:
                raise ConnectionError

        return request.rstrip()

    def parse_request(self):
        logging.debug("Parse request")
        lines = self.request.decode().split("\r\n")
        method, url, http_ver = lines[0].split(" ")
        return method, url, http_ver

    def method_handler(self):
        if self.method in VALID_METHODS:
            methods = {
                "GET": self.get_method(),
                "HEAD": self.head_method()
            }
            return methods[self.method]
        else:
            raise ConnectionError(f"Invalid method {self.method}")

    def get_method(self):
        try:
            logging.debug("Get method")
            path = self.get_path()

            if path:
                if not os.path.isfile(path):

                    self.response_data = "<html>Directory index file</html>\n"





        except Exception as error:
            print(error)

        response = self.create_response()
        logging.info("get method end")
        self.conn.sendall(response)
        self.conn.close()

    def head_method(self):
        pass

    def get_path(self):
        logging.debug("Get path")
        path = os.path.abspath(self.document_root + self.uri)
        if os.path.exists(path):
            return path
        else:
            print("Path not exist")
            return None

    def create_header(self):
        logging.debug("Create Header")
        try:
            headers = ""

            if self.response_data:
                self.response_header["Content-Length"] = len(self.response_data)
                self.response_header["Content-Type"] = "text/html"

            for key, value in self.response_header.items():
                headers += f"{key}: {value}\r\n"
            return headers
        except Exception as error:
            print(111,error)

    def create_response(self):
        try:
            logging.debug("Create response")
            headers = self.create_header()
            response = self.response_status + "\r\n" + headers + "\r\n"

            if self.response_data:
                response += self.response_data + "\r\n"


            logging.debug(f"Response {response.encode()}")
            return response.encode()
        except Exception as error:
            print(222,error)



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
