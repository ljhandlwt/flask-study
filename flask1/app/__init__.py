#coding=utf-8
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import sys,os
sys.path.append('..')
import config

app=Flask(__name__)
app.config.from_object('config')
app.config['avatar_dir']=os.path.join(config.basedir,'app','static','avatar')
db=SQLAlchemy(app)

lm=LoginManager()
lm.init_app(app)
lm.login_view='login'
lm.login_message=u'请先登录'

from app import views,models