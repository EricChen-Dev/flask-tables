import csv
import datetime
import re
import sqlite3
from sqlite3 import Error

db_file_path = "test.db"


def initial():
	connection = create_connection(db_file_path)
	# create Patient Table
	# readTableHeadCsv(connection)

	# convert str to date for column RYSJ and CYSJ
	reformatDate(connection)




def create_connection(db_file):
	""" create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		print("connected to db")
		for item in conn.execute('select * from dbz_zd where "name" like "%时间%"').fetchall():
			conn.execute('update dbz_zd set sql_type = ? where id = ?', ('datetime', item[0]))

			conn.commit()
		return conn

	except Error as e:
		print(e)

	return conn


def readTableHeadCsv(DB_Connection):
	sql_create_table = "CREATE TABLE Patients ({0});"
	fileName = "table_heads.csv"
	with open(fileName) as csv_file:
		reader = csv.reader(csv_file, delimiter=',')
		count = 0
		sql_create_table_statements = ""
		temp = []
		for row in reader:
			if not count == 0:  # Ignore 1st line
				if "varchar" in row[2]:
					temp.append("{0} {1} {2}".format(row[1], "varchar(255)", row[3], row[0]))
				else:
					temp.append("{0} {1} {2}".format(row[1], row[2], row[3], row[0]))
			count += 1
		sql_create_table_statements = ",".join(temp)
		sql_create_table = sql_create_table.format(sql_create_table_statements)
		print(sql_create_table)
	DB_Connection.execute(sql_create_table)


def reformatDate(connection):
	# 将原来的字符形式改为DateTime
	results = connection.execute("select SBM, RYSJ, CYSJ from Patients")
	for result in results:
		print(result[1])
		print(result[2])
		RYSJ_datetime = datetime.datetime.strptime(str(result[1]), '%d/%m/%Y %H:%M:%S').strftime('%Y/%m/%d %H:%M:%S')
		CYSJ_datetime = datetime.datetime.strptime(str(result[2]), '%d/%m/%Y %H:%M:%S').strftime('%Y/%m/%d %H:%M:%S')
		sql = "update Patients set RYSJ = '{0}', CYSJ = '{1}' where SBM = '{2}'".format(RYSJ_datetime, CYSJ_datetime,
		                                                                                result[0])
		print(sql)
		connection.execute(sql)

	connection.commit()


def convert_string_to_DateTime(dateStr):
	numbers = re.findall('[0-9]+', dateStr)
	print(numbers)
	return datetime.datetime(int(numbers[0]), int(numbers[1]), int(numbers[2]))


if __name__ == '__main__':
	initial()
