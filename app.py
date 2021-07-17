import json
import random
from flask import Flask, render_template, request

import Patient
import pgc
import test
from CsvReader import csvReader
from TableTypes import Table_Type

app = Flask(__name__)

# add route /chart_demo here
app.register_blueprint(test.bp)

# add gpc route
app.register_blueprint(pgc.bp)


@app.route('/')
def hello_world():
	"""主页"""
	return 'Hello World!'


@app.route('/main')
def main_table():
	# 这里请求得到数据库数据，这里以数据文件为例
	reader = csvReader("test_main_data.csv").read()

	# 初始化病人model列表
	patient_list = Patient.mapper(reader, Table_Type.MAIN)

	return render_template('index_table.html', tableData=patient_list)


@app.route('/main/edit', methods=["POST"])
def edit_patient():
	# 这里Id帮助定位
	Id = request.args.get('id')
	print(json.loads(request.data))
	# 更改DB数据
	# 测试
	if Id == '7519d739-a8b3-4fbc-9313-31e571fad76f':
		# 可以直接返回200或者200+消息
		# return 200
		return {'msg': 'error message from server'}, 404
	else:
		return {'msg': 'success message from server'}, 201


@app.route('/operation')
def operation_table():
	# 这里请求得到数据库数据，这里以数据文件为例
	reader = csvReader("operation_test_data.csv").read()

	# 初始化病人model列表
	patient_list = Patient.mapper(reader, Table_Type.OPERATION)

	return render_template('operation_table.html', tableData=patient_list)


@app.route('/diagnosis')
def diagnosis_table():
	# 这里请求得到数据库数据，这里以数据文件为例
	reader = csvReader("diagnosis_test_data.csv").read()

	# 初始化病人model列表
	patient_list = Patient.mapper(reader, Table_Type.DIAGNOSIS)

	return render_template('diagnosis_table.html', tableData=patient_list)


@app.route('/updateData')
def getData():
	"""请求并返回数据"""
	return {'data': random.randint(0, 200)}, 200


@app.context_processor
def my_utility_processor():
	def existsInLists(target, lists):
		return any(target in sublist for sublist in lists)
	return dict(existsInLists=existsInLists)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port='8080', debug=True)
