#coding=utf-8
from flask import Flask,render_template,request,flash,url_for,redirect,session,jsonify,g
from forms import UserForms,StudentsInfoForms,SearchIdForms,RegisterForms,UploadFileForms
from werkzeug.utils import  secure_filename
from config import DataBaseConfig,Config
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
import hashlib
import xlrd
import time


app = Flask(__name__)
app.config.from_object(DataBaseConfig)
app.config.from_object(Config)

#定义数据库模型
db = SQLAlchemy(app)
class studentsInfo(db.Model):
    id = db.Column('student_id', db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    sex = db.Column(db.String(50))
    date = db.Column(db.String(50)) 
    nation = db.Column(db.String(50))
    height = db.Column(db.String(50))
    idCard = db.Column(db.String(50))
    PhoneNumber = db.Column(db.String(50)) 
    address = db.Column(db.String(50))
    teacher = db.Column(db.String(50))
    hobbies = db.Column(db.String(50))

    def __init__(self,id,name,sex,date,nation,height,idCard,PhoneNumber,address,teacher,hobbies):
        self.id = id
        self.name = name
        self.sex = sex
        self.date = date
        self.nation = nation
        self.height = height
        self.idCard = idCard
        self.PhoneNumber = PhoneNumber
        self.address = address
        self.teacher = teacher
        self.hobbies = hobbies

class userInfo(db.Model):
    username = db.Column(db.String(50),primary_key = True)
    hash_pwd = db.Column(db.String(100))
    salt = db.Column(db.String(100))

    def __init__(self,username,hash_pwd,salt):
        self.username = username
        self.hash_pwd = hash_pwd
        self.salt = salt

#hash加密
def get_hash_value(pwd,salt):
    hash = hashlib.sha256(salt.encode('utf-8'))
    hash.update(pwd.encode('utf-8'))
    hash_value = hash.hexdigest()
    return hash_value

#检查登录
def login_required(func):
    @wraps(func) # 修饰内层函数，防止当前装饰器去修改被装饰函数的属性
    def inner(*args, **kwargs):
        # 从session获取用户信息，如果有，则用户已登录，否则没有登录
        user_id = session.get('user_id')
        #print("session user_id:", user_id)
        if not user_id:
            # WITHOUT_LOGIN是一个常量
            return jsonify({'error':'User not logged in'}
                           )
        else:
            # 已经登录的话 g变量保存用户信息，相当于flask程序的全局变量
            g.user_id = user_id
            return func(*args, **kwargs)
    return inner

#重定向到登陆页面
@app.route('/',methods = ['POST','GET'])
def index():
    if 'user_id' in session:
       return redirect('home') 
    else:
        return redirect('login')

#注册
@app.route('/register',methods = ['POST','GET'])
def register():
    form = RegisterForms()
    if request.method == 'GET':
        return render_template('register.html',form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user=request.form['username']
            passw=request.form['password'] 
            res = userInfo.query.filter_by(username = user).all()
            if len(res) == 0:
                salt = str(time.time())
                hash_pwd = str(get_hash_value(passw,salt + '@@'))
                data = userInfo(user,hash_pwd,salt)
                db.session.add(data)
                db.session.commit()
                return redirect('login')
            else:
                dic1 = {'title':'fail','message':'重复注册！'}
                return render_template('info.html',dic1 = dic1)
        else:
            return render_template('register.html',form = form) 

#登录
@app.route('/login',methods = ['POST','GET'])
def login():
    form = UserForms()
    if request.method == 'GET':
        return render_template('login.html',form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user=request.form['username']
            passw=request.form['password'] 
            res = userInfo.query.filter_by(username = user). all()
            if len(res) == 1:
                #获取对应的salt
                for i in res:
                    dict_user = i.__dict__
                #print(dict_user)
                new_pwd = get_hash_value(passw,dict_user['salt'] + '@@')
                if new_pwd == dict_user['hash_pwd']:
                    # dic1 = {'title':'ok','message':'验证成功！'}
                    # return render_template('info.html',dic1 = dic1)
                    session['user_id'] = user
                    return redirect(url_for('management'))
                else:
                    dic1 = {'title':'error','message':'密码错误或用户不存在！'}
                    return render_template('info.html',dic1 = dic1)
            else:
                dic1 = {'title':'error','message':'密码错误或用户不存在！'}
                return render_template('info.html',dic1 = dic1)
        else:
            return render_template('login.html',form = form)       

#管理
@app.route('/addStudents',methods = ['POST','GET'])
@login_required
def addStudents():
    form = StudentsInfoForms()
    if request.method == 'GET':
        return render_template('addStudents.html',form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            #写入数据库
            #id name sex date nation height	idCard PhoneNumber address teacher hobbies
            try:
                id = request.form['id']
                name = request.form['name']
                sex = request.form['sex']
                date = request.form['date']
                nation = request.form['nation']
                height = request.form['height']
                idCard = request.form['idCard']
                PhoneNumber = request.form['PhoneNumber']
                address = request.form['address']
                teacher = request.form['teacher']
                hobbies = request.form['hobbies']
                db.session.add(studentsInfo(id ,name, sex, date, nation, height,idCard, PhoneNumber, address, teacher, hobbies))
                db.session.commit()
                dic1 = {'title':'success','message':'导入成功！'}
                return render_template('info.html',dic1 = dic1)
            except:
                db.session.rollback()
                dic1 = {'title':'error','message':'导入失败！'}
                return render_template('info.html',dic1 = dic1)
            finally:
                db.session.close()
        else:
            return render_template('addStudents.html',form = form)

#批量导入学生信息
@app.route('/upload',methods = ['POST','GET'])
@login_required
def upload():
    form = UploadFileForms()
    if request.method == 'POST':
        if form.validate_on_submit():
            #通过表单验证
            f = request.files['file']
            file_extension = str(f.filename).split('.')[1]
            file_name = str(time.time()).replace('.','') + '.' + file_extension
            f.save(os.getcwd()+'\\Temp\\'+secure_filename(file_name))
            #打开文件
            if '.xlsx'  in file_name or '.xls' in file_name :
                table_head = ['学号','姓名','性别','出生年月','民族','身高','身份证号码','家长电话','家庭住址','班主任','兴趣爱好']
                work_book = xlrd.open_workbook(os.getcwd()+'\\Temp\\'+file_name)
                work_sheet = work_book.sheet_by_name('Sheet1')
                data_list = []
                if work_sheet.row_values(0) == table_head:
                    try:
                        for i in range(1,work_sheet.nrows):
                            excelData = work_sheet.row_values(i)
                            id,name,sex,date,nation,height,idCard,PhoneNumber,address,teacher,hobbies = excelData
                            data_list.append(studentsInfo(id,name,sex,date,nation,height,idCard,PhoneNumber,address,teacher,hobbies))
                        db.session.add_all( data_list)
                        db.session. commit()
                    except:
                        db.session.rollback()
                        dic1 = {'title':'SQLerror','message':'导入SQL失败！'}
                        return render_template('info.html',dic1 = dic1)
                        
                    else:
                        dic1 = {'title':'success','message':'导入SQL成功！'}
                        return render_template('info.html',dic1 = dic1)
                    finally:
                        db.session.close()
                        #xlrd 1.2 版本的workbook 没有close方法
                        work_book.release_resources()
                        #os.remove(os.getcwd()+'\\Temp\\'+file_name)
                else:
                    dic1 = {'title':'error','message':'excel文件数据错误，请检查excel文件！'}
                    return render_template('info.html',dic1 = dic1)
            else:
                dic1 = {'title':'error','message':'excel文件传输错误！'}
                return render_template('info.html',dic1 = dic1)
                
        else:
            return render_template('upload.html',form = form)
    elif request.method == 'GET':
        return render_template('upload.html',form = form)

#批量导入用户
@app.route('/uploadUser',methods = ['POST','GET'])
@login_required
def uploadUser():
    form = UploadFileForms()
    if request.method == 'POST':
        if form.validate_on_submit():
            #通过表单验证
            f = request.files['file']
            file_extension = str(f.filename).split('.')[1]
            file_name = str(time.time()).replace('.','') + '.' + file_extension
            f.save(os.getcwd()+'\\Temp\\'+secure_filename(file_name))
            #打开文件
            if '.xlsx'  in file_name or '.xls' in file_name :
                table_head = ['用户名','密码']
                work_book = xlrd.open_workbook(os.getcwd()+'\\Temp\\'+file_name)
                work_sheet = work_book.sheet_by_name('Sheet1')
                data_list = []
                if work_sheet.row_values(0) == table_head:
                    try:
                        for i in range(1,work_sheet.nrows):
                            time.sleep(0.001)
                            excelData = work_sheet.row_values(i)
                            username,password = excelData
                            time_salt = time.time()
                            salt = str(time_salt)
                            hash_pwd = get_hash_value(password,salt + '@@')
                            data_list.append(userInfo(username = str(username),hash_pwd= hash_pwd,salt = salt))
                            #data_list.append((username,hash_pwd,salt))
                        
                        db.session.add_all(data_list)
                        db.session.commit()
                    except:
                        db.session.rollback()
                        dic1 = {'title':'SQLerror','message':'导入SQL失败！'}
                        return render_template('info.html',dic1 = dic1)
                        
                    else:
                        dic1 = {'title':'success','message':'导入SQL成功！'}
                        return render_template('info.html',dic1 = dic1)
                    finally:
                        db.session.close()
                        #xlrd 1.2 版本的workbook 没有close方法
                        work_book.release_resources()
                        #os.remove(os.getcwd()+'\\Temp\\'+file_name)
                else:
                    dic1 = {'title':'error','message':'excel文件数据错误，请检查excel文件！'}
                    return render_template('info.html',dic1 = dic1)
            else:
                dic1 = {'title':'error','message':'excel文件传输错误！'}
                return render_template('info.html',dic1 = dic1)
        else:
            return render_template('uploadUser.html',form = form)
    elif request.method == 'GET':
        return render_template('uploadUser.html',form = form)

#退出登录
@app.route('/logout',methods = ['POST','GET'])
@login_required
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return render_template('logout.html')
        
#查询
@app.route('/home',methods = ['POST','GET'])
@login_required
def home():
    form2 = SearchIdForms()
    if request.method == 'GET':
        return render_template('home.html',form = form2)
    elif request.method == 'POST':
        if form2.validate_on_submit():
            searchId = request.form['searchId']
            if str.isdigit(searchId):
                data = studentsInfo.query.filter_by(id = searchId).all()
                #print(type(data))
                if len(data) == 1: 
                    dic2 = data[0].__dict__
                    return render_template('data.html',dic = dic2)
                else:
                    dic1 = {'title':'fail','message':'查询错误！'}
                    return render_template('info.html',dic1 = dic1)
            else:
                data = studentsInfo.query.filter_by(name = searchId).first()
                
                if data:
                    dic2 = data.__dict__
                    return render_template('data.html',dic = dic2)
                else:
                    #未查询到数据，报错
                    dic1 = {'title':'fail','message':'查询错误！'}
                    return render_template('info.html',dic1 = dic1)       
        else:
            return render_template('home.html',form = form2)

#管理页面
@app.route('/management',methods = ['POST','GET'])
@login_required
def management():
    return render_template('management.html')


if __name__ == '__main__':
    db.create_all()
    app.run(host = '0.0.0.0',debug = True)
