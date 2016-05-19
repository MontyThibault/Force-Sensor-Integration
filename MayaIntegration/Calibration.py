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

	@staticmethod
	def insert_factory_six_axis_calibrations():
		M5237 = SixAxisCalibrationMatrix(name = 'M5237', load = False)
		M5237.matrix = [
			[0.6789, 0.0034, -0.0013, -0.2676, 0.2778, 0.0501],
			[0.0098, 0.6808, 0.0023, -0.4103, -0.1925, 0.0485],
			[-0.0040, -0.0045, 0.1643, -0.0228, -0.0171, 0.0114],
			[-0.0059, -0.0037, -0.0029, 38.7248, 0.0656, -0.0667],
			[-0.0037, 0.0103, 0.0064, 0.1106, 38.6657, 0.0941],
			[0.0024, -0.0004, 0.0008, -0.0325, -0.0992, 27.5819]
		]
		M5237.save()

		M5237_inv = SixAxisCalibrationMatrix(name = 'M5237_inv', load = False)
		M5237_inv.matrix = [
			[1.4732, -0.0070, 0.126, 0.0101, -.0106, -0.0026],
			[-0.0211, 1.4689, -0.0209, 0.0154, 0.0074, -0.0025],
			[0.0352, 0.0399, 6.0877, 0.0042, 0.0026, -0.0026],
			[0.0002, 0.0001, 0.0005, 0.0256, 0.0000, 0.0001],
			[0.0001, -0.0004, -0.0010, -0.0001, 0.0259, -0.0001],
			[-0.0001, 0.0000, -0.0002, 0.0000, 0.0001, 0.0363]
		]
		M5237_inv.save()

		#################

		M5238 = SixAxisCalibrationMatrix(name = 'M5238', load = False)
		M5238.matrix = [
			[0.3374, -0.0003, -0.0017, -0.0726, -0.0125, 0.225],
			[0.0021, 0.3382, 0.0004, 0.0098, -0.0433, -0.0117],
			[-0.0005, -0.0008, 0.0847, -0.0082, -0.0051, 0.0035],
			[0.0030, 0.0026, -0.0012, 19.7556, 0.0741, 0.0014],
			[0.0026, 0.0055, 0.0088, -0.0181, 19.8361, 0.1955],
			[-0.0019, 0.0002, -0.0006, 0.0638, -0.0470, 13.1748],
		]
		M5238.save()

		M5238_inv = SixAxisCalibrationMatrix(name = 'M5238_inv', load = False)
		M5238_inv.matrix = [
			[2.9640, 0.0025, 0.0610, 0.0109, 0.0018, -0.0051],
			[-0.0188, 2.9567, -0.0161, -0.0015, 0.0064, 0.0026],
			[0.0172, 0.0281, 11.8009, 0.0050, 0.0031, -0.0032],
			[-0.0004, -0.0004, 0.0008, 0.0506, -0.0002, 0.0000],
			[-0.0004, -0.0008, -0.0052, 0.0000, 0.0504, -0.0007],
			[0.0004, 0.0000, 0.0005, -0.0002, 0.0002, 0.0760]
		]
		M5238_inv.save()

		##################

		M5239 = SixAxisCalibrationMatrix(name = 'M5239', load = False)
		M5239.matrix = [
			[0.3482, -0.0008, -0.0006, -0.0782, -0.0230, -0.0396],
			[0.0036, 0.3468, 0.0009, 0.0216, -0.0857, -0.0781],
			[-0.0016, -0.001, 0.0871, -0.0030, 0.0184, 0.0192],
			[0.0005, -0.0030, -0.0056, 20.4536, -0.428, -0.0628],
			[-0.0030, 0.0067, 0.0013, 0.0971, 20.4307, 0.2442],
			[0.0051, 0.0020, 0.0002, 0.0854, 0.0779, 13.5338]
		]
		M5239.save()

		M5239_inv = SixAxisCalibrationMatrix(name = 'M5239_inv', load = False)
		M5239_inv.matrix = [
			[2.8717, 0.0065, 0.0194, 0.0109, 0.0032, 0.0084],
			[-0.0297, 2.8833, -0.0299, -0.0033, 0.0120, 0.0164],
			[0.0547, 0.0326, 11.4879, 0.0020, -0.0101, -0.0158],
			[-0.0001, 0.0004, 0.0032, 0.0489, 0.0001, 0.0002],
			[0.0004, -0.0009, -0.0007, -0.0002, 0.0489, -0.0009],
			[-0.0011, -0.0005, -0.0002, -0.0003, -0.0003, 0.0739]
		]
		M5239_inv.save()

		#################

		M5240 = SixAxisCalibrationMatrix(name = 'M5240', load = False)
		M5240.matrix = [
			[0.3430, -0.0014, -0.0005, -0.0006, 0.0005, 0.0072],
			[0.0049, 0.3424, 0.0009, 0.0003, -0.0017, -0.0047],
			[-0.0001, -0.0009, 0.0855, 0.0007, 0.0008, 0.0012],
			[0.0026, 0.0043, -0.0065, 20.1865, -0.0904, -0.2634],
			[0.0043, 0.0064, 0.0060, 0.1375, 21.1264, -0.0404],
			[-0.0008, -0.0020, 0.0008, -0.0601, 0.0344, 13.6804]
		]
		M5240.save()

		M5240_inv = SixAxisCalibrationMatrix(name = 'M5240_inv', load = False)
		M5240_inv.matrix = [
			[2.9151, 0.0120, 0.0170, 0.0034, -0.0001, -0.0014],
			[-0.0422, 2.9202, -0.0318, -0.0017, 0.0099, 0.0395],
			[0.0049, 0.0324, 11.6915, -0.0182, -0.0279, -0.0266],
			[-0.0004, -0.0006, 0.0038, 0.0495, 0.0002, 0.0009],
			[-0.0006, -0.0009, -0.0035, -0.0003, 0.0497, 0.0001],
			[0.0002, 0.0004, -0.0007, 0.0002, -0.0001, 0.0731]
		]
		M5240_inv.save()

		####################

		M5170 = SixAxisCalibrationMatrix(name = 'M5170', load = False)
		M5170.matrix = [
			[0.3534, -0.0004, -0.0009, -0.0883, -0.0571, -0.0063],
			[0.0030, 0.3523, 0.0004, 0.0555, -0.0295, -0.0488],
			[-0.0010, -0.0008, 0.0881, -0.0130, -0.0092, -0.0456],
			[0.0007, -0.0013, -0.0070, 20.5413, -0.978, 0.1023],
			[-0.0012, 0.0010, 0.0024, 0.1935, 20.4513, 0.0734],
			[0.0021, 0.0045, 0.0003, 0.0003, -0.0132, 13.7464]
		]
		M5170.save()

		M5170_inv = SixAxisCalibrationMatrix(name = 'M5170_inv', load = False)
		M5170_inv.matrix = [
			[2.8297, 0.0030, 0.0308, 0.0121, 0.0080, 0.0013],
			[-0.0240, 2.8383, -0.0143, -0.0078, 0.0040, 0.0101],
			[0.0330, 0.0240, 11.3551, 0.0072, 0.0053, 0.0377],
			[-0.0001, 0.0002, 0.0039, 0.0487, 0.0002, -0.0004],
			[0.0002, -0.0001, -0.0014, -0.0005, 0.0489, -0.0003],
			[-0.0004, -0.0009, -0.0003, 0.0000, 0.0000, 0.0727]
		]
		M5170_inv.save()



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
		SixAxisCalibrationMatrix.insert_factory_six_axis_calibrations()