from ctypes import *
import Calibration as C

class Singleton(object):
	"""Ensures only one instance of subtypes exist at a time."""

	_instance = None
	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance


class LabProUSB(Singleton):
	""" Load the library only once & prints error message given the common 
	interface is `0 = success`. See `LabProUSB_interface.h for function 
	descriptions. """

	_raw = cdll.LoadLibrary('C:/Users/Monty/Desktop/forcePlates/LabProUSB_SDK/redist/LabProUSB_lib/win64/LabProUSB.dll')

	# Oddballs
	def Close(self):
		self._raw.LabProUSB_Close()

	def IsOpen(self):
		return self._raw.LabProUSB_Close()

	def SendString(self, string):
		length = c_int32(len(string) + 1)
		encoded = string.encode('ASCII')

		self.WriteBytes(byref(length), c_char_p(encoded))

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

		self.measurements = (c_float * 4)()
		self.calibrations = [C.Calibration() for i in range(4)]

		if name:
			self.name = 'ForcePlates_%s' % name
		else:
			self.name = 'ForcePlates_%s' % hash(self)

		self.Open()
		self.SetNumChannelsAndModes(4, 1, 0)

		self.program()

	def __del__(self):
		self.Close()

	def blink(self):
		self.SendString('s')

	def updateMeasurements(self):
		n = self.GetAvailableBytes()
		
		# No new data
		if n == 0:
			return

		buffer_ = create_string_buffer(n + 1)
		data = self.ReadBytes(byref(n), buffer_)

		print(buffer_)


	@property
	def forces(self):
		""" Converts from a c_types float array to a native Python number array and applies 
	   calibration. """

		return [self.calibrations[i].process(self.measurements[i])
				for i in range(4)]

	def program(self):
		""" Sends a program line-by-line to the LabPro. Thre instruction manual has more 
		information for the specification of such programs. """

		file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/programs/simple_program.txt', 'r')
		for line in file.readlines():
			self.SendString("s{%s}/n" % line.strip('/n'))
		file.close()

	def __getattr__(self, key):
		return getattr(self.labpro, key)