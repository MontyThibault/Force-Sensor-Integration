import maya.cmds as cmds
import maya.utils

import threading
import time

# ForcePlates module should be loaded in Maya along with this script
# import ForcePlates

plates = None

def main(ForcePlates):
	print("Loaded!")

	cmds.scriptJob(killAll = True)
	cmds.scriptJob(tc = "MayaScript.updateLocator()")

	global plates

	plates = ForcePlates.ForcePlates()
	plates.openDevice()
	ForcePlates.program(plates)

	SensorUpdate().start()


def updateLocator():
	print("Time changed")
	cmds.move(0, plates.forces[0], 0, "plate1", relative=True)


class SensorUpdate(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.dead = False
		self.disabled = 0
		self.modifiers = 0
		self.available = True

		# Kill previous threat if script reloads
		try:
			globals()['sensor_thread'].kill()
		except:
			pass

		globals()['sensor_thread'] = self

	
	def kill(self):
		self.dead = True
		print("Thread killed")

	def update(self):
		""" Limit to only one request at a time in the event that Maya is busy. """

		if self.available:

			def request():
				self.modifiers = cmds.getModifiers()
				cmds.move(plates.forces[1], plates.forces[0], 0, "plate1")
				cmds.refresh()
				self.available = True
	
			self.available = False
			maya.utils.executeInMainThreadWithResult(request)
		

	def run(self):
		while not self.dead:

			# This should coincide with the number of seconds delay for the
			# program fed into the LabPro
			time.sleep(1.0 / 20.0)

			# Alt key down kills sensor thread
			if (self.modifiers & 8) != 0:
				self.kill()

			# Shift key down disables sensor thread
			self.disabled = (self.modifiers & 1) == 0 
			if self.disabled == 0:
				continue

			plates.getForces()
			self.update()