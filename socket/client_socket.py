#!/usr/bin/python

import socket 

def local_socket():
    s = socket.socket()
    host = '127.0.0.1'
    port=2016
    s.connect((host,port))
    #should have threads for handle request
    while True:
        msg=s.recv(1024)
        ## handle msg in a thread
        handle_msg(msg)

def handle_msg(msg):
    print msg

if __name__ == '__main__':
    local_socket()

