import argparse
import logging
import socket
from concurrent.futures import ThreadPoolExecutor

DOCUMENT_ROOT = "./"
TIME_OUT_SERVER = 10
VALID_METHODS = ["GET", "HEAD"]



class Server:
    def __init__(self, host, port, max_workers, document_root):
        self.host = host
        self.port = port
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
                executor.submit(ConnectHandler, client_sock)
        finally:
            server.close()


class ConnectHandler:
    def __init__(self, conn):
        self.conn = conn
        self.request = self.get_request(self.conn)
        self.method, self.url, self.http_ver = self.parse_request()

    def get_request(self, conn):
        request = b''

        while b"\r\n\r\n" not in request:
            chunk = conn.recv(1024)
            request += chunk
            if not chunk:
                raise ConnectionError

        logging.debug(f"Receive {request}")
        conn.send(b'ACK!')
        conn.close()
        return request.rstrip()

    def parse_request(self):
        lines = self.request.decode().split("\r\n")
        if len(lines) != 3:
            raise Exception("Invalid HTTP request")
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
        pass

    def head_method(self):
        pass

    def get_path(self, uri: str):
        pass


if __name__ == "__main__":
    arg_pars = argparse.ArgumentParser()
    arg_pars.add_argument('--host', default="127.0.0.1")
    arg_pars.add_argument('-p', '--port', default=8080, type=int)
    arg_pars.add_argument('-w', '--workers', default=1, type=int, help="Count workers")
    arg_pars.add_argument('-r', '--document-root', default=DOCUMENT_ROOT, help='Document root folder')
    args = arg_pars.parse_args()

    logging.basicConfig(level=logging.DEBUG,
                        datefmt='%Y.%m.%d %H:%M:%S',
                        format='[%(asctime)s] %(threadName)s %(levelname)s %(message)s',
                        )

    server = Server(host=args.host,
                    port=args.port,
                    max_workers=args.workers,
                    document_root=args.document_root,
                    )

    server.run_server_forever()
