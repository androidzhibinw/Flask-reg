from flask import Flask,render_template,redirect,make_response,request
import datetime
app = Flask(__name__)
@app.route('/')
def index():
    #check cookie, if not set render register
    getip()
    username = request.cookies.get('username')
    if not username:
        return render_template('reg.html')
    else:
        return  render_template('home.html')

def genSecCode(number):
    return '123456'

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

if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=True)
