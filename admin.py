import json

from flask import Blueprint, render_template, request
from flask_login import current_user

from flask_user import roles_required

import user_manager
from model import User

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@roles_required(['Admin'])
def admin_index():
	"""管理员主页"""
	# 分组情况
	group_structure = json.load(open('static/datafile/report_structure.json'), encoding='utf-8')
	return render_template('admin_index.html', structure=group_structure)


@bp.route('/searchUser', methods=['POST'])
@roles_required(['Admin'])
def search_user():
	"""依据姓名，科室，用户名查找用户"""
	req = json.loads(request.data)
	xm = req.get('xm')
	major = req.get('major')
	username = req.get('username')

	if User.query.filter(User.username == username, User.xm == xm, User.major == major).first():
		return {'data': True}, 200
	else:
		return {'data': False}, 200
