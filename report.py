import json
from flask import Blueprint, redirect, render_template, request, url_for

from flask_login import current_user
from flask_user import roles_required

import db_connection

bp = Blueprint('report_disease', __name__, url_prefix='/report')


@bp.route('/')
@roles_required(['Admin', 'IT', 'Other_Role'])
def report_event():
	"""上报单病种页面
		可选 sbm: string (SBM)
	"""
	# 这里sbm帮助定位
	SBM = request.args.get('sbm')

	major_report_structure = json.load(open('static/datafile/ks_dbz.json', encoding='utf-8'))
	# 主要的本科室上报的病种
	major_report_structure = major_report_structure[current_user.major] if len(major_report_structure[
																				   current_user.major]) > 0 else []

	# 分组情况
	group_structure = json.load(open('static/datafile/report_structure.json'), encoding='utf-8')

	return render_template('report_page.html', sbm=SBM, structure=group_structure,
						   major_structure=major_report_structure)


@bp.route('/<operation_id>', methods=['GET', 'POST'])
@roles_required(['Admin', 'IT', 'Other_Role'])
def new_form(operation_id):
	"""
	获取病人信息并生成表格数据，传递至前端
	operation_id: 单病种代码
	"""
	# 需要填报的sbm
	reported_sbm = request.args.get('sbm')
	if request.method == 'GET':
		# 单病种字段数据
		zdmData = db_connection.generate_report_by_dbz(operation_id)
		dbz_name = db_connection.get_dbz(operation_id)

		# reorganised_zdm, groups = reorganise(zdmData)

		# 单病种字段选项
		# xzData = db_connection.generate_report_options_by_dbz(operation_id)
		xzData = json.load(open('static/datafile/test/xz.json', encoding='utf-8'))
		if reported_sbm:
			# 从数据库摘取这条信息
			patientData = db_connection.get_patient_case(reported_sbm)
			zzys = db_connection.get_user(patientData['ZZYS'])
			zdmData = json.load(open('static/datafile/test/cs_zdm.json', encoding='utf-8'))
			reorganised_zdm = reorganised_2(zdmData)

			return render_template('new_report_form_2.html',
								   zdm=reorganised_zdm,
								   xz=xzData,  # 选择型字段选择项
								   patient=patientData,
								   dbz_name=dbz_name,  # 单病种名称
								   zzys=zzys  # 主治医师
								   )

		# return render_template('new_report_form.html',
		# 					   zdm=reorganised_zdm,  # 分组及字段，字段类型，字段在报告中出现的条件等
		# 					   xz=xzData,  # 选择型字段选择项
		# 					   groups=groups,  # 分组信息，这个可能不需要
		# 					   patient=patientData,  # 病人信息
		# 					   major=current_user.major,  # 主治医生专业
		# 					   user_name=current_user.xm,  # 现在的用户姓名
		# 					   dbz_name=dbz_name,  # 单病种名称
		# 					   zzys=zzys)  # 主治医师
		else:
			# sbm为空，代表没有选择病例，跳转病例选择页面，并传递operation_id（单病种id）
			return redirect(url_for('main_table', operation_id=operation_id))

	elif request.method == 'POST':
		# 已通过前端验证提交表单
		request_data = json.loads(request.data)
		sbm = request_data['sbm']
		dbz = request_data['dbz']  # 单病种id
		dbz_name = request_data['dbz_name']  # 病种名称
		cykb = request_data['cykb']  # 出院科别
		zzys = request_data['zzys']  # 主治医生
		zzysks = request_data['zzysks']  # 主治医生科室
		txys = request_data['txys']  # 填写医生
		finishedDate = request_data['finishedDate']  # 完成日期
		status = request_data['status']  # 状态
		data = request_data['data']  # 表格数据
		sbks = current_user.major  # 上报科室

		return {'outcome': True, 'next': '/main'}, 200


@bp.route('/draft', methods=['GET', 'POST'])
@roles_required(['Admin', 'IT', 'Other_Role'])
def save_as_draft():
	"""处理草稿箱"""
	if request.method == 'POST':
		request_data = json.loads(request.data)
		# 	传入数据和new_form post一样，但finished date为空，状态为草稿或废弃
		return {'outcome': True, 'next': '/main'}, 200
	elif request.method == 'GET':
		# TODO 提取所有草稿为Array并作为drafts变量传递
		return render_template('drafts.html', drafts=[])


@bp.route('/draft/get')
@roles_required(['Admin', 'IT', 'Other_Role'])
def get_draft():
	"""查找草稿功能 - 根据参数提取草稿, 根据起始时间或关键词查找"""
	start_date = request.args.get('start_date')
	end_date = request.args.get('end_date')
	query = request.args.get('query')

	# 检索并返回数据
	return {'data': [{}]}, 200


def reorganise(zdmData):
	"""根据分组重新整理分类表单项
	返回Dict
	key:
		{"name": "分组名group_name",
		"data": []
		}

	如：
	"data": ['26', 'CS-1-1-1', '产次', '字符串', '是', 'null', 'not null', 'varchar(max)', ...]
	"""
	organised_zdm = dict()
	group = dict()
	for data in zdmData:
		# print(data)
		key = data['group']
		if not organised_zdm.get(key):
			# 过滤是否已存在基本信息
			jbxx_key = next((key for key, value in organised_zdm.items() if value['name'] == '基本信息'), None)
			if data['group_name'] == '基本信息' and jbxx_key:
				# 	如果存在已基本键值对，并且本行也是基本信息
				organised_zdm[jbxx_key]['data'].append(data)
			else:
				organised_zdm[key] = {"name": data['group_name'], "data": [data]}
				group[key] = data['group_name']
		else:
			organised_zdm[key]['data'].append(data)

	print(organised_zdm)
	return organised_zdm, group


def reorganised_2(zdmData):
	organised_zdm = dict()
	rawData = []
	for row in zdmData.values():
		rawData = rawData + row['data']

	for data in rawData:
		key = data['分组代号']
		# print(key)
		if not organised_zdm.get(key):
			# 过滤是否已存在分组名称
			duplicated_key = next((key for key, value in organised_zdm.items() if value.get('数据采集项目') == data[
				'分组名称']), None)
			if duplicated_key:
				organised_zdm[duplicated_key]['data'].append(data)
			else:
				organised_zdm[key] = {"数据采集项目": data['分组名称'], "data": [data]}

		else:
			organised_zdm[key]['data'].append(data)

	organised_zdm = dict(sorted(organised_zdm.items()))

	for x in organised_zdm:
		organised_zdm[x]['data'] = sorted(organised_zdm[x]['data'], key=lambda y: y['字段名称'])

	return organised_zdm
