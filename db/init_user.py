import json
import uuid

from CsvReader import csvReader
from model import *


def init(db_conn, user_manager):
	# 新建小兵 '123123test' , 'Password123' 无角色分配
	if not User.query.filter(User.username == '123123test').first():
		user = User(id=str(uuid.uuid4()), username='123123test', password=user_manager.hash_password('Password123'),
		            xm='qinqing')
		db_conn.session.add(user)
		db_conn.session.commit()

	# 新建admin '123123admin', 'adminPassword', admin角色
	if not User.query.filter(User.username == '123123admin').first():
		user = User(id=str(uuid.uuid4()), username='123123admin', password=user_manager.hash_password(
			'adminPassword'), xm='qinqingAdmin')
		# 添加角色
		user.roles.append(Role(name='Admin'))
		db_conn.session.add(user)
		db_conn.session.commit()

	# 新建IT department '123123it', 'itPassword', IT部门角色
	if not User.query.filter(User.username == '123123it').first():
		user = User(id=str(uuid.uuid4()), username='123123it', password=user_manager.hash_password(
			'itPassword'), xm='qinqingIT')
		# 添加角色
		user.roles.append(Role(name='IT'))
		db_conn.session.add(user)
		db_conn.session.commit()


# data = csvReader('pgc_form/zdm.csv').read()[1::]
# options = csvReader('pgc_form/xz.csv').read()[1::]
#
# if not SingleDisease.query.filter(SingleDisease.id == 'CS').first():
# 	db_conn.session.add(SingleDisease(id='CS', name='剖宫产'))
# 	db_conn.session.commit()
# for line in data:
# 	if not DiseaseItem.query.filter(DiseaseItem.id == line[1]).first():
# 		db_conn.session.add(
# 			DiseaseItem(
# 				id=line[1],
# 				name=line[2],
# 				group=format_group_id(line),
# 				group_name=get_group_name(format_group_id(line)),
# 				type=line[3],
# 				sql_type=line[7],
# 				nullable=line[4],
# 				related_id=line[8],
# 				related_id_condition=line[9],
# 				min=line[10],
# 				max=line[11],
# 			)
# 		)
# 		db_conn.session.commit()
#
# for line in options:
# 	if not DiseaseItemOptions.query.filter(DiseaseItem.id == line[1], DiseaseItemOptions.value == line[2]).first():
# 		db_conn.session.add(DiseaseItemOptions(disease_item_id=line[1], id=str(uuid.uuid4()), value=line[2],
# 		                                       label=line[3]))
# 		db_conn.session.commit()


def format_group_id(data):
	key_id = [data[1].split("-")[0], data[1].split("-")[1]] if len(data[1].split("-")) > 2 else data[1]
	key = "-".join(key_id) if type(key_id) != str else key_id
	return key


def get_group_name(key):
	try:
		if groups[key]:
			return groups[key]
	except KeyError:
		return groups['']


groups = json.load(open('static/datafile/disease_item_groups.json', encoding='utf-8'))
