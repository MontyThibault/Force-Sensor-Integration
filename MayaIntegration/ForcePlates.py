from ctypes import *
import time

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

    @property
    def forces(self):
        """ Converts from a c_types float array to a native Python number array and applies 
       calibration. """
        return [(self._forces[i] + self._offset[i]) * self._normalization[i]
                for (i, _) in enumerate(self._forces)]

    def openDevice(self, **kwargs):
        if "surpress_error" in kwargs:
            return force_plates.openDevice()
        elif not force_plates.openDevice() == 1:
            print("Error opening device")

    def closeDevice(self):
        return force_plates.closeDevice()

    def sendString(self, str, **kwargs):
        """ Sends a program line-by-line to the LabPro. Thre instruction manual has more 
        information for the specification of such programs. """

        # Convert from Python 3 string to byte array
        # Python 2 reads simply c_char_p(str)
        ctype_str = c_char_p(str.encode("ascii"))

        if "surpress_error" in kwargs:
            return force_plates.sendString(ctype_str)
        elif not force_plates.sendString(ctype_str) == 1:
            print("Error sending string")

    def getBytes(self):
        return force_plates.getBytes()
            
    def getForces(self, **kwargs):
        if "surpess_error" in kwargs:
            return force_plates.getForces(self._forces)
        elif not force_plates.getForces(self._forces) == 1:
            print("Error getting forces %s" % time.time())

    def setZero(self):
        """ Sets the "_offset" component of the calibration. """

        for (i, _) in enumerate(self._forces):
            self._offset[i] = -self._forces[i]

    def setOne(self, i):
        """ Sets the "_normalization" component of the calibration for plate `i`, such that
        the current force measurement is scaled to the value `1.0`. """

        self._normalization[i] = 1.0 / self._forces[i]


# Example
def main():
    sensor = ForcePlates()

    sensor.openDevice()

    program(sensor)

    while True:
        time.sleep(1.0 / 60.0)

        sensor.getForces()
        print(sensor.forces)

def program(sensor):
    file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/programs/simple_program.txt', 'r')
    for line in file.readlines():
        sensor.sendString("s{%s}\n" % line.strip('\n'))

if __name__ == "__main__":
    main()