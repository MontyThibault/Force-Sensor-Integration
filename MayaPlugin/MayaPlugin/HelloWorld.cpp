#include <iostream>

#include <maya/MSimple.h>
#include <maya/MIOStream.h>
#include <maya/MGlobal.h>

#ifndef MAYAPLUGIN_LOADED
#define MAYAPLUGIN_LOADED
#endif

DeclareSimpleCommand(HelloWorld, "Autodesk", "2016");

MStatus HelloWorld::doIt(const MArgList&) {

	std::cout << "Hello World\n" << std::endl;
	MGlobal::displayInfo("Goodbye cruel World!");

	return MS::kSuccess;
}