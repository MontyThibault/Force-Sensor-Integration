// dllmain.cpp : Defines the entry point for the DLL application.

#include <windows.h>
#include "../LabProUSB_SDK/redist/include/LabProUSB_interface.h"
#include "python_export.h"
#include <stdlib.h>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <iostream>


#ifdef _MANAGED
#pragma managed(push, off)
#endif


BOOL APIENTRY PythonDLL(HMODULE hModule,
		DWORD  ul_reason_for_call,
		LPVOID lpReserved) {
	switch (ul_reason_for_call) {
		case DLL_PROCESS_ATTACH:
		case DLL_THREAD_ATTACH:
		case DLL_THREAD_DETACH:
		case DLL_PROCESS_DETACH:
			break;
	}

	return TRUE;
}


bool sendString(char *string) {
	short length = strlen(string);

	std::cout << string << std::endl;

	if (LabProUSB_WriteBytes(&length, string) != 0)
		return false;
	return true;
}

char* getBytes() {
	char *buffer;
	gtype_int32 numBytes = LabProUSB_GetAvailableBytes();

	if (numBytes > 0) {
		buffer = (char*) malloc(numBytes + 1);
		memset(buffer, 0, sizeof(char) * (numBytes + 1));

		int requested = numBytes;
		if (LabProUSB_ReadBytes(&requested, buffer) == 0) {

			//printf("Returning: '%s'\n", buffer);
			return buffer;

		} else {
			std::cout << "LabProUSB_ReadBytes failed." << std::endl;

			free(buffer);
			return NULL;
		}

		LabProUSB_ClearInputs(0);
		free(buffer);
	}

	std::cout << "Num bytes = 0" << std::endl;
	return NULL;
}

bool openDevice() {
	if (LabProUSB_Open() == -1) {
		return false;
	}

	if (LabProUSB_SetNumChannelsAndModes(4, 0, 1) != 0) {
		return false;
	}

	if (!sendString("s") || !sendString("s{0}\n"))
		return false;

	return true;
}

void closeDevice() {
	sendString("s{0}\n");
	LabProUSB_Close();
}

bool getForces(float outputArray[]) {
	try {
		char *buffer = getBytes();
		if (buffer == NULL) {
			std::cout << "[forcePlateJNI]: Null buffer!" << std::endl;
			return false;
		}

		//std::cout<<"Matching: "<<buffer<<std::endl;
		boost::regex regEx("\\s*\\{\\s*(.*?),\\s*(.*?),\\s*(.*?),\\s*(.*?),\\s*(.*?)\\s*\\}\\s*");
		boost::regex sciRegEx("^(.*)?E(.*)$");
		boost::cmatch matches, secondMatch;
		if (!boost::regex_match(buffer, matches, regEx)) {
			std::cout << "[forcePlateJNI]: Match failed!" << std::endl;
			free(buffer);
			return false;
		}

		for (unsigned int i = 1; i < matches.size(); i++) {
			//std::cout<<"Doing internal repeat "<<i<<std::endl;
			std::string match(matches[i].first, matches[i].second);
			double base, answer;
			int power;
			if (!boost::regex_match(match.c_str(), secondMatch, sciRegEx)) {
				std::cout << "[forcePlateJNI]: Match failed!" << std::endl;
				free(buffer);
				return false;
			}
			std::string sBase(secondMatch[1].first, secondMatch[1].second);
			std::string sPowe(secondMatch[2].first, secondMatch[2].second);
			base = boost::lexical_cast<double>(sBase);
			power = boost::lexical_cast<int>(sPowe);

			answer = base * pow(10.0, power);
			outputArray[i - 1] = answer;

			std::cout << "Answer: " << answer << std::endl;
		}

		//std::cout<<std::endl;
		free(buffer);
		return true;

	} catch (boost::bad_lexical_cast &e) {
		std::cout << "[forcePlateJNI]: lexical cast exception: " << e.what() << std::endl;
	} catch (std::runtime_error &e) {
		std::cout << "[forcePlateJNI]: " << e.what() << std::endl;
	} catch (...) {
		std::cout << "[forcePlateJNI]: Caught an -UNKNOWN- exception" << std::endl;
		return false;
	}
}

#ifdef _MANAGED
#pragma managed(pop)
#endif