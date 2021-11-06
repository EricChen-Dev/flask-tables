import csv
import json
import os.path
import re
import sqlite3
from sqlite3 import IntegrityError
from tempfile import NamedTemporaryFile

tempfile = NamedTemporaryFile(mode='w', delete=False)
groups = json.load(open('static/datafile/disease_item_groups.json', encoding='utf-8'))
db_path = os.path.join(os.getcwd(), "db", "test.db")
db = sqlite3.connect(db_path)
db.row_factory = lambda cursor, row: row[0]


def reformat():
	print(db_path)

	dbz_names = json.load(open('static/datafile/report_structure.json', encoding='utf-8'))

	# 整理并将单病种id和中文名放入dbz表
	for major in dbz_names:

		for items in dbz_names[major]:
			dbz_id = items
			val = dbz_names[major][items]
			try:
				db.execute("insert into dbz values (?,?,?)", (val, dbz_id, major))
				db.commit()
			except IntegrityError:
				db.rollback()

	# 将单病种报告单条显示条件进行整理
	dbz_ids = db.execute("select id from dbz").fetchall()
	for dbz_id in dbz_ids:
		zdm_filename = "{0}-zdm.csv".format(dbz_id)

		xz_filename = "{0}-xz.csv".format(dbz_id)

		# 处理选项表
		with open(os.path.join('static/datafile/dbz_form/', xz_filename), mode='r+', encoding='utf-8') as xz_csv:
			print("正在处理单病种 - {0}填报选择...".format(dbz_id))
			reader = list(csv.reader(xz_csv))[2::]  # 跳过前两行
			for row in reader:
				x_id = row[1]
				option = row[2]
				label = row[3]
				dbz = dbz_id
				try:
					if not db.execute("select * from dbz_xz where dbz_id=? and label=? and option=? and dbz=?", (x_id,
					                                                                                             label,
					                                                                                             option,
					                                                                                             dbz
					                                                                                             )).fetchall():
						db.execute("insert into dbz_xz values (?,?,?,?)", (x_id, option, label, dbz))
						db.commit()
				except Exception:
					db.rollback()

		# 处理字段表格 - 非完美
		with open(os.path.join('static/datafile/dbz_form/', zdm_filename), mode='r+', encoding='utf-8') as csvfile:
			print("正在处理单病种 - {0}填报表单条件...".format(dbz_id))
			reader = list(csv.reader(csvfile))[2::]
			for row in reader:
				condition = []
				note = re.findall(re.compile(r'[(](.*?)[)]', re.S), row[6])

				if len(note) == 2:
					if not db.execute("select * from dbz_zd where id=?", (row[1],)).fetchall():
						try:
							group = find_group(row[1], dbz_id)
							try:
								group_name = groups[group]
							except KeyError:
								group_name = groups["CM-0"]
							db.execute("insert into dbz_zd values (?,?,?,?,?,?,?,?,?,?,?)", (
								row[1], row[2], group, group_name, row[3], '', row[4], note[0], note[1], None, None
							))
							db.commit()

						except IntegrityError:
							db.rollback()

				elif len(note) >= 1:
					if not db.execute("select * from dbz_zd where id=?", (row[1],)).fetchall():
						try:
							group = find_group(row[1], dbz_id)
							group_name = groups[group]
							print("note is: {0}".format(note))
							print(row[6])
							inputs = input("please enter: ")

							if 'delete' in inputs or 'del' in inputs:
								delete_index = inputs.split('//')[1::]
								for index in delete_index:
									note.remove(index)
								print(note)
								db.execute("insert into dbz_zd values (?,?,?,?,?,?,?,?,?,?,?)", (
									row[1], row[2], group, group_name, row[3], '', row[4], note[0], note[1], None, None
								))
								db.commit()

							elif 'add' in inputs and 'addrange' not in inputs:
								values = inputs.split('-')[1::]
								for val in values:
									note.append(val)
								print(note)
								db.execute("insert into dbz_zd values (?,?,?,?,?,?,?,?,?,?,?)", (
									row[1], row[2], group, group_name, row[3], '', row[4], note[0], note[1], None, None
								))
								db.commit()

							elif 'addrange' in inputs:
								values = inputs.split('-')[1::]
								for val in values:
									note.append(val)
								print(note)
								db.execute("insert into dbz_zd values (?,?,?,?,?,?,?,?,?,?,?)", (
									row[1], row[2], group, group_name, row[3], '', row[4], None, None, note[1], note[2],
								))
								db.commit()


							else:
								db.execute("insert into dbz_zd values (?,?,?,?,?,?,?,?,?,?,?)", (
									row[1], row[2], group, group_name, row[3], '', row[4], None, None, None, None,
								))
								db.commit()


						except KeyError:
							group_name = groups["CM-0"]
						except IntegrityError:
							db.rollback()


				elif len(note) == 0:
					try:
						group = find_group(row[1], dbz_id)
						try:
							group_name = groups[group]
						except KeyError:
							group_name = groups["CM-0"]
						if not db.execute("select * from dbz_zd where id=?", (row[1],)).fetchall():
							db.execute("insert into dbz_zd values (?,?,?,?,?,?,?,?,?,?,?)", (
								row[1], row[2], group, group_name, row[3], '', row[4], None, None, None, None,
							))
							db.commit()
					except IntegrityError:
						db.rollback()

				# 写入dbz_and_dbz_zd表格用于join
				try:
					if not db.execute("select * from dbz_and_dbz_zd where dbz_id=? and dbz_zd_id=?",
					                  (dbz_id, row[1])).fetchall():
						db.execute("insert into dbz_and_dbz_zd values (?,?)", (dbz_id, row[1]))
						db.commit()
				except IntegrityError:
					db.rollback()


def find_group(dbz_item_id, dbz_id):
	try:
		span = dbz_item_id.split(dbz_id)
		return "{0}{1}".format(dbz_id, span[1][0:2])
	except IndexError:
		return "CM-0"


if __name__ == '__main__':
	reformat()
