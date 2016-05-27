#coding=utf-8
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy
from app import db,app
from hashlib import md5
from datetime import datetime
import os

user_user_concern=db.Table('user_user_concern',
db.Column('user1_id',db.Integer,db.ForeignKey('user.id'),primary_key=True),
db.Column('user2_id',db.Integer,db.ForeignKey('user.id'),primary_key=True))
user_user_blacklist=db.Table('user_user_blacklist',
db.Column('user1_id',db.Integer,db.ForeignKey('user.id'),primary_key=True),
db.Column('user2_id',db.Integer,db.ForeignKey('user.id'),primary_key=True))

class User(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	nickname=db.Column(db.String(80),unique=True)
	password=db.Column(db.String(120))
	email=db.Column(db.String(120),unique=True)
	information=db.Column(db.String(250))
	posts=db.relationship('Post',backref='author',lazy='dynamic')
	has_avatar=db.Column(db.Integer,default=0)
	create_time=db.Column(db.DateTime,default=datetime.now())
	messages=db.relationship('Message',backref='people',lazy='dynamic')
	
	concern=db.relationship('User',secondary=user_user_concern,primaryjoin=id==user_user_concern.c.user1_id,
	secondaryjoin=id==user_user_concern.c.user2_id,backref='concerned')
	blacklist=db.relationship('User',secondary=user_user_blacklist,primaryjoin=id==user_user_blacklist.c.user1_id,
	secondaryjoin=id==user_user_blacklist.c.user2_id,backref='blackedlist')
	
	is_authenticated=True
	is_active=True
	is_anonymous=False
	
	def __init__(self,nickname,password,email):
		self.nickname=nickname
		self.password=password
		self.email=email
		self.information=u'这个人很懒,什么都没有写...'
		
	def get_id(self):
		try:
			return unicode(self.id)
		except NameError:
			return str(self.id)
	
	def avatar(self):
		if self.has_avatar:
			return '/static/avatar/'+self.nickname+'.jpg'
		else:
			return url_for('static',filename='favicon.ico')
	
	def has_concern(self,user):
		return self.concern.count(user)
		
	def has_concerned(self,user):
		return self.concerned.count(user)
	
	def has_black(self,user):
		return self.blacklist.count(user)
	
	def count_new_message(self):
		return Message.query.filter_by(user_id=self.id,has_showed=0).count()
	
	def is_admin(self):
		return Admin.query.filter_by(nickname=self.nickname).first() is not None
	
	def __repr__(self):
		return '<User %r>' % self.nickname
	
class Post(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	title=db.Column(db.String(80))
	body=db.Column(db.Text)
	date=db.Column(db.DateTime)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
		
	def __init__(self,title,body,author):
		self.title=title
		self.body=body
		self.date=datetime.now()
		self.author=author
	
	def __repr__(self):
		return '<Post %r>' % self.body

class Message(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	content=db.Column(db.Text)
	user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
	date=db.Column(db.DateTime)
	has_showed=db.Column(db.Integer,default=0)
	
	def __init__(self,content,people):
		self.content=content
		self.people=people
		self.date=datetime.now()
	
	def __repr__(self):
		return '<%r>' % self.content
		
class Admin(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	nickname=db.Column(db.String(80),unique=True)
	
	def __repr__(self):
		return '<User %r>' % self.nickname
		
class PublicConfig(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	sicily_message=db.Column(db.String(500))
	
	def __repr__(self):
		return '<'+self.sicily_message+'>'