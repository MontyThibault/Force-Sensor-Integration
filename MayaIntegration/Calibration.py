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

		for row in self.matrix:
			out_vec.append(0)

			for i, j in zip(row, vec):
				out_vec[-1] += i * j

		return out_vec


	def load(self):
		assert LoadHelper.exists(self.name), "Error: Attempting to load non-existant SixAxis calibration data: %s" % self.name

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
	calibration_file = os.path.dirname(os.path.realpath(__file__)) + "/calibration/calib.txt"

	@classmethod
	def _getdict(cls):
		file = open(cls.calibration_file, 'rb')
		dictionary = pickle.load(file)
		file.close()

		return dictionary

	@classmethod
	def _savedict(cls, dictionary):
		file = open(cls.calibration_file, 'wb')
		pickle.dump(dictionary, file)
		file.close()

	@classmethod
	def exists(cls, key):
		dictionary = cls._getdict()
		return key in dictionary

	@classmethod
	def load(cls, key):
		return cls._getdict()[key]
	
	@classmethod
	def save(cls, key, value):
		dictionary = cls._getdict()
		dictionary[key] = value

		cls._savedict(dictionary)

	@classmethod
	def delete(cls, key):
		dictionary = cls._getdict()
		dictionary.pop(key, None)

		cls._savedict(dictionary)

	@classmethod
	def clear(cls):
		cls._savedict({})



class Tests(object):
	def test_calibrate_single_number(self):

		x = Calibration()

		assert x.process(5) == 5

		x.setZero()
		x.setOne(10)

		assert x.process(15) == 2

	def test_save_single_calibration(self):

		x = Calibration()
		x.offset = 10

		x.name = 'test'
		x.save()
		x.offset = 15
		x.load()

		assert x.offset == 10

		x.delete()

	def test_save_and_delete_new_persistent_entry(self):

		LoadHelper.save('test', hash(self))
		assert LoadHelper.load('test') == hash(self)

		LoadHelper.delete('test')
		assert not LoadHelper.exists('test')


	def test_calibrate_matrix_test_and_save(self):

		x = SixAxisCalibrationMatrix()

		assert x.process([1, 2, 3, 4, 5, 6]) == [1, 2, 3, 4, 5, 6]

		x.matrix[2][3] = 1
		assert x.process([0, 0, 0, 1, 0, 0]) == [0, 0, 1, 1, 0, 0]

		x.name = 'test'
		x.save()

		x.matrix[2][3] = 0

		x.load()
		assert x.process([0, 0, 0, 1, 0, 0]) == [0, 0, 1, 1, 0, 0]

		x.delete()

	def test_insert_factory_six_axis_calibrations(self):
		x = SixAxisCalibrationMatrix(name = 'M5237', load = False)
		x.matrix = [
			[0.6789, 0.0034, -0.0013, -0.2676, 0.2778, 0.0501],
			[0.0098, 0.6808, 0.0023, -0.4103, -0.1925, 0.0485],
			[-0.0040, -0.0045, 0.1643, -0.0228, -0.0171, 0.0114],
			[-0.0059, -0.0037, -0.0029, 38.7248, 0.0656, -0.0667],
			[-0.0037, 0.0103, 0.0064, 0.1106, 38.6657, 0.0941],
			[0.0024, -0.0004, 0.0008, -0.0325, -0.0992, 27.5819]
		]
		x.save()
		SixAxisCalibrationMatrix(name = 'M5237')