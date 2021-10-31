import json
from flask import Blueprint, render_template, request

from flask_login import current_user
from flask_user import roles_required

from CsvReader import csvReader
from db_connection import get_db
from model import *

bp = Blueprint('report_disease', __name__, url_prefix='/report')
report_structure = json.load(open('static/datafile/report_structure.json'), encoding='utf-8')


@bp.route('/')
@roles_required(['Admin', 'IT', 'Other_Role'])
def report_event():
	"""上报单病种页面
		可选 sbm: string (SBM)
	"""
	# 这里idh帮助定位
	SBM = request.args.get('sbm')

	major_report_structure = json.load(open('static/datafile/ks_dbz.json', encoding='utf-8'))
	major_report_structure = major_report_structure[current_user.major] if len(major_report_structure[
		                                                                           current_user.major]) > 0 else []
	return render_template('report_page.html', sbm=SBM, structure=report_structure,
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
	print(reported_sbm, operation_id)

	zdmData = get_db().cursor().execute('select zd.id as id, zd.name as name, "group", zd.group_name as group_name, '
	                                  'zd.type as '
	                          'type, zd.sql_type as sql_type, zd.nullable as nullable, zd.related_id as related_id, '
	                          'zd.related_id_condition as related_id_condition, zd.min as min, zd.max as max from '
	                          'dbz_zd zd left join dbz_and_dbz_zd dadz on zd.id = dadz.dbz_zd_id left join dbz on '
	                          'dbz.id = dadz.dbz_id where dbz.id=?', (operation_id,)).fetchall()
	# reorganised_zdm = reorganise(groups, zdmData)

	if reported_sbm:
		# 从数据库摘取这条信息
		cursor_result = get_db().cursor().execute("select * from Patients where SBM='{0}'".format(
			reported_sbm)).fetchone()
		return render_template('new_report_form.html', zdm=reorganised_zdm, xz=xzData, groups=groups,
		                       patient=cursor_result, major=current_user.major)
	else:
		return 404


def reorganise(groups, zdm):
	"""根据分组重新整理分类表单项
	返回Dict
	key:[value]
	如：
	CS-1: ['26', 'CS-1-1-1', '产次', '字符串', '是', 'null', 'not null', 'varchar(max)', ...]
	"""
	organised_zdm = dict()
	optioned = dict()
	for group in groups:
		# 为每个信息新建空组，键值为前缀，如 CS-1
		organised_zdm[str(group).split(' ')[0]] = []

	for data in zdm:
		key_id = [data[1].split("-")[0], data[1].split("-")[1]] if len(data[1].split("-")) > 2 else data[1]
		key = "-".join(key_id) if type(key_id) != str else key_id  # 键值 如CS-1
		if data[9]:
			data[9] = str(data[9]).lower()  # 转小写
		if organised_zdm.get(key) is not None:
			# 如果存在这个分类就归入这个分类下
			organised_zdm.get(key).append(data)
		else:
			# 其他情况，如果字段中有CM、caseId、SBM、IDCard归入基本信息
			organised_zdm.get("基本信息").append(data)

	print(organised_zdm)
	return organised_zdm
