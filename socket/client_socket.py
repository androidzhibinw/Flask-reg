#!/usr/bin/python

import socket 

s = socket.socket()
host = socket.gethostname()
port=2016
s.connect((host,port))
while True:
    msg=s.recv(1024)
    print msg

