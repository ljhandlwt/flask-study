#coding=utf-8
from flask import render_template,request,redirect,url_for,flash,abort,g
from flask.ext.login import login_user,logout_user,current_user,login_required
from app import app,db,lm
from models import User,Post,Admin,Message,PublicConfig
from datetime import datetime
import os
from sqlalchemy import or_,not_,and_

@app.route('/')
@app.route('/index')
@login_required
def index():
	posts=Post.query.filter_by(user_id=g.user.id).order_by(Post.date.desc()).limit(3)
	sicily_message=get_public_config().sicily_message
	return render_template('index.html',title='Home',posts=posts,sicily_message=sicily_message)

@app.route('/login',methods=['GET','POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))		
	if request.method=='POST':
		user=User.query.filter_by(nickname=request.form.get('nickname')).first()
		if user is not None:
			if user.password!=request.form.get('password'):
				error=u'密码错误!'
				return render_template('login.html',title="login",error=error)
			else:
				login_user(user)
				flash(u'欢迎回来,'+user.nickname+'!')
				return redirect(url_for('index'))
		else:
			error=u"用户名不存在!"
			return render_template('login.html',title="login",error=error)
	return render_template('login.html',title="login")
	
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))
	
@app.route('/register',methods=['GET','POST'])
def register():
	if request.method=='GET':
		return render_template('register.html',title='register')
	elif request.method=='POST':
		if User.query.filter_by(nickname=request.form.get('nickname')).first() is not None:
			error=u"用户名已存在!"
			return render_template('register.html',title='register',error=error)
		elif User.query.filter_by(email=request.form.get('email')).first() is not None:
			error=u"该邮箱已注册!"
			return render_template('register.html',title='register',error=error)
		else:
			db.session.add(User(request.form.get('nickname'),request.form.get('password'),request.form.get('email')))
			db.session.commit()
			flash(u'注册成功')
			login_user(User.query.filter_by(nickname=request.form.get('nickname')).first())
			return redirect(url_for('index'))

@app.route('/write',methods=['GET','POST'])
@login_required
def write():
	if request.method=='GET':
		return render_template('write.html',title=u'写微博',user=g.user)
	elif request.method=='POST':
		user=User.query.filter_by(nickname=g.user.nickname).first()
		db.session.add(Post(title=request.form.get('title'),body=request.form.get('body'),author=user))
		db.session.commit()
		flash(u'发布成功')
		return redirect(url_for('index'))

@app.route('/concern')
@login_required
def concern():
	posts=Post.query.join(Post.author)\
	.filter(and_(User.id.in_(u.id for u in g.user.concern),or_(not_(User.id.in_(u.id for u in g.user.blackedlist)),g.user.is_admin())))\
	.order_by(Post.date.desc()).limit(30)
	return render_template('concern.html',title=u'关注圈',posts=posts)
		
@app.route('/world')
@login_required
def world():
	posts=Post.query.order_by(Post.date.desc()).limit(30)
	return render_template('world.html',title=u'世界圈',posts=posts)

@app.route('/message')
@login_required
def message():
	messages=Message.query.filter_by(user_id=g.user.id).order_by(Message.date.desc()).limit(30)
	for message in messages:
		message.has_showed=1
	db.session.commit()
	return render_template('message.html',title=u'消息',messages=messages)
		
@app.route('/message/new')
@login_required
def message_new():
	messages=Message.query.filter_by(user_id=g.user.id,has_showed=0).order_by(Message.date.desc()).all()
	for message in messages:
		message.has_showed=1
	db.session.commit()
	return render_template('message_new.html',title=u'新消息',messages=messages)

@app.route('/search/user',methods=['POST'])
@login_required
def search_user():
	nickname=request.form.get('search')
	users=User.query.filter(User.nickname.like('%'+nickname+'%')).all()
	return render_template('search_user.html',title=u'找人',search=nickname,users=users)
	
@app.route('/user')
@login_required
def person():
	return redirect('/user/'+g.user.nickname)
			
@app.route('/user/<nickname>')
@login_required
def personal(nickname):
	user=get_user(nickname)
	if user is not None:
		return render_template('user.html',title=u"个人信息",user=user)
	else:
		abort(404)

@app.route('/user/<nickname>/blog')
@login_required
def personal_blog(nickname):
	user=get_user(nickname)
	if user is not None:
		if g.user not in user.blacklist or g.user.is_admin():
			posts=Post.query.filter_by(user_id=user.id).order_by(Post.date.desc())
		else:
			posts=[]
		return render_template('user_blog.html',user=user,title=nickname+u"的微博",posts=posts)
	else:
		abort(404)

@app.route('/user/<nickname>/concern')
@login_required
def personal_concern(nickname):
	user=get_user(nickname)
	if user is not None:
		return render_template('user_concern.html',title=u'ta关注的人',this_user=user)
	else:
		abort(404)
		
@app.route('/user/<nickname>/concerned')
@login_required
def personal_concerned(nickname):
	user=get_user(nickname)
	if user is not None:
		return render_template('user_concerned.html',title=u'关注ta的人',this_user=user)
	else:
		abort(404)

@app.route('/blacklist')
@login_required
def blacklist():
	return render_template('blacklist.html',title=u'黑名单')
	
