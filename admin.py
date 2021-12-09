import json
from flask import Blueprint, render_template, request

from flask_login import current_user
from flask_user import roles_required

import db_connection

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@roles_required(['Admin'])
def admin_index():
	"""管理员主页"""
	return 'admin', 200
