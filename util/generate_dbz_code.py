import json
import os.path
import re
import sqlite3
from datetime import datetime

dbz_conditions = json.load(open('../static/datafile/dbz_code_generate_condition.json', encoding='utf-8'))

# 链接db
db_path = os.path.join(os.getcwd(), "..", "db", "test.db")
db = sqlite3.connect(db_path)


def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


db.row_factory = dict_factory  # 返回字典


def generate(date_from="2021/01/01", date_to="2021/05/01"):
	# 默认查找所有2021/01/01 - 2021/05/01病例
	# cursor = db.execute('select * from Patients where CYSJ >= ? and CYSJ <= ?', (date_from, date_to,))
	cursor = db.execute('select * from Patients')
	for case in cursor:
		patient = get_basic_info(case)
		matched = match_case(patient)

		# 结果
		if matched:
			print("SBM: {}, matched dbz code: {}".format(case['SBM'], matched))


def get_basic_info(case):
	# 年龄
	patient = {'age': int(re.search(r'\d+', case['NL']).group())}

	# 住院时长 - 天
	date_format = '%Y/%m/%d %H:%M:%S'
	date_from = datetime.strptime(case['RYSJ'], date_format)
	date_to = datetime.strptime(case['CYSJ'], date_format)
	date_diff = date_to - date_from
	patient['hospital_days'] = int(date_diff.days)

	# 主要诊断
	patient['main_diagnosis'] = case['CYZD_ZYJBBM']
	# 其他诊断
	patient['other_diagnosis'] = case['CYZD_JBBM1']
	# 主要手术
	patient['main_operation'] = case['SSJCZBM1']

	return patient


def match_case(patient):
	query = [patient['main_diagnosis'], patient['other_diagnosis']]
	dbz_matched_codes = []

	def fun(variable):
		if type(variable) is list:
			return len(list(filter(lambda element: variable in element, query))) > 0
		elif type(variable) is str:
			return variable in query
		else:
			return list(variable.keys())[0] in query

	def includes(sequence):
		# sequence is a array may includes str and dict
		return list(filter(fun, sequence))

	def check_main_diagnosis():
		# 是否有吻合的诊断
		if len(dbz.get("if_conditions").get("main_diagnosis")) > 0:
			main_diagnosis_result = includes(dbz.get("if_conditions").get("main_diagnosis"))
			if main_diagnosis_result is not None and len(main_diagnosis_result) > 0:
				return check_discard_diagnosis()
			else:
				return False
		else:
			return check_discard_diagnosis()

	def check_discard_diagnosis():
		# 检查排除项
		try:
			if len(dbz.get("discard_conditions").get("diagnosis")) > 0:
				result = includes(dbz.get("discard_conditions").get("diagnosis"))
				if result is None or len(result) > 0:
					return True
				else:
					return False
			else:
				return True
		except TypeError:
			return True

	def check_main_operation():
		# 是否和操作吻合
		if len(dbz.get("if_conditions").get("main_operation")) > 0:
			main_operation_result = includes(dbz.get("if_conditions").get("main_operation"))
			if main_operation_result is not None and len(main_operation_result) > 0:
				return check_discard_operation()
			else:
				return False
		else:
			return check_discard_operation()

	def check_discard_operation():
		# 检查排除项
		try:
			if len(dbz.get("discard_conditions").get("operation")) > 0:
				result = includes(dbz.get("discard_conditions").get("operation"))
				if result is None or len(result) > 0:
					return True
				else:
					return False
			else:
				return True
		except TypeError:
			return True

	def check_age():
		# 符合年龄要求
		return dbz.get("if_conditions").get('min_age') <= patient.get('age') <= dbz.get(
			"if_conditions").get('max_age')

	def check_hospital_days():
		# 检查住院时长
		if patient.get('hospital_days') <= 90 and dbz.get('discard_conditions').get('hospital_over_90_days'):
			return True
		elif patient.get('hospital_days') <= 365 and dbz.get('discard_conditions').get('hospital_over_365_days'):
			return True
		else:
			return False

	for dbz_code in dbz_conditions.keys():
		dbz = dbz_conditions[dbz_code]
		query = patient.get('main_diagnosis')

		if check_main_diagnosis():
			query = patient.get('main_operation')
			if check_main_operation() and check_age() and check_hospital_days():
				print(patient.get('main_diagnosis'))
				dbz_matched_codes.append(dbz_code)

	if 'dvt' in dbz_matched_codes and 'pip' in dbz_matched_codes:
		# 如果 dvt 和 pip同时存在，只填写dvt
		return 'dvt'
	elif len(dbz_matched_codes) == 1:
		# 如果有且存在一个符合的代码
		return dbz_matched_codes[0]
	else:
		return None


if __name__ == '__main__':
	generate()
