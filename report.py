from flask import Blueprint, render_template, request

from flask_user import login_required, roles_required

import app
from CsvReader import csvReader

bp = Blueprint('report_disease', __name__, url_prefix='/report')

report_structure = {
	"呼吸系统疾病/手术": [{"慢性阻塞性肺疾病急性发作（住院）": "AECOPD"}, {"哮喘（成人，急性发作，住院）": "CAC"}, {"哮喘（儿童，住院）": "CACC"},
	              {"社区获得性肺炎（儿童，首次住院）": "Cap"},
	              {"社区获得性肺炎（成人，首次住院）": "Cap-Adult"}],
	"口腔系统疾病/手术": [{"口腔种植术": "OIT"}, {"腮腺肿瘤（手术治疗）": "OIT"}, {"舌鳞状细胞癌（手术治疗）": "TSCC"}],
	"泌尿系统疾病/操作": [{"糖尿病肾病": "DKD"}, {"终末期肾病腹膜透析": "DPD"}, {"终末期肾病血液透析": "HD"}],
	"神经系统疾病/手术": [{"急性动脉瘤性蛛网膜下腔出血（初发，手术治疗）": "aSAH"}, {"惊厥性癫痫持续状态": "CSE"}, {"胶质瘤（初发，手术治疗）": "GLI"}, {"脑出血": "ICH"},
	              {"脑膜瘤（初发手术治疗）": "MEN"},
	              {"垂体腺瘤（初发，手术治疗）": "PA"},
	              {"帕金森病": "PD"}, {"脑梗死（首次住院）": "STK"}, {"短暂性脑缺血发作": "TIA"}],
	"生殖系统疾病/手术": [{"剖宫产": "CS"}, {"异位妊娠（手术治疗）": "DG"}, {"子宫肌瘤（手术治疗）": "UM"}],
	"心血管系统疾病/手术": [{"房颤": "AF"}, {"房间隔缺损手术": "ASD"}, {"主动脉瓣置换术": "AVR"}, {"冠状动脉旁路移植术": "CABG"}, {"心力衰竭": "HF"},
	               {"二尖瓣置换术": "MVR"},
	               {"急性心肌梗死（ST 段抬高型，首次住院）": "STEMI"},
	               {"室间隔缺损手术": "VSD"}],
	"眼科系统疾病/手术": [{"原发性急性闭角型青光眼（手术治疗）": "PACG"}, {"复杂性视网膜脱离（手术治疗）": "RD"}],
	"运动系统疾病/手术": [{"发育性髋关节发育不良": "DDH"}, {"髋关节置换术": "Hip"}, {"膝关节置换术": "Knee"}],
	"肿瘤(手术治疗)": [{"乳腺癌（手术治疗）": "BC"}, {"宫颈癌（手术治疗）": "CC"}, {"结肠癌（手术治疗）": "CoC"}, {"胃癌（手术治疗）": "GC"}, {"肺癌（手术治疗）": "LC"},
	             {"甲状腺癌（手术治疗）": "TC"}],
	"其他疾病/手术": [{"儿童急性淋巴细胞白血病（初始诱导化疗）": "ALL"}, {"儿童急性早幼粒细胞白血病（初始化疗）": "APL"}, {"围手术期预防深静脉血栓栓塞": "DVT"}, {"住院精神疾病":
		                                                                                                  "HBIPS"},
	            {"HBV 感染分娩母婴阻断": "HBV"},
	            {"围手术期预防感染": "PIP"}, {"严重脓毒症和脓毒症休克早期治疗": "SEP"}, {"甲状腺结节（手术治疗）": "TN"}, {"中高危风险患者预防静脉血栓栓塞症": "VTE"}]
}


@bp.route('/')
@roles_required(['Admin', 'IT'])
def report_event():
	"""上报单病种页面
		可选 sbm: string (SBM)
	"""
	# 这里idh帮助定位
	SBM = request.args.get('sbm')

	return render_template('report_page.html', sbm=SBM, structure=report_structure)


@bp.route('/<operation_id>', methods=['GET', 'POST'])
@roles_required(['Admin', 'IT'])
def new_form(operation_id):
	"""operation_id: 单病种代码"""
	# 需要填报的sbm
	reported_sbm = request.args.get('sbm')


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

	if reported_sbm:
		# 从数据库摘取这条信息
		cursor_results = app.get_db().cursor().execute("select * from Patients where SBM='{0}'".format(reported_sbm))
		for result in cursor_results:
			print(result)

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
