#coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class DataBaseConfig(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI =   "sqlite:///"+os.path.join(basedir +"\\database\\", "database123.db")

class EmailConfig(object):
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = '1300202481@qq.com'
    MAIL_PASSWORD = 'univlugrxnlbhcdd'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True



class Config:
    SECRET_KEY = '21e2eddqe'
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    # FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
