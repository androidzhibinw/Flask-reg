#!/usr/bin/python 
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port=2016
s.bind((host,port))
s.listen(3)

while True:
    con,addr = s.accept()
    print 'Got connection from', addr
    con.send('Thank you for connecting')
    
    




