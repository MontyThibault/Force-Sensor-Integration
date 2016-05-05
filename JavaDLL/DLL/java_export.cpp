// dllmain.cpp : Defines the entry point for the DLL application.

#include <windows.h>
#include "jni.h"
#include "../../LabProUSB_SDK/redist/include/LabProUSB_interface.h"
#include "java_export.h"
#include <stdlib.h>
#include <boost/lexical_cast.hpp>
#include <boost/regex.hpp>
#include <iostream>


#ifdef _MANAGED
#pragma managed(push, off)
#endif

BOOL APIENTRY JavaDLL( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
					 )
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	case DLL_THREAD_ATTACH:
	case DLL_THREAD_DETACH:
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}

bool sendString(char *data)
{
	short len = (short)strlen(data);
	if (LabProUSB_WriteBytes(&len, data) != 0)
		return false;
	return true;
}

char* getBytes()
{
	char *buffer;
	gtype_int32 numBytes = LabProUSB_GetAvailableBytes();
	if (numBytes>0)
	{
		buffer = (char*)malloc(numBytes + 1);
		memset(buffer, 0, sizeof(char) * (numBytes + 1));
		gtype_int32 requested = numBytes;
		if (LabProUSB_ReadBytes(&requested, buffer) == 0)
		{
			//printf("Returning: '%s'\n", buffer);
			return buffer;
		}
		else
		{
			free(buffer);
			return NULL;
		}
		LabProUSB_ClearInputs(0);
		free(buffer);
	}
	return NULL;
}

JNIEXPORT jboolean JNICALL Java_forcePates_ForcePlates_openDevice
(JNIEnv *env, jobject obj)
{
	jclass cls = env->GetObjectClass(obj);
	if (LabProUSB_Open() == -1)
	{
		return false;
	}
	//jfieldID numPlatesID = env->GetFieldID(cls, "numPlates", "I");
	//jint numPlates = env->GetIntField(obj, numPlatesID);
	jint numPlates = 4;
	if (numPlates > 4)
		numPlates = 4;
	if (numPlates <= 0)
		numPlates = 1;
	//printf("forcePlates.dll: Registering %i plates.\n", numPlates);
	if (LabProUSB_SetNumChannelsAndModes(numPlates, 0, 1) != 0)
	{
		return false;
	}
	if (!sendString("s") || !sendString("s{0}\n"))
		return false;
	return true;
}

JNIEXPORT jboolean JNICALL Java_forcePates_ForcePlates_sendString
(JNIEnv *env, jobject obj, jstring javaString)
{
	unsigned int length = env->GetStringLength(javaString);
	char *buffer = (char*)malloc(length + 1);
	strcpy(buffer, env->GetStringUTFChars(javaString, NULL));
	bool result = sendString(buffer);
	free(buffer);
	env->ReleaseStringUTFChars(javaString, env->GetStringUTFChars(javaString, NULL));
	return result;
}

JNIEXPORT jstring JNICALL Java_forcePates_ForcePlates_getBytes
(JNIEnv *env, jobject)
{
	char *buffer = getBytes();
	if (buffer != NULL)
	{
		//printf("dll: trying ot create a string with: '%s'\n", buffer);
		jstring result = env->NewStringUTF(buffer);
		free(buffer);
		return result;
	}
	else
	{

		//printf("No bytes to get.\n");
		return NULL;
	}
}

JNIEXPORT void JNICALL Java_forcePates_ForcePlates_closeDevice
(JNIEnv *, jobject)
{
	sendString("s{0}\n");
	LabProUSB_Close();
}

JNIEXPORT jboolean JNICALL Java_forcePates_ForcePlates_getForces
(JNIEnv *env, jobject, jfloatArray outputArray)
{
	std::vector<float> answers {};

	try
	{
		char *buffer = getBytes();
		if (buffer == NULL)
			return false;
		//std::cout<<"Matching: "<<buffer<<std::endl;
		boost::regex regEx("\\s*\\{\\s*(.*?),\\s*(.*?),\\s*(.*?),\\s*(.*?),\\s*(.*?)\\s*\\}\\s*");
		boost::regex sciRegEx("^(.*)?E(.*)$");
		boost::cmatch matches, secondMatch;
		if (!boost::regex_match(buffer, matches, regEx))
		{
			std::cout << "[forcePlateJNI]: Match failed!" << std::endl;
			free(buffer);
			return false;
		}

		for (unsigned int i = 1; i < matches.size(); i++)
		{
			//std::cout<<"Doing internal repeat "<<i<<std::endl;
			std::string match(matches[i].first, matches[i].second);
			double base, answer;
			int power;
			if (!boost::regex_match(match.c_str(), secondMatch, sciRegEx))
			{
				std::cout << "[forcePlateJNI]: Match failed!" << std::endl;
				free(buffer);
				return false;
			}
			std::string sBase(secondMatch[1].first, secondMatch[1].second);
			std::string sPowe(secondMatch[2].first, secondMatch[2].second);
			base = boost::lexical_cast<double>(sBase);
			power = boost::lexical_cast<int>(sPowe);
			answer = base*pow(10.0, power);
			answers.push_back(answer);
			std::cout << "Answer: " << answer << std::endl;
		}

		//Copy out our data.
		float *cArrayPtr;
		cArrayPtr = env->GetFloatArrayElements(outputArray, 0);
		memcpy(cArrayPtr, answers.data(), 16); // answers.size() * sizeof(float));
		env->ReleaseFloatArrayElements(outputArray, cArrayPtr, 0);

		//std::cout<<std::endl;
		free(buffer);
		return true;
	}
	catch (boost::bad_lexical_cast &e)
	{
		std::cout << "[forcePlateJNI]: lexical cast exception: " << e.what() << std::endl;
	}
	catch (std::runtime_error &e)
	{
		std::cout << e.what() << std::endl;
	}
	catch (...)
	{
		std::cout << "[forcePlateJNI]: Caught an -UNKNOWN- exception" << std::endl;
		return false;
	}
}

#ifdef _MANAGED
#pragma managed(pop)
#endif