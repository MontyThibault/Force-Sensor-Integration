#ifndef _Included_forcePates_ForcePlates
#define _Included_forcePates_ForcePlates
#ifdef __cplusplus
extern "C" {
#endif
	/*
	* Class:     forcePates_ForcePlates
	* Method:    openDevice
	* Signature: ()Z
	*/
	JNIEXPORT jboolean JNICALL Java_forcePates_ForcePlates_openDevice
		(JNIEnv *, jobject);

	/*
	* Class:     forcePates_ForcePlates
	* Method:    sendString
	* Signature: (Ljava/lang/String;)Z
	*/
	JNIEXPORT jboolean JNICALL Java_forcePates_ForcePlates_sendString
		(JNIEnv *, jobject, jstring);

	/*
	* Class:     forcePates_ForcePlates
	* Method:    getBytes
	* Signature: ()Ljava/lang/String;
	*/
	JNIEXPORT jstring JNICALL Java_forcePates_ForcePlates_getBytes
		(JNIEnv *, jobject);

	/*
	* Class:     forcePates_ForcePlates
	* Method:    closeDevice
	* Signature: ()V
	*/
	JNIEXPORT void JNICALL Java_forcePates_ForcePlates_closeDevice
		(JNIEnv *, jobject);

	/*
	* Class:     forcePates_ForcePlates
	* Method:    getForces
	* Signature: ([F)Z
	*/
	JNIEXPORT jboolean JNICALL Java_forcePates_ForcePlates_getForces
		(JNIEnv *, jobject, jfloatArray);

#ifdef __cplusplus
}
#endif
#endif
