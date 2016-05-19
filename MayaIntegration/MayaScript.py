import maya.cmds as cmds
import maya.utils
import maya.OpenMaya

import threading
import time

import sys 
import os

from ctypes import *

import LabPro
import PAIO
import SixAxis
import Calibration

reload(LabPro)
reload(PAIO)
reload(SixAxis)
reload(Calibration)


def testSuite():
	print "--------- Running tests -------------"

	def runTests(mod):
		obj = mod.Tests()

		if hasattr(obj, 'setUp'):
			obj.setUp()

		for key in dir(obj):
			if key.startswith('test'):
				print "Running test: %s.%s" % (mod.__name__, key)
				getattr(obj, key)()
				print "Test passed.\n"

		if hasattr(obj, 'tearDown'):
			obj.tearDown()

	runTests(Calibration)
	runTests(PAIO)
	runTests(SixAxis)

	print "---------- All tests passed! ---------"


def main():
	""" Main entry point """
	
	print("MayaScript loaded at %s!" % time.time())

	cmds.stackTrace(state = True)


	if not cmds.objExists('plate1'):
		cmds.createNode( "transform", name = "plate1" )
		cmds.createNode( "locator", parent = "plate1" )
		cmds.move(10, 0, -10, "plate1")

	if not cmds.objExists('plate2'):
		cmds.createNode( "transform", name="plate2" )
		cmds.createNode( "locator", parent = "plate2" )
		cmds.move(-10, 0, -10, "plate2")
	if not cmds.objExists('plate3'):
		cmds.createNode( "transform", name="plate3" )
		cmds.createNode( "locator", parent = "plate3" )
		cmds.move(10, 0, 10, "plate3")

	if not cmds.objExists('center'):
		cmds.createNode( "transform", name="center" )
		cmds.createNode( "locator", parent = "center" )


	plates = LabPro.ForcePlates()

	deviceA001 = PAIO.AIODevice(b'AIO001')
	aio = PAIO.AIO()

	deviceA001.Init()
	deviceA001.AioSetAiRangeAll(aio.PM10)

	channels = [6, 7, 8, 9, 10, 11]
	rock = SixAxis.SixAxis(deviceA001, channels, "M5237")

	cmds.createNode("locator", n = "locator%s" % hash(rock), p = rock.transform)

	SensorUpdate(plates, rock).start()


def callWith(f, *args, **kwargs):
	""" Returns a function that will be called with the given *args and **kwargs. """

	def g(*_args, **_kwargs):
		f(*args, **kwargs)

	return g


class SensorUpdate(threading.Thread):
	def __init__(self, plates, rock):
		threading.Thread.__init__(self)
		self.dead = False
		self.modifiers = 0
		self.available = True

		self.plates = plates
		self.rock = rock

		# Kill previous thread if script reloads
		try:
			globals()['sensor_thread'].kill()
		except:
			pass

		globals()['sensor_thread'] = self

		print("Thread started")

		self.initWindow()

	def initWindow(self):

		if cmds.window("ForceSensors", exists = True):
			cmds.deleteUI("ForceSensors")

		cmds.window("ForceSensors", width = 350, sizeable = False)
		cmds.columnLayout(adjustableColumn = True)

		# The button command will add an extra argument that we don't want, hence the callWith() wrapper
		cmds.button(label = 'Kill Thread', command = callWith(self.kill))

		cmds.text(label='LabPro Force Plates')

		cmds.button(label = 'Set Zero', command = callWith(self.plates.setAllZero))
		cmds.button(label = 'Set One (1)', command = callWith(self.plates.calibrations[0].setOne))
		cmds.button(label = 'Set One (2)', command = callWith(self.plates.calibrations[1].setOne))
		cmds.button(label = 'Set One (3)', command = callWith(self.plates.calibrations[2].setOne))

		cmds.button(label = 'Blink (kills program)', command = callWith(self.plates.blink))


		cmds.text(label='Contec Six-Axis Sensors')

		# cmds.rowColumnLayout(numberOfColumns = 2, columnWidth = [(1, 350 / 2), (2, 350 / 2)])

		# cmds.button(label = 'Set All Forces Zero', 
		# 	command = callWith(self.rock.setChannelsZero, [0, 1, 2]))
		# cmds.button(label = 'Set All Forces One', 
		# 	command = callWith(self.rock.setChannelsOne, [0, 1, 2]))

		# cmds.button(label = 'Set All Torques Zero', 
		# 	command = callWith(self.rock.setChannelsZero, [3, 4, 5]))
		# cmds.button(label = 'Set All Torques One', 
		# 	command = callWith(self.rock.setChannelsOne, [3, 4, 5]))

		# for i, a in enumerate(['Force', 'Torque']):
		# 	for j, b in enumerate(['X', 'Y', 'Z']):
		# 		cmds.button(label = 'Set %s%s Zero' % (a, b), 
		# 			command = callWith(self.rock.setChannelsZero, [3 * i + j]))
		# 		cmds.button(label = 'Set %s%s One' % (a, b), 
		# 			command = callWith(self.rock.setChannelsOne, [3 * i + j]))
		
		cmds.showWindow()

		# Reopen window when closed (You need the button to kill threads safely)
		self.reopen_id = cmds.scriptJob(uiDeleted = ["ForceSensors", self.initWindow])

	def kill(self):
		self.dead = True

		if cmds.scriptJob(ex = self.reopen_id):
			cmds.scriptJob(kill = self.reopen_id, force = True)
		cmds.deleteUI("ForceSensors")

		self.plates.blink()
		self.plates.Close()
		self.plates.save()

		del self.rock

		print("Thread killed")

	def update(self):

		if self.dead:
			return

		self.rock.updateMeasurements()
		self.rock.updateTransform()

		self.plates.updateMeasurements()


		cmds.xform("plate1", s = [self.plates.forces[0] * 18 for i in range(3)])
		cmds.xform("plate2", s = [self.plates.forces[1] * 18 for i in range(3)])
		cmds.xform("plate3", s = [self.plates.forces[2] * 18 for i in range(3)])

		# Get translation vectors for plates
		vecs = [(self.plates.forces[i], 
				maya.OpenMaya.MVector(
					*cmds.xform('plate%s' % (i + 1), ws = True, t = 1, q = 1)
				)) for i in range(3)]
				
		# Barycentric interpolation between vectors
		center = maya.OpenMaya.MVector(0, 0, 0)
		totalWeight = 0

		for (weight, vec) in vecs:
			vec = vec * weight
			center += vec
			totalWeight += weight

		center /= totalWeight
		center.y = 0

		cmds.move(center.x, center.y, center.z, 'center')
		cmds.refresh()

		self.available = True

	def updateRequest(self):
		""" Limit to only one request at a time in the event that Maya is busy. """

		if self.available:
			self.available = False
			maya.utils.executeDeferred(self.update)
		

	def run(self):
		while not self.dead:
			time.sleep(1.0 / 60.0)
			self.updateRequest()