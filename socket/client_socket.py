#!/usr/bin/python

import socket
import time

HOST = socket.gethostname()
PORT = 2016
SOCK_RETRY_SEC = 10
BUFF_SIZE = 1024


def local_socket():
    s = try_to_connect()
    # should have threads for handle request
    while True:
        msg = s.recv(BUFF_SIZE)
        # handle msg in a thread
        if len(msg) == 0:
            s = try_to_connect()
        else:
            handle_msg(msg)


def handle_msg(msg):
    print msg


def try_to_connect():
    s = socket.socket()
    while True:
        try:
            s.connect((HOST, PORT))
            return s
        except Exception as e:
            print e
            time.sleep(SOCK_RETRY_SEC)


if __name__ == '__main__':
    local_socket()
