import sqlite3

from flask import g


def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect("db/test.db")
		g.db.row_factory = dict_factory

	return g.db


def close_db(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()


def dict_factory(cursor, row):
	d = {}
	for idx, col in enumerate(cursor.description):
		d[col[0]] = row[idx]
	return d


def generate_report_by_dbz(operation_id):
	# 根据单病种类型提起单病种字段
	return get_db().cursor().execute('select zd.id as id, zd.name as name, "group", zd.group_name as group_name, '
	                                 'zd.type as '
	                                 'type, zd.sql_type as sql_type, zd.nullable as nullable, zd.related_id as related_id, '
	                                 'zd.related_id_condition as related_id_condition, zd.min as min, zd.max as max from '
	                                 'dbz_zd zd left join dbz_and_dbz_zd dadz on zd.id = dadz.dbz_zd_id left join dbz on '
	                                 'dbz.id = dadz.dbz_id where dbz.id=?', (operation_id,)).fetchall()


def generate_report_options_by_dbz(operation_id):
	# 提取单病种报告选项
	return get_db().cursor().execute('select xz.dbz_id as dbz_id, xz.option as option, xz.label as label '
	                                 'from '
	                                 'dbz_xz as xz left join dbz_and_dbz_zd dadz on xz.dbz_id = dadz.dbz_zd_id '
	                                 'join dbz on dadz.dbz_id = dbz.id where dbz.id=? and xz.dbz=?', (operation_id,
	                                                                                                  operation_id)).fetchall()


def get_patient_case(patient_sbm):
	# 根据sbm提取病例
	return get_db().cursor().execute('select * from Patients where SBM=?', (patient_sbm,)).fetchone()


def get_dbz(dbz):
	return get_db().cursor().execute('select * from dbz where dbz.id=?', (dbz,)).fetchone()
