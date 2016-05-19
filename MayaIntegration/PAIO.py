from ctypes import *
import unittest

class Singleton(object):
	"""Ensures only one instance of subtypes exist at a time."""

	_instance = None
	def __new__(class_, *args, **kwargs):
		if not isinstance(class_._instance, class_):
			class_._instance = object.__new__(class_, *args, **kwargs)
		return class_._instance


class AIO(Singleton):
	""" This class overrides the default attribute lookup of the aio DLL library
	in to implement automated error catching for all functions, assuming the 
	common interface is a zero-valued return. 

	Alternatively, the original functions can still be called via `aio._raw.f()"""

	# Should be on system path if device drivers were installed properly
	_raw = cdll.LoadLibrary('CAIO.dll')

	class ErrorWrapper:
		def __init__(self, f):
			self.f = f

		def __call__(self, *args, **kwargs):
			errorCode = self.f(*args, **kwargs)

			if errorCode != 0:

				# Max error string length of 200 characters
				errorStringBuffer = create_string_buffer(200)

				# Copy error code into buffer
				AIO()._raw.AioGetErrorString(errorCode, errorStringBuffer)

				print("aio.%s = %s : %s" % 
					(self.f.__name__, errorCode, errorStringBuffer.value.decode("utf-8")))
			
			return errorCode

	def __getattr__(self, key):
		if key in consts:

			# For constants (defined below)
			return consts[key]
		else:

			# For functions
			return self.ErrorWrapper(getattr(self._raw, key))
	


class AIODevice(object):
	""" Sensor instance with single device name and device ID (each device has 
	up to 32 channels). """

	aio = AIO()

	def __init__(self, name = b"AIO000"):
		self.deviceName = c_char_p(name)
		self.deviceID = c_short()

	def Init(self):
		""" This is the only function in the AIO library that does not follow
		the convention of passing DeviceID as the first argument; this is the
		function that generates the ID and sets the value via the pointer in the
		second argument. It gets a special name without a `Aio` prefix. """

		self.aio.AioInit(self.deviceName, byref(self.deviceID))

	def _callableWithID(self, f):

		def composite(*args, **kwargs):
			f(self.deviceID, *args, **kwargs)

		return composite

	def __getattr__(self, key):
		""" Eliminates "deviceID" syntax from all AIO functions. Note: C function 
		usage & examples are specified in the Contec help files """
		return self._callableWithID(getattr(self.aio, key))


class Tests(object):
	def test_paio_singleton_interface(self):
		x = AIO()
		x.test = 10
		y = AIO()

		assert y.test == 10

	def test_access_PAIO_functions(self):
		assert hasattr(AIO(), 'AioInit')
		assert hasattr(AIO(), 'AioGetErrorString')

	def test_access_PAIO_constants(self):
		assert hasattr(AIO(), 'PM10')
		assert hasattr(AIO(), 'AIOM_CNTM_CARRY_BORROW')

	def test_PAIO_error_wrapping(self):

		def alwaysFails():
			return 10101

		AIO()._raw.bad = alwaysFails
		assert AIO().bad() == 10101

		del AIO()._raw.bad

	def test_PAIO_device_argument_elision(self):

		def noArguments(deviceID):
			assert deviceID == 123

		AIO()._raw.noargs = noArguments

		d = AIODevice('name')
		d.deviceID = 123

		d.noargs()

		del AIO()._raw.noargs


