#!/usr/bin/env python
import os
import sys
import socket
import pickle
import argparse
import time
import multiprocessing

from database import query_database_reg, query_database_regdetails

def parse_args():
    # parse command line arguments
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        description="Server for the registrar application")
    parser.add_argument(
        "port", metavar="port", type=int,
        help="the port at which the server should listen")
    parser.add_argument(
        "delay", metavar="delay", type=int,
        help="delay for busy wait")

    args = parser.parse_args()

    return args.port, args.delay


def consume_cpu_time(delay):
    initial_time = time.process_time()
    while(time.process_time() - initial_time) < delay:
        pass


def handle_client(sock, delay):
    print('Forked child process')
    try:
        # get query
        in_flo = sock.makefile(mode='rb')
        command, query = pickle.load(in_flo)

        consume_cpu_time(delay)

        # connect to database and get data from query
        print(f"Received command: {command}")
        if command == "get_overviews":
            response = query_database_reg(query)
        elif command == "get_detail":
            response = query_database_regdetails(query)
            if not response:
                raise Exception("classid does not exist")
        else:
            raise Exception(
                "Command must be either get_overviews or get_detail")
        # write to client
        out_flo = sock.makefile(mode='wb')
        pickle.dump((True, response), out_flo)
        out_flo.flush()
        sock.close()
        print('Closed socket in child process')
    except Exception as ex:
        out_flo = sock.makefile(mode='wb')
        pickle.dump((False, ex), out_flo)
        out_flo.flush()
        print(f"{ex}")
    print('Exiting child process')


def main():
    port, delay = parse_args()

    try:
        port = int(port)
        delay = int(delay)
        server_sock = socket.socket()
        if os.name != 'nt':
            server_sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Opened server socket.socket')
        server_sock.bind(('', port))
        print('Bound server socket.socket to port')
        server_sock.listen()
        print('Listening')
        while True:
            try:
                sock, _ = server_sock.accept()
                with sock:
                    print('Accepted connection, opened socket.socket')
                    print("Opened socket")
                    process = multiprocessing.Process(
                        target=handle_client,
                        args=[sock,delay])
                    process.start()
            except Exception as ex:
                print(ex, file=sys.stderr)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
