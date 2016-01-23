from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, make_response, request
from threading import Thread
import datetime
import random
import socket
import time
import Queue
import json

RANDOM_MIN = 100000
RANDOM_MAX = 999999

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

# for sms service
WORK_Q = Queue.Queue()
is_serv_ready = False
CONN = None
END_STR = '\n'


@app.route('/')
def index():
    # check cookie, if not set render register
    getip()
    username = request.cookies.get('username')
    if not username:
        return render_template('reg.html')
    else:
        return render_template('home.html')


def genSecCode(number):
    rand_no = random.randint(RANDOM_MIN, RANDOM_MAX)
    return '%d' % rand_no


@app.route('/getcode', methods=['POST'])
def getcode():
    # gen security code , insert to db
    if request.method == 'POST':
        try:
            app.logger.info('getcode pass in:' + str(request.json))
            number = request.json['number']
            if check_phonenumber(number):
                send_sms4no(number)
            else:
                return 'fail:number invalid'
        except Exception as e:
            return str(e)

    return 'success'


def getip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    print ip


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form.to_dict()
        print data

        #resp = make_response(redirect('/'))
        #expire_date = datetime.datetime.now() + datetime.timedelta(days=365)
        #resp.set_cookie('username', 'myname',expires=expire_date)
        # return resp
    return render_template('reg.html')


def send_sms4no(number):
    app.logger.info('send_sms4no:' + str(number))
    code = genSecCode(number)
    data = {}
    data['number'] = number
    data['code'] = code
    json_data = json.dumps(data)
    app.logger.info('sms_json' + str(json_data))
    reg = Register(number, str(code), False)
    db.session.add(reg)
    db.session.commit()
    app.logger.info('insert to db' + str(json_data))


def check_phonenumber(number):
    # restrict records <=3
    now = datetime.datetime.today()
    yesterday = now + datetime.timedelta(hours=-24)
    print now, yesterday
    result = Register.query.filter(Register.phone_number == number and (
        Register.created_on >= yesterday)).count()
    app.logger.info(number + 'have recoreds number' + str(result))
    if result >= 3:
        return False

    return True

# for sms service


def enqueue_sms_request(json):
    WORK_Q.put(json)


def sms_worker():
    app.logger.info('sms worker')
    while True:
        if not CONN:
            app.logger.info('sms sock connection not ready sleep 30s')
            time.sleep(30)
            continue
        item = WORK_Q.get()
        send_sms(item)


def create_serv_sock():
    app.logger.info('create_serv_sock start')
    global is_serv_ready, CONN
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # use public ip here.
    host = '127.0.0.1'
    port = 2016
    app.logger.info('before bind')
    s.bind((host, port))
    app.logger.info('after bind')
    s.listen(1)
    con, addr = s.accept()
    is_serv_ready = True
    app.logger.info('sock accept:' + str(addr))
    CONN = con


def send_sms(msg):
    global CONN
    CONN.send(msg + END_STR)
    app.logger.info('send to client:' + msg)


def prepare_sms_service():
    t_serv = Thread(target=create_serv_sock)
    t_serv.setDaemon(True)
    t_serv.start()
    t_work = Thread(target=sms_worker)
    t_work.setDaemon(True)
    t_work.start()
    WORK_Q.put('test msg 1')
    WORK_Q.put('test msg 2')
# for db


class Register(db.Model):
    __tablename__ = 'register'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, phone_number, code, verified):
        self.phone_number = phone_number
        self.code = code
        self.verified = verified

    def __repr__(self):
        return '<Reg: no=%r, code=%r, verified=%>' % (self.phone_number, self.code, self.verified)

if __name__ == '__main__':
    prepare_sms_service()
    app.run(host='0.0.0.0', debug=True, port=8000, use_reloader=False)