consts = {

	# # ----------------------------------------------------------------------------------------------
	# # 	External Control Signal																				
	# # ----------------------------------------------------------------------------------------------
	'AIO_AIF_CLOCK':				0,	# Analog input external clock
	'AIO_AIF_START':				1,	# Analog input external start trigger
	'AIO_AIF_STOP':				2,	# Analog input external stop trigger
	'AIO_AOF_CLOCK':				3,	# Analog output external clock
	'AIO_AOF_START':				4,	# Analog output external start trigger
	'AIO_AOF_STOP':				5,	# Analog output external stop trigger

	# # ----------------------------------------------------------------------------------------------
	# # 	Input/Output Range																			
	# # ----------------------------------------------------------------------------------------------
	'PM10':						0,	# +/-10V
	'PM5':							1,	# +/-5V
	'PM25':						2,	# +/-2.5V
	'PM125':						3,	# +/-1.25V
	'PM1':							4,	# +/-1V
	'PM0625':						5,	# +/-0.625V
	'PM05':						6,	# +/-0.5V
	'PM03125':						7,	# +/-0.3125V
	'PM025':						8,	# +/-0.25V
	'PM0125':						9,	# +/-0.125V
	'PM01':						10,	# +/-0.1V
	'PM005':						11,	# +/-0.05V
	'PM0025':						12,	# +/-0.025V
	'PM00125':						13,	# +/-0.0125V
	'PM001':						14,	# +/-0.01V
	'P10':							50,	# 0 ~ 10V
	'P5':							51,	# 0 ~ 5V
	'P4095':						52,	# 0 ~ 4.095V
	'P25':							53,	# 0 ~ 2.5V
	'P125':						54,	# 0 ~ 1.25V
	'P1':							55,	# 0 ~ 1V
	'P05':							56,	# 0 ~ 0.5V
	'P025':						57,	# 0 ~ 0.25V
	'P01':							58,	# 0 ~ 0.1V
	'P005':						59,	# 0 ~ 0.05V
	'P0025':						60,	# 0 ~ 0.025V
	'P00125':						61,	# 0 ~ 0.0125V
	'P001':						62,	# 0 ~ 0.01V
	'P20MA':						100,	# 0 ~ 20mA
	'P4TO20MA':					101,	# 4 ~ 20mA
	'P1TO5':						150,	# 1 ~ 5V

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Input Event																
	# # ----------------------------------------------------------------------------------------------
	'AIE_START':			0x00000002,	# Event that AD converting start conditions are satisfied
	'AIE_RPTEND':			0x00000010,	# Event of repeat end
	'AIE_END':				0x00000020,	# Event of device operation end
	'AIE_DATA_NUM':		0x00000080,	# Event that data of the specified sampling times are stored
	'AIE_DATA_TSF':		0x00000100,	# Event that data of the specified number are transferred
	'AIE_OFERR':			0x00010000,	# Event of Overflow
	'AIE_SCERR':			0x00020000,	# Event of sampling clock error
	'AIE_ADERR':			0x00040000,	# Event of AD converting error

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Output Event																		
	# # ----------------------------------------------------------------------------------------------
	'AOE_START':			0x00000002,	# Event that DA converting start conditions are satisfied
	'AOE_RPTEND':			0x00000010,	# Event of repeat end
	'AOE_END':				0x00000020,	# Event of device operation end
	'AOE_DATA_NUM':		0x00000080,	# Event that data of the specified sampling times are output
	'AOE_DATA_TSF':		0x00000100,	# Event that data of the specified number are transferred
	'AOE_SCERR':			0x00020000,	# Event of sampling clock error
	'AOE_DAERR':			0x00040000,	# Event of DA converting error

	# # ----------------------------------------------------------------------------------------------
	# # 	Counter Event																			
	# # ----------------------------------------------------------------------------------------------
	'CNTE_DATA_NUM':		0x00000010,	# Event of count comparison match
	'CNTE_ORERR':			0x00010000,	# Event of count overrun
	'CNTE_ERR':			0x00020000,	# Counter operating error

	# # ----------------------------------------------------------------------------------------------
	# # 	Timer Event																				
	# # ----------------------------------------------------------------------------------------------
	'TME_INT':				0x00000001,	# Event that interval is satisfied

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Input Status																		
	# # ----------------------------------------------------------------------------------------------
	'AIS_BUSY':			0x00000001,	# Device is working
	'AIS_START_TRG':		0x00000002,	# Wait the start trigger
	'AIS_DATA_NUM':		0x00000010,	# Store the data of the specified number of samplings
	'AIS_OFERR':			0x00010000,	# Overflow
	'AIS_SCERR':			0x00020000,	# Sampling clock error
	'AIS_AIERR':			0x00040000,	# AD converting error
	'AIS_DRVERR':			0x00080000,	# Driver spec error

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Output Status																		
	# # ----------------------------------------------------------------------------------------------
	'AOS_BUSY':			0x00000001,	# Device is working
	'AOS_START_TRG':		0x00000002,	# /Wait the start trigger
	'AOS_DATA_NUM':		0x00000010,	# Output the data of the specified number of samplings
	'AOS_SCERR':			0x00020000,	# Sampling clock error
	'AOS_AOERR':			0x00040000,	# DA converting error
	'AOS_DRVERR':			0x00080000,	# Driver spec error

	# # ----------------------------------------------------------------------------------------------
	# # 	Counter Status																			
	# # ----------------------------------------------------------------------------------------------
	'CNTS_BUSY':			0x00000001,	# Counter is working
	'CNTS_DATA_NUM':		0x00000010,	# Count comparison match
	'CNTS_ORERR':			0x00010000,	# Overrun
	'CNTS_ERR':			0x00020000,	# Count operating error

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Input Message																		
	# # ----------------------------------------------------------------------------------------------
	'AIOM_AIE_START':			0x1000,	# Event that AD converting start condition are satisfied
	'AIOM_AIE_RPTEND':			0x1001,	# Event of repeat end
	'AIOM_AIE_END':			0x1002,	# Event of device operation end
	'AIOM_AIE_DATA_NUM':		0x1003,	# Event that data of the specified sampling times are stored
	'AIOM_AIE_DATA_TSF':		0x1007,	# Event that data of the specified number are transferred
	'AIOM_AIE_OFERR':			0x1004,	# Event of Overflow
	'AIOM_AIE_SCERR':			0x1005,	# Event of sampling clock error
	'AIOM_AIE_ADERR':			0x1006,	# Event of AD converting error

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Output Message																		
	# # ----------------------------------------------------------------------------------------------
	'AIOM_AOE_START':			0x1020,	# Event that DA converting start conditions are satisfied
	'AIOM_AOE_RPTEND':			0x1021,	# Event of repeat end
	'AIOM_AOE_END':			0x1022,	# Event of device operation end
	'AIOM_AOE_DATA_NUM':		0x1023,	# Event that data of the specified sampling times are output
	'AIOM_AOE_DATA_TSF':		0x1027,	# Event that data of the specified number are transferred
	'AIOM_AOE_SCERR':			0x1025,	# Event of sampling clock error
	'AIOM_AOE_DAERR':			0x1026,	# Event of DA converting error

	# # ----------------------------------------------------------------------------------------------
	# # 	Counter Message																			
	# # ----------------------------------------------------------------------------------------------
	'AIOM_CNTE_DATA_NUM':		0x1042,	# Event of count comparison match
	'AIOM_CNTE_ORERR':			0x1043,	# Event of count overrun
	'AIOM_CNTE_ERR':			0x1044,	# Event of counter operating error

	# # ----------------------------------------------------------------------------------------------
	# # 	Timer Message																			
	# # ----------------------------------------------------------------------------------------------
	'AIOM_TME_INT':			0x1060,	# Event that interval is satisfied

	# # ----------------------------------------------------------------------------------------------
	# # 	Analog Input Attached Data																		
	# # ----------------------------------------------------------------------------------------------
	'AIAT_AI':				0x00000001,	# Analog input attached information
	'AIAT_AO0':			0x00000100,	# Analong output data
	'AIAT_DIO0':			0x00010000,	# Digital input and output data
	'AIAT_CNT0':			0x01000000,	# Data of counter channel 0
	'AIAT_CNT1':			0x02000000,	# Data of counter channel 1

	# # ----------------------------------------------------------------------------------------------
	# # 	Counter Action Mode																			
	# # ----------------------------------------------------------------------------------------------
	'CNT_LOADPRESET':		0x0000001,	# Load the preset count value
	'CNT_LOADCOMP':		0x0000002,	# Load the count comparison value

	# # ----------------------------------------------------------------------------------------------
	# # 	Event Controller Destination Signal																
	# # ----------------------------------------------------------------------------------------------
	'AIOECU_DEST_AI_CLK':			4,	# Analog input sampling clock
	'AIOECU_DEST_AI_START':		0,	# Analog input converting start signal
	'AIOECU_DEST_AI_STOP':			2,	# Analog input converting stop signal
	'AIOECU_DEST_AO_CLK':			36,	# Analog output sampling clock
	'AIOECU_DEST_AO_START':		32,	# Analog output converting start signal
	'AIOECU_DEST_AO_STOP':			34,	# Analog output converting stop signal
	'AIOECU_DEST_CNT0_UPCLK':		134,	# Up clock signal of counter 0
	'AIOECU_DEST_CNT1_UPCLK':		135,	# Up clock signal of counter 1
	'AIOECU_DEST_CNT0_START':		128,	# Start signal of counter 0, timer 0
	'AIOECU_DEST_CNT1_START':		129,	# Start signal of counter 1, timer 1
	'AIOECU_DEST_CNT0_STOP':		130,	# Stop signal of counter 0, timer 0
	'AIOECU_DEST_CNT1_STOP':		131,	# Stop signal of counter 1, timer 1
	'AIOECU_DEST_MASTER1':			104,	# Synchronization bus master signal 1
	'AIOECU_DEST_MASTER2':			105,	# Synchronization bus master signal 2
	'AIOECU_DEST_MASTER3':			106,	# Synchronization bus master signal 3

	# # ----------------------------------------------------------------------------------------------
	# # 	Event Controller Source Signal																
	# # ----------------------------------------------------------------------------------------------
	'AIOECU_SRC_OPEN':				-1,	# Not connect
	'AIOECU_SRC_AI_CLK':			4,	# Analog input internal clock signal
	'AIOECU_SRC_AI_EXTCLK':		146,	# Analog input external clock signal
	'AIOECU_SRC_AI_TRGSTART':		144,	# Analog input external trigger start signal
	'AIOECU_SRC_AI_LVSTART':		28,	# Analog input level trigger start signal
	'AIOECU_SRC_AI_STOP':			17,	# Analog input signal that data of the specified sampling times have been converted (No delay)
	'AIOECU_SRC_AI_STOP_DELAY':	18,	# Analog input signal that data of the specified sampling times have been converted (delay)
	'AIOECU_SRC_AI_LVSTOP':		29,	# Analog input level trigger stop signal
	'AIOECU_SRC_AI_TRGSTOP':		145,	# Analog input external trigger stop signal
	'AIOECU_SRC_AO_CLK':			66,	# Analog output internal clock signal
	'AIOECU_SRC_AO_EXTCLK':		149,	# Analog output external clock signal
	'AIOECU_SRC_AO_TRGSTART':		147,	# Analog output external trigger start signal
	'AIOECU_SRC_AO_STOP_FIFO':		352,	# Analog output signal that data of the specified sampling times have been output (FIFO)
	'AIOECU_SRC_AO_STOP_RING':		80,	# Analog output signal that data of the specified sampling times have been output (RING)
	'AIOECU_SRC_AO_TRGSTOP':		148,	# Analog output external trigger stop signal
	'AIOECU_SRC_CNT0_UPCLK':		150,	# Up clock signal of counter 0
	'AIOECU_SRC_CNT1_UPCLK':		152,	# Up clock signal of counter 1
	'AIOECU_SRC_CNT0_CMP':			288,	# Count comparison match of counter 0
	'AIOECU_SRC_CNT1_CMP':			289,	# Count comparison match of counter 1
	'AIOECU_SRC_SLAVE1':			136,	# Synchronization bus master signal 1
	'AIOECU_SRC_SLAVE2':			137,	# Synchronization bus master signal 2
	'AIOECU_SRC_SLAVE3':			138,	# Synchronization bus master signal 3
	'AIOECU_SRC_START':			384,	# Ai, Ao, Cnt, Tm software start signal
	'AIOECU_SRC_STOP':				385,	# Ai, Ao, Cnt, Tm software stop signal

	# # ----------------------------------------------------------------------------------------------
	# #  Mdevice counter Message
	# # ----------------------------------------------------------------------------------------------
	'AIOM_CNTM_COUNTUP_CH0':	0x1070,	#  COUNTUP, CHANNEL No.0
	'AIOM_CNTM_COUNTUP_CH1':	0x1071,	#         "            1
	'AIOM_CNTM_TIME_UP':		0x1090,	#  Timer
	'AIOM_CNTM_COUNTER_ERROR':	0x1091,	#  Counter error
	'AIOM_CNTM_CARRY_BORROW':	0x1092	#  Carry/Borrow
}