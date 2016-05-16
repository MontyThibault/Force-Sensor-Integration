import pickle

calibration_file = 'C:/Users/Monty/Desktop/forcePlates/MayaIntegration/calibration/calib.txt'

class Calibration(object):
	def __init__(self, name = False, load = True):
		self.name = name
		self.offset = 0
		self.gain = 1

		self.last = 0

		if name and load:
			self.load()

	def process(self, c):
		self.last = c

		return (c + self.offset) * self.gain

	def setZero(self, c = None):
		if c is None:
			c = self.last

		self.offset = -c

	def setOne(self, c = None):
		if c is None:
			c = self.last

		self.gain = 1.0 / (c + self.offset)

	def load(self):
		if not self.name:
			print("Trying to load calibration data with unspecified name. %s" % self.name)
			return

		file = open(calibration_file, 'rb')
		dictionary = pickle.load(file)
		file.close()

		if self.name not in dictionary:
			print("Trying to load non-existant calibration data. %s" % self.name)
			return

		(self.offset, self.gain) = dictionary[self.name]


	def save(self):
		if not self.name:
			print("Trying to load calibration data with unspecified name. %s" % self.name)
			return

		file = open(calibration_file, 'rb')
		dictionary = pickle.load(file)
		file.close()

		dictionary[self.name] = (self.offset, self.gain)

		file = open(calibration_file, 'wb')
		pickle.dump(dictionary, file)
		file.close()