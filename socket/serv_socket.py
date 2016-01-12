#!/usr/bin/python 
import socket,time
from threading import Thread
import Queue

WORK_Q = Queue.Queue()
is_serv_ready=False
CONN=None
def worker():
    print 'worker..'
    while True:
        item = WORK_Q.get()
        do_work(item)
def sock_accept():
    global is_serv_ready,CONN
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = socket.gethostname()
    port=2016
    s.bind((host,port))
    s.listen(3)
    con,addr = s.accept()
    is_serv_ready = True
    print "sock accept"
    CONN=con
def do_work(item):
    print 'send to client'
    global CONN
    CONN.send(item)
if __name__=='__main__':
    ##create in a new thread.
    t_serv = Thread(target=sock_accept)
    t_serv.setDaemon(True)
    t_serv.start()
    print 'has started'
    while not is_serv_ready:
        time.sleep(5)
        print 'not ready'

    WORK_Q.put('test msg')
    print 'after work q 1'
    t = Thread(target=worker)
    t.setDaemon(True)
    t.start()
    print 'new thread..'
    WORK_Q.put('test msg2')
    print 'after workq2'
    while not WORK_Q.empty():
        time.sleep(1)
    print 'task done'
