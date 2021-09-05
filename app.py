import itertools
import json
import random
import sqlite3
import uuid
from flask import Flask, abort, g, redirect, render_template, request
from itertools import zip_longest

from flask_babelex import Babel
from flask_login import current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_user import UserManager, UserMixin, login_required

import Patient
import errorHandler
import report
import test
from CsvReader import csvReader
from TableTypes import Table_Type


class ConfigClass(object):
	"""
	flask application configuration class
	flask全局配置类
	"""
	# flask settings
	SECRET_KEY = 'DO NOT USE IN PRODUCTION'

	# sqlalchemy 数据库链接
	SQLALCHEMY_DATABASE_URI = 'sqlite:///db/test.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

	USER_APP_NAME = "flask-table"  # 你的app名字
	USER_ENABLE_USERNAME = True  # 启用 username 验证
	USER_ENABLE_EMAIL = False  # 关闭 email 验证
	USER_AUTO_LOGIN = True  # 如果session未到期，自动登陆
	USER_USER_SESSION_EXPIRATION = 86400  # session过期时间为24小时 = 86400秒

	USER_LOGIN_URL = '/login'  # 登录路由
	USER_LOGOUT_URL = '/logout'  # 登出路由
	USER_REGISTER_URL = '/register'  # 注册路由


