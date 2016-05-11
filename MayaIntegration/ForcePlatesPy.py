import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "spAnimCube"
kPluginNodeId = OpenMaya.MTypeId(0xB00B1E5)

##########################################################
# Plug-in 
##########################################################



class animCube(OpenMayaMPx.MPxNode):
    time = OpenMaya.MObject()
    outputMesh = OpenMaya.MObject()

    
    def __init__(self):
        ''' Constructor. '''

        # print("\n\n\n\n\n")

       # try:
        #    import imp
        #    plates = imp.load_source("ForcePlates", "C:\Users\Monty\Desktop\forcePlates\MayaPlugin\MayaPlugin")
        #except IOError, e:
        #    print(str(e))

        #self.sensor = plates.ForcePlates()
        #self.senor.openDevice()

        OpenMayaMPx.MPxNode.__init__(self)
    
    
    def createMesh(self, tempTime, outData):
        ''' 
        Create a cube mesh, and scale it given the current frame number. 
        The resulting mesh data is stored within outData.
        '''
        
        frame = int(tempTime.asUnits(OpenMaya.MTime.kFilm))
        if frame is 0:
            frame = 1

        cubeSize = 2

        numPolygons = 6
        numVertices = 8
        numPolygonConnects = 4 * numPolygons # four vertices are needed per polygon. (i.e. 24 numPolygonConnects)

        #self.sensor.getForces()
        #y = self.sensor.forces[0] * 10
        cmds.move(0, 0.02, 0, 'plate1')

        vertexArray = OpenMaya.MFloatPointArray()
        vertexArray.setLength( numVertices )
        vertexArray.set( OpenMaya.MFloatPoint(-cubeSize, y, -cubeSize), 0)
        vertexArray.set( OpenMaya.MFloatPoint( cubeSize, y, -cubeSize), 1)
        vertexArray.set( OpenMaya.MFloatPoint( cubeSize, y,  cubeSize), 2)
        vertexArray.set( OpenMaya.MFloatPoint(-cubeSize, y,  cubeSize), 3)
        vertexArray.set( OpenMaya.MFloatPoint(-cubeSize, y, -cubeSize), 4)
        vertexArray.set( OpenMaya.MFloatPoint(-cubeSize, y,  cubeSize), 5)
        vertexArray.set( OpenMaya.MFloatPoint( cubeSize, y,  cubeSize), 6)
        vertexArray.set( OpenMaya.MFloatPoint( cubeSize, y, -cubeSize), 7)
        
        polygonCounts = OpenMaya.MIntArray()
        polygonCounts.setLength( numPolygons )
        polygonCounts.set(4, 0)
        polygonCounts.set(4, 1)
        polygonCounts.set(4, 2)
        polygonCounts.set(4, 3)
        polygonCounts.set(4, 4)
        polygonCounts.set(4, 5)
        
        polygonConnects = OpenMaya.MIntArray()
        polygonConnects.setLength( numPolygonConnects )
        polygonConnects.set(0, 0)
        polygonConnects.set(1, 1)
        polygonConnects.set(2, 2)
        polygonConnects.set(3, 3)
        polygonConnects.set(4, 4)
        polygonConnects.set(5, 5)
        polygonConnects.set(6, 6)
        polygonConnects.set(7, 7)
        polygonConnects.set(3, 8)
        polygonConnects.set(2, 9)
        polygonConnects.set(6, 10)
        polygonConnects.set(5, 11)
        polygonConnects.set(0, 12)
        polygonConnects.set(3, 13)
        polygonConnects.set(5, 14)
        polygonConnects.set(4, 15)
        polygonConnects.set(0, 16)
        polygonConnects.set(4, 17)
        polygonConnects.set(7, 18)
        polygonConnects.set(1, 19)
        polygonConnects.set(1, 20)
        polygonConnects.set(7, 21)
        polygonConnects.set(6, 22)
        polygonConnects.set(2, 23)

        meshFn = OpenMaya.MFnMesh()
        newMesh = meshFn.create(numVertices, numPolygons, vertexArray, polygonCounts, polygonConnects, outData)
        # newMesh = meshFn.create(numVertices, numPolygons, vertexArray, polygonCounts, polygonConnects, outData

    def compute(self, plug, data):



        if plug == animCube.outputMesh:
            timeData = data.inputValue(animCube.time)
            tempTime = timeData.asTime()

            outputHandle = data.outputValue(animCube.outputMesh)

            dataCreator = OpenMaya.MFnMeshData()
            newOutputData = dataCreator.create()

            self.createMesh(tempTime, newOutputData)

            outputHandle.setMObject(newOutputData)
            data.setClean(plug)
        else:
            return OpenMaya.kUnknownParameter
        
##########################################################
# Plug-in initialization.
##########################################################
def nodeCreator():
    ''' Creates an instance of our node class and delivers it to Maya as a pointer. '''
    return OpenMayaMPx.asMPxPtr( animCube() )

def nodeInitializer():
    ''' Defines the input and output attributes as static variables in our plug-in class. '''
    unitAttr = OpenMaya.MFnUnitAttribute()
    typedAttr = OpenMaya.MFnTypedAttribute()
    
    animCube.time = unitAttr.create("time", "tm", OpenMaya.MFnUnitAttribute.kTime, 0.0)
    animCube.outputMesh = typedAttr.create("outputMesh", "out", OpenMaya.MFnData.kMesh)

    animCube.addAttribute(animCube.time)
    animCube.addAttribute(animCube.outputMesh)

    animCube.attributeAffects(animCube.time, animCube.outputMesh)


def initializePlugin(mobject):
    ''' Initialize the plug-in '''
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
    except:
        sys.stderr.write( "Failed to register node: " + kPluginNodeName )
        raise

    onload()

def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in '''

    onunload()

    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( kPluginNodeId )
    except:
        sys.stderr.write( "Failed to deregister node: " + kPluginNodeName )
        raise



import maya.cmds as cmds

def onload():

    cmds.createNode( "locator", name="plate1" )

    cmds.createNode( "transform", name="animCube1" )
    cmds.createNode( "mesh", name="animCubeShape1", parent="animCube1" )
    cmds.sets( "animCubeShape1", add="initialShadingGroup" )
    cmds.createNode( "spAnimCube", name="animCubeNode1" )
    cmds.connectAttr( "time1.outTime", "animCubeNode1.time" )
    cmds.connectAttr( "animCubeNode1.outputMesh", "animCubeShape1.inMesh" )

def onunload():
    pass