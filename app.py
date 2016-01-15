from flask import Flask,render_template,redirect,make_response,request
from threading import Thread
import datetime,random,socket,time,Queue
RANDOM_MIN=100000
RANDOM_MAX=999999
app = Flask(__name__)

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
    app.logger.info('sms worker')
    while True:
        if not CONN:
            app.logger.info('sms sock connection not ready')
            time.sleep(5)
            continue
        item = WORK_Q.get()
        send_sms(item)

def create_serv_sock():
    app.logger.info('create_serv_sock start')
    global is_serv_ready,CONN
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    host = socket.gethostname()
    port=2016
    app.logger.info('before bind')
    s.bind((host,port))
    app.logger.info('after bind')
    s.listen(1)
    con,addr = s.accept()
    is_serv_ready = True
    app.logger.info('sock accept:' + str(addr))
    CONN=con

def send_sms(msg):
    global CONN
    CONN.send(msg)
    app.logger.info('send to client:' +msg)

def prepare_sms_service():
    t_serv = Thread(target=create_serv_sock)
    t_serv.setDaemon(True)
    t_serv.start()
    t_work = Thread(target=sms_worker)
    t_work.setDaemon(True)
    t_work.start()
    WORK_Q.put('test msg 1')
    WORK_Q.put('test msg 2')
if __name__ == '__main__':
    prepare_sms_service()
    app.run(host='0.0.0.0',debug=True,port=8000,use_reloader=False)
