#!/usr/bin/python 
import socket,time

def create_server_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port=2016
    s.bind((host,port))
    s.listen(3)
    #only listen to one 
    con,addr = s.accept()
    return con,addr


if __name__=='__main__':
    ##create in a new thread.
    conn,addr = create_server_socket()
    conn.send('Wlecome!')
    time.sleep(5)
    conn.close()
