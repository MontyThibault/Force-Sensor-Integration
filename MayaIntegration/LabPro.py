from ctypes import *
import Calibration as C
import os
import unittest

class Singleton(object):
	"""Ensures only one instance of subtypes exist at a time."""

	_instance = None
	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance

print(os.path.dirname(os.path.realpath(__file__)) + 
		"/../LabProUSB_SDK/redist/LabProUSB_lib/win64/LabProUSB.dll")

class LabProUSB(Singleton):
	""" Load the library only once & prints error message given the common 
	interface is `0 = success`. See `LabProUSB_interface.h for function 
	descriptions. """

	_raw = cdll.LoadLibrary(
		os.path.dirname(os.path.realpath(__file__)) + 
		"/../LabProUSB_SDK/redist/LabProUSB_lib/win64/LabProUSB.dll")

	# Oddballs
	def Close(self):
		self._raw.LabProUSB_Close()

	def IsOpen(self):
		return self._raw.LabProUSB_Close()

	def SendString(self, string):
		length = c_int32(len(string) + 1)
		encoded = string.encode('ASCII')

		self.WriteBytes(byref(length), c_char_p(encoded))

		print("Sending program string: %s" % string)

	class ErrorWrapper(object):
		def __init__(self, f):
			self.f = f

		def __call__(self, *args, **kwargs):
			errorCode = self.f(*args, **kwargs)

			if errorCode < 0:
				print("%s = %s : Returned unsuccessful." % 
					(self.f.__name__, errorCode))
			
			return errorCode

	def __getattr__(self, key):
		return self.ErrorWrapper(getattr(self._raw, "LabProUSB_" + key))


class ForcePlates(Singleton):
	labpro = LabProUSB()

	def __init__(self, name = 'plates'):

		self.measurements = [0, 0, 0, 0]

		if name:
			self.name = 'ForcePlates_%s' % name
		else:
			self.name = 'ForcePlates_%s' % hash(self)

		self.calibrations = [C.Calibration('%s_%s' % (self.name, i)) 
			for i in range(4)]

		self.Open()
		self.SetNumChannelsAndModes(c_int32(4), c_int16(1), c_int16(0))
		self.program()

	def __del__(self):
		self.blink()
		self.Close()

	def blink(self):
		self.SendString('s')

	def updateMeasurements(self):
		n = self.GetAvailableBytes()
		
		# No new data
		if n == 0:
			return

		n_ = c_int32(n)
		buffer_ = create_string_buffer(n + 1)

		data = self.ReadBytes(byref(n_), buffer_)

		try:
			# Crazy hack
			data = eval(buffer_.value.replace('{', '[').replace('}', ']'))
			self.measurements = data[:4]

			# time_interval = data[4]
		except:
			return


	@property
	def forces(self):
		""" Converts from a c_types float array to a native Python number array and applies 
	   calibration. """

		return [self.calibrations[i].process(self.measurements[i])
				for i in range(4)]

	def save(self):
		""" Saves calibration on all channels. Load is handled automatically on 
		creation. """
		
		for cal in self.calibrations:
			cal.save()

	def setAllZero(self):
		""" Sets all sensors to zero. """

		for cal in self.calibrations:
			cal.setZero()

	def program(self):
		""" Sends a program line-by-line to the LabPro. Thre instruction manual has more 
		information for the specification of such programs. """

		file = open(os.path.dirname(os.path.realpath(__file__)) + 
			'/programs/simple_program.txt', 'r')

		for line in file.readlines():
			self.SendString("s{%s}\n" % line.strip('\n'))
		file.close()

	def __getattr__(self, key):
		return getattr(self.labpro, key)