## Building the forcePlates library for Java

The project is located in the DLL directory. Building the C++ project requires:

Visual Studio C++ 2015
Including Java's jni.h
Including headers from LabPro Windows SDK - https://svn.concord.org/svn/projects/trunk/common/java/sensor/labpro-usb/labpro-sdk/
(& installing drivers for LabPro)
Including Boost C++ library v. 1.60.0 including prebuilt libraries for Visual Studio 2015 (downloadable)

Project builds to "jni/forcePlates/x64/Debug/DLL.dll", which can then be linked as a Java library. VS should be set to a 64-bit build configuration.


Problems: 
Missing dependency errors: Try to remove the LabProUSB.lib dependency from the VC project.
If so, that's the problem. (See LabProSDK readme) If not, create a new project from scratch.


Monty
4/5/2016