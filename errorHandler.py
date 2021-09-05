from flask import Blueprint, render_template

bp = Blueprint('error', __name__, url_prefix='/error')


@bp.errorhandler(404)
def page_not_found(e):
	# note that we set the 404 status explicitly
	return render_template('404.html'), 404


@bp.errorhandler(401)
def unauthorized(e):
	# note that we set the 401 status explicitly
	return render_template('401.html'), 401
