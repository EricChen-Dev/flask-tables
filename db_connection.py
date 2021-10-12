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
