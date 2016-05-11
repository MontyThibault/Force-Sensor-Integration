import maya.cmds as cmds
import maya.utils

import threading
import time

# ForcePlates.py module should be loaded in Maya along with this script (See MayaReload.py)
# import ForcePlates

def main(ForcePlates):
	print("MayaScript loaded at %s!" % time.time())

	cmds.scriptJob(killAll = True)
	cmds.scriptJob(tc = "MayaScript.updateLocator()")

	if not cmds.objExists('plate1'):
		cmds.createNode( "locator", name="plate1" )
		cmds.move(10, 0, -10, "plate1")
	if not cmds.objExists('plate2'):
		cmds.createNode( "locator", name="plate2" )
		cmds.move(-10, 0, -10, "plate2")
	if not cmds.objExists('plate3'):
		cmds.createNode( "locator", name="plate3" )
		cmds.move(10, 0, 10, "plate3")

	if not cmds.objExists('center'):
		cmds.createNode( "locator", name="center" )

	if 'plates' not in globals().keys():
		plates = ForcePlates.ForcePlates()
		plates.openDevice()
		ForcePlates.program(plates)

		globals()['plates'] = plates

	SensorUpdate().start()


def updateLocator():
	print("Time changed")
	cmds.move(0, plates.forces[0], 0, "plate1", relative=True)


class SensorUpdate(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.dead = False
		self.modifiers = 0
		self.available = True

		self.plates = globals()['plates']

		# Kill previous threat if script reloads
		try:
			globals()['sensor_thread'].kill()
		except:
			pass

		globals()['sensor_thread'] = self

		self.initWindow()

	def initWindow(self):
		cmds.window("ForcePlates", width = 350)
		cmds.columnLayout(adjustableColumn = True)
	
		def callable(f, *args, **kwargs):
			""" Returns a function that will be called with the given *args and **kwargs. """

			def g(*_args, **_kwargs):
				f(*args, **kwargs)

			return g

		cmds.button(label = 'Kill Thread', command = callable(self.kill))
		cmds.button(label = 'Set Zero', command = callable(self.plates.setZero))
		cmds.button(label = 'Set One (1)', command = callable(self.plates.setOne, 0))
		cmds.button(label = 'Set One (2)', command = callable(self.plates.setOne, 1))
		cmds.button(label = 'Set One (3)', command = callable(self.plates.setOne, 2))
		cmds.showWindow()

		# Reopen window when closed (You need it to kill threads safely)
		self.reopen_id = cmds.scriptJob(uiDeleted = ["ForcePlates", self.initWindow])

	def kill(self):
		self.dead = True

		cmds.scriptJob(kill = self.reopen_id, force = True)
		cmds.deleteUI("ForcePlates")

		print("Thread killed")

	def update(self):
		""" Limit to only one request at a time in the event that Maya is busy. """

		if self.available:

			def request():

				self.modifiers = cmds.getModifiers()
				cmds.move(self.plates.forces[0] * 30, "plate1", y = True)
				cmds.move(self.plates.forces[1] * 30, "plate2", y = True)
				cmds.move(self.plates.forces[2] * 30, "plate3", y = True)

				t1 = cmds.xform('plate1', t = 1, q = 1)
				t2 = cmds.xform('plate2', t = 1, q = 1)
				t3 = cmds.xform('plate3', t = 1, q = 1)
				
				#t1 * t1.y + t2 * t2.y + t3 * t3.y

				cmds.xform('center', t = [1, 2, 3])

				cmds.refresh()

				self.available = True
	
			self.available = False
			maya.utils.executeDeferred(request)
		

	def run(self):
		while not self.dead:

			# This should coincide with the number of seconds delay for the
			# program fed into the LabPro
			time.sleep(1.0 / 20.0)

			self.plates.getForces()
			self.update()