import csv


class csvReader:
	def __init__(self, filename):
		self.fileName = filename
		self.path = "static/datafile/" + str(filename)

	def read(self):
		with open(self.path) as csvFile:
			reader = csv.reader(csvFile, delimiter=',')  # csv分隔符为','

			data = []
			for row in reader:
				data.append(row)

			return data
