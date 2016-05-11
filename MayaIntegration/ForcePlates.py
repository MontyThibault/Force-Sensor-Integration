from ctypes import *

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

    @property
    def forces(self):
        return [self._forces[i] for (i, _) in enumerate(self._forces)]

    def openDevice(self, **kwargs):
        if "surpress_error" in kwargs:
            return force_plates.openDevice()
        elif not force_plates.openDevice() == 1:
            print("Error opening device")

    def closeDevice(self):
        return force_plates.closeDevice()

    def sendString(self, str, **kwargs):

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
            print("Error getting forces")


def main():
    sensor = ForcePlates()

    sensor.openDevice()

    program(sensor)

    from time import sleep
    while True:
        sleep(1.0 / 60.0)

        sensor.getForces()
        print(sensor.forces)

def program(sensor):
    file = open('C:/Users/Monty/Desktop/forcePlates/MayaIntegration/programs/simple_program.txt', 'r')
    for line in file.readlines():
        sensor.sendString("s{%s}\n" % line.strip('\n'))

if __name__ == "__main__":
    main()