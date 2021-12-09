#coding=utf-8
from flask import Flask,request,flash,render_template
from forms import RegisterForms
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib
from time import time


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.secret_key = '2dass21'
app.config['SQLALCHEMY_DATABASE_URI'] =   "sqlite:///"+os.path.join(basedir +"\\database\\", "database123.db")

db = SQLAlchemy(app)
class userInfo(db.Model):
    username = db.Column(db.String(50),primary_key = True)
    hash_pwd = db.Column(db.String(100))
    salt = db.Column(db.String(100))

    def __init__(self,username,hash_pwd,salt):
        self.username = username
        self.hash_pwd = hash_pwd
        self.salt = salt

#加密函数
def get_hash_value(pwd,salt):
    hash = hashlib.sha256(salt.encode('utf-8'))
    hash.update(pwd.encode('utf-8'))
    hash_value = hash.hexdigest()
    return hash_value

#注册
@app.route('/register',methods = ['POST','GET'])
def register():
    form3 = RegisterForms()
    if request.method == 'GET':
        return render_template('register.html',form = form3)
    elif request.method == 'POST':
        if form3.validate_on_submit():
            if not request.form['username'] or not request.form['password'] or not request.form['password1']:
                flash('failed!','error')
                return 'error!'
            else:
                user=request.form['username']
                passw=request.form['password'] 
                res = userInfo.query.filter_by(username = user).all()
                if len(res) == 0:
                   salt = str(time())
                   hash_pwd = get_hash_value(passw,salt)
                   data = userInfo(user,hash_pwd,salt)
                   db.session.add(data)
                   db.session.commit()
                   return '注册成功！'
                else:
                    return '重复注册！'
        else:
            return 'failed'  

if __name__ == '__main__':
    app.run(debug=True)