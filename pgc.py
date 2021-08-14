from flask import Blueprint, render_template

from CsvReader import csvReader

bp = Blueprint('pgc', __name__, url_prefix='/pgc')


@bp.route('/new', methods=['GET', 'POST'])
def new_pgc_form():
	"""新建剖宫产表单"""
	zdmData = csvReader('pgc_form/zdm.csv').read()[1::]  # 截取取第一行之后，这里的zdm可以是不根据字段名称排序过的
	xzData = csvReader('pgc_form/xz.csv').read()[1::]  # 截取第一行之后
	# 摘取到分组信息
	groups = ['基本信息', 'CS-1 剖宫产术前评估', 'CS-2 手术指征', 'CS-3 手术前预防性抗菌药物选用一、二代头孢', 'CS-4 新生儿Apgar评分',
	          'CS-5 输血量', 'CS-6 手术并发症与再次手术情况', 'CS-7 手术相关新生儿并发症', 'CS-8 提供母乳喂养教育情况',
	          'CS-9 住院期间为产妇提供术前、术后健康教育与出院时提供教育告知五要素情况'
	          'CS-10 手术切口愈合情况', 'CS-11 离院方式', 'CS-12 患者对服务的体验与评价', 'CS-13 住院费用']
	# print(xzData)
	# reorganise()会将zdm根据groups进行分组
	reorganised_zdm = reorganise(groups, zdmData)
	return render_template('new_pgc_form.html', zdm=reorganised_zdm, xz=xzData, groups=groups)


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
		key = data[1][0:4]  # 键值 如CS-1
		if data[9]:
			data[9] = str(data[9]).lower()  # 转小写
		if organised_zdm.get(key) is not None:
			# 如果存在这个分类就归入这个分类下
			organised_zdm.get(key).append(data)
		else:
			# 其他情况，如果字段中有CM、caseId、SBM、IDCard归入基本信息
			organised_zdm.get("基本信息").append(data)

	return organised_zdm
