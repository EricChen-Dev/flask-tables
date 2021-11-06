import json
from flask import Blueprint, render_template, request

from flask_login import current_user
from flask_user import roles_required

import db_connection
from model import *

bp = Blueprint('report_disease', __name__, url_prefix='/report')


@bp.route('/')
@roles_required(['Admin', 'IT', 'Other_Role'])
def report_event():
	"""上报单病种页面
		可选 sbm: string (SBM)
	"""
	# 这里idh帮助定位
	SBM = request.args.get('sbm')

	major_report_structure = json.load(open('static/datafile/ks_dbz.json', encoding='utf-8'))
	# 主要的本科室上报的病种
	major_report_structure = major_report_structure[current_user.major] if len(major_report_structure[
		                                                                           current_user.major]) > 0 else []

	# 分组情况
	group_structure = json.load(open('static/datafile/report_structure.json'), encoding='utf-8')

	print(group_structure)
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

	# 单病种字段数据
	zdmData = db_connection.generate_report_by_dbz(operation_id)
	dbz_name = db_connection.get_dbz(operation_id)
	reorganised_zdm, groups = reorganise(zdmData)
	# 单病种字段选项
	xzData = db_connection.generate_report_options_by_dbz(operation_id)

	if reported_sbm:
		# 从数据库摘取这条信息
		patientData = db_connection.get_patient_case(reported_sbm)
		return render_template('new_report_form.html', zdm=reorganised_zdm, xz=xzData, groups=groups,
		                       patient=patientData, major=current_user.major, user=current_user, dbz_name=dbz_name)
	else:
		return 404


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
	for data in zdmData:
		key = data['group']
		if not organised_zdm.get(key):
			organised_zdm[key] = {"name": data['group_name'], "data": []}
		organised_zdm[key]['data'].append(data)

	return organised_zdm, list(organised_zdm.keys())
