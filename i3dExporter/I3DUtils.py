import math
import os
import fnmatch
import xml.etree.ElementTree as ET
import maya.cmds as cmds

def transformPoint(point, mat):
    return [mat[0]*point[0] + mat[4]*point[1] + mat[8]*point[2] + mat[12],
            mat[1]*point[0] + mat[5]*point[1] + mat[9]*point[2] + mat[13],
            mat[2]*point[0] + mat[6]*point[1] + mat[10]*point[2] + mat[14]]

def transformDirection(dir, mat):
    return [mat[0]*dir[0] + mat[4]*dir[1] + mat[8]*dir[2],
            mat[1]*dir[0] + mat[5]*dir[1] + mat[9]*dir[2],
            mat[2]*dir[0] + mat[6]*dir[1] + mat[10]*dir[2]]

def invertTransformationMatrix(m):
    ret = [m[0],m[4],m[8],0.0,
           m[1],m[5],m[9],0.0,
           m[2],m[6],m[10],0.0]

    ret.append(-(m[12]*ret[0]+m[13]*ret[4]+m[14]*ret[8]))
    ret.append(-(m[12]*ret[1]+m[13]*ret[5]+m[14]*ret[9]))
    ret.append(-(m[12]*ret[2]+m[13]*ret[6]+m[14]*ret[10]))
    return ret


def vectorLength(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def vectorDot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vectorCross(a, b):
    return [a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]]

def vectorNorm(v):
    length = vectorLength(v)
    if length == 0:
        length = 1

    return [v[0]/length,
            v[1]/length,
            v[2]/length
           ]

def getFiles(path, filter):
    if filter is None:
        filter = '*'
    matches = []
    for root, dirnames, filenames in os.walk(path):
      for filename in fnmatch.filter(filenames, filter):
        matches.append(os.path.join(root, filename))
    return matches

def getFilesInDir(path, filter):
    if filter is None:
        filter = '*'
    matches = []
    for filename in fnmatch.filter(os.listdir(path), filter):
        matches.append(filename)

    return matches


def getShaderInfo(shaderPath):
    shaderInfo = {}
    tree = ET.parse(shaderPath)
    root = tree.getroot()
    parameters = root.find('Parameters')
    if not parameters is None:
        shaderInfo['parameters'] = []
        for parameter in parameters.findall('Parameter'):
            name = parameter.get('name')
            target = parameter.get('target')
            type = parameter.get('type')
            minValue = getNoNone(parameter.get('minValue'), '1 1 1 1')
            maxValue = getNoNone(parameter.get('maxValue'), '1 1 1 1')
            defaultValue = getNoNone(parameter.get('defaultValue'), '1 1 1 1')
            shaderInfo['parameters'].append({'name':name, 'target':target, 'minValue':minValue, 'maxValue':maxValue, 'defaultValue':defaultValue})

    textures = root.find('Textures')
    if not textures is None:
        shaderInfo['textures'] = {}
        for texture in textures.findall('Texture'):
            name = texture.get('name')
            defaultColorProfile = texture.get('defaultColorProfile')
            defaultFilename = texture.get('defaultFilename')
            shaderInfo['textures'][name] = {'name':name, 'defaultColorProfile':defaultColorProfile, 'defaultFilename':defaultFilename}

    variations = root.find('Variations')
    if not variations is None:
        shaderInfo['variations'] = {}
        for variation in variations.findall('Variation'):
            name = variation.get('name')
            shaderInfo['variations'][name] = {'name':name}

    return shaderInfo

def getNoNone(value, default):
    if value is None:
        return default
    return value

def getRelativePath(root, path):
    return os.path.relpath(root, path)

def getMergePaths(root, path):
    return os.path.abspath(os.path.join(root, path))

def getRelativeShaderPath(shaderPath):
        '''Gets relative path to shader file starting from maya file'''
        result = ""
        mayaFile = cmds.file(q=True,sn=True)
        mayaFile = os.path.dirname(mayaFile)
        if ( not  mayaFile ):
            return result
        if ( not ( os.path.splitdrive(shaderPath)[0] == os.path.splitdrive(mayaFile)[0] ) ):
            return result
        result  = os.path.relpath( shaderPath, mayaFile )
        result  = result.replace( "\\","/")
        return result


def linearInternalToUIVector( linear ):
    return [linearInternalToUI(linear[0]), linearInternalToUI(linear[1]), linearInternalToUI(linear[2])]

def linearUIToInternal( linear ):
    factor = 1.0
    pref = cmds.currentUnit(q=True, l=True)
    if ( pref == 'mm' ): factor = 0.1
    if ( pref == 'm' ): factor = 100.0
    if ( pref == 'inch' ): factor = 2.54
    if ( pref == 'ft' ): factor = 30.48
    if ( pref == 'yard' ): factor = 91.44
    return (linear * factor)

def linearUIToInternalVector( linear ):
    return [linearUIToInternal(linear[0]), linearUIToInternal(linear[1]), linearUIToInternal(linear[2])]

def linearInternalToUI( linear ):
    factor = 1.0
    pref = cmds.currentUnit(q=True, l=True)
    if ( pref == 'mm' ): factor = 10.0
    if ( pref == 'm' ): factor = 0.01
    if ( pref == 'inch' ): factor = 0.3937007874
    if ( pref == 'ft' ): factor = 0.03280839895
    if ( pref == 'yard' ): factor = 0.01093613298
    return ( linear * factor )

