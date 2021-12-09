import itertools
import json
import random
import sqlite3
from flask import Flask, render_template, request
from itertools import zip_longest

from flask_login import current_user
from flask_user import login_required

import Patient
import admin
import db_connection
import errorHandler
import report
from CsvReader import csvReader
from TableTypes import Table_Type
from db.init_user import init as init_user
from db_connection import get_db
from model import *


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
	USER_REGISTER_URL = '/register'  # 注册用户路由


def create_app():
	"""flask app generator"""

	app = Flask(__name__)
	app.config.from_object(__name__ + '.ConfigClass')  # 导入配置

	# Flask-SqlAlchemy and init
	from model import db
	db.init_app(app)
	from user_manager import CustomUserManager
	# 关联 User模型和flask-user
	user_manager = CustomUserManager(app, db, User)
	# 建表
	with app.app_context():
		db.create_all()
		init_user(db, user_manager)

	# add /report route
	app.register_blueprint(report.bp)
	app.register_blueprint(admin.bp)

	# add error page /404, /401
	app.register_error_handler(404, errorHandler.page_not_found)
	app.register_error_handler(401, errorHandler.unauthorized)

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
		cursor_results = get_db().cursor().execute("select * from Patients where ZZYS = '{0}' limit "
												   "200".format(current_user.xm)).fetchall()
		major_cases = db_connection.get_cases_with_same_major(current_user.major)
		print(len(major_cases))
		return render_template('index_table.html', tableData=cursor_results, major_cases=major_cases)

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
		patients_list = get_db().cursor().execute(sql).fetchall()
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
		def existsInXzLists(target, lists):
			return any(target == sublist['dbz_id'] for sublist in lists)

		def grouper(n, iterable_list, compared_list, fillValue=None):
			reorganised = iterable_list.copy()
			if compared_list:
				for item in iterable_list:
					if item not in compared_list:
						reorganised.pop(item)
			args = [iter(reorganised)] * n
			return zip_longest(fillvalue=fillValue, *args)

		def grouper_more(n, iterable_list, fillValue=None):
			reorganised = iterable_list.copy()
			args = [iter(reorganised)] * n
			return zip_longest(fillvalue=fillValue, *args)

		def dictValues(Dict):
			return list(itertools.chain.from_iterable(Dict.values()))

		return dict(existsInXzLists=existsInXzLists, grouper=grouper, grouper_more=grouper_more, dictValues=dictValues)

	return app


if __name__ == '__main__':
	flask_app = create_app()
	flask_app.run(host='0.0.0.0', port='8080', debug=True)
