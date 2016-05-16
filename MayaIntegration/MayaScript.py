import maya.cmds as cmds
import maya.utils
import maya.OpenMaya

import threading
import time

import sys 
import os

from ctypes import *

import ForcePlates
import PAIO
import SixAxis
import Calibration

reload(ForcePlates)
reload(PAIO)
reload(SixAxis)
reload(Calibration)


def main():
	maya.utils.executeDeferred(init)

def init():
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


	plates = ForcePlates.ForcePlates()

	deviceA000 = PAIO.AIODevice()
	aio = PAIO.AIO()

	deviceA000.Init()
	deviceA000.AioSetAiRangeAll(aio.PM10)

	channels = [6, 7, 8, 9, 10, 11]
	rock = SixAxis.SixAxis(deviceA000, channels, "rock1")

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

		cmds.window("ForceSensors", width = 350)
		cmds.columnLayout(adjustableColumn = True)

		# The button command will add an extra argument that we don't want, hence the callWith() wrapper
		cmds.button(label = 'Kill Thread', command = callWith(self.kill))

		# cmds.button(label = 'Set Zero', command = callWith(self.plates.setZero))
		# cmds.button(label = 'Set One (1)', command = callWith(self.plates.setOne, 0))
		# cmds.button(label = 'Set One (2)', command = callWith(self.plates.setOne, 1))
		# cmds.button(label = 'Set One (3)', command = callWith(self.plates.setOne, 2))

		cmds.button(label = 'Set Forces Zero', 
			command = callWith(self.rock.setChannelsZero, [0, 1, 2]))
		cmds.button(label = 'Set Torques Zero', 
			command = callWith(self.rock.setChannelsZero, [3, 4, 5]))

		cmds.showWindow()

		# Reopen window when closed (You need the button to kill threads safely)
		self.reopen_id = cmds.scriptJob(uiDeleted = ["ForceSensors", self.initWindow])

	def kill(self):
		self.dead = True

		if cmds.scriptJob(ex = self.reopen_id):
			cmds.scriptJob(kill = self.reopen_id, force = True)
		cmds.deleteUI("ForceSensors")

		self.plates.closeDevice()
		self.rock.save()

		print("Thread killed")

	def update(self):

		# self.plates.getForces()
		# print(self.plates._forces[0])

		self.rock.updateMeasurements()
		self.rock.updateTransform()

		print(self.rock.forces, self.rock.torques)

		# cmds.move(0, 30.0 * voltage.value, 0, "center")


		# self.modifiers = cmds.getModifiers()
		# cmds.move(self.plates.forces[0] * 30, "plate1", y = True)
		# cmds.move(self.plates.forces[1] * 30, "plate2", y = True)
		# cmds.move(self.plates.forces[2] * 30, "plate3", y = True)

		# # Get translation vectors for plates
		# vecs = [(self.plates.forces[i], 
		# 		maya.OpenMaya.MVector(
		# 			*cmds.xform('plate%s' % (i + 1), ws = True, t = 1, q = 1)
		# 		)) for i in range(3)]
				
		# # Barycentric interpolation between vectors
		# center = maya.OpenMaya.MVector(0, 0, 0)
		# totalWeight = 0

		# for (weight, vec) in vecs:
		# 	vec = vec * weight
		# 	center += vec
		# 	totalWeight += weight

		# center /= totalWeight
		# center.y = 0

		# cmds.move(center.x, center.y, center.z, 'center')
		# cmds.refresh()

		self.available = True

	def updateRequest(self):
		""" Limit to only one request at a time in the event that Maya is busy. """

		if self.available:
			self.available = False
			maya.utils.executeDeferred(self.update)
		

	def run(self):
		while not self.dead:

			# This should coincide with the number of seconds delay for the
			# program fed into the LabPro
			time.sleep(1.0 / 25.0)

			self.updateRequest()

if __name__ == '__main__':
	main()