This project undertakes integrating Contec and LabPro force sensors into a real-time Maya plugin for application in computer graphics research.

### Contec and LabPro modules
The Python application interfaces with the software .dll's through the ctypes module. All functions are available in Python, however those used in practice are limited to simple sensory input. There is a calibration module implemented in Python that can do post-processing.

### Maya plugin
The plugin is the MayaPlugin.py script that can be found in the MayaIntegration folder. This script spawns a Python thread that runs inside of Maya and updates the sensors at 60Hz. Automated reloading is done by binding the MayaReload.py script to a shelf button within Maya.