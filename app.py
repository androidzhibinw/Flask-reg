from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, make_response, request, session, url_for
from threading import Thread
import datetime
import random
import socket
import time
import Queue
import json

RANDOM_MIN = 100000
RANDOM_MAX = 999999
SMS_CODE_LIMIT = 3
SMS_CODE_VALID_TIME_HOUR = 24

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
app.secret_key = 'test key ..'

# for sms service
WORK_Q = Queue.Queue()
is_serv_ready = False
CONN = None
END_STR = '\n'


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(days=365)


@app.route('/')
def index():
    # check cookie, if not set render register
    app.logger.info('ip:' + str(getip()))
    app.logger.info('cookies:' + str(request.cookies))
    #username = request.cookies.get('username')
    if 'user' in session:
        return render_template('home.html', user=session['user'])
    else:
        return render_template('reg.html')


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
                return 'fail:number invalid or time limit'
        except Exception as e:
            return str(e)

    return 'success'


def getip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    return ip


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if 'user' in session:
            return redirect(url_for('index'))
        data = request.form.to_dict()
        app.logger.info(str(data))
        if 'login' in data:
            number = data['phone-number']
            code = data['dynamic-code']
            app.logger.info('login:' + number + ',' + code)
            yesterday = datetime.datetime.today(
            ) - datetime.timedelta(hours=SMS_CODE_VALID_TIME_HOUR)
            res = Register.query.filter((Register.phone_number == number) & (
                Register.code == code) & (Register.created_on > yesterday)).count()
            if res == 1:
                app.logger.info('login success')
                add_user(number)
                session['user'] = number
                #resp = make_response(redirect('/'))
                #expire_date = datetime.datetime.now() + datetime.timedelta(days=365)
                #resp.set_cookie('username', number, expires=expire_date)
                # return resp
                return redirect(url_for('index'))
            else:
                error = 'phone number or security code not correct !'
                app.logger.info(error)
        else:
            error = 'press login button to login'

    return redirect(url_for('index'))
@app.route('/logoutabc')
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))

def add_user(number):
    count = User.query.filter_by(phone_number=number).count()
    if count == 0:
        try:
            user = User(number,number)
            db.session.add(user)
            db.session.commit()
            app.logger.info('add_user User:' + number)
        except Exception as e:
            app.logger.error(str(e))
    else:
        app.logger.warning('add_user User:' + number + ' already exist!')

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
    now = datetime.datetime.today()
    yesterday = now - datetime.timedelta(hours=SMS_CODE_VALID_TIME_HOUR)
    app.logger.info('yesterday:' + str(yesterday))
    result = Register.query.filter((Register.phone_number == number) & (
        Register.created_on > yesterday)).count()
    app.logger.info(number + ' have recoreds number ' + str(result))
    if result >= SMS_CODE_LIMIT:
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


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String, unique=True)
    name = db.Column(db.String)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __init__(self, phone_number, name):
        self.phone_number = phone_number
        self.name = name

    def __repr__(self):
        return '<User: no=%r, name=%r>' % (self.phone_number, self.name)


if __name__ == '__main__':
    prepare_sms_service()
    app.run(host='0.0.0.0', debug=True, port=8000, use_reloader=False)