@app.route('/admin')
@login_required
def admin():
	if g.user.is_admin():
		return render_template('admin.html',title='admin',users=User.query.all())
	else:
		abort(403)

@app.route('/admin/change_sicily_message',methods=['POST'])
@login_required
def admin_change_sicily_message():
	if g.user.is_admin():
		public_config=get_public_config()
		public_config.sicily_message=request.form.get('sicily_message')
		db.session.commit()
		return redirect(url_for('index'))
	else:
		abort(400)

@app.route('/admin/world_message',methods=['POST'])
@login_required
def admin_world_message():
	if g.user.is_admin():
		message=request.form.get('world_message')
		for user in User.query.all():
			db.session.add(Message(message,user))
		db.session.commit()
		return redirect(url_for('index'))
	else:
		abort(400)


@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
	if request.method=='GET':
		return render_template('settings.html',title=u'修改个人信息')
	elif request.method=='POST':
		if request.form.get('button')==u'确定':
			user=User.query.filter_by(nickname=g.user.nickname).first()
			user.information=request.form.get('information')
			file=request.files['avatar']
			if file:
				file.save(os.path.join(app.config['avatar_dir'],g.user.nickname+'.jpg'))
				user.has_avatar=1
			db.session.commit()
			flash(u'修改成功!')
		return redirect('/user')
	
@app.route('/settings/password',methods=['GET','POST'])
@login_required
def settings_password():
	if request.method=='GET':
		return render_template('settings_password.html',title=u'修改密码')
	elif request.method=='POST':
		if request.form.get('old_password')!=g.user.password:
			error=u'原密码不正确!'
			return render_template('settings_password.html',title=u'修改密码',user=g.user,error=error)
		else:
			user=User.query.filter_by(nickname=g.user.nickname).first()
			user.password=request.form.get('new_password')
			db.session.commit()
			logout_user()
			flash(u'修改密码成功,请重新登录!')
			return redirect(url_for("login"))
		
@app.route('/delete/<id>')
@login_required
def delete(id):
	post=Post.query.get(int(id))
	user=post.author
	if post is not None and (user.id==g.user.id or g.user.is_admin()):
		if g.user.is_admin() and user.id!=g.user.id:
			db.session.add(Message(u'您的一篇微博被管理员删除,标题为:'+post.title,user))
		db.session.delete(post)
		db.session.commit()
		flash(u"删除成功!")
	else:
		abort(400)
	return redirect(url_for("personal_blog",nickname=user.nickname))
		
@app.route('/concern_ta/<id>')
@login_required
def concern_ta(id):
	user=User.query.get(int(id))
	if user is None or g.user.has_concern(user) or g.user.id==user.id:
		abort(400)
	else:
		g.user.concern.append(user)
		db.session.add(Message(g.user.nickname+u'关注了你!',user))
		db.session.commit()
		flash(u'关注ta成功!')
		return redirect(url_for('personal',nickname=user.nickname))
		
@app.route('/unconcern_ta/<id>')
@login_required
def unconcern_ta(id):
	user=User.query.get(int(id))
	if user is not None and g.user.has_concern(user):
		g.user.concern.remove(user)
		db.session.add(Message(g.user.nickname+u'取消关注了你!',user))
		db.session.commit()
		flash(u'取消关注ta成功')
		return redirect(url_for('personal',nickname=user.nickname))	
	else:
		abort(400)	
	
@app.route('/black_ta/<id>')
@login_required
def black_ta(id):
	user=User.query.get(int(id))
	if user is None or g.user.has_black(user):
		abort(400)
	else:
		g.user.blacklist.append(user)
		db.session.commit()
		flash(u'拉黑成功')
		return redirect(url_for('blacklist'))
		
@app.route('/unblack_ta/<id>')
@login_required
def unblack_ta(id):
	user=User.query.get(int(id))
	if user is not None and g.user.has_black(user):
		g.user.blacklist.remove(user)
		db.session.commit()
		flash(u'取消拉黑成功')
		return redirect(url_for('blacklist'))
	else:
		abort(400)
	
@app.errorhandler(404)
def error_404(error):
	return render_template('page_error.html',title='404:Not found',error=u'没有找到这个页面'),404
	
@app.errorhandler(403)
def error_403(error):
	return render_template('page_error.html',title='403:Forbidden',error=u'页面可能被和谐了'),403

@app.errorhandler(405)
def error_405(error):
	return render_template('page_error.html',title='405:Forbidden',error=u'你的打开方式有问题'),405
	
@app.errorhandler(400)
def error_400(error):
	return render_template('page_error.html',title='400:Bad Request',error=u'服务器没法理解这个请求'),400

@app.errorhandler(500)
def error_500(error):
	return render_template('page_error.html',title='500:Internal Server Error',error=u'服务器异常'),500

@app.route('/favicon.ico')
def favicon():
	return redirect(url_for('static',filename='favicon.ico'))
	
@lm.user_loader
def load_user(id):
	return User.query.get(int(id))
	
@app.before_request
def before_request():
	g.user=current_user
	
def get_user(nickname):
	return User.query.filter_by(nickname=nickname).first()
	
def get_public_config():
	return PublicConfig.query.get(1)