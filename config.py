#coding=utf-8
import os
import sys
import json
basedir = os.path.abspath(os.path.dirname(__file__))
system_type = sys.platform

#get Parameters
paras = None
para_path = basedir +os.sep + "parameters.json"
if os.path.isfile(para_path) == True:
    try:
        with open(para_path) as f:
            paras = json.load(f)
            
    except:
        Error2 = Exception("读取json异常!")
        raise Error2
else:
    Error1 = Exception("读取参数失败!")
    raise Error1

class DataBaseConfig(object):
    DEBUG = True
    if system_type == 'win32':
        #windows
        SQLALCHEMY_DATABASE_URI =   "sqlite:///"+os.path.join(basedir +"\\database\\", "database123.db")
    elif system_type == 'linux':
        #linux
        SQLALCHEMY_DATABASE_URI =   "sqlite:///"+os.path.join(basedir +"/database/", "database123.db")


class EmailConfig(object):
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = paras["MAIL_USERNAME"]
    MAIL_PASSWORD = paras["MAIL_PASSWORD"]
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True



class Config:
    SECRET_KEY = '21e2eddqe'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
