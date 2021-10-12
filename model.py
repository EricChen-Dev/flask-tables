from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
	"""用户模型，用于登陆"""
	__tablename__ = 'users'
	id = db.Column(db.String(), primary_key=True)

	# 需要验证的信息
	username = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
	password = db.Column(db.String(255), nullable=False, server_default='')

	# 用户信息
	xm = db.Column(db.String(30, collation='NOCASE'), nullable=False, server_default='')
	major = db.Column(db.String(255), nullable=False, server_default='')
	active = db.Column(db.Boolean(), default=True)
	# 用户角色
	roles = db.relationship('Role', secondary='user_roles')


class Role(db.Model):
	"""用户角色"""
	__tablename__ = 'roles'
	id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
	name = db.Column(db.String(50))


class UserRoles(db.Model):
	__tablename__ = 'user_roles'
	id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
	role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


class SingleDisease(db.Model):
	"""51个单病种，上报单病种用"""
	__tablename__ = 'dbz'
	id = db.Column(db.String(50), primary_key=True)  # 单病种病种id， 如 CS
	name = db.Column(db.String(255))  # 单病种病种名称，如 剖腹产
	zd = db.relationship('DiseaseItem')  # 单病种包含的条目


class DiseaseItem(db.Model):
	"""每个单病种条目，上报单病种用"""
	__tablename__ = 'dbz_zd'
	dbz_id = db.Column(db.String(50), db.ForeignKey('dbz.id'))  # 所属单病种的ID
	id = db.Column(db.String(50), primary_key=True)  # 如CS-1-1-1, caseId
	name = db.Column(db.String(255), nullable=False)  # 字段名称，如质控医师
	group = db.Column(db.String(50))  # id组 如，CS-1，定位用
	group_name = db.Column(db.String(255))  # id组名 如 剖宫产术前评估
	type = db.Column(db.String(20))  # 上传时数据类型
	sql_type = db.Column(db.String(20))  # 数据库存储数据类型
	nullable = db.Column(db.String(20))  # 可否为空

	# 当关联字段和关联字段条件达成时此条才能出现
	related_id = db.Column(db.String(50))  # 关联字段，
	related_id_condition = db.Column(db.String(50))  # 关联字段条件

	# 最大最小值
	min = db.Column(db.Integer())  # 可取的最小值
	max = db.Column(db.Integer())  # 可取的最大值

	options = db.relationship('DiseaseItemOptions')  # 可选值


class DiseaseItemOptions(db.Model):
	"""单病种条目可选项"""
	disease_item_id = db.Column(db.String(50), db.ForeignKey('dbz_zd.id'))
	id = db.Column(db.String, primary_key=True)
	value = db.Column(db.String(50))  # 选项值
	label = db.Column(db.String(50))  # 选项内容
