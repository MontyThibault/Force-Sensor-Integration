import pdb
import maya.cmds as cmds
import ForcePlates


def main():
	print("Loaded!")

	cmds.createNode("locator", name="plate1")
	cmds.move(0, 1, 0, "plate1")
