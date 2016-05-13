from ctypes import *
import time
import pickle

force_plates = cdll.LoadLibrary('C:/Users/Monty/Desktop/forcePlates/x64/Debug/PythonDLL.dll')

class Singleton(object):
	"""Ensures only one instance of subtypes exist at a time."""

	_instance = None
	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance

class ForcePlates(Singleton):
	_forces = (c_float * 4)()
	
	_offset = [0, 0, 0, 0]
	_normalization = [1, 1, 1, 1]

	def __init__(self):
		self.refresh()

	def refresh(self):
		self.load()
		self.openDevice()
		self.program()

	@property
	def forces(self):
		""" Converts from a c_types float array to a native Python number array and applies 
	   calibration. """
		return [(self._forces[i] + self._offset[i]) * self._normalization[i]
				for (i, _) in enumerate(self._forces)]

	def openDevice(self, **kwargs):
		success = force_plates.openDevice()
		if not success: and 'surpress_error' not in kwargs.keys():
			print("Error opening device")

		return success

	def closeDevice(self):
		return force_plates.closeDevice()

	def sendString(self, str, **kwargs):
		""" Sends a program line-by-line to the LabPro. Thre instruction manual has more 
		information for the specification of such programs. """

		# Convert from Python 3 string to byte array
		# Python 2 reads simply c_char_p(str)
		ctype_str = c_char_p(str.encode("ascii"))

		success = force_plates.sendString(str)
		if not success and 'surpress_error' not in kwargs:
			print("Error sending string")

		return success

	def getBytes(self):
		return force_plates.getBytes()
			
	def getForces(self, **kwargs):
		success = force_plates.getForces()
		if not success and 'surpress_error' not in kwargs:
			print("Error getting forces %s" % time.time())

		return success

	def setZero(self, **kwargs):
		""" Sets the "_offset" component of the calibration such that the current measurment
	   is set to the value `0.0`. """

		for (i, _) in enumerate(self._forces):
			self._offset[i] = -self._forces[i]

		if 'nosave' not in kwargs:
			self.save()

	def setOne(self, i, **kwargs):
		""" Sets the "_normalization" component of the calibration for plate `i`, such that
		the current force measurement is scaled to the value `1.0`. """

		self._normalization[i] = 1.0 / self._forces[i]

		if 'nosave' not in kwargs:
			self.save()

	def save(self):
		calib = [self._offset, self._normalization]
		file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/calibration/calib.txt', 'w')
		pickle.dump(calib, file)
		file.close()
	
	def load(self):
		file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/calibration/calib.txt', 'r')
		(self._offset, self._normalization) = pickle.load(file)
		file.close()

	def program(self):
		file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/programs/simple_program.txt', 'r')
		for line in file.readlines():
			self.sendString("s{%s}\n" % line.strip('\n'))
		file.close()


# Example
def main():
	sensor = ForcePlates()
	sensor.refresh()

	while True:
		time.sleep(1.0 / 60.0)

		sensor.getForces()
		print(sensor.forces)

if __name__ == "__main__":
	main()