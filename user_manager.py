import json
import uuid
from flask import abort, redirect, render_template, request

from flask_login import current_user, login_user, logout_user
from flask_user import UserManager, UserMixin, login_required, user_manager
from model import *


class CustomUserManager(UserManager):
	"""重构flask-user UserManager"""

	# override login, register view here
	def login_view(self):
		""" 验证 username 并且登录有效用户."""
		next_url = request.args.get('next')
		safe_next_url = next_url if next_url else '/main'

		# 如果是已经登录的用户直接跳转到后续链接
		if self.call_or_get(current_user.is_authenticated) and self.USER_AUTO_LOGIN_AT_LOGIN:
			return redirect(safe_next_url)

		if request.method != 'POST':
			return render_template('login.html')
		else:
			request_data = json.loads(request.data)
			# 取得输入的账号和密码
			username = request_data['username']
			password = request_data['password']
			generatedUser = User.query.filter(User.username == username).first()
			if generatedUser:
				if UserManager.verify_password(self, password, generatedUser.password):
					login_user(generatedUser, safe_next_url)
					return {'outcome': True, 'next': safe_next_url}, 200
				else:
					return {'outcome': False}, 200
			else:
				return {'outcome': False}, 200

	def logout_view(self):
		"""登出"""
		logout_user()
		return redirect('/')

	def register_view(self):
		"""注册新用户"""
		safe_reg_next_url = request.args.get('next') if request.args.get('next') else '/main'
		if request.method != 'POST':
			return render_template('register.html')
		else:
			# 处理注册请求
			request_data = json.loads(request.data)

			username = request_data['username']
			password = request_data['password']
			xm = request_data['xm']
			major = request_data['major']

			if not User.query.filter(User.username == username).first():
				# 如果这个用户名不存在，新建用户并保存至数据库
				new_user = User(id=str(uuid.uuid4()), username=username,
				                password=user_manager.hash_password(password),
				                xm=xm, major=major)
				new_user.roles.append(Role(name='Other_Role'))  # 这里赋予角色
				# new_user.roles.append(Role(name='Other_Role2'))  # 这里赋予角色
				db.session.add(new_user)
				db.session.commit()
				if self.USER_AUTO_LOGIN_AFTER_REGISTER:
					login_user(new_user, safe_reg_next_url)
					return {'outcome': True, 'next': safe_reg_next_url}
				else:
					return {'outcome': True, 'next': '/login'}

			else:
				return {'outcome': False, 'msg': '用户名已被占用'}

	def unauthorized_view(self):
		return abort(401)
