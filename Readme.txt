## Building the forcePlates library for Java/Python

The project is located in the JavaDLL/PythonDLL directories. Building the C++ project requires:

### Java 
- Visual Studio C++ 2015
- Including Java's jni.h
- Including headers from LabPro Windows SDK - https://svn.concord.org/svn/projects/trunk/common/java/sensor/labpro-usb/labpro-sdk/
(& installing drivers for LabPro)
- Including Boost C++ library v. 1.60.0 including prebuilt libraries for Visual Studio 2015 (downloadable)

Project builds to "JavaDLL.dll", which can then be linked as a Java library. VS should be set to a 64-bit build configuration.


Problems: 
Missing dependency errors: Try to remove the LabProUSB.lib dependency from the VC project.
If so, that's the problem. (See LabProSDK readme) If not, create a new project from scratch.

### Python
More simple; conversion to and from C_types are done from within the python module.

### Maya plugin
The plugin is the MayaPlugin.py script that can be found in the MayaIntegration folder. This script spawns a Python thread that runs inside of Maya and updates the sensors however many times per second. Automated testing is done by binding the MayaReload.py script to a shelf button within Maya.