def angleUIToInternal(angle):
    pref = cmds.currentUnit(q=True, a=True)
    if ( pref == 'deg' ):  angle = angle * 0.0174532925
    return angle

def angleInternalToUI(angle):
    pref = cmds.currentUnit(q=True, a=True)
    if ( pref == 'deg' ): angle = angle * 57.29577951308
    return angle

def getIndexPath(node):
    indexPath = str(getCurrentNodeIndex(node))

    currentNode = node
    while True:
        parent = cmds.listRelatives(currentNode, parent=True, fullPath=True)
        if parent is None:
            break
        indexPath = str(getCurrentNodeIndex(parent[0])) + '|' + indexPath
        currentNode = parent[0]

    if indexPath.find('|') != -1:
        indexPath = indexPath.replace('|', '>', 1)
    else:
        indexPath = indexPath + '>'

    return indexPath

def getObjectByIndex(indexPath):
    def analyseIndexPath(path):
        indexParts = path.split(">")
        component = indexParts[0]
        childs = indexParts[1].split("|")

        return component, childs

    def getValidChilds(parent):
        childs = cmds.listRelatives(parent, c=True, f=True)
        valid = []
        for child in childs:
            if cmds.nodeType(child) != "mesh":
                valid.append(child)
        return valid

    component, childs = analyseIndexPath(indexPath)
    components = getComponents()
    component = components[int(component)]

    currentObject = component
    for child in childs:
        if child != '':
            currentChilds = getValidChilds(currentObject)
            if int(child) >= len(currentChilds):
                print("Could not find given index '"+indexPath+"'!")
                if len(currentChilds) > 0:
                    currentObject = currentChilds[len(currentChilds)-1]
                break
            currentObject = currentChilds[int(child)]

    return currentObject

def getCurrentNodeIndex(node):
    parent = cmds.listRelatives(node, parent=True, fullPath=True)
    elements = None
    if not parent is None:
        elements = cmds.listRelatives(parent, children=True, type='transform', fullPath=True)
    else:
        elements = cmds.ls(assemblies=True, long=True)
    i = -1
    if not elements is None:
        for elem in elements:
            if not isDefaultCamera(elem):
                i = i + 1
            if elem == node:
                break

    return i

def getParent(node):
    parents = cmds.listRelatives(node, p=True, pa=True, f=True)
    parent = None
    if not parents is None:
        parent = parents[0]

    return parent

def isDefaultCamera(node):
    try:
        return cmds.camera(node, q=True, startupCamera=True)
    except:
        return False

def isCamera(node):
    return cmds.nodeType(cmds.listRelatives(node, s=True, pa=True)) == 'camera'

def isShape(node):
    if node.find("Shape") > -1:
        return True
    else:
        return False

def getComponents():
    valid = []
    objects = cmds.ls(l=True)

    for object in objects:
        childs = object.split("|")
        if len(childs) == 2:
            if not isCamera(object) and not isShape(object):
                valid.append(object)

    return valid

def getMeshVolume(node):
    selection = cmds.ls(selection=True)

    # based on http://www.vfxoverflow.com/questions/getting-the-volume-of-an-arbitrary-closed-mesh
    duplicate = cmds.duplicate(node, rr=True, inputConnections=False, upstreamNodes=False)
    children = cmds.listRelatives(duplicate, type='transform', fullPath=True)
    if not children is None:
        for child in children:
            print("Delete " + child)
            cmds.delete(child)

    cmds.makeIdentity(duplicate, apply=True, t=True, r=True, s=True, n=False)
    cmds.polyTriangulate(duplicate)
    triangles = cmds.ls(duplicate[0]+'.f[*]', flatten=True)
    volume = 0
    for triangle in triangles:
        triVolume = 0
        triVertices = cmds.polyListComponentConversion(triangle, tv=True)
        triVertices = cmds.ls(triVertices, flatten=True)

        if len(triVertices) != 3:
            cmds.error(triangle + " is not a triangle")

        v1 = cmds.pointPosition(triVertices[0], w=True)
        v2 = cmds.pointPosition(triVertices[1], w=True)
        v3 = cmds.pointPosition(triVertices[2], w=True)

        res = cmds.polyInfo(triangle, fn=True)

        buff = res[0].split(":")
        buff = buff[1].split(" ")
        vector = [float(buff[1]), float(buff[2]), float(buff[3])]
        faceNormal = vectorNorm(vector)
        area = abs(((v1[0])*((v3[1])-(v2[1])))+((v2[0])*((v1[1])-(v3[1])))+((v3[0])*((v2[1])-(v1[1])))) *0.5
        triVolume = 0
        triVolume = ((v1[2] + v2[2] + v3[2]) / 3.0) * area
        if ((faceNormal[2]) < 0):
            triVolume = -triVolume

        volume = volume + triVolume

    cmds.delete(duplicate)

    cmds.select(selection)

    return volume

def getSelectedObjects():
    # returns selected objects, even if we only select a vertex of the object
    selection = [object.split('.')[0] for object in cmds.ls(sl=True)]

    # remove multiple instances of one object
    selection = list(set(selection))
    return selection
