#!/usr/bin/python 
import socket,time
from threading import Thread
import Queue

WORK_Q = Queue.Queue()
def create_server_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    port=2016
    s.bind((host,port))
    s.listen(3)
    #only listen to one 
    con,addr = s.accept()
    return con,addr
def worker():
    print 'worker..'
    while True:
        item = WORK_Q.get()
        do_work(item)

def do_work(item):
    print item
if __name__=='__main__':
    ##create in a new thread.
    #conn,addr = create_server_socket()
    WORK_Q.put('test msg')
    print 'after work q 1'
    t = Thread(target=worker)
    t.setDaemon(True)
    t.start()
    print 'new thread..'
    WORK_Q.put('test msg2')
    print 'after workq2'
