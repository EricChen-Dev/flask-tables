import datetime
import json
import re
from uuid import uuid4  # uuid4() 随机独立id

from TableTypes import Table_Type


class Patient:
	def __init__(self, Id='',
	             patient_id='',
	             patient_name='',
	             incoming_date='',
	             out_date='',
	             total_expense=0,
	             hospitalised_id='',
	             operation_date='',
	             operation_index='',
	             operation_sort_id='',
	             operation_id='',
	             operation_type='',
	             operation_name='',
	             anesthesia_method='',
	             diagnosis_id='',
	             diagnosis_type='',
	             diagnosis_index=''):
		self.id = Id  # 识别码
		self.patient_id = patient_id  # 病人ID
		self.patient_name = patient_name  # 病人姓名
		self.incoming_date = incoming_date  # 入院日期
		self.out_date = out_date  # 出院日期
		self.total_expense = total_expense  # 总费用
		self.hospitalised_id = hospitalised_id  # 住院号
		self.operation_date = operation_date  # 手术日期
		self.operation_index = operation_index  # 手术序号
		self.operation_sort_id = operation_sort_id  # 手术排序
		self.operation_id = operation_id  # 手术编号
		self.operation_type = operation_type  # 手术类型
		self.operation_name = operation_name  # 手术名称
		self.anesthesia_method = anesthesia_method  # 麻醉方法
		self.diagnosis_id = diagnosis_id  # 诊断编码
		self.diagnosis_type = diagnosis_type  # 诊断类型
		self.diagnosis_index = diagnosis_index  # 序号

	def toJSON(self):
		# return json.dumps(self, default=lambda o: o.__dict__)
		return self.__dict__


def mapper(csvReader, TableType):
	patientList = []
	count = 0
	for row in csvReader:
		if not count == 0:  # 忽略第一行
			if TableType == Table_Type.MAIN:  # 数据为首页数据
				patientList.append(
					Patient(Id=str(uuid4()), patient_id=row[280], patient_name=row[6],
					        incoming_date=StrToDateStr(row[33]), out_date=StrToDateStr(row[37]),
					        total_expense=row[234])
				)  # 这里可以将时间转换或者选择字符形式
			# 数据筛选
			elif TableType == Table_Type.OPERATION:
				patientList.append(
					Patient(Id=str(uuid4()), patient_id=row[0], patient_name=row[1], incoming_date=StrToDateStr(row[2]),
					        out_date=StrToDateStr(row[3]),
					        hospitalised_id=row[4], operation_date=StrToDateStr(row[5]), operation_index=row[6],
					        operation_sort_id=row[7], operation_id=row[8], operation_type=row[9],
					        operation_name=row[10], anesthesia_method=row[11]))

			elif TableType == Table_Type.DIAGNOSIS:
				print(row)
				patientList.append(
					Patient(Id=str(uuid4()), patient_id=row[0], patient_name=row[1], incoming_date=StrToDateStr(row[3]),
					        out_date=StrToDateStr(row[4]), diagnosis_id=row[7], diagnosis_index=row[5],
					        diagnosis_type=row[6]))
		count += 1

	# 将Patient对象序列化
	return json.dumps(patientList, default=lambda o: o.toJSON())


def StrToDateStr(DateStr):
	# 将时间字符串转为Date对象
	dateList = re.findall("\d+", DateStr)
	# DateStr example: 2020年11月06日16时，但有些没有小时
	if len(dateList) == 4:
		return datetime.datetime(year=int(dateList[0]), month=int(dateList[1]), day=int(dateList[2]),
		                         hour=int(dateList[3])).strftime("%Y-%m-%d")
	else:
		return datetime.datetime(year=int(dateList[0]), month=int(dateList[1]), day=int(dateList[2])).strftime(
			"%Y-%m-%d")


class PatientListJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Patient):
			return obj.toJSON()
		return super(PatientListJsonEncoder, self).dumps(obj)
