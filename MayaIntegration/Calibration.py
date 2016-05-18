import pickle
import os
import unittest

class Calibration(object):
	""" Defines an affine transformation on a single input. """

	def __init__(self, name = False, load = True):
		self.name = name
		self.offset = 0
		self.gain = 1

		# The last 
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
		(self.offset, self.gain) = LoadHelper.load(self.name)

	def save(self):
		LoadHelper.save(self.name, (self.offset, self.gain))

	def delete(self):
		""" Deletes the calibration entry, not the instance. """
		LoadHelper.delete(self.name)
		


class SixAxisCalibrationMatrix(object):
	""" Defines a 6x6 matrix from the voltages to the output channels. The 
	calibrations are sourced from the manufacturer and should be already
	saved within the calibration file. """

	def __init__(self, name = False, load = True):
		self.name = name
		
		if name and load:
			self.load()
		else:

			# 6x6 identity of nested lists
			self.matrix = []
			for i in range(6):
				self.matrix.append([int(i == j) for j in range(6)])


	def process(self, vec):
		""" Performs matrix multiplication.

		vec: a six-vector to process. For instance: [0, 1, .. 5] will return a list 
		[0', 1', .. 5'] where `'`' denotes the calibrated version of the corresponding
		channels. """

		out_vec = []

		for i in range(6):

			row = self.matrix[i]
			out_vec[i] = 0

			for j in vec:
				out_vec[i] += i * j

		return out_vec


	def load(self):
		self.matrix = LoadHelper.load(self.name)

	def save(self):
		LoadHelper.save(self.name, self.matrix)

	def delete(self):
		""" Deletes calibration entry, not the instance. """
		LoadHelper.delete(self.name)


class LoadHelper(object):
	""" Keeps calibration data persistent between sessions. This class defines 
	a simple interface from which other functions can read and write aribtrary
	data to a dictionary stored in a file somewhere in the system. """

	# Append to Calibration.py's directory
	calibration_file = os.path.realpath(__file__) + "/calibration/calib.txt"

	@staticmethod
	def _getdict():
		file = open(self.calibration_file, 'rb')
		dictionary = pickle.load(file)
		file.close()

		return dictionary

	@staticmethod
	def _savedict(dictionary):
		file = open(self.calibration_file, 'rb')
		pickle.dump(file, dictionary)
		file.close()

	@staticmethod
	def exists(key):
		if not key:
			return False

		return key in dictionary

	@staticmethod
	def load(key):
		if not self.exists(key):
			return False

		return self._getdict()[key]
	
	@staticmethod
	def save(key, value):
		if not self.exists(key)
			return False

		dictionary = self._getdict()
		dictionary[key] = value

		self._savedict(dictionary)

	@staticmethod
	def delete(key):
		if not self.exists(key)
			return False

		dictionary = self._getdict()
		dictionary.pop(key, None)

		self._savedict(dictionary)

	@staticmethod
	def clear():
		self._savedict({})



class Tests(unittest.TestCase):

	def calibrate_single_number(self):

		x = Calibration()

		self.assertEqual(x.process(5), 5)

		x.setZero()
		x.setOne(10)

		self.assertEqual(x.process(15), 2)

	def save_single_calibration(self):

		x = Calibration()
		x.offset = 10

		x.name = 'test'
		x.save()
		x.offset = 15
		x.load()

		self.assertEqual(x.offset, 10)

		x.delete()

	def save_and_delete_new_persistent_entry(self):

		LoadHelper.save('test', hash(self))
		self.assertEqual(LoadHelper.load('test'), hash(self))

		LoadHelper.delete('test')
		self.assertEqual(LoadHelper.exists('test'), False)


	def calibrate_matrix_test_and_save(self):

		x = SixAxisCalibrationMatrix()
		self.assertEqual(x.process([1, 2, 3, 4, 5, 6]), [1, 2, 3, 4, 5, 6])

		x[2][3] = 1
		self.assertEqual(x.process([0, 0, 0, 1, 0, 0]), [0, 0, 1, 0, 0, 0])

		x.name = 'test'
		x.save()

		x[2][3] = 0

		x.load()
		self.assertEqual(x.process([0, 0, 0, 1, 0, 0]), [0, 0, 1, 0, 0, 0])

		x.delete()