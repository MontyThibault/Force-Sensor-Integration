from ctypes import *
import Calibration as C
import time

class Singleton(object):
	"""Ensures only one instance of subtypes exist at a time."""

	_instance = None
	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance


class LabPro(Singleton):
	""" This class implements error printing on all the underlying C functions. """

	_raw = cdll.LoadLibrary('C:/Users/Monty/Desktop/forcePlates/x64/Debug/PythonDLL.dll')

	class ErrorWrapper(object):
		def __init__(self, f):
			self.f = f

		def __call__(self, *args, **kwargs):
			errorCode = self.f(*args, **kwargs)

			if errorCode != 1:
				print("ForcePlates.%s = %s : Error" % 
					(self.f.__name__, errorCode))
			
			return errorCode

	def __getattr__(self, key):
		return self.ErrorWrapper(getattr(self._raw, key))

class ForcePlates(Singleton):

	labpro = LabPro()

	_forces = (c_float * 4)()
	calib = [C.Calibration() for _ in range(4)]

	def __init__(self):
		self.openDevice()
		self.program()

	@property
	def forces(self):
		""" Converts from a c_types float array to a native Python number array and applies 
	   calibration. """

		return [self.calib[i].process(self._forces[i])
				for (i, _) in enumerate(self._forces)]

	def closeDevice(self):
		return self.labpro.closeDevice()

	def getBytes(self):
		return self.labpro.getBytes()

	def program(self):
		""" Sends a program line-by-line to the LabPro. Thre instruction manual has more 
		information for the specification of such programs. """

		file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/programs/simple_program.txt', 'r')
		for line in file.readlines():
			self.sendString(c_char_p(b"s{%s}\n" % line.strip('\n')))
		file.close()

	def __getattr__(self, key):
		return getattr(self.labpro, key)