from ctypes import *
force_plates = cdll.LoadLibrary('../../x64/Debug/PythonDLL.dll')

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

    def openDevice(self):
        return force_plates.openDevice()

    def closeDevice(self):
        return force_plates.closeDevice()

    def sendString(self, str):
        return force_plates.sendString(str)

    def getBytes(self):
        return force_plates.getBytes()
            
    def getForces(self):
        return force_plates.getForces(self._forces)


def main():
    sensor = ForcePlates()

    sensor.openDevice()
    program(sensor)

def program(controller):
    controller.sendString("s{1, 1, 14, 0, 0, 1}\n")
    controller.sendString("s{4, 1, 1, 1, -2.24810E+02, 2.24810E+02}\n")
    controller.sendString("s{1, 1, 14, 0, 0, 1}\n")
    controller.sendString("s{4, 1, 1, 1, -2.24810E+02, 2.24810E+02}\n")
    controller.sendString("s{1, 1, 14, 0, 0, 1}\n")
    controller.sendString("s{4, 1, 1, 1, -2.24810E+02, 2.24810E+02}\n")
    controller.sendString("s{1, 1, 14, 0, 0, 1}\n")
    controller.sendString("s{4, 1, 1, 1, -2.24810E+02, 2.24810E+02}\n")
    controller.sendString("s{3, 0.5, -1, 0, 0, 0, 0, 0, 0, 0, 0}\n")
    controller.sendString("s{7}\n")


if __name__ == "__main__":
    main()