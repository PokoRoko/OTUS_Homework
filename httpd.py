import argparse
import logging

DOCUMENT_ROOT = "./"


class Server:
    pass


class RequestHandler:
    pass


if __name__ == "__main__":
    arg_pars = argparse.ArgumentParser()
    arg_pars.add_argument('-h', '--host', default="127.0.0.1")
    arg_pars.add_argument('-p', '--port', default=8000, type=int)
    arg_pars.add_argument('-w', '--workers', default=1, type=int, help="Count workers")
    arg_pars.add_argument('-r', '--document-root', default=DOCUMENT_ROOT, help='Document root folder')
    args = arg_pars.parse_args()

    logging.basicConfig(level=logging.INFO,
                        filename=args.file_log,
                        datefmt='%Y.%m.%d %H:%M:%S',
                        format='[%(asctime)s] %(threadName)s %(levelname)s %(message)s',
                        )

    server = Server(host=args.host,
                    port=args.port,
                    workers=args.workers,
                    document_root=args.document_root,
                    )

    server.create_server()
    server.run_forever()
