import json
import os.path
import re
import csv
from tempfile import NamedTemporaryFile

from CsvReader import csvReader

tempfile = NamedTemporaryFile(mode='w', delete=False)
groups = json.load(open('../static/datafile/disease_item_groups.json', encoding='utf-8'))


def reformat():
	dbz_names = json.load(open('../static/datafile/report_structure.json', encoding='utf-8'))
	dbz_ids = ['AECOPD', 'CAC', 'CACC', 'Cap', 'Cap-Adult', 'OIT', 'PT', 'TSCC', 'DKD', 'DPD', 'HD', 'aSAH', 'CSE',
	           'GLI', 'ICH', 'MEN', 'PA', 'PD', 'STK', 'TIA', 'CS', 'DG', 'UM', 'AF', 'ASD', 'AVR', 'CABG', 'HF', 'MVR',
	           'STEMI', 'VSD', 'PACG', 'RD', 'DDH', 'Hip', 'Knee', 'BC', 'CC', 'CoC', 'GC', 'LC', 'TC', 'ALL', 'APL',
	           'DVT', 'HBIPS', 'HBV', 'PIP', 'SEP', 'TN', 'VTE']
	# for main in dbz_names:
	# 	for item in dbz_names[main]:
	# 		dbz_ids.append(list(item.values())[0])

	# print(dbz_ids)

	for dbz_id in dbz_ids:
		data = []
		zdm_filename = "{0}-zdm.csv".format(dbz_id)

		# xz_filename = "{0}-xz.csv".format(dbz_id)
		with open(os.path.join('../static/datafile/dbz_form/', zdm_filename), mode='r+', encoding='utf-8') as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				condition = []
				note = re.findall(re.compile(r'[(](.*?)[)]',re.S), row[6])
				if len(note) == 1:
					print(row[6])
					print(note)


if __name__ == '__main__':
	reformat()
