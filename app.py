from flask import Flask,render_template,redirect,make_response,request
from threading import Thread
import datetime,random,socket,time,Queue
app = Flask(__name__)
RANDOM_MIN=100000
RANDOM_MAX=999999


##for sms service
WORK_Q = Queue.Queue()
is_serv_ready=False
CONN=None

@app.route('/')
def index():
    #check cookie, if not set render register
    getip()
    username = request.cookies.get('username')
    if not username:
        return render_template('reg.html')
    else:
        return render_template('home.html')

def genSecCode(number):
    rand_no=random.randint(RANDOM_MIN,RANDOM_MAX)
    return '%d' % rand_no

@app.route('/getcode')
def getcode():
    #gen security code , insert to db
    return genSecCode('10086')
def getip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    print ip

@app.route('/login')
def login():
    #check phonenumber with security code.
    resp = make_response(redirect('/'))
    expire_date = datetime.datetime.now() + datetime.timedelta(days=365)
    resp.set_cookie('username', 'myname',expires=expire_date)
    #set cookie
    return resp

##for sms service
def enqueue_sms_request(json):
    WORK_Q.put(json)

def sms_worker():
    print 'sms worker'
    while True:
        if not CONN:
            print 'not ready'
            time.sleep(5)
            continue
        item = WORK_Q.get()
        send_sms(item)
def create_serv_sock():
    global is_serv_ready,CONN
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = socket.gethostname()
    port=2017
    s.bind((host,port))
    s.listen(1)
    con,addr = s.accept()
    is_serv_ready = True
    print "\nsock accept"
    CONN=con
def send_sms(msg):
    print 'send to client',msg
    global CONN
    CONN.send(msg)

def prepare_sms_service():
    t_serv = Thread(target=create_serv_sock)
    t_serv.setDaemon(True)
    t_serv.start()
    print 'serv sock has started'
    t_work = Thread(target=sms_worker)
    t_work.setDaemon(True)
    t_work.start()
    print 'worker thread started'
    WORK_Q.put('test msg 1')
    WORK_Q.put('test msg 2')
if __name__ == '__main__':
        prepare_sms_service()
        app.run(host='0.0.0.0',debug=True,port=8000)