def create_app():
	"""flask app generator"""

	app = Flask(__name__)
	app.config.from_object(__name__ + '.ConfigClass')  # 导入配置

	# flask-babelex
	babel = Babel(app)

	# Flask-SqlAlchemy
	db = SQLAlchemy(app)

	# add route /chart_demo here
	app.register_blueprint(test.bp)

	# add /report_disease route
	app.register_blueprint(report.bp)

	# add error page /404, /401
	app.register_error_handler(404, errorHandler.page_not_found)
	app.register_error_handler(401, errorHandler.unauthorized)

	# User data model
	class User(db.Model, UserMixin):
		__tablename__ = 'users'
		id = db.Column(db.String(), primary_key=True)

		# 需要验证的信息
		username = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
		password = db.Column(db.String(255), nullable=False, server_default='')

		# 用户信息
		xm = db.Column(db.String(30, collation='NOCASE'), nullable=False, server_default='')
		active = db.Column(db.Boolean())
		# 用户角色
		roles = db.relationship('Role', secondary='user_roles')

	class Role(db.Model):
		__tablename__ = 'roles'
		id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
		name = db.Column(db.String(50), unique=True)

	class UserRoles(db.Model):
		__tablename__ = 'user_roles'
		id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
		user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
		role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

	class CustomUserManager(UserManager):
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
				username = request.form.get('username')
				password = request.form.get('password')
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
			safe_reg_next_url = self._get_safe_next_url('reg_next', self.USER_AFTER_REGISTER_ENDPOINT)
			if request.method != 'POST':
				# return render_template('login.html')
				return "registration page"
			else:
				username = request.form.get('username')
				password = request.form.get('password')
				xm = request.form.get('xm')

				if not User.query.filter(User.username == username).first():
					# 如果这个用户名不存在，新建用户并保存至数据库
					new_user = User(id=str(uuid.uuid4()), username=username,
					                password=user_manager.hash_password(password),
					                xm=xm)
					new_user.roles.append(Role(name='Other_Role'))  # 这里赋予角色
					new_user.roles.append(Role(name='Other_Role2'))  # 这里赋予角色
					db.session.add(new_user)
					db.session.commit()
					if self.USER_AUTO_LOGIN_AFTER_REGISTER:
						return self._do_login_user(new_user, '/')
					else:
						return redirect('/login')

		def unauthorized_view(self):
			return abort(401)

	# 关联 User模型和flask-user
	user_manager = CustomUserManager(app, db, User)

	# 建表
	db.create_all()

	# 新建小兵 '123123test' , 'Password123' 无角色分配
	if not User.query.filter(User.username == '123123test').first():
		user = User(id=str(uuid.uuid4()), username='123123test', password=user_manager.hash_password('Password123'),
		            xm='qinqing')
		db.session.add(user)
		db.session.commit()

	# 新建admin '123123admin', 'adminPassword', admin角色
	if not User.query.filter(User.username == '123123admin').first():
		user = User(id=str(uuid.uuid4()), username='123123admin', password=user_manager.hash_password(
			'adminPassword'), xm='qinqingAdmin')
		# 添加角色
		user.roles.append(Role(name='Admin'))
		db.session.add(user)
		db.session.commit()

	# 新建IT department '123123it', 'itPassword', IT部门角色
	if not User.query.filter(User.username == '123123it').first():
		user = User(id=str(uuid.uuid4()), username='123123it', password=user_manager.hash_password(
			'itPassword'), xm='qinqingIT')
		# 添加角色
		user.roles.append(Role(name='IT'))
		db.session.add(user)
		db.session.commit()

	# 一级路由
	# 任意角色都可以进
	@app.route('/')
	def hello_world():
		"""主页"""
		return 'Hello World!'

	# /main路径只能登陆的用户看到
	@app.route('/main')
	@login_required
	def main_table():
		# 这里请求得到数据库数据，这里以数据文件为例
		# reader = csvReader("test_main_data.csv").read()
		cursor_results = get_db().cursor().execute("select * from Patients limit 200").fetchall()
		# 初始化病人model列表
		patient_list = Patient.mapper(cursor_results, Table_Type.MAIN)

		return render_template('index_table.html', tableData=patient_list)

	@app.route('/main/edit', methods=["POST"])
	@login_required
	def edit_patient():
		"""编辑病人信息"""
		request_data = json.loads(request.data)
		print(request_data)
		# 这里sbm帮助定位
		sbm_id = request_data['SBM']
		return {'msg': '修改失败'}, 400

		# 更改DB数据
		update_sql = "update Patients " \
		             "set RYSJ='{0}', CYSJ='{1}', ZFY={2} where SBM='{3}'" \
			.format(request_data['RYSJ'], request_data['CYSJ'], request_data['ZFY'], request_data['SBM'])
		try:
			get_db().cursor().execute(update_sql)
			get_db().commit()
			return {'msg': '修改成功'}, 201

		except sqlite3.Error:
			get_db().rollback()

	@app.route('/main/get_patients')
	@login_required
	def get_patients():
		query = request.args.get('query')
		sql = "select * from Patients where XM='{0}' or SBM='{0}' or IDH='{0}'".format(str(query))
		cursor_results = get_db().cursor().execute(sql)
		patients_list = Patient.mapper(cursor_results, Table_Type.MAIN)
		# print(patients_list)
		return {'data': patients_list}, 200

	@app.route('/operation')
	@login_required
	def operation_table():
		# 这里请求得到数据库数据，这里以数据文件为例
		reader = csvReader("operation_test_data.csv").read()

		# 初始化病人model列表
		patient_list = Patient.mapper(reader, Table_Type.OPERATION)

		return render_template('operation_table.html', tableData=patient_list)

	@app.route('/diagnosis')
	@login_required
	def diagnosis_table():
		# 这里请求得到数据库数据，这里以数据文件为例
		reader = csvReader("diagnosis_test_data.csv").read()

		# 初始化病人model列表
		patient_list = Patient.mapper(reader, Table_Type.DIAGNOSIS)

		return render_template('diagnosis_table.html', tableData=patient_list)

	@app.route('/updateData')
	@login_required
	def getData():
		"""请求并返回数据"""
		return {'data': random.randint(0, 200)}, 200

	@app.context_processor
	def my_utility_processor():
		def existsInLists(target, lists):
			return any(target in sublist for sublist in lists)

		def grouper(n, iterable, fillValue=None):
			args = [iter(iterable)] * n
			return zip_longest(fillvalue=fillValue, *args)

		def dictValues(Dict):
			return list(itertools.chain.from_iterable(Dict.values()))

		return dict(existsInLists=existsInLists, grouper=grouper, dictValues=dictValues)

	@login_required
	def get_db():
		_db = getattr(g, '_database', None)
		if _db is None:
			_db = g._database = sqlite3.connect("db/test.db")
		return _db

	@app.teardown_appcontext
	def close_connection(exception):
		_db = getattr(g, '_database', None)
		if _db is not None:
			_db.close()

	return app


if __name__ == '__main__':
	flask_app = create_app()
	flask_app.run(host='0.0.0.0', port='8080', debug=True)
