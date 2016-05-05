#pragma once

extern "C" {
	__declspec(dllexport) bool sendString(char *string);
	__declspec(dllexport) char* getBytes();
	__declspec(dllexport) bool openDevice();
	__declspec(dllexport) void closeDevice();
	__declspec(dllexport) bool getForces(float outputArray[]);
}