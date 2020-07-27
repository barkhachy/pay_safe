from db import Base, User
from flask import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from flask_httpauth import HTTPBasicAuth
from flask import render_template, Response
import json
import requests
import os


auth = HTTPBasicAuth()

engine = create_engine("sqlite:///users.db")
Base.metadata.bind = engine
DBsession = sessionmaker(bind = engine)
db_session = DBsession()
app = Flask(__name__)

app.secret_key = os.urandom(24)
@auth.verify_password
def verify_password(mail, password):
    user = db_session.query(User).filter_by(e_mail = mail).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        return render_template("cart.html")

@app.route('/signup', methods = ['GET','POST'])
def new_user():
    if request.method == 'POST':
        mail = request.form['mail']
        username = request.form['username']
        password = request.form['password']
        if mail is None or password is None:
            abort(400)
        if db_session.query(User).filter_by( e_mail = mail).first() is not None:
            return "already registered"
        user = User(e_mail = mail)
        user.name = username
        user.hash_password(password)
        db_session.add(user)
        db_session.commit()
        return render_template("login.html")
    else:
        return render_template("signup.html")

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        username = request.form['username']
        password = request.form['password']
        if mail is None or password is None:
            render_template("signup.html")
        if verify_password(mail, password):
            session['user'] = username 
            return redirect(url_for('cart'))
    else:
        return render_template("login.html")

@app.route('/logout', methods = ['GET','POST'])
def logout():
    session.pop('user', None)
    return render_template('login.html')
@app.route('/cart', methods = ['GET','POST'])
def cart():
    if g.user:
        if request.method == 'GET':
            return render_template('cart.html')
        else:
            with open('paysafe.json') as f:
                data = json.load(f)
            api = data['credentials']['public']['base64']
            date = request.form['dob'].split("-")
            dateOfBirth =   {
                                 "day":date[2],
                                 "month":date[1],
                                 "year":date[0]
                             }
            customer_info = {"firstName" : request.form['f_name'],
                             "lastName":request.form['l_name'],
                             "email": request.form['mail'],
                             "phone": request.form['phone'],
                             
                             }
            billing_info = {
                            "nickName":request.form['f_name']+request.form['l_name'],
                            "street":request.form['street_1'],
                            "street2":request.form['street_2'],
                            "city":request.form['city'],
                            "zip":request.form['zip'],
                            "country":request.form['country'],
                            "state":request.form["state"]
            }
            j_data = {
                "merchantCustomerId":customer_info["firstName"]+customer_info["lastName"],
                "locale":data['locale'],
                "firstName":customer_info['firstName'],
                "lastName":customer_info['lastName'],
                "dateOfBirth":
                {
                    "year":1980,
                    "month":10,
                    "day":10
                },
                "email":customer_info['email'],
                "phone":customer_info['phone']
            }
            headers = {
                "Content-Type":"application/json",
                "Authorization" : "Basic cHJpdmF0ZS03NzUxOkItcWEyLTAtNWYwMzFjZGQtMC0zMDJkMDIxNDQ5NmJlODQ3MzJhMDFmNjkwMjY4ZDNiOGViNzJlNWI4Y2NmOTRlMjIwMjE1MDA4NTkxMzExN2YyZTFhODUzMTUwNWVlOGNjZmM4ZTk4ZGYzY2YxNzQ4",
                "Simulator" : "EXTERNAL",
                "Access-Control-Allow-Origin":"*"
            }
            body = json.dumps(j_data)
            #res = requests.post("https://api.test.paysafe.com/paymenthub/v1/customers", body, headers = headers)
            #print(res.json())
            customer_id = "a0959a5e-ed56-4bc5-a415-a400db5c3a6f"
            customer_info['customer_id'] = customer_id
            return render_template('checkout.html',config = api,  customer = customer_info, add = billing_info, data = data, dob = dateOfBirth)
    else:
        return render_template('login.html')

@app.route('/tokens', methods = ['POST'])
def token():
    if g.user:
        headers = {
        "Content-Type":"application/json",
            "Authorization" : "Basic cHJpdmF0ZS03NzUxOkItcWEyLTAtNWYwMzFjZGQtMC0zMDJkMDIxNDQ5NmJlODQ3MzJhMDFmNjkwMjY4ZDNiOGViNzJlNWI4Y2NmOTRlMjIwMjE1MDA4NTkxMzExN2YyZTFhODUzMTUwNWVlOGNjZmM4ZTk4ZGYzY2YxNzQ4",
            "Simulator" : "EXTERNAL",
            "Access-Control-Allow-Origin":"*"
        }
        data = {
        "merchantRefNum": request.form['merchantRefNum'],
        "paymentTypes":["CARD"]
        }
        body = json.dumps(data)
        id = request.form['consumerId']
        url = "https://api.test.paysafe.com/paymenthub/v1/customers/"+id+"/singleusecustomertokens"
        print(url)
        res = requests.post(url, body, headers = headers)
        j_res = res.json()
        print(j_res['singleUseCustomerToken'])
        res = {"singleUseCustomerToken": j_res['singleUseCustomerToken']}
        return jsonify(res)
    else:
        render_template('login.html')

@app.route('/saved', methods = ['GET','POST'])
def save_card():
    if g.user:
        if request.method == 'POST':
                #print(request.body)
                data ={
                    "merchantRefNum":request.form['merchantRefNum'],
                    "amount":request.form['amount'],
                    "currencyCode": "USD",
                    "dupCheck":True,
                    "settleWithAuth":False,
                    "paymentHandleToken":request.form['paymentHandleToken'],
                    "customerIp":"172.0.0.1",
                    "description":"some"
                }
                headers ={
                    "Content-Type":"application/json",
                    "Authorization" : "Basic cHJpdmF0ZS03NzUxOkItcWEyLTAtNWYwMzFjZGQtMC0zMDJkMDIxNDQ5NmJlODQ3MzJhMDFmNjkwMjY4ZDNiOGViNzJlNWI4Y2NmOTRlMjIwMjE1MDA4NTkxMzExN2YyZTFhODUzMTUwNWVlOGNjZmM4ZTk4ZGYzY2YxNzQ4",
                    "Simulator" : "EXTERNAL",
                    "Access-Control-Allow-Origin":"*"
                }
                body = json.dumps(data)
                res = requests.post(
                    "https://api.test.paysafe.com/paymenthub/v1/payments",
                    body, headers = headers
                )
                print(res.status_code)
                if res.status_code == 201:
                    response = {
                        'success':True,
                        'id':res.json()['id']
                    }
                    return res.content
                else:
                    return response.status("400")
    else:
        render_template('login.html')

@app.route('/payment_successfull/')
def payment_successfull(request):
        if g.user:
                return render_template('payment_successfull.html')
        else:
                return render_template('login.html')

def payment_unsucessful(request):
        if request.user.is_authenticated:
                return render(request, 'payment_unsucessful.html')
        else:
                return render_template('login.html')
@app.route('/payment_handle_not_created/')
def payment_handle_not_created(request):
        if g.user:
                return render_template('payment_handle_not_ceated.html')
        else:
                return render_template('login.html')

if __name__=="__main__":
    app.debug = True
    app.run(host = "0.0.0.0",port = 5000)
