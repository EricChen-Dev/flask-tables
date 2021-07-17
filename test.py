from flask import Blueprint, render_template

bp = Blueprint('chart_demo', __name__, url_prefix='/test')


@bp.route('/chart_demo', methods=['GET'])
def chart_demo():
    return render_template('chart_demo/chart.html')


@bp.route('/getLiveData', methods=['GET'])
def getLiveData(data):
    """返回载入数据"""
    return data, 200
