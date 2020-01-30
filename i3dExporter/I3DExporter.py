#
# i3D Toolbox (.py)
#
# @author Christian Ammann, Stefan Geiger
# @modified Evgeniy Zaitsev, Manuel Leithner
# @created 03/05/03
# @modified 24/06/15
#
# Copyright (c) 2008-2015 GIANTS Software GmbH, Confidential, All Rights Reserved.
# Copyright (c) 2003-2015 Christian Ammann and Stefan Geiger, Confidential, All Rights Reserved.
#

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import I3DUtils as I3DUtils
import tempfile
import sys
import math
import os
import re
import fnmatch
import deleteDuplicateMaterials
import deleteDuplicateTextures
import MaterialRenamer
import getComponentShader

reload(I3DUtils)

g_exportWarningCount = 0
g_exportErrorCount = 0
g_exportSkinnedMergeMaterials = {}
g_exportNumSkinnedMergeJoints = {}
g_exportSkinnedMergeVolumes = {}
g_exportSkinnedMergeRootNodes = {}
g_exportXMLIdentifiers = {}

VERSION = '8.0.0'

export_PolyCount = 0
export_ObjectCount = 0

# constants
TITLE = 'GIANTS Software - I3D Toolbox (Version ' + VERSION + ')'
SETTINGS_PREFIX = 'I3DExportSettings'
NODETYPE_GROUP = 0
NODETYPE_MESH = 1
TYPE_BOOL = 1
TYPE_INT = 2
TYPE_FLOAT = 3
TYPE_STRING = 4
TEXT_WIDTH = 110
DEFAULT_FIELD_WIDTH = 60
MASK_FIELD_WIDTH = 70
WINDOW_WIDTH = 460
MAX_POLYCOUNT = 180000
MAX_OBJECTCOUNT = 150
MAX_SKINNED_JOINTS = 60

UI_OPTIONS_PREDEFINED_VEHICLES_ATTRIBUTES = 'giants_optionsPredefinedVehicleAttributes'
UI_OPTIONS_PREDEFINED_MESH_ATTRIBUTES = 'giants_optionsPredefinedMeshAttributes'
UI_OPTIONS_PREDEFINED_SHADER_ATTRIBUTES = 'giants_optionsPredefinedShaderAttributes'
UI_OPTIONS_PREDEFINED_PHYSICS = 'giants_optionsPredefinedPhysics'
UI_OPTIONS_PREDEFINED_BOUNDINGVOLUME = 'giants_optionsBoundingVolume'
UI_OPTIONS_SKELETONS = 'giants_optionsSkeletons'

# UI_CONTROL_DOCK = 'giants_dockControl'
UI_CONTROL_WINDOW = 'i3DExport'
UI_CONTROL_EXPORT_1 = 'ExportParts'
UI_CONTROL_EXPORT_2 = 'ExportParts2'
UI_CONTROL_EXPORT_3 = 'ExportParts3'
UI_CONTROL_EXPORT_4 = 'ExportParts4'
UI_CONTROL_SHAPES_1 = 'ShapeIncludes'
UI_CONTROL_SHAPES_2 = 'ShapeIncludes2'
UI_CONTROL_MISC_1 = 'Misc'
UI_CONTROL_MISC_2 = 'Misc2'
UI_CONTROL_BOOL_USE_MAYA_FILENAME = 'FilenameInfo'
UI_CONTROL_STRING_VALIDATION = 'giants_validationField'
UI_CONTROL_STRING_FILE_PATH = 'giants_outputFileLocationPath'
UI_CONTROL_STRING_XML_FILE_PATH = 'giants_xmlConfigFileLocationPath'
UI_CONTROL_STRING_XML_TAG = 'giants_xmlConfigFileTag'
UI_CONTROL_STRING_SHADER_ATTRIBUTE = 'giants_attributecustomValue'
UI_CONTROL_STRING_LOADED_NODE_NAME = 'giants_attributeLoadedObjectName'
UI_CONTROL_STRING_NODE_TO_SELECT = 'giants_attributeObjectIndexToSelect'
UI_CONTROL_STRING_NODE_NAME = 'giants_attributeObjectName'
UI_CONTROL_STRING_NODE_INDEX = 'giants_attributeObjectIndex'
UI_CONTROL_STRING_IDENTIFIER = 'giants_attributeStringXmlIdentifier'
UI_CONTROL_BOOL_STATIC = 'giants_attributeBoolStatic'
UI_CONTROL_BOOL_KINEMATIC = 'giants_attributeBoolKinematic'
UI_CONTROL_BOOL_DYNAMIC = 'giants_attributeBoolDynamic'
UI_CONTROL_BOOL_COMPOUND = 'giants_attributeBoolCompound'
UI_CONTROL_BOOL_COMPOUND_CHILD = 'giants_attributeBoolCompoundChild'
UI_CONTROL_BOOL_COLLISION = 'giants_attributeBoolCollision'
UI_CONTROL_BOOL_CPUMESH = 'giants_attributeBoolCPUMesh'
UI_CONTROL_BOOL_LOD = 'giants_attributeBoolLOD'
UI_CONTROL_BOOL_CCD = 'giants_attributeBoolCCD'
UI_CONTROL_BOOL_TRIGGER = 'giants_attributeBoolTrigger'
UI_CONTROL_BOOL_JOINT = 'giants_attributeBoolJoint'
UI_CONTROL_BOOL_PROJECTION = 'giants_attributeBoolProjection'
UI_CONTROL_BOOL_XAXIS_DRIVE = 'giants_attributeBoolXAxisDrive'
UI_CONTROL_BOOL_YAXIS_DRIVE = 'giants_attributeBoolYAxisDrive'
UI_CONTROL_BOOL_ZAXIS_DRIVE = 'giants_attributeBoolZAxisDrive'
UI_CONTROL_BOOL_DRIVE_POSITION = 'giants_attributeBoolDrivePosition'
UI_CONTROL_BOOL_BREAKABLE = 'giants_attributeBoolBreakable'
UI_CONTROL_BOOL_OCCLUSION_CULLING = 'giants_attributeBoolOcclusionCulling'
UI_CONTROL_BOOL_NON_RENDERABLE = 'giants_attributeBoolNonRenderable'
UI_CONTROL_INT_COLLISION_MASK = 'giants_attributeIntCollisionMask'
UI_CONTROL_INT_SOLVER_ITERATIONS = 'giants_attributeIntSolverIterations'
UI_CONTROL_INT_DECAL_LAYER = 'giants_attributeIntDecalLayer'
UI_CONTROL_INT_MERGE_GROUP = 'giants_attributeIntMergeGroup'
UI_CONTROL_BOOL_MERGE_GROUP_ROOT = 'giants_attributeBoolMergeGroupRoot'
UI_CONTROL_INT_SPLITTYPE = 'giants_attributeIntSplitType'
UI_CONTROL_FLOAT_SPLIT_MIN_U = 'giants_attributeFloatSplitMinU'
UI_CONTROL_FLOAT_SPLIT_MIN_V = 'giants_attributeFloatSplitMinV'
UI_CONTROL_FLOAT_SPLIT_MAX_U = 'giants_attributeFloatSplitMaxU'
UI_CONTROL_FLOAT_SPLIT_MAX_V = 'giants_attributeFloatSplitMaxV'
UI_CONTROL_FLOAT_SPLIT_UV_WORLD_SCALE = 'giants_attributeFloatSplitUvWorldScale'
UI_CONTROL_INT_OBJECT_MASK = 'giants_attributeFloatObjectMask'
UI_CONTROL_FLOAT_PROJECTION_DISTANCE = 'giants_attributeFloatProjectionDistance'
UI_CONTROL_FLOAT_PROJECTION_ANGLE = 'giants_attributeFloatProjectionAngle'
UI_CONTROL_FLOAT_DRIVE_FORCE_LIMIT = 'giants_attributeFloatDriveForceLimit'
UI_CONTROL_FLOAT_DRIVE_SPRING = 'giants_attributeFloatDriveSpring'
UI_CONTROL_FLOAT_DRIVE_DAMPING = 'giants_attributeFloatDriveDamping'
UI_CONTROL_FLOAT_BREAK_FORCE = 'giants_attributeFloatBreakForce'
UI_CONTROL_FLOAT_BREAK_TORQUE = 'giants_attributeFloatBreakTorque'
UI_CONTROL_FLOAT_CLIP_DISTANCE = 'giants_attributeFloatClipDistance'
UI_CONTROL_FLOAT_RESTITUTION = 'giants_attributeFloatRestitution'
UI_CONTROL_FLOAT_STATIC_FRICTION = 'giants_attributeFloatStaticFriction'
UI_CONTROL_FLOAT_DYNAMIC_FRICTION = 'giants_attributeFloatDynamicFriction'
UI_CONTROL_FLOAT_LINEAR_DAMPING = 'giants_attributeFloatLinearDamping'
UI_CONTROL_FLOAT_ANGULAR_DAMPING = 'giants_attributeFloatAngularDamping'
UI_CONTROL_FLOAT_DENSITY = 'giants_attributeFloatDensity'
UI_CONTROL_FLOAT_MASS = 'giants_attributeFloatMass'
UI_CONTROL_STRING_MASS_NODE = 'giants_attributeStringMassNode'
UI_CONTROL_LABEL_MASS = 'giants_attributeLabelMass'
UI_CONTROL_FLOAT_CHILD_0_DISTANCE = 'giants_attributeFloatChild0Distance'
UI_CONTROL_FLOAT_CHILD_1_DISTANCE = 'giants_attributeFloatChild1Distance'
UI_CONTROL_FLOAT_CHILD_2_DISTANCE = 'giants_attributeFloatChild2Distance'
UI_CONTROL_FLOAT_CHILD_3_DISTANCE = 'giants_attributeFloatChild3Distance'
UI_CONTROL_BOOL_SCALED = 'giants_attributeBoolScaled'
UI_CONTROL_STRING_LIGHT_MASK = 'giants_attributeStringLightMask'
UI_CONTROL_STRING_BOUNDINGVOLUME = 'giants_attributeStringBoundingVolume'
UI_CONTROL_PARAMETERS_SCROLL = 'giants_shaderParametersScroll'
UI_CONTROL_TEXTURES_SCROLL = 'giants_shaderTexturesScroll'
UI_CONTROL_PARAMETERS = 'giants_shaderParameters'
UI_CONTROL_TEXTURES = 'giants_shaderTextures'
UI_CONTROL_VARIATIONS = 'giants_shaderVariations'
UI_CONTROL_LAYOUT_PARAMETERS = 'giants_layoutShaderParameters'
UI_CONTROL_LAYOUT_TEXTURES = 'giants_layoutShaderTextures'
UI_CONTROL_LAYOUT_VARIATIONS = 'giants_layoutShaderVariations'
UI_CONTROL_MENU_VARIATIONS = 'giants_shaderSettingsVariations'
UI_CONTROL_STRING_SHADER_PATH = 'giants_shaderPath'
UI_CONTROL_STRING_UVSET_NAME = 'giants_uvSetName'

UI_CONTROL_FRAME_OPTIONS = 'giants_frameOptions'
UI_CONTROL_FRAME_SHAPE_SUBPARTS = 'giants_frameShapeSubparts'
UI_CONTROL_FRAME_MISC = 'giants_frameMisc'
UI_CONTROL_FRAME_XML_FILE = 'giants_frameXmlFile'
UI_CONTROL_FRAME_OUTPUT_FILE = 'giants_frameOutputFile'
UI_CONTROL_FRAME_EXPORT = 'giants_frameExport'
UI_CONTROL_FRAME_ERRORS = 'giants_frameErrors'
UI_CONTROL_FRAME_XML_IDENTIFIER = 'giants_frameXmlIdentifier'
UI_CONTROL_FRAME_RIGID_BODY = 'giants_frameRigidBody'
UI_CONTROL_FRAME_JOINT = 'giants_frameJoint'
UI_CONTROL_FRAME_RENDERING = 'giants_frameRendering'
UI_CONTROL_FRAME_PIVOT = 'giants_framePivot'
UI_CONTROL_FRAME_FREEZE = 'giants_frameFreeze'
UI_CONTROL_FRAME_MESH = 'giants_frameMesh'
UI_CONTROL_FRAME_MATERIAL = 'giants_frameMaterial'
UI_CONTROL_FRAME_UVS = 'giants_frameUVs'
UI_CONTROL_FRAME_SKELETON = 'giants_frameSkeleton'
UI_CONTROL_FRAME_UI = 'giants_frameUI'

SETTINGS_VEHICLE_ATTRIBUTES = []
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Default', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 0,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Vehicle - Compound (Tractor, Truck)', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 2105410,
                                                        'clipDistance': 300, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Vehicle - CompoundChild (Tractor, Truck)', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': False, 'compoundChild': True, 'trigger': False,
                                                        'collision': True, 'collisionMask': 2105410, 'clipDistance': 0,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 0.001}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Combine - Compound', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 4202626,
                                                        'clipDistance': 300, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Combine - CompoundChild', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': False, 'compoundChild': True, 'trigger': False,
                                                        'collision': True, 'collisionMask': 4202626, 'clipDistance': 0,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 0.001}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Fillable', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 8397058,
                                                        'clipDistance': 300, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Tool - Compound', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 8194, 'clipDistance': 300,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Tool - CompoundChild', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': False, 'compoundChild': True, 'trigger': False,
                                                        'collision': True, 'collisionMask': 8194, 'clipDistance': 0,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 0.001}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Cutter', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 67121154,
                                                        'clipDistance': 300, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Shovel', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': True, 'kinematic': False,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 8396802,
                                                        'clipDistance': 300, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'TrafficVehicle', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': True,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 2105442,
                                                        'clipDistance': 350, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0, 'objectMask': 65535}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'FillVolume', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 300,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 1,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'EmitterShape', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 300,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 1,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'ShadowFocusBox', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 150,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 1,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Trigger - Trailer/ShovelTip Trigger', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': True,
                                                        'compound': True, 'compoundChild': False, 'trigger': True,
                                                        'collision': True, 'collisionMask': 1073741824,
                                                        'clipDistance': 0, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Trigger - ExactFillRootNode', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': True,
                                                        'compound': True, 'compoundChild': False, 'trigger': False,
                                                        'collision': True, 'collisionMask': 1073741824,
                                                        'clipDistance': 0, 'nonRenderable': True, 'decalLayer': 0,
                                                        'cpuMesh': 0, 'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Trigger - AICollisionTrigger', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': True,
                                                        'compound': True, 'compoundChild': False, 'trigger': True,
                                                        'collision': True, 'collisionMask': 1056768, 'clipDistance': 0,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Trigger - TrafficCollisionTrigger', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': True,
                                                        'compound': True, 'compoundChild': False, 'trigger': True,
                                                        'collision': True, 'collisionMask': 34611200, 'clipDistance': 0,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Trigger - DynamicMountTrigger', 'isPhyiscObject': True,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': True,
                                                        'compound': True, 'compoundChild': False, 'trigger': True,
                                                        'collision': True, 'collisionMask': 83886080, 'clipDistance': 0,
                                                        'nonRenderable': True, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Lights -  Real', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 75,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Lights -  Coronas', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 200,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Lights -  Static', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 35,
                                                        'nonRenderable': False, 'decalLayer': 1, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Decals - Small', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 30,
                                                        'nonRenderable': False, 'decalLayer': 1, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Decals - Big', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 50,
                                                        'nonRenderable': False, 'decalLayer': 1, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Exterior', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 300,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Interior', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 75,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'IndoorHud', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 20,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'Mirrors', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 20,
                                                        'nonRenderable': False, 'decalLayer': 1, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'WindowsInside', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 20,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})
SETTINGS_VEHICLE_ATTRIBUTES.append({'name': 'WindowsOutside', 'isPhyiscObject': False,
                                    'attributeValues': {'static': False, 'dynamic': False, 'kinematic': False,
                                                        'compound': False, 'compoundChild': False, 'trigger': False,
                                                        'collision': False, 'collisionMask': 255, 'clipDistance': 200,
                                                        'nonRenderable': False, 'decalLayer': 0, 'cpuMesh': 0,
                                                        'density': 1.0}})

SETTINGS_ATTRIBUTES = {}
SETTINGS_ATTRIBUTES['i3D_static'] = {'type': TYPE_BOOL, 'defaultValue': True, 'uiControl': UI_CONTROL_BOOL_STATIC}
SETTINGS_ATTRIBUTES['i3D_dynamic'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_DYNAMIC}
SETTINGS_ATTRIBUTES['i3D_kinematic'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                        'uiControl': UI_CONTROL_BOOL_KINEMATIC}
SETTINGS_ATTRIBUTES['i3D_compound'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_COMPOUND}
SETTINGS_ATTRIBUTES['i3D_compoundChild'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                            'uiControl': UI_CONTROL_BOOL_COMPOUND_CHILD}
SETTINGS_ATTRIBUTES['i3D_collision'] = {'type': TYPE_BOOL, 'defaultValue': True, 'uiControl': UI_CONTROL_BOOL_COLLISION}
SETTINGS_ATTRIBUTES['i3D_collisionMask'] = {'type': TYPE_INT, 'defaultValue': 255,
                                            'uiControl': UI_CONTROL_INT_COLLISION_MASK}
SETTINGS_ATTRIBUTES['i3D_solverIterationCount'] = {'type': TYPE_INT, 'defaultValue': 4,
                                                   'uiControl': UI_CONTROL_INT_SOLVER_ITERATIONS}
SETTINGS_ATTRIBUTES['i3D_restitution'] = {'type': TYPE_FLOAT, 'defaultValue': 0,
                                          'uiControl': UI_CONTROL_FLOAT_RESTITUTION}
SETTINGS_ATTRIBUTES['i3D_staticFriction'] = {'type': TYPE_FLOAT, 'defaultValue': 0.5,
                                             'uiControl': UI_CONTROL_FLOAT_STATIC_FRICTION}
SETTINGS_ATTRIBUTES['i3D_dynamicFriction'] = {'type': TYPE_FLOAT, 'defaultValue': 0.5,
                                              'uiControl': UI_CONTROL_FLOAT_DYNAMIC_FRICTION}
SETTINGS_ATTRIBUTES['i3D_linearDamping'] = {'type': TYPE_FLOAT, 'defaultValue': 0.0,
                                            'uiControl': UI_CONTROL_FLOAT_LINEAR_DAMPING}
SETTINGS_ATTRIBUTES['i3D_angularDamping'] = {'type': TYPE_FLOAT, 'defaultValue': 0.01,
                                             'uiControl': UI_CONTROL_FLOAT_ANGULAR_DAMPING}
SETTINGS_ATTRIBUTES['i3D_density'] = {'type': TYPE_FLOAT, 'defaultValue': 1.0, 'uiControl': UI_CONTROL_FLOAT_DENSITY}
SETTINGS_ATTRIBUTES['i3D_ccd'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_CCD}
SETTINGS_ATTRIBUTES['i3D_trigger'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_TRIGGER}
SETTINGS_ATTRIBUTES['i3D_splitType'] = {'type': TYPE_INT, 'defaultValue': 0, 'uiControl': UI_CONTROL_INT_SPLITTYPE}
SETTINGS_ATTRIBUTES['i3D_splitMinU'] = {'type': TYPE_FLOAT, 'defaultValue': 0.0,
                                        'uiControl': UI_CONTROL_FLOAT_SPLIT_MIN_U}
SETTINGS_ATTRIBUTES['i3D_splitMinV'] = {'type': TYPE_FLOAT, 'defaultValue': 0.0,
                                        'uiControl': UI_CONTROL_FLOAT_SPLIT_MIN_V}
SETTINGS_ATTRIBUTES['i3D_splitMaxU'] = {'type': TYPE_FLOAT, 'defaultValue': 1.0,
                                        'uiControl': UI_CONTROL_FLOAT_SPLIT_MAX_U}
SETTINGS_ATTRIBUTES['i3D_splitMaxV'] = {'type': TYPE_FLOAT, 'defaultValue': 1.0,
                                        'uiControl': UI_CONTROL_FLOAT_SPLIT_MAX_V}
SETTINGS_ATTRIBUTES['i3D_splitUvWorldScale'] = {'type': TYPE_FLOAT, 'defaultValue': 1.0,
                                                'uiControl': UI_CONTROL_FLOAT_SPLIT_UV_WORLD_SCALE}
SETTINGS_ATTRIBUTES['i3D_joint'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_JOINT}
SETTINGS_ATTRIBUTES['i3D_projection'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                         'uiControl': UI_CONTROL_BOOL_PROJECTION}
SETTINGS_ATTRIBUTES['i3D_projDistance'] = {'type': TYPE_FLOAT, 'defaultValue': 0.01,
                                           'uiControl': UI_CONTROL_FLOAT_PROJECTION_DISTANCE}
SETTINGS_ATTRIBUTES['i3D_projAngle'] = {'type': TYPE_FLOAT, 'defaultValue': 0.01,
                                        'uiControl': UI_CONTROL_FLOAT_PROJECTION_ANGLE}
SETTINGS_ATTRIBUTES['i3D_xAxisDrive'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                         'uiControl': UI_CONTROL_BOOL_XAXIS_DRIVE}
SETTINGS_ATTRIBUTES['i3D_yAxisDrive'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                         'uiControl': UI_CONTROL_BOOL_YAXIS_DRIVE}
SETTINGS_ATTRIBUTES['i3D_zAxisDrive'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                         'uiControl': UI_CONTROL_BOOL_ZAXIS_DRIVE}
SETTINGS_ATTRIBUTES['i3D_drivePos'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                       'uiControl': UI_CONTROL_BOOL_DRIVE_POSITION}
SETTINGS_ATTRIBUTES['i3D_driveForceLimit'] = {'type': TYPE_FLOAT, 'defaultValue': 100000,
                                              'uiControl': UI_CONTROL_FLOAT_DRIVE_FORCE_LIMIT}
SETTINGS_ATTRIBUTES['i3D_driveSpring'] = {'type': TYPE_FLOAT, 'defaultValue': 1.0,
                                          'uiControl': UI_CONTROL_FLOAT_DRIVE_SPRING}
SETTINGS_ATTRIBUTES['i3D_driveDamping'] = {'type': TYPE_FLOAT, 'defaultValue': 0.01,
                                           'uiControl': UI_CONTROL_FLOAT_DRIVE_DAMPING}
SETTINGS_ATTRIBUTES['i3D_breakableJoint'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                             'uiControl': UI_CONTROL_BOOL_BREAKABLE}
SETTINGS_ATTRIBUTES['i3D_jointBreakForce'] = {'type': TYPE_FLOAT, 'defaultValue': 0.0,
                                              'uiControl': UI_CONTROL_FLOAT_BREAK_FORCE}
SETTINGS_ATTRIBUTES['i3D_jointBreakTorque'] = {'type': TYPE_FLOAT, 'defaultValue': 0.0,
                                               'uiControl': UI_CONTROL_FLOAT_BREAK_TORQUE}
SETTINGS_ATTRIBUTES['i3D_oc'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                 'uiControl': UI_CONTROL_BOOL_OCCLUSION_CULLING}
SETTINGS_ATTRIBUTES['i3D_nonRenderable'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                            'uiControl': UI_CONTROL_BOOL_NON_RENDERABLE}
SETTINGS_ATTRIBUTES['i3D_clipDistance'] = {'type': TYPE_FLOAT, 'defaultValue': 0,
                                           'uiControl': UI_CONTROL_FLOAT_CLIP_DISTANCE}
SETTINGS_ATTRIBUTES['i3D_objectMask'] = {'type': TYPE_INT, 'defaultValue': 255, 'uiControl': UI_CONTROL_INT_OBJECT_MASK}
SETTINGS_ATTRIBUTES['i3D_lightMask'] = {'type': TYPE_STRING, 'defaultValue': 'FFFF',
                                        'uiControl': UI_CONTROL_STRING_LIGHT_MASK}
SETTINGS_ATTRIBUTES['i3D_decalLayer'] = {'type': TYPE_INT, 'defaultValue': 0, 'uiControl': UI_CONTROL_INT_DECAL_LAYER}
SETTINGS_ATTRIBUTES['i3D_mergeGroup'] = {'type': TYPE_INT, 'defaultValue': 0, 'uiControl': UI_CONTROL_INT_MERGE_GROUP}
SETTINGS_ATTRIBUTES['i3D_mergeGroupRoot'] = {'type': TYPE_BOOL, 'defaultValue': False,
                                             'uiControl': UI_CONTROL_BOOL_MERGE_GROUP_ROOT}
SETTINGS_ATTRIBUTES['i3D_boundingVolume'] = {'type': TYPE_STRING, 'defaultValue': '',
                                             'uiControl': UI_CONTROL_STRING_BOUNDINGVOLUME}

SETTINGS_ATTRIBUTES['i3D_cpuMesh'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_CPUMESH}
SETTINGS_ATTRIBUTES['i3D_lod'] = {'type': TYPE_BOOL, 'defaultValue': False, 'uiControl': UI_CONTROL_BOOL_LOD}
SETTINGS_ATTRIBUTES['i3D_lod1'] = {'type': TYPE_FLOAT, 'defaultValue': 0,
                                   'uiControl': UI_CONTROL_FLOAT_CHILD_1_DISTANCE}
SETTINGS_ATTRIBUTES['i3D_lod2'] = {'type': TYPE_FLOAT, 'defaultValue': 0,
                                   'uiControl': UI_CONTROL_FLOAT_CHILD_2_DISTANCE}
SETTINGS_ATTRIBUTES['i3D_lod3'] = {'type': TYPE_FLOAT, 'defaultValue': 0,
                                   'uiControl': UI_CONTROL_FLOAT_CHILD_3_DISTANCE}
SETTINGS_ATTRIBUTES['i3D_scaled'] = {'type': TYPE_BOOL, 'defaultValue': 0, 'uiControl': UI_CONTROL_BOOL_SCALED}

SETTINGS_EXPORTER = {}
SETTINGS_EXPORTER['i3D_exportIK'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_EXPORT_1}
SETTINGS_EXPORTER['i3D_exportAnimation'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2, 'uiControl': UI_CONTROL_EXPORT_1}
SETTINGS_EXPORTER['i3D_exportShapes'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 3, 'uiControl': UI_CONTROL_EXPORT_1}
SETTINGS_EXPORTER['i3D_exportNurbsCurves'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_EXPORT_2}
SETTINGS_EXPORTER['i3D_exportLights'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2, 'uiControl': UI_CONTROL_EXPORT_2}
SETTINGS_EXPORTER['i3D_exportCameras'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 3, 'uiControl': UI_CONTROL_EXPORT_2}
SETTINGS_EXPORTER['i3D_exportParticleSystems'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1,
                                                  'uiControl': UI_CONTROL_EXPORT_3}
SETTINGS_EXPORTER['i3D_exportDefaultCameras'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2,
                                                 'uiControl': UI_CONTROL_EXPORT_3}
SETTINGS_EXPORTER['i3D_exportUserAttributes'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 3,
                                                 'uiControl': UI_CONTROL_EXPORT_3}
SETTINGS_EXPORTER['i3D_exportBynaryFiles'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_EXPORT_4}
SETTINGS_EXPORTER['i3D_exportIgnoreBindPoses'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2,
                                                  'uiControl': UI_CONTROL_EXPORT_4}
SETTINGS_EXPORTER['i3D_exportNormals'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_SHAPES_1}
SETTINGS_EXPORTER['i3D_exportColors'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2, 'uiControl': UI_CONTROL_SHAPES_1}
SETTINGS_EXPORTER['i3D_exportTexCoords'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 3, 'uiControl': UI_CONTROL_SHAPES_1}
SETTINGS_EXPORTER['i3D_exportSkinWeigths'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_SHAPES_2}
SETTINGS_EXPORTER['i3D_exportMergeGroups'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2, 'uiControl': UI_CONTROL_SHAPES_2}
SETTINGS_EXPORTER['i3D_exportVerbose'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_MISC_1}
SETTINGS_EXPORTER['i3D_exportRelativePaths'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 2, 'uiControl': UI_CONTROL_MISC_1}
SETTINGS_EXPORTER['i3D_exportFloatEpsilon'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 3, 'uiControl': UI_CONTROL_MISC_1}
SETTINGS_EXPORTER['i3D_exportUpdateXML'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1, 'uiControl': UI_CONTROL_MISC_2}
SETTINGS_EXPORTER['i3D_exportUseMayaFilename'] = {'type': TYPE_BOOL, 'checkBoxGrpId': 1,
                                                  'uiControl': UI_CONTROL_BOOL_USE_MAYA_FILENAME}
SETTINGS_EXPORTER['i3D_exportOutputFile'] = {'type': TYPE_STRING, 'uiControl': UI_CONTROL_STRING_FILE_PATH}
SETTINGS_EXPORTER['i3D_exportXMLConfigFile'] = {'type': TYPE_STRING, 'uiControl': UI_CONTROL_STRING_XML_FILE_PATH}
SETTINGS_EXPORTER['i3D_exportXMLConfigFileTag'] = {'type': TYPE_STRING, 'uiControl': UI_CONTROL_STRING_XML_TAG}

SETTINGS_FRAMES = {}
SETTINGS_FRAMES['giants_frameOptions'] = {'uiControl': UI_CONTROL_FRAME_OPTIONS}
SETTINGS_FRAMES['giants_frameShapeSubparts'] = {'uiControl': UI_CONTROL_FRAME_SHAPE_SUBPARTS}
SETTINGS_FRAMES['giants_frameMisc'] = {'uiControl': UI_CONTROL_FRAME_MISC}
SETTINGS_FRAMES['giants_frameXmlFile'] = {'uiControl': UI_CONTROL_FRAME_XML_FILE}
SETTINGS_FRAMES['giants_frameOutputFile'] = {'uiControl': UI_CONTROL_FRAME_OUTPUT_FILE}
SETTINGS_FRAMES['giants_frameExport'] = {'uiControl': UI_CONTROL_FRAME_EXPORT}
SETTINGS_FRAMES['giants_frameErrors'] = {'uiControl': UI_CONTROL_FRAME_ERRORS}
SETTINGS_FRAMES['giants_frameRigidBody'] = {'uiControl': UI_CONTROL_FRAME_RIGID_BODY}
SETTINGS_FRAMES['giants_frameJoint'] = {'uiControl': UI_CONTROL_FRAME_JOINT}
SETTINGS_FRAMES['giants_frameRendering'] = {'uiControl': UI_CONTROL_FRAME_RENDERING}
SETTINGS_FRAMES['giants_framePivot'] = {'uiControl': UI_CONTROL_FRAME_PIVOT}
SETTINGS_FRAMES['giants_frameFreeze'] = {'uiControl': UI_CONTROL_FRAME_FREEZE}
SETTINGS_FRAMES['giants_frameMesh'] = {'uiControl': UI_CONTROL_FRAME_MESH}
SETTINGS_FRAMES['giants_frameMaterial'] = {'uiControl': UI_CONTROL_FRAME_MATERIAL}
SETTINGS_FRAMES['giants_frameUVs'] = {'uiControl': UI_CONTROL_FRAME_UVS}
SETTINGS_FRAMES['giants_frameSkeleton'] = {'uiControl': UI_CONTROL_FRAME_SKELETON}
SETTINGS_FRAMES['giants_frameUI'] = {'uiControl': UI_CONTROL_FRAME_UI}

SETTINGS_SHADERS = []
SETTINGS_SHADER_PARAMETERS = {}
SETTINGS_SHADER_TEXTURES = {}
SETTINGS_SHADER_VARIATIONS = {}


def I3DExportToFile(filename, ik, animation, shapes, nurbscurves, lights, cameras, userattributes, defaultcameras,
                    particlesystems, exportBinaryFiles, ignoreBindPoses, normals, colors, texCoords, skinWeights,
                    mergeGroups, verbose, exportSelection, relativePaths, template, floatEpsilon):
    cmds.waitCursor(state=True)

    try:
        fwrite = open(filename, 'w')
        fwrite.close()
    except IOError:
        cmds.waitCursor(state=False)
        I3DAddError('Could not open file: ' + filename)
        return 1

    command = 'I3DExporter '

    if (verbose):
        command = command + '-v '
    if (floatEpsilon):
        command = command + '-fe '
    if (shapes):
        command = command + '-shapes '
    if (normals):
        command = command + '-n '
    if (colors):
        command = command + '-c '
    if (texCoords):
        command = command + '-uvs '
    if (skinWeights):
        command = command + '-sw '
    if (mergeGroups):
        command = command + '-mg '
    if (nurbscurves):
        command = command + '-nurbscurves '
    if (relativePaths):
        command = command + '-rp '
    if (ik):
        command = command + '-ik '
    if (lights):
        command = command + '-lights '
    if (userattributes):
        command = command + '-userattributes '
    if (cameras):
        command = command + '-cameras '
        if (defaultcameras):
            command = command + '-dcams '
    if (particlesystems):
        command = command + '-particlesystems '
    if (exportBinaryFiles):
        command = command + '-binaryfiles '
    if (ignoreBindPoses):
        command = command + '-ignoreBindPoses '
    if (animation):
        command = command + '-animation '
    if (exportSelection):
        command = command + '-selection '

    filename = filename.replace('\\', '$')
    filename = filename.replace('/', '$')

    command = command + '-file "'
    command = command + filename
    command = command + '"'

    mel.eval(command)

    cmds.waitCursor(state=False)

    return 0


def I3DLoadSettings(unused):
    if cmds.objExists(SETTINGS_PREFIX):
        # load export settings
        for k, v in SETTINGS_EXPORTER.iteritems():
            if v['type'] == TYPE_BOOL:
                if I3DAttributeExists(SETTINGS_PREFIX, k):
                    value = cmds.getAttr(SETTINGS_PREFIX + '.' + k)
                    if v['checkBoxGrpId'] == 1:
                        cmds.checkBoxGrp(v['uiControl'], edit=True, v1=value)
                    elif v['checkBoxGrpId'] == 2:
                        cmds.checkBoxGrp(v['uiControl'], edit=True, v2=value)
                    elif v['checkBoxGrpId'] == 3:
                        cmds.checkBoxGrp(v['uiControl'], edit=True, v3=value)

        # output file
        outputFileLocationPath = ''
        if I3DAttributeExists(SETTINGS_PREFIX, 'i3D_exportOutputFile'):
            outputFileLocationPath = cmds.getAttr(SETTINGS_PREFIX + '.i3D_exportOutputFile')
        if (outputFileLocationPath == 0 or outputFileLocationPath == ''):
            outputFileLocationPath = 'C:/myExport.i3d'
        cmds.textField(UI_CONTROL_STRING_FILE_PATH, edit=True, text=outputFileLocationPath)

        # xml config file
        xmlConfigFilePath = ''
        if I3DAttributeExists(SETTINGS_PREFIX, 'i3D_exportXMLConfigFile'):
            xmlConfigFilePath = cmds.getAttr(SETTINGS_PREFIX + '.i3D_exportXMLConfigFile')
        if (xmlConfigFilePath == 0 or xmlConfigFilePath == ''):
            xmlConfigFilePath = ''
        cmds.textField(UI_CONTROL_STRING_XML_FILE_PATH, edit=True, text=xmlConfigFilePath)

    # update all nodes
    dagObjects = cmds.ls(dag=True, l=True, tr=True)
    for node in dagObjects:
        I3DUpdateLayers(node)

    return


def I3DSaveSettings(unused):
    if cmds.objExists(SETTINGS_PREFIX):
        # delete old settings node
        cmds.delete(SETTINGS_PREFIX)
    # add new settings node
    cmds.createNode('script', name=SETTINGS_PREFIX)
    cmds.setAttr(SETTINGS_PREFIX + '.st', 2)
    # add export settings
    for k, v in SETTINGS_EXPORTER.iteritems():
        if v['type'] == TYPE_BOOL:
            cmds.addAttr(sn=k, ln=k, nn=k, at='bool')
            if v['checkBoxGrpId'] == 1:
                cmds.setAttr(SETTINGS_PREFIX + '.' + k, cmds.checkBoxGrp(v['uiControl'], q=True, v1=True))
            elif v['checkBoxGrpId'] == 2:
                cmds.setAttr(SETTINGS_PREFIX + '.' + k, cmds.checkBoxGrp(v['uiControl'], q=True, v2=True))
            elif v['checkBoxGrpId'] == 3:
                cmds.setAttr(SETTINGS_PREFIX + '.' + k, cmds.checkBoxGrp(v['uiControl'], q=True, v3=True))
        elif v['type'] == TYPE_STRING:
            cmds.addAttr(sn=k, ln=k, nn=k, dt='string')
            cmds.setAttr(SETTINGS_PREFIX + '.' + k, cmds.textField(v['uiControl'], q=True, text=True), type='string')

    # add loading script
    cmds.setAttr(SETTINGS_PREFIX + '.b', I3DGetLoadScript(), type='string')

    return


def I3DSetShaderPath(folderPath):
    cmds.textField(UI_CONTROL_STRING_SHADER_PATH, edit=True, text=folderPath)
    if folderPath != '' and os.path.exists(folderPath):
        PROJECT_PATH = folderPath
        I3DUpdateShaderList(folderPath)
        cmds.optionVar(stringValue=('GIANTS_SHADER_DIR', folderPath))

    return


def I3DGetLoadScript():
    script = 'if(`window -ex "i3DExport"`)\n{\n\tif(objExists("I3DExportSettings"))\n\t{\n\t\tint $tmpInt;\n\t\tstring $tmpStr;\n\t\t'
    for k, v in SETTINGS_EXPORTER.iteritems():
        if v['type'] == TYPE_BOOL:
            script = script + '\n\t\tif (!catchQuiet( $tmpInt = `getAttr "' + SETTINGS_PREFIX + '.' + k + '"`))\n\t\t\tcheckBoxGrp -e -v' + str(
                v['checkBoxGrpId']) + ' $tmpInt "' + v['uiControl'] + '";'
        elif v['type'] == TYPE_STRING:
            script = script + '\n\t\tif (!catchQuiet( $tmpStr = `getAttr "' + SETTINGS_PREFIX + '.' + k + '"`))\n\t\t\ttextField -e -text $tmpStr "' + \
                     v['uiControl'] + '";'

    script = script + '\n\t}\n}'

    print(script)
    return script


def I3DOnSelectionChanged():
    if cmds.window(UI_CONTROL_WINDOW, exists=True):
        obj = cmds.ls(sl=True, long=True)
        if not obj is None and len(obj) > 0:
            index = I3DUtils.getIndexPath(obj[0])
            cmds.textField(UI_CONTROL_STRING_NODE_INDEX, edit=True, text=index)
            cmds.textField(UI_CONTROL_STRING_NODE_NAME, edit=True, text=obj[0])
            cmds.textField(UI_CONTROL_STRING_IDENTIFIER, edit=True,
                           text=I3DGetAttributeValue(obj[0], 'i3D_xmlIdentifier', ''))
        return


def I3DCloseExporter():
    I3DRemoveSelectionChangedListener()
    cmds.optionVar(intValue=('GIANTS_EXPORTER_WIDTH', cmds.window(UI_CONTROL_WINDOW, q=True, width=True)))
    cmds.optionVar(intValue=('GIANTS_EXPORTER_HEIGHT', cmds.window(UI_CONTROL_WINDOW, q=True, height=True)))
    cmds.deleteUI(UI_CONTROL_WINDOW, window=True)


def I3DExport():
    # if hasattr(cmds, 'dockControl'):
    # if cmds.dockControl(UI_CONTROL_DOCK, exists=True):
    # cmds.optionVar( intValue=('GIANTS_EXPORTER_WIDTH', cmds.window(UI_CONTROL_WINDOW, q=True, width=True)))
    # cmds.optionVar( intValue=('GIANTS_EXPORTER_HEIGHT', cmds.window(UI_CONTROL_WINDOW, q=True, height=True)))
    # cmds.deleteUI(UI_CONTROL_DOCK)

    if cmds.window(UI_CONTROL_WINDOW, exists=True):
        I3DCloseExporter()

    mainWindow = cmds.window(UI_CONTROL_WINDOW, title=TITLE, maximizeButton=False, menuBar=True)
    # MAIN MENU
    editMenu = cmds.menu(parent=mainWindow, label='Edit')
    cmds.menuItem(parent=editMenu, label='Load Options', command=I3DLoadSettings)
    cmds.menuItem(parent=editMenu, label='Save Options', command=I3DSaveSettings)
    cmds.menuItem(parent=editMenu, divider=True)
    cmds.menuItem(parent=editMenu, label='Quit', command=I3DCloseExporter)
    helpMenu = cmds.menu(parent=mainWindow, label='Help', helpMenu=True)
    cmds.menuItem(parent=helpMenu, label='GDN Homepage...', image='help.png',
                  command=('cmds.showHelp(\'http://gdn.giants-software.com/index.php\', absolute=True )'))

    form = cmds.formLayout(parent=mainWindow)
    curSelectionFrame = cmds.frameLayout(parent=form, label='Current selection', cll=False, mh=5, mw=5)
    curSelectionLayout = cmds.rowLayout('curSelectionLayout', parent=curSelectionFrame, adjustableColumn=3,
                                        numberOfColumns=3)
    cmds.text(parent=curSelectionLayout, label='Node', width=60, align='left', annotation='')
    cmds.textField(UI_CONTROL_STRING_NODE_INDEX, parent=curSelectionLayout, text='', editable=True, width=145,
                   enterCommand=I3DSelectIndex)
    cmds.textField(UI_CONTROL_STRING_NODE_NAME, parent=curSelectionLayout, text='', editable=False)

    # xml identifier
    xmlIdItems = cmds.rowLayout(UI_CONTROL_FRAME_XML_IDENTIFIER, parent=form, adjustableColumn=4, numberOfColumns=4)
    cmds.text(parent=xmlIdItems, label='Identifier', width=60, align='left', annotation='')
    cmds.textField(UI_CONTROL_STRING_IDENTIFIER, parent=xmlIdItems, text='',
                   annotation='XMl-Config identifier. Valid characters [A-Z0-9_]', editable=True, width=145)
    cmds.button(parent=xmlIdItems, label='Set', height=17, width=110, command=I3DSetIdentifier)
    cmds.button(parent=xmlIdItems, label='Remove', height=17, command=I3DRemoveIdentifier)

    tabs = cmds.tabLayout(parent=form, innerMarginWidth=5, innerMarginHeight=5, height=700)
    cmds.formLayout(form, edit=True, attachForm=(
        (curSelectionFrame, 'top', 5), (curSelectionFrame, 'left', 5), (curSelectionFrame, 'right', 5),
        (xmlIdItems, 'top', 55), (xmlIdItems, 'left', 10), (xmlIdItems, 'right', 10),
        (tabs, 'top', 90), (tabs, 'left', 5), (tabs, 'right', 5), (tabs, 'bottom', 5)))

    # TAB EXPORT
    tabExport = cmds.formLayout()
    exportColums = cmds.columnLayout(parent=tabExport, adjustableColumn=True)

    # export options
    exportOptionsFrame = cmds.frameLayout(UI_CONTROL_FRAME_OPTIONS, parent=exportColums, label='Options', w=390,
                                          cll=True, mh=2, mw=2, expandCommand=I3DSaveFrameState,
                                          collapseCommand=I3DSaveFrameState)
    exportOptionsItems = cmds.columnLayout(parent=exportOptionsFrame)
    cmds.checkBoxGrp(UI_CONTROL_EXPORT_1, parent=exportOptionsItems, height=28, numberOfCheckBoxes=3, v1=False, v2=True,
                     v3=True, labelArray3=['IK', 'Animation', 'Shapes'], cc=I3DSaveSettings)
    cmds.checkBoxGrp(UI_CONTROL_EXPORT_2, parent=exportOptionsItems, height=28, numberOfCheckBoxes=3, v1=False, v2=True,
                     v3=True, labelArray3=['Nurbs Curves', 'Lights', 'Cameras'], cc=I3DSaveSettings)
    cmds.checkBoxGrp(UI_CONTROL_EXPORT_3, parent=exportOptionsItems, height=28, numberOfCheckBoxes=3, v1=False,
                     v2=False, v3=True, labelArray3=['Particle System', 'Default Cameras', 'User Attributes'],
                     cc=I3DSaveSettings)
    cmds.checkBoxGrp(UI_CONTROL_EXPORT_4, parent=exportOptionsItems, height=28, numberOfCheckBoxes=2, v1=True, v2=False,
                     labelArray2=['Binary Files', 'Ignore Bind Poses'], cc=I3DSaveSettings)

    # shape export subparts
    exportSubpartsFrame = cmds.frameLayout(UI_CONTROL_FRAME_SHAPE_SUBPARTS, parent=exportColums, label='Shape Subparts',
                                           cll=True, mh=2, mw=2, expandCommand=I3DSaveFrameState,
                                           collapseCommand=I3DSaveFrameState)
    exportSubpartsItems = cmds.columnLayout(parent=exportSubpartsFrame)
    cmds.checkBoxGrp(UI_CONTROL_SHAPES_1, parent=exportSubpartsItems, height=28, numberOfCheckBoxes=3, v1=True, v2=True,
                     v3=True, labelArray3=['Normals', 'Vertex Colors', 'UVs'], cc=I3DSaveSettings)
    cmds.checkBoxGrp(UI_CONTROL_SHAPES_2, parent=exportSubpartsItems, height=28, numberOfCheckBoxes=2, v1=True, v2=True,
                     labelArray2=['Skin Weights', 'Merge Groups'], cc=I3DSaveSettings)

    # miscellaneous
    exportMiscFrame = cmds.frameLayout(UI_CONTROL_FRAME_MISC, parent=exportColums, label='Miscellaneous', cll=True,
                                       mh=2, mw=2, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    exportMiscItems = cmds.columnLayout(parent=exportMiscFrame)
    cmds.checkBoxGrp(UI_CONTROL_MISC_1, parent=exportMiscItems, height=28, numberOfCheckBoxes=3, v1=True, v2=True,
                     v3=True, labelArray3=['Verbose', 'Relative Paths', 'Float Epsilon'], cc=I3DSaveSettings)

    # xml config file
    xmlFileFrame = cmds.frameLayout(UI_CONTROL_FRAME_XML_FILE, parent=exportColums, label='XML Config File(s)', w=390,
                                    cll=True, mh=3, mw=3, expandCommand=I3DSaveFrameState,
                                    collapseCommand=I3DSaveFrameState)
    fileItems = cmds.columnLayout('xmlFileColumnItem', parent=xmlFileFrame, adjustableColumn=True)
    cmds.checkBoxGrp(UI_CONTROL_MISC_2, parent=fileItems, height=28, numberOfCheckBoxes=1, v1=True,
                     label1='Update XML on Export', cc=I3DSaveSettings)

    xmlFileTags = cmds.formLayout('xmlFileTags', parent=fileItems)
    textXmlTag = cmds.text('textXmlTag', parent=xmlFileTags, label='XML root tag')
    textFieldXmlTag = cmds.textField(UI_CONTROL_STRING_XML_TAG, parent=xmlFileTags, text='vehicle', width=150,
                                     editable=True)

    cmds.formLayout(xmlFileTags, edit=True, attachForm=((textXmlTag, 'top', 4), (textXmlTag, 'left', 2),
                                                        (textFieldXmlTag, 'top', 0),
                                                        (textFieldXmlTag, 'left', 80),
                                                        (textFieldXmlTag, 'right', 35)))

    xmlFileItems = cmds.formLayout('xmlFileItems', parent=fileItems)
    textXmlFolder = cmds.text('textXmlFolder', parent=xmlFileItems, label='XML location')
    textFieldXmlFolder = cmds.textField(UI_CONTROL_STRING_XML_FILE_PATH, parent=xmlFileItems, width=250, editable=False)
    buttonSelectXml = cmds.symbolButton('buttonSelectXml', parent=xmlFileItems, image='navButtonBrowse.xpm',
                                        command=I3DOpenXmlConfigDialog, annotation='Set Vehicle XML-Config file')

    cmds.formLayout(xmlFileItems, edit=True, attachForm=((textXmlFolder, 'top', 4), (textXmlFolder, 'left', 2),
                                                         (textFieldXmlFolder, 'top', 0),
                                                         (textFieldXmlFolder, 'left', 80),
                                                         (textFieldXmlFolder, 'right', 35),
                                                         (buttonSelectXml, 'top', 0), (buttonSelectXml, 'right', 5)))
    # output file
    fileFrame = cmds.frameLayout(UI_CONTROL_FRAME_OUTPUT_FILE, parent=exportColums, label='Output File', w=390,
                                 cll=True, mh=2, mw=2, expandCommand=I3DSaveFrameState,
                                 collapseCommand=I3DSaveFrameState)
    fileItems = cmds.columnLayout('fileItems', parent=fileFrame, adjustableColumn=True)

    cmds.checkBoxGrp(UI_CONTROL_BOOL_USE_MAYA_FILENAME, parent=fileItems, height=28, numberOfCheckBoxes=1, v1=False,
                     label1='Use maya filename', cc=I3DSaveSettings)

    fileLayout = cmds.formLayout('fileLayout', parent=fileItems)
    textI3dFile = cmds.text('textI3dFile', parent=fileLayout, label='File Location')
    textFieldI3dFile = cmds.textField(UI_CONTROL_STRING_FILE_PATH, parent=fileLayout, width=250, editable=False)
    buttonSelectI3dFile = cmds.symbolButton('buttonSelectI3dFile', parent=fileLayout, image='navButtonBrowse.xpm',
                                            command=I3DOpenExportDialog, annotation='Set Export file')

    cmds.formLayout(fileLayout, edit=True, attachForm=((textI3dFile, 'top', 4), (textI3dFile, 'left', 2),
                                                       (textFieldI3dFile, 'top', 0), (textFieldI3dFile, 'left', 80),
                                                       (textFieldI3dFile, 'right', 35),
                                                       (buttonSelectI3dFile, 'top', 0),
                                                       (buttonSelectI3dFile, 'right', 5),
                                                       (buttonSelectI3dFile, 'bottom', 5)))

    # buttons
    buttonFrame = cmds.frameLayout(UI_CONTROL_FRAME_EXPORT, parent=exportColums, label='Export', cll=True, mh=2, mw=2,
                                   expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    buttonColumns = cmds.columnLayout('buttonColumns', parent=buttonFrame, adjustableColumn=True, rowSpacing=5)
    buttonItems1 = cmds.formLayout('buttonItems1', parent=buttonColumns)
    buttonCheck = cmds.button(parent=buttonItems1, label='Check for Errors', height=30, command=I3DErrorCheck)
    buttonUpdate = cmds.button(parent=buttonItems1, label='Update XML', height=30, command=I3DUpdateXML)
    cmds.formLayout(buttonItems1, edit=True,
                    attachPosition=((buttonCheck, 'left', 0, 0), (buttonCheck, 'right', 5, 50),
                                    (buttonUpdate, 'left', 0, 50), (buttonUpdate, 'right', 0, 100)))

    buttonItems2 = cmds.formLayout('buttonItems2', parent=buttonColumns)
    buttonExport = cmds.button(parent=buttonItems2, label='Export Selected', height=30, command=I3DExportSelected)
    buttonExportAll = cmds.button(parent=buttonItems2, label='Export All', height=30, command=I3DExportAll)
    cmds.formLayout(buttonItems2, edit=True,
                    attachPosition=((buttonExport, 'left', 0, 0), (buttonExport, 'right', 5, 50),
                                    (buttonExportAll, 'left', 0, 50), (buttonExportAll, 'right', 0, 100)))

    # errors
    errorFrame = cmds.frameLayout(UI_CONTROL_FRAME_ERRORS, parent=exportColums, label='Validation & Errors', cll=True,
                                  mh=0, mw=2, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    errorField = cmds.scrollField(UI_CONTROL_STRING_VALIDATION, parent=tabExport, wordWrap=False, editable=True)

    cmds.formLayout(tabExport, edit=True, attachForm=(
        (exportColums, 'top', 1), (exportColums, 'left', 1), (exportColums, 'right', 1), (errorField, 'left', 2),
        (errorField, 'right', 2), (errorField, 'bottom', 2)), attachControl=((errorField, 'top', 0, exportColums)))

    # TAB ATTRIBUTES
    tabAttributes = cmds.formLayout('TabAttributes', parent=tabs)

    # selected node
    loadedNodeFrame = cmds.frameLayout('loadedNodeFrame', parent=tabAttributes, label='Loaded Node', w=390, cll=False,
                                       mh=2, mw=2)
    loadedNodeItems = cmds.rowLayout('loadedNodeItems', parent=loadedNodeFrame, adjustableColumn=2, numberOfColumns=2)
    cmds.text(parent=loadedNodeItems, label='Node Name', width=TEXT_WIDTH, align='left')
    cmds.textField(UI_CONTROL_STRING_LOADED_NODE_NAME, parent=loadedNodeItems, editable=False, width=245)

    # predefined
    predefinedFrame = cmds.frameLayout(parent=tabAttributes, label='Predefined', w=390, cll=False, mh=2, mw=2)
    predefinedItems = cmds.rowColumnLayout(parent=predefinedFrame, numberOfRows=1)
    vehicleAttributes = cmds.optionMenu(UI_OPTIONS_PREDEFINED_VEHICLES_ATTRIBUTES, parent=predefinedItems,
                                        annotation='Vehicle physics', changeCommand=I3DSetAttributePreset)
    for attribute in SETTINGS_VEHICLE_ATTRIBUTES:
        if attribute['isPhyiscObject']:
            cmds.menuItem(parent=vehicleAttributes, label=attribute['name'])
    meshAttributes = cmds.optionMenu(UI_OPTIONS_PREDEFINED_MESH_ATTRIBUTES, parent=predefinedItems,
                                     annotation='Mesh attributes', changeCommand=I3DSetAttributePreset)
    for attribute in SETTINGS_VEHICLE_ATTRIBUTES:
        if not attribute['isPhyiscObject']:
            cmds.menuItem(parent=meshAttributes, label=attribute['name'])

    # attributes
    attributesFrame = cmds.frameLayout(parent=tabAttributes, label='Attributes', w=390, cll=False, mh=2, mw=2)
    scrollAttributes = cmds.scrollLayout('scrollAttributes', parent=attributesFrame, cr=True,
                                         verticalScrollBarAlwaysVisible=False)

    # rigid body
    rigidBodyFrame = cmds.frameLayout(UI_CONTROL_FRAME_RIGID_BODY, parent=scrollAttributes, label='Rigid Body',
                                      cll=True, mh=2, mw=2, expandCommand=I3DSaveFrameState,
                                      collapseCommand=I3DSaveFrameState)
    rigidBodyItems = cmds.columnLayout('rigidBodyItems', parent=rigidBodyFrame)
    I3DAddCheckBoxElement(rigidBodyItems, 'Static', UI_CONTROL_BOOL_STATIC, False, 'passive Rigid Body non movable')
    I3DAddCheckBoxElement(rigidBodyItems, 'Kinematic', UI_CONTROL_BOOL_KINEMATIC, False, 'passive Rigid Body moveable')
    I3DAddCheckBoxElement(rigidBodyItems, 'Dynamic', UI_CONTROL_BOOL_DYNAMIC, False, 'active Rigid Body simulated')
    I3DAddCheckBoxElement(rigidBodyItems, 'Compound', UI_CONTROL_BOOL_COMPOUND, False, 'group of Rigid Bodies')
    I3DAddCheckBoxElement(rigidBodyItems, 'Compound child', UI_CONTROL_BOOL_COMPOUND_CHILD, False,
                          'part of a group of Rigid Bodies')
    I3DAddCheckBoxElement(rigidBodyItems, 'Collision', UI_CONTROL_BOOL_COLLISION)
    I3DAddIntFieldElement(rigidBodyItems, 'Collision Mask', UI_CONTROL_INT_COLLISION_MASK, 255, '',
                          width=MASK_FIELD_WIDTH)
    I3DAddRestitution(rigidBodyItems)
    I3DAddFloatFieldElement(rigidBodyItems, 'Static Friction', UI_CONTROL_FLOAT_STATIC_FRICTION, 0.5,
                            'The force that resists motion between two non-moving surfaces')
    I3DAddFloatFieldElement(rigidBodyItems, 'Dynamic Friction', UI_CONTROL_FLOAT_DYNAMIC_FRICTION, 0.5,
                            'The force that resists motion between two moving surfaces')
    I3DAddFloatFieldElement(rigidBodyItems, 'Linear Damping', UI_CONTROL_FLOAT_LINEAR_DAMPING, 0.0,
                            'Defines the slowdown factor for linear movement, affecting speed')
    I3DAddFloatFieldElement(rigidBodyItems, 'Angular Damping', UI_CONTROL_FLOAT_ANGULAR_DAMPING, 0.01,
                            'Defines the slowdown factor for angular movement, affecting spin')
    I3DAddMass(rigidBodyItems)
    I3DAddIntFieldElement(rigidBodyItems, 'Solver Iterations', UI_CONTROL_INT_SOLVER_ITERATIONS, 4, '')
    I3DAddCheckBoxElement(rigidBodyItems, 'CCD', UI_CONTROL_BOOL_CCD)
    I3DAddCheckBoxElement(rigidBodyItems, 'Trigger', UI_CONTROL_BOOL_TRIGGER)
    I3DAddIntFieldElement(rigidBodyItems, 'Split Type', UI_CONTROL_INT_SPLITTYPE, 0, '')
    I3DAddFloatFieldElements(rigidBodyItems, 'Split Uvs',
                             [UI_CONTROL_FLOAT_SPLIT_MIN_U, UI_CONTROL_FLOAT_SPLIT_MIN_V, UI_CONTROL_FLOAT_SPLIT_MAX_U,
                              UI_CONTROL_FLOAT_SPLIT_MAX_V, UI_CONTROL_FLOAT_SPLIT_UV_WORLD_SCALE], [0, 0, 1, 1, 1],
                             ['', 'Min U', 'Min V', 'Max U', 'Max V', 'Uv World Scale'])

    # joint
    jointFrame = cmds.frameLayout(UI_CONTROL_FRAME_JOINT, parent=scrollAttributes, label='Joint', cll=1, mh=2, mw=2,
                                  cl=True, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    jointItems = cmds.columnLayout('jointItems', parent=jointFrame)
    I3DAddCheckBoxElement(jointItems, 'Joint', UI_CONTROL_BOOL_JOINT)
    I3DAddCheckBoxElement(jointItems, 'Projection', UI_CONTROL_BOOL_PROJECTION)
    I3DAddFloatFieldElement(jointItems, 'Projection distance', UI_CONTROL_FLOAT_PROJECTION_DISTANCE, 0, '')
    I3DAddFloatFieldElement(jointItems, 'Projection angle', UI_CONTROL_FLOAT_PROJECTION_ANGLE, 0, '')
    I3DAddCheckBoxElement(jointItems, 'X-Axis Drive', UI_CONTROL_BOOL_XAXIS_DRIVE)
    I3DAddCheckBoxElement(jointItems, 'Y-Axis Drive', UI_CONTROL_BOOL_YAXIS_DRIVE)
    I3DAddCheckBoxElement(jointItems, 'Z-Axis Drive', UI_CONTROL_BOOL_ZAXIS_DRIVE)
    I3DAddCheckBoxElement(jointItems, 'Drive Position', UI_CONTROL_BOOL_DRIVE_POSITION)
    I3DAddFloatFieldElement(jointItems, 'Drive Force Limit', UI_CONTROL_FLOAT_DRIVE_FORCE_LIMIT, 0, '')
    I3DAddFloatFieldElement(jointItems, 'Drive Spring', UI_CONTROL_FLOAT_DRIVE_SPRING, 0, '')
    I3DAddFloatFieldElement(jointItems, 'Drive Damping', UI_CONTROL_FLOAT_DRIVE_DAMPING, 0, '')
    I3DAddCheckBoxElement(jointItems, 'Breakable', UI_CONTROL_BOOL_BREAKABLE)
    I3DAddFloatFieldElement(jointItems, 'Break Force', UI_CONTROL_FLOAT_BREAK_FORCE, 0, '')
    I3DAddFloatFieldElement(jointItems, 'Break Torque', UI_CONTROL_FLOAT_BREAK_TORQUE, 0, '')

    # rendering
    renderingFrame = cmds.frameLayout(UI_CONTROL_FRAME_RENDERING, parent=scrollAttributes, label='Rendering', cll=True,
                                      mh=2, mw=2, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    renderingItems = cmds.columnLayout('renderingItems', parent=renderingFrame)
    I3DAddCheckBoxElement(renderingItems, 'Occlusion Culling', UI_CONTROL_BOOL_OCCLUSION_CULLING)
    I3DAddCheckBoxElement(renderingItems, 'Non Renderable', UI_CONTROL_BOOL_NON_RENDERABLE)
    I3DAddFloatFieldElement(renderingItems, 'Clip Distance', UI_CONTROL_FLOAT_CLIP_DISTANCE, 0, '')
    I3DAddIntFieldElement(renderingItems, 'Object Mask', UI_CONTROL_INT_OBJECT_MASK, 255, '', width=MASK_FIELD_WIDTH)
    I3DAddTextFieldElement(renderingItems, 'Light Mask (Hex)', UI_CONTROL_STRING_LIGHT_MASK, 'FFFF', '')
    I3DAddIntFieldElement(renderingItems, 'Decal Layer', UI_CONTROL_INT_DECAL_LAYER, 0, '')
    I3DAddMergeGroup(renderingItems)
    I3DAddBoundVolume(renderingItems)
    I3DAddCheckBoxElement(renderingItems, 'CPU Mesh', UI_CONTROL_BOOL_CPUMESH)
    I3DAddCheckBoxElement(renderingItems, 'LOD', UI_CONTROL_BOOL_LOD)
    I3DAddFloatFieldElement(renderingItems, 'Child 0 Distance', UI_CONTROL_FLOAT_CHILD_0_DISTANCE, 0, '', False)
    I3DAddFloatFieldElement(renderingItems, 'Child 1 Distance', UI_CONTROL_FLOAT_CHILD_1_DISTANCE, 0, '')
    I3DAddFloatFieldElement(renderingItems, 'Child 2 Distance', UI_CONTROL_FLOAT_CHILD_2_DISTANCE, 0, '')
    I3DAddFloatFieldElement(renderingItems, 'Child 3 Distance', UI_CONTROL_FLOAT_CHILD_3_DISTANCE, 0, '')
    I3DAddCheckBoxElement(renderingItems, 'Scaled', UI_CONTROL_BOOL_SCALED)

    # buttons
    attributeButtonItems = cmds.formLayout('ToolButtons', parent=tabAttributes)
    buttonLoad = cmds.button(parent=attributeButtonItems, label='Load', height=30, width=126,
                             command=I3DLoadObjectAttributes)
    buttonApply = cmds.button(parent=attributeButtonItems, label='Apply', height=30, width=126,
                              command=I3DApplySelectedAttributes)
    buttonRemove = cmds.button(parent=attributeButtonItems, label='Remove', height=30, width=126,
                               command=I3DRemoveObjectAttributes)
    cmds.formLayout(attributeButtonItems, edit=True,
                    attachPosition=((buttonLoad, 'left', 0, 0), (buttonLoad, 'right', 5, 33),
                                    (buttonApply, 'left', 0, 33), (buttonApply, 'right', 5, 66),
                                    (buttonRemove, 'left', 0, 66), (buttonRemove, 'right', 0, 100)))

    cmds.formLayout(tabAttributes, edit=True, attachForm=(
        (loadedNodeFrame, 'top', 2), (loadedNodeFrame, 'left', 2), (loadedNodeFrame, 'right', 2),
        (predefinedFrame, 'top', 48), (predefinedFrame, 'left', 2), (predefinedFrame, 'right', 2),
        (attributesFrame, 'top', 95), (attributesFrame, 'left', 2), (attributesFrame, 'right', 2),
        (attributesFrame, 'bottom', 32),
        (attributeButtonItems, 'left', 2), (attributeButtonItems, 'right', 2), (attributeButtonItems, 'bottom', 2)))

    # TAB TOOLS
    tabTools = cmds.formLayout('TabTools', parent=tabs)
    scrollTools = cmds.scrollLayout('scrollTools', parent=tabTools, cr=True, verticalScrollBarAlwaysVisible=False)
    scrollToolsLayout = cmds.columnLayout('scrollToolsLayout', parent=scrollTools, adjustableColumn=True,
                                          columnOffset=('right', 1))

    # pivot tools
    pivotFrame = cmds.frameLayout(UI_CONTROL_FRAME_PIVOT, parent=scrollToolsLayout, label='Pivot-Tools', cll=True, mh=2,
                                  mw=2, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    pivotColumns = cmds.columnLayout('pivotColumns', parent=pivotFrame, adjustableColumn=True, rowSpacing=5)
    pivotItems1 = cmds.formLayout('pivotItems1', parent=pivotColumns)
    buttonFreeze = cmds.button(parent=pivotItems1, label='FreezeToPivot', height=30, command=I3DFreezeToPivot)
    buttonEqual = cmds.button(parent=pivotItems1, label='EqualizeWorldPivots', height=30, command=I3DAdjustWorldPivot,
                              annotation='Adjusts the selected node pivots. Sets the pivot of the first node to the second node\'s pivot position')

    cmds.formLayout(pivotItems1, edit=True,
                    attachPosition=((buttonFreeze, 'left', 0, 0), (buttonFreeze, 'right', 5, 50),
                                    (buttonEqual, 'left', 0, 50), (buttonEqual, 'right', 0, 100)))

    pivotItems2 = cmds.formLayout('pivotItems2', parent=pivotColumns)
    buttonToPivot = cmds.button(parent=pivotItems2, label='ManipulatorToPivot', height=30,
                                command=I3DManipulatorToPivot,
                                annotation='Sets the pivot of the node to the manipulator position')
    buttonToGroup = cmds.button(parent=pivotItems2, label='ManipulatorToGroup', height=30,
                                command=I3DManipulatorToGroup,
                                annotation='Creates a transform group based on current selection')
    cmds.formLayout(pivotItems2, edit=True,
                    attachPosition=((buttonToPivot, 'left', 0, 0), (buttonToPivot, 'right', 5, 50),
                                    (buttonToGroup, 'left', 0, 50), (buttonToGroup, 'right', 0, 100)))

    # freeze transformation tools
    freezeFrame = cmds.frameLayout(UI_CONTROL_FRAME_FREEZE, parent=scrollToolsLayout, label='Freeze Transformation',
                                   cll=True, mh=2, mw=2, expandCommand=I3DSaveFrameState,
                                   collapseCommand=I3DSaveFrameState)
    freezeColumns = cmds.columnLayout('freezeColumns', parent=freezeFrame, adjustableColumn=True, rowSpacing=5)
    freezeItems1 = cmds.formLayout('freezeItems1', parent=freezeColumns)
    buttonFreezeTrans = cmds.button(parent=freezeItems1, label='Freeze Translation', height=30,
                                    command=I3DFreezeTranslation, annotation='Freezes translation')
    buttonFreezeRot = cmds.button(parent=freezeItems1, label='Freeze Rotation', height=30, command=I3DFreezeRotation,
                                  annotation='Freezes rotation')

    cmds.formLayout(freezeItems1, edit=True,
                    attachPosition=((buttonFreezeTrans, 'left', 0, 0), (buttonFreezeTrans, 'right', 5, 50),
                                    (buttonFreezeRot, 'left', 0, 50), (buttonFreezeRot, 'right', 0, 100)))

    freezeItems2 = cmds.formLayout('freezeItems2', parent=freezeColumns)
    buttonFreezeScale = cmds.button(parent=freezeItems2, label='Freeze Scale', height=30, command=I3DFreezeScale,
                                    annotation='Freezes scale')
    buttonFreezeAll = cmds.button(parent=freezeItems2, label='Freeze All', height=30, command=I3DFreezeAll,
                                  annotation='Freezes translation, rotation and scale')
    cmds.formLayout(freezeItems2, edit=True,
                    attachPosition=((buttonFreezeScale, 'left', 0, 0), (buttonFreezeScale, 'right', 5, 50),
                                    (buttonFreezeAll, 'left', 0, 50), (buttonFreezeAll, 'right', 0, 100)))

    # mesh tools
    meshFrame = cmds.frameLayout(UI_CONTROL_FRAME_MESH, parent=scrollToolsLayout, label='Mesh-Tools', cll=True, mh=2,
                                 mw=2, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    meshColumns = cmds.columnLayout('meshColumns', parent=meshFrame, adjustableColumn=True, rowSpacing=5)
    meshItems1 = cmds.formLayout('meshItems1', parent=meshColumns)
    buttonDetachFaces = cmds.button(parent=meshItems1, label='DetachFaces', height=30, command=I3DDetachFaces,
                                    annotation='Detached the selcted faces from the node')
    buttonSetMirrorAxis = cmds.button(parent=meshItems1, label='SetMirrorAxis', height=30, command=I3DSetupMirrorAxis,
                                      annotation='Sets axis of mirror')

    cmds.formLayout(meshItems1, edit=True,
                    attachPosition=((buttonDetachFaces, 'left', 0, 0), (buttonDetachFaces, 'right', 5, 50),
                                    (buttonSetMirrorAxis, 'left', 0, 50), (buttonSetMirrorAxis, 'right', 0, 100)))

    meshItems2 = cmds.formLayout('meshItems2', parent=meshColumns)
    buttonAlignZ = cmds.button(parent=meshItems2, label='AlignZAxis', height=30, command=I3DAlignZAxis,
                               annotation='Aligns the z-axis of the node against the selected second node')
    buttonAlignNegZ = cmds.button(parent=meshItems2, label='AlignNegativeZAxis', height=30,
                                  command=I3DAlignNegativeZAxis,
                                  annotation='Aligns the negative z-axis of the node against the selected second node')
    cmds.formLayout(meshItems2, edit=True,
                    attachPosition=((buttonAlignZ, 'left', 0, 0), (buttonAlignZ, 'right', 5, 50),
                                    (buttonAlignNegZ, 'left', 0, 50), (buttonAlignNegZ, 'right', 0, 100)))

    meshItems3 = cmds.formLayout('meshItems3', parent=meshColumns)
    buttonRemoveNS = cmds.button(parent=meshItems3, label='Remove Namespace', height=30, command=I3DRemoveNameSpace,
                                 annotation='Removes obsolte namespaces')
    buttonZAxisToMani = cmds.button(parent=meshItems3, label='ZAxisToManipulator', height=30,
                                    command=I3DAlignZAxisToManipulator,
                                    annotation='Aligns the z-axis of the node against the selected manipulator')
    cmds.formLayout(meshItems3, edit=True,
                    attachPosition=((buttonRemoveNS, 'left', 0, 0), (buttonRemoveNS, 'right', 5, 50),
                                    (buttonZAxisToMani, 'left', 0, 50), (buttonZAxisToMani, 'right', 0, 100)))

    # Material tools
    materialFrame = cmds.frameLayout(UI_CONTROL_FRAME_MATERIAL, parent=scrollToolsLayout, label='Material-Tools',
                                     cll=True, mh=2, mw=2, expandCommand=I3DSaveFrameState,
                                     collapseCommand=I3DSaveFrameState)
    materialColumns = cmds.columnLayout('materialColumns', parent=materialFrame, adjustableColumn=True, rowSpacing=5)
    materialItems1 = cmds.formLayout('materialItems1', parent=materialColumns)
    buttonRemoveDuplicateMaterials = cmds.button(parent=materialItems1, label='Remove Duplicate Materials', height=30,
                                                 command=I3DRemoveDuplicateMaterials,
                                                 annotation='Removes duplicate materials')
    buttonRemoveDuplicateTextures = cmds.button(parent=materialItems1, label='Remove Duplicate Textures', height=30,
                                                command=I3DRemoveDuplicateTextures,
                                                annotation='Removes duplicate textures')

    cmds.formLayout(materialItems1, edit=True,
                    attachPosition=(
                        (buttonRemoveDuplicateMaterials, 'left', 0, 0),
                        (buttonRemoveDuplicateMaterials, 'right', 5, 50),
                        (buttonRemoveDuplicateTextures, 'left', 0, 50),
                        (buttonRemoveDuplicateTextures, 'right', 0, 100)))

    materialItems2 = cmds.formLayout('meshItems2', parent=materialColumns)
    buttonMaterialRenamer = cmds.button(parent=materialItems2, label='Rename Materials', height=30,
                                        command=I3DMaterialRenamer,
                                        annotation='Renames materials based on GIANTS guidelines')
    buttonGetComponentShader = cmds.button(parent=materialItems2, label='Get Component Shader', height=30,
                                           command=I3DGetComponentShader, annotation='Gets the component shader')
    cmds.formLayout(materialItems2, edit=True,
                    attachPosition=((buttonMaterialRenamer, 'left', 0, 0), (buttonMaterialRenamer, 'right', 5, 50),
                                    (buttonGetComponentShader, 'left', 0, 50),
                                    (buttonGetComponentShader, 'right', 0, 100)))

    # uv tools
    uvFrame = cmds.frameLayout(UI_CONTROL_FRAME_UVS, parent=scrollToolsLayout, label='UV-Tools', cll=True, mh=2, mw=2,
                               expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    uvColumns = cmds.columnLayout('uvColumns', parent=uvFrame, adjustableColumn=True, rowSpacing=5)
    uvItems1 = cmds.formLayout('uvItems1', parent=uvColumns)
    textUVSet = cmds.textField(UI_CONTROL_STRING_UVSET_NAME, parent=uvItems1, height=30, editable=True)
    textUVClean = cmds.button(parent=uvItems1, label='Cleanup UVs', height=30, command=I3DCleanupUVSet,
                              annotation='Cleanup UVSets')

    cmds.formLayout(uvItems1, edit=True,
                    attachPosition=((textUVSet, 'left', 0, 0), (textUVSet, 'right', 5, 50),
                                    (textUVClean, 'left', 0, 50), (textUVClean, 'right', 0, 100)))

    # skeleton creation
    skeletonFrame = cmds.frameLayout(UI_CONTROL_FRAME_SKELETON, parent=scrollToolsLayout, label='Skeletons', cll=True,
                                     mh=2, mw=2, expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    skeletonItems = cmds.formLayout('skeletonItems', parent=skeletonFrame)
    menuSkeleton = cmds.optionMenu(UI_OPTIONS_SKELETONS, parent=skeletonItems, height=31, annotation='Skeletons')
    for attribute in SETTINGS_SKELETONS:
        cmds.menuItem(parent=menuSkeleton, label=attribute['name'])
    buttonCreate = cmds.button(parent=skeletonItems, label='Create', height=30, command=I3DCreateSkeleton,
                               annotation='Create skeleton')
    cmds.formLayout(skeletonItems, edit=True,
                    attachPosition=((menuSkeleton, 'left', 0, 0), (menuSkeleton, 'right', 5, 70),
                                    (buttonCreate, 'left', 0, 70), (buttonCreate, 'right', 0, 100)))

    # ui tools
    uiFrame = cmds.frameLayout(UI_CONTROL_FRAME_UI, parent=scrollToolsLayout, label='UV-Tools', cll=True, mh=2, mw=2,
                               expandCommand=I3DSaveFrameState, collapseCommand=I3DSaveFrameState)
    uiColumns = cmds.columnLayout('uiColumns', parent=uiFrame, adjustableColumn=True, rowSpacing=5)
    uiItems1 = cmds.formLayout('uiItems1', parent=uiColumns)
    buttonToggleVC = cmds.button(parent=uiItems1, label='Toggle ViewCube', height=30, command=I3DToggleViewCube,
                                 annotation='Turns the viewCube on/off')

    cmds.formLayout(uiItems1, edit=True,
                    attachPosition=((buttonToggleVC, 'left', 0, 0), (buttonToggleVC, 'right', 5, 50)))

    cmds.formLayout(tabTools, edit=True, attachForm=(
        (scrollTools, 'top', 0), (scrollTools, 'left', 0), (scrollTools, 'right', 0), (scrollTools, 'bottom', 0)))

    # TAB SHADER
    tabShader = cmds.formLayout('TabShader', parent=tabs)

    shaderFolderFrame = cmds.frameLayout('shaderFolderFrame', parent=tabShader, label='Shaders Folder', cll=False, mh=2,
                                         mw=2)
    shaderFolderItems = cmds.formLayout('shaderFolderItems', parent=shaderFolderFrame)
    textShaderFolder = cmds.text('textShaderFolder', parent=shaderFolderItems, label='Path')
    textFieldShaderFolder = cmds.textField(UI_CONTROL_STRING_SHADER_PATH, parent=shaderFolderItems, width=250,
                                           editable=False, cc=I3DSetShaderPath)
    buttonSelectShader = cmds.symbolButton('buttonSelectShader', parent=shaderFolderItems, image='navButtonBrowse.xpm',
                                           command=I3DOpenShaderDialog, annotation='Set shader path')
    cmds.formLayout(shaderFolderItems, edit=True,
                    attachForm=((textShaderFolder, 'top', 4), (textShaderFolder, 'left', 2),
                                (textFieldShaderFolder, 'top', 0), (textFieldShaderFolder, 'left', 45),
                                (textFieldShaderFolder, 'right', 35),
                                (buttonSelectShader, 'top', 0), (buttonSelectShader, 'right', 5)))

    shadersFrame = cmds.frameLayout('shadersFrame', parent=tabShader, label='Shaders', cll=False, mh=2, mw=2)
    menuShaders = cmds.optionMenu(UI_OPTIONS_PREDEFINED_SHADER_ATTRIBUTES, parent=shadersFrame, label='',
                                  changeCommand=I3DUpdateShaderUI)

    parameterFrame = cmds.frameLayout(UI_CONTROL_LAYOUT_PARAMETERS, parent=tabShader, label='Parameters', cll=False,
                                      mh=2, mw=2)
    parameterScroll = cmds.scrollLayout(UI_CONTROL_PARAMETERS_SCROLL, parent=parameterFrame, cr=True)
    cmds.columnLayout(UI_CONTROL_PARAMETERS, parent=parameterScroll, adjustableColumn=True)

    texturesFrame = cmds.frameLayout(UI_CONTROL_LAYOUT_TEXTURES, parent=tabShader, label='Textures', cll=False, mh=2,
                                     mw=2, visible=True)
    texturesScroll = cmds.scrollLayout(UI_CONTROL_TEXTURES_SCROLL, parent=texturesFrame, cr=True)
    cmds.columnLayout(UI_CONTROL_TEXTURES, parent=texturesScroll, adjustableColumn=True)

    variationsFrame = cmds.frameLayout(UI_CONTROL_LAYOUT_VARIATIONS, parent=tabShader, label='Variations', cll=False,
                                       mh=2, mw=2, visible=True)
    cmds.optionMenu(UI_CONTROL_MENU_VARIATIONS, parent=variationsFrame)

    buttonAdd = cmds.button(parent=tabShader, label='Add shader', height=30, command=I3DSetShader,
                            annotation='Adds the shader to the selected material')

    cmds.formLayout(tabShader, edit=True, attachForm=(
        (shaderFolderFrame, 'top', 2), (shaderFolderFrame, 'left', 2), (shaderFolderFrame, 'right', 2),
        (shadersFrame, 'top', 50), (shadersFrame, 'left', 2), (shadersFrame, 'right', 2),
        (parameterFrame, 'top', 100), (parameterFrame, 'left', 2), (parameterFrame, 'right', 2),
        (parameterFrame, 'bottom', 210),
        (texturesFrame, 'bottom', 108), (texturesFrame, 'left', 2), (texturesFrame, 'right', 2),
        (variationsFrame, 'bottom', 40), (variationsFrame, 'left', 2), (variationsFrame, 'right', 2),
        (buttonAdd, 'left', 2), (buttonAdd, 'right', 2), (buttonAdd, 'bottom', 2)))

    # TAB USER ATTRIBUTES
    cmds.tabLayout(tabs, edit=True, parent=form, cr=True, tabLabel=(
        (tabExport, 'Export'), (tabAttributes, 'Attributes'), (tabTools, 'Tools'), (tabShader, 'Shader')), width=WINDOW_WIDTH)

    # if hasattr(cmds, 'dockControl'):
    # width = cmds.optionVar( q='GIANTS_EXPORTER_WIDTH' )
    # height = cmds.optionVar( q='GIANTS_EXPORTER_HEIGHT' )
    # if width == 0:
    # width = 470
    # if height == 0:
    # height = 760
    # cmds.dockControl(UI_CONTROL_DOCK, label=TITLE, floating=True, area='right', content=UI_CONTROL_WINDOW, width=width, height=height, allowedArea=['left', 'right'])
    # else:
    cmds.showWindow(UI_CONTROL_WINDOW)

    I3DLoadSettings(None)
    I3DLoadFrameState()

    shaderDir = cmds.optionVar(q='GIANTS_SHADER_DIR')
    if (shaderDir):
        I3DSetShaderPath(str(shaderDir))

    I3DRemoveSelectionChangedListener()

    # add onSelectionChange listener
    jobNum = cmds.scriptJob(e=['SelectionChanged', I3DOnSelectionChanged], protected=False)

    return 0


def I3DRemoveSelectionChangedListener():
    # remove old onSelectionChange listener
    jobs = cmds.scriptJob(listJobs=True)
    for job in sorted(jobs):
        pos = job.find('I3DOnSelectionChanged')
        if pos != -1:
            id = int(job[:job.find(':')])
            cmds.scriptJob(kill=id, force=True)


def I3DLoadFrameState():
    global SETTINGS_FRAMES

    for k, v in SETTINGS_FRAMES.iteritems():
        collapsed = cmds.optionVar(q=k)
        if collapsed == 1:
            cmds.frameLayout(v['uiControl'], edit=True, collapse=True)
    return


def I3DSaveFrameState():
    global SETTINGS_FRAMES

    for k, v in SETTINGS_FRAMES.iteritems():
        collapsed = cmds.frameLayout(v['uiControl'], q=True, collapse=True)
        value = 0
        if collapsed:
            value = 1
        cmds.optionVar(intValue=(k, value))
    return


def I3DOpenExportDialog(unused):
    file = None
    if hasattr(cmds, 'fileDialog2'):
        files = cmds.fileDialog2(fileMode=0, fileFilter='GIANTS i3D File (*.i3d)', dialogStyle=2,
                                 caption='Choose Export File', okCaption='Set File')
        if not files is None:
            file = files[0]
    else:
        file = cmds.fileDialog(m=1, dm='*.i3d', title='Choose Export File')
        if not file is None:
            if not file.endswith('.i3d'):
                file = file + '.i3d'

    if not file is None:
        cmds.textField(UI_CONTROL_STRING_FILE_PATH, edit=True, text=file)
        I3DSaveSettings(None)


def I3DOpenXmlConfigDialog(unused):
    files = []
    if hasattr(cmds, 'fileDialog2'):
        files = cmds.fileDialog2(fileMode=4, fileFilter='Vehicle XML-File(s) (*.xml)', dialogStyle=2,
                                 caption='Choose XML-Config File(s)', okCaption='Set File(s)')
    else:
        file = cmds.fileDialog(m=1, dm='*.xml', title='Choose XML-Config File(s)')
        if not file is None:
            if not file.endswith('.xml'):
                file = file + '.xml'
                files.append(file)

    if len(files) > 0:
        paths = None
        for file in files:
            mayaFilePath = str(os.path.dirname(cmds.file(q=True, sn=True)).replace('\\', '/'))
            xmlFile = str(file.replace('\\', '/'))
            relPath = I3DUtils.getRelativePath(xmlFile, mayaFilePath)
            if paths is None:
                paths = relPath
            else:
                paths = paths + ';' + relPath

        cmds.textField(UI_CONTROL_STRING_XML_FILE_PATH, edit=True, text=paths)
        I3DSaveSettings(None)


def I3DOpenShaderDialog(unused):
    shaderDir = cmds.optionVar(q='GIANTS_SHADER_DIR')
    if not shaderDir:
        shaderDir = None

    if hasattr(cmds, 'fileDialog2'):
        folders = cmds.fileDialog2(fileMode=3, dialogStyle=2, caption='Set the current project path',
                                   okCaption='Set project path', startingDirectory=shaderDir)
        if not folders is None:
            shaderDir = folders[0]
    else:
        shaderDir = cmds.fileDialog(m=0, title='Set the current project path', dm='*.xml')
        if not shaderDir is None:
            shaderDir = os.path.dirname(shaderDir)

    if not shaderDir is None:
        I3DSetShaderPath(shaderDir)


def I3DUpdateXML(unused):
    global g_exportXMLIdentifiers

    I3DAddMessage('Updating config xml file...')

    xmlFilesStr = cmds.textField(UI_CONTROL_STRING_XML_FILE_PATH, q=True, text=True)
    xmlFileTagStr = cmds.textField(UI_CONTROL_STRING_XML_TAG, q=True, text=True)

    xmlFiles = xmlFilesStr.split(';')
    for xmlFile in xmlFiles:
        for k in g_exportXMLIdentifiers.keys():
            del g_exportXMLIdentifiers[k]

        mayaFilePath = str(os.path.dirname(cmds.file(q=True, sn=True)).replace('\\', '/'))
        xmlFile = I3DUtils.getMergePaths(mayaFilePath, xmlFile)

        if xmlFile == '':
            I3DAddInfo('No config xml file set!')
            return

        if not os.path.isfile(xmlFile):
            I3DAddWarning('Could not find xml file! (%s)' % xmlFile)
            return

        file = open(xmlFile, 'r')
        if file is None:
            I3DAddWarning('Could not find xml file! (%s)' % xmlFile)
            return

        lines = file.readlines()
        file.close()
        newLines = I3DRemoveI3dMapping(lines)

        endRootTag = 0
        found = False
        ### TODO: Change this to the generic one.
        for line in newLines:
            endRootTag = endRootTag + 1
            if len(re.findall('</' + xmlFileTagStr + '>', line)) > 0:
                found = True
                break

        if found:
            i3dMappings = []
            I3DAddI3dMapping(i3dMappings, None)

            if len(i3dMappings) > 0:
                i3dMappings.insert(0, '    <i3dMappings>\n')
                i3dMappings.append('    </i3dMappings>\n')

                for i in range(len(i3dMappings) - 1, -1, -1):
                    mapping = i3dMappings[i]
                    newLines.insert(endRootTag - 1, mapping)

                file = open(xmlFile, 'w')
                for line in newLines:
                    file.write(line)
                file.close()

            I3DAddMessage('')
            I3DAddMessage('Updated xml config file! (%s)' % xmlFile)
            I3DAddMessage('')
        else:
            I3DAddWarning('Could not find end tag "</' + xmlFileTagStr + '>". Ignoring i3dMappings!')

    return


def I3DAddI3dMapping(list, root):
    global g_exportXMLIdentifiers

    nodes = cmds.ls(assemblies=True)
    if not root is None:
        nodes = cmds.listRelatives(root, pa=True, f=True)

    if not nodes is None:
        for node in nodes:
            nodeType = cmds.objectType(node)
            if ((
                    nodeType == 'transform' or nodeType == 'joint') and node != 'top' and node != 'side' and node != 'front' and node != 'persp'):
                xmlIdentifier = I3DGetAttributeValue(node, 'i3D_xmlIdentifier', '')
                xmlIdentifier = xmlIdentifier.strip()
                if xmlIdentifier != '':
                    nodeName = node
                    if not nodeName.startswith("|"):
                        nodeName = "|" + nodeName
                    indexPath = I3DUtils.getIndexPath(nodeName)
                    if not indexPath is None:
                        if xmlIdentifier in g_exportXMLIdentifiers:
                            I3DAddError(node + ' XML-Identifier "' + xmlIdentifier + '" already used for node "' +
                                        g_exportXMLIdentifiers[xmlIdentifier] + '"!')
                        else:
                            g_exportXMLIdentifiers[xmlIdentifier] = node
                            list.append('        <i3dMapping id="' + xmlIdentifier + '" node="' + indexPath + '" />\n')

                I3DAddI3dMapping(list, node)


def I3DRemoveI3dMapping(lines):
    cleanedLines = []
    for line in lines:
        found = re.findall('i3dMapping', line)
        if len(found) == 0:
            cleanedLines.append(line)

    return cleanedLines


def I3DErrorCheck(unused):
    I3DClearErrors()
    I3DAddMessage('Checking for errors:\n')
    errorCount, warningCount = I3DExportValidate()
    I3DAddMessage('')
    if errorCount == 0:
        if warningCount == 0:
            I3DAddMessage('Successfully finished error check (' + str(export_ObjectCount) + ' objects)')
        else:
            I3DAddMessage('Successfully finished error check (' + str(export_ObjectCount) + ' objects) with ' + str(
                warningCount) + ' warnings')
    else:
        I3DAddMessage('Finished error check (' + str(export_ObjectCount) + ' objects) with ' + str(
            errorCount) + ' errors and ' + str(warningCount) + ' warnings')


def I3DExportAll(unused):
    I3DExportSaveAsDialog(False, True, None)
    I3DAddMessage('')
    if cmds.checkBoxGrp(UI_CONTROL_MISC_2, q=True, v1=True):
        I3DUpdateXML(None)
    I3DSaveSettings(None)


def I3DExportSelected(unused):
    I3DExportSaveAsDialog(True, True, None)
    I3DSaveSettings(None)


def I3DExportSingleFiles(unused):
    I3DClearErrors()
    sceneName = cmds.file(q=True, sceneName=True)
    file = cmds.file(q=True, sceneName=True, shortName=True)
    path = sceneName[:len(sceneName) - len(file)]

    nodes = cmds.selectedNodes(dagObjects=True)
    if not nodes is None:
        for node in nodes:
            cmds.select(node)
            filePath = path + node[1:] + ".i3d"
            I3DExportSaveAsDialog(True, False, filePath)


def I3DExportSaveAsDialog(exportSelection, clearErrors, path):
    global g_exportWarningCount, export_ObjectCount, g_exportErrorCount

    if clearErrors:
        I3DClearErrors()
    I3DAddMessage('Start export...')
    I3DAddMessage('')

    scenegraph = cmds.checkBoxGrp(UI_CONTROL_EXPORT_1, q=True, v1=True)
    animation = cmds.checkBoxGrp(UI_CONTROL_EXPORT_1, q=True, v2=True)
    shapes = cmds.checkBoxGrp(UI_CONTROL_EXPORT_1, q=True, v3=True)
    shaders = cmds.checkBoxGrp(UI_CONTROL_EXPORT_2, q=True, v1=True)
    lights = cmds.checkBoxGrp(UI_CONTROL_EXPORT_2, q=True, v2=True)
    cameras = cmds.checkBoxGrp(UI_CONTROL_EXPORT_2, q=True, v3=True)
    particlesystems = cmds.checkBoxGrp(UI_CONTROL_EXPORT_3, q=True, v1=True)
    defaultcameras = cmds.checkBoxGrp(UI_CONTROL_EXPORT_3, q=True, v2=True)
    userattributes = cmds.checkBoxGrp(UI_CONTROL_EXPORT_3, q=True, v3=True)
    exportBinaryFiles = cmds.checkBoxGrp(UI_CONTROL_EXPORT_4, q=True, v1=True)
    ignoreBindPoses = cmds.checkBoxGrp(UI_CONTROL_EXPORT_4, q=True, v2=True)
    normals = cmds.checkBoxGrp(UI_CONTROL_SHAPES_1, q=True, v1=True)
    colors = cmds.checkBoxGrp(UI_CONTROL_SHAPES_1, q=True, v2=True)
    texCoords = cmds.checkBoxGrp(UI_CONTROL_SHAPES_1, q=True, v3=True)
    skinWeigths = cmds.checkBoxGrp(UI_CONTROL_SHAPES_2, q=True, v1=True)
    mergeGroups = cmds.checkBoxGrp(UI_CONTROL_SHAPES_2, q=True, v2=True)
    verbose = cmds.checkBoxGrp(UI_CONTROL_MISC_1, q=True, v1=True)
    relativePaths = cmds.checkBoxGrp(UI_CONTROL_MISC_1, q=True, v2=True)
    templates = cmds.checkBoxGrp(UI_CONTROL_MISC_1, q=True, v3=True)
    floatEpsilon = cmds.checkBoxGrp(UI_CONTROL_MISC_1, q=True, v3=True)

    outputFile = ''
    if path is None:
        outputFile = cmds.textField(UI_CONTROL_STRING_FILE_PATH, q=True, text=True)

        if (cmds.checkBoxGrp(UI_CONTROL_BOOL_USE_MAYA_FILENAME, q=True, v1=True)):
            sceneName = cmds.file(q=True, sceneName=True)
            outputFile, fileExtension = os.path.splitext(sceneName)

        # add extension if missing
        fileName, fileExtension = os.path.splitext(outputFile)
        if (fileExtension != '.i3d'):
            outputFile = outputFile + '.i3d'

        # cancel export if no path is given
        if (outputFile == ''):
            I3DAddError('No output path given. Canceled exporting!')
            return outputFile
    else:
        outputFile = path

    I3DAddMessage('Export to: ' + outputFile + '\n')
    errorCount, warningCount = I3DExportValidate()

    g_exportWarningCount = 0
    g_exportErrorCount = 0
    callbackId = OpenMaya.MCommandMessage.addCommandOutputCallback(I3DMelMessageCallback, None)

    errorCount += I3DExportToFile(str(outputFile), scenegraph, animation, shapes, shaders, lights, cameras,
                                  userattributes, defaultcameras, particlesystems, exportBinaryFiles, ignoreBindPoses,
                                  normals, colors, texCoords, skinWeigths, mergeGroups, verbose, exportSelection,
                                  relativePaths, templates, floatEpsilon)

    OpenMaya.MMessage.removeCallback(callbackId)

    errorCount += g_exportErrorCount
    warningCount += g_exportWarningCount

    I3DAddMessage('')
    if errorCount == 0:
        if warningCount == 0:
            I3DAddMessage('Successfully finished export (' + str(export_ObjectCount) + ' objects)')
        else:
            I3DAddMessage('Successfully finished export (' + str(export_ObjectCount) + ' objects) with ' + str(
                warningCount) + ' warnings')
    else:
        I3DAddMessage(
            'Finished export (' + str(export_ObjectCount) + ' objects) with ' + str(errorCount) + ' errors and ' + str(
                warningCount) + ' warnings')

    I3DExportCustomAttributes(outputFile)

    return outputFile


def I3DExportSaveWithoutUI(exportSelection=False):
    ik = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportIK', False)
    animation = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportAnimation', True)
    shapes = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportShapes', True)
    nurbscurves = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportNurbsCurves', False)
    lights = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportLights', True)
    cameras = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportCameras', True)
    particlesystems = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportParticleSystems', False)
    defaultcameras = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportDefaultCameras', False)
    userattributes = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportUserAttributes', True)
    exportBinaryFiles = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportBynaryFiles', True)
    ignoreBindPoses = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportIgnoreBindPoses', False)
    normals = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportNormals', True)
    colors = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportColors', True)
    texCoords = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportTexCoords', True)
    skinWeigths = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportSkinWeigths', True)
    mergeGroups = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportMergeGroups', True)
    verbose = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportVerbose', True)
    relativePaths = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportRelativePaths', True)
    floatEpsilon = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportFloatEpsilon', True)
    useMayaFilename = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportUseMayaFilename', True)
    outputFile = I3DGetAttributeValue(SETTINGS_PREFIX, 'i3D_exportOutputFile', '')
    templates = floatEpsilon
    if useMayaFilename:
        sceneName = cmds.file(q=True, sceneName=True)
        outputFile, fileExtension = os.path.splitext(sceneName)
    fileName, fileExtension = os.path.splitext(outputFile)
    if (fileExtension != '.i3d'):
        outputFile = outputFile + '.i3d'
    if (outputFile == ''):
        return outputFile
    I3DExportToFile(str(outputFile), ik, animation, shapes, nurbscurves, lights, cameras, userattributes,
                    defaultcameras, particlesystems, exportBinaryFiles, ignoreBindPoses, normals, colors, texCoords,
                    skinWeigths, mergeGroups, verbose, exportSelection, relativePaths, templates, floatEpsilon)
    return outputFile


def I3DExportValidate():
    cmds.waitCursor(state=True)
    errorCount, warningCount = I3DCheckScenegraph()
    cmds.waitCursor(state=False)
    return (errorCount, warningCount)


def I3DCheckScenegraph():
    global export_ObjectCount, export_PolyCount, g_exportNumSkinnedMergeJoints, g_exportSkinnedMergeVolumes, g_exportSkinnedMergeRootNodes

    errorCount = 0
    warningCount = 0
    export_PolyCount = 0
    export_ObjectCount = 0
    nodes = cmds.ls(assemblies=True)

    for node in nodes:
        nodeType = cmds.objectType(node)
        if (nodeType == 'transform' and node != 'top' and node != 'side' and node != 'front' and node != 'persp'):
            errorCountI, warningCountI = I3DCheckTransfromGroup(node)
            errorCount += errorCountI
            warningCount += warningCountI

    if export_PolyCount > MAX_POLYCOUNT:
        I3DAddWarning('Polycount ' + str(
            export_PolyCount) + ' is very high. This causes performance issues. Try to reduce polycount')
        errorCount = errorCount + 1

    if export_ObjectCount > MAX_OBJECTCOUNT:
        I3DAddWarning('Objectcount ' + str(
            export_ObjectCount) + ' is very high. This causes performance issues. Try to combine some objects')
        errorCount = errorCount + 1

    for mergeGroup, numSkinnedMergeJoints in g_exportNumSkinnedMergeJoints.iteritems():
        if numSkinnedMergeJoints > MAX_SKINNED_JOINTS:
            I3DAddWarning('MergeGroup ' + str(mergeGroup) + ' has ' + str(
                numSkinnedMergeJoints) + ' joints. Maximum number of joints is ' + str(
                MAX_SKINNED_JOINTS) + '. Use an additional mergegroup!')
            errorCount = errorCount + 1

    for boundingVolume, isDefined in g_exportSkinnedMergeVolumes.iteritems():
        if not isDefined:
            I3DAddInfo('No bounding-volume defined for ' + str(
                boundingVolume) + '. Automatically calculating bounding volume!')

    textures = cmds.ls(fl=True, textures=True)

    missing = []
    missingPath = []
    mayaFileName = cmds.file(query=True, sceneName=True)
    for texture in textures:
        p = cmds.getAttr(texture + ".fileTextureName")
        print(p)
        if ":" in str(p).split("/")[0]:
            # absolute path, contains drive
            if p.split("/")[0] == mayaFileName.split("/")[0]:
                if not os.path.exists(p):
                    if texture not in missing:
                        missing.append(texture)
                        missingPath.append(p)
            elif str(cmds.filePathEditor(p, query=True, status=True)).rpartition(" ")[2] == "0":
                if texture not in missing:
                    missing.append(texture)
                    missingPath.append(p)
        if not os.path.exists(p):
            if texture not in missing:
                missing.append(texture)
                missingPath.append(p)
    if len(missing) > 0:
        for index, texture in enumerate(missing):
            I3DAddWarning('Texture "' + str(texture) + '" is missing (' + missingPath[index] + ')!')
            errorCount = errorCount + 1

    materials = cmds.ls(fl=True, materials=True)
    folder = os.path.dirname(os.path.abspath(mayaFileName))
    for material in materials:
        shaderPath = I3DGetAttributeValue(material, 'customShader', None)
        if not shaderPath is None:
            shaderPath = I3DUtils.getMergePaths(folder, shaderPath)
            if not os.path.exists(shaderPath):
                I3DAddWarning('Material "' + material + '" customShader does not exist "' + str(shaderPath) + '"!')

    if len(g_exportNumSkinnedMergeJoints) > 0:
        I3DAddMessage('\nMergeGroup-Info:')
        for mergeGroup, numSkinnedMergeJoints in g_exportNumSkinnedMergeJoints.iteritems():
            I3DAddMessage('    MergeGroup ' + str(mergeGroup))
            I3DAddMessage('        - Joints: ' + str(numSkinnedMergeJoints))

            path = None
            rootNode = None
            if mergeGroup in g_exportSkinnedMergeRootNodes:
                rootNode = g_exportSkinnedMergeRootNodes[mergeGroup]
                path = I3DUtils.getIndexPath(rootNode)
            if rootNode is None:
                rootNode = g_exportSkinnedMergeMaterials[mergeGroup]['node'] + ' (Default)'
                path = I3DUtils.getIndexPath(g_exportSkinnedMergeMaterials[mergeGroup]['node'])

            I3DAddMessage('        - Node:   ' + rootNode)
            I3DAddMessage('        - Index:  ' + path)
        I3DAddMessage('')

    return (errorCount, warningCount)


def I3DCheckTransfromGroup(node):
    global export_ObjectCount, export_PolyCount, g_exportNumSkinnedMergeJoints, g_exportSkinnedMergeVolumes, g_exportSkinnedMergeRootNodes

    nodeInfos = ''
    nodeWarnings = ''
    nodeErrors = ''
    errorCount = 0
    warningCount = 0
    infoCount = 0
    nodeName = cmds.ls(node, l=False)[0]
    loweredNodeName = nodeName.lower()

    nodeType = I3DGetNodeType(node)
    isStatic = I3DGetAttributeValue(node, 'i3D_static', True)
    clipDistance = I3DGetAttributeValue(node, 'i3D_clipDistance', 0.0)
    isNonRenderable = I3DGetAttributeValue(node, 'i3D_nonRenderable', False)
    isScaled = I3DGetAttributeValue(node, 'i3D_scaled', False)
    mergeGroup = I3DGetAttributeValue(node, 'i3D_mergeGroup', 0)
    boundingVolume = I3DGetAttributeValue(node, 'i3D_boundingVolume', '')

    if mergeGroup > 0:
        for object in cmds.listHistory(node):
            if 'skinCluster' in object:
                nodeInfos += '     (Warning) MergeGroup: Skinned node is added to a mergeGroup!\n'
                warningCount += 1
                break

    if cmds.objExists(node + '.fc'):
        polyCount = cmds.getAttr(node + '.fc', s=True)
        if polyCount > 0 and mergeGroup == 0 and not isNonRenderable and not I3DUtils.isCamera(node):
            export_ObjectCount = export_ObjectCount + 1
            export_PolyCount = export_PolyCount + polyCount

    if (isStatic and nodeType == NODETYPE_MESH):
        nodeInfos += '     (Info) RigidBody: Node is marked as static!\n'
        infoCount += 1

    if (
            nodeType == NODETYPE_MESH and not isNonRenderable and mergeGroup == 0 and boundingVolume == '' and not I3DUtils.isCamera(
        node) and clipDistance == 0.0):
        nodeInfos += '     (Info) Clipdistance: Node has no clipdistance set. This causes performance issues!\n'
        infoCount += 1

    if nodeType == NODETYPE_MESH and mergeGroup > 0:
        if not mergeGroup in g_exportNumSkinnedMergeJoints:
            g_exportNumSkinnedMergeJoints[mergeGroup] = 0
        g_exportNumSkinnedMergeJoints[mergeGroup] = g_exportNumSkinnedMergeJoints[mergeGroup] + 1

        mergeGroupName = "MERGEGROUP_" + str(mergeGroup)
        if not mergeGroupName in g_exportSkinnedMergeVolumes:
            g_exportSkinnedMergeVolumes[mergeGroupName] = False

    if boundingVolume != '':
        g_exportSkinnedMergeVolumes[boundingVolume] = True

    if nodeType == NODETYPE_MESH:
        decalLayer = I3DGetAttributeValue(node, 'i3D_decalLayer', 0)
        if decalLayer == 0 and (loweredNodeName.find('decal') != -1 or loweredNodeName.find('static') != -1):
            nodeInfos += '     (Info) DecalLayer: Node named "decal" or "static" but decalLayer-attribute is set to 0\n'
            infoCount += 1
        elif decalLayer != 0 and (loweredNodeName.find('decal') == -1 and loweredNodeName.find('static') == -1):
            nodeInfos += '     (Info) DecalLayer: Nodes have to be pre-/postfixed by "decal" or "static" if decalLayer-attribute > 0\n'
            infoCount += 1

        if loweredNodeName.find('fillvolume') != -1:
            if not I3DGetIsVisible(node):
                nodeWarnings += '  (Warning) FillVolume node is hidden! Use "nonRenderable" instead of hiding the node!'
                warningCount += 1
            if I3DGetAttributeValue(node, 'i3D_cpuMesh', 0) == 0:
                nodeWarnings += '  (Warning) FillVolume is not marked as CPU-Mesh!'
                warningCount += 1

    shear = cmds.getAttr(node + '.shear')
    if (shear[0][0] != 0.0 or shear[0][1] != 0.0 or shear[0][2] != 0.0):
        warningCount += 1
        nodeWarnings += '  (Warning) Shear: Run \'FreezeTransformation\'!\n'

    rotatePivot = cmds.getAttr(node + '.rotatePivot')
    scalePivot = cmds.getAttr(node + '.scalePivot')
    if (math.fabs(rotatePivot[0][0]) > 1.0e-10 or math.fabs(rotatePivot[0][1]) > 1.0e-10 or math.fabs(
            rotatePivot[0][2]) > 1.0e-10 or math.fabs(scalePivot[0][0]) > 1.0e-10 or math.fabs(
        scalePivot[0][1]) > 1.0e-10 or math.fabs(scalePivot[0][2]) > 1.0e-10):
        warningCount += 1
        nodeWarnings += '  (Warning) Pivot: Run \'FreezeToPivot\'!\n'

    scale = cmds.getAttr(node + '.scale')
    if (math.fabs(1.0 - scale[0][0]) > 0.1e-10 or math.fabs(1.0 - scale[0][1]) > 0.1e-10 or math.fabs(
            1.0 - scale[0][2]) > 0.1e-10):
        if not isScaled:
            warningCount += 1
            nodeWarnings += '  (Warning) Scaled: Run \'FreezeTransformation\' or set node attribute \'scale\' to true!\n'
    elif isScaled:
        warningCount += 1
        nodeWarnings += '  (Warning) Scaled: Node is marked as scaled but scaling is (1,1,1)!'

    errorCountJ, warningCountJ, infos, warnings, errors = I3DCheckMaterials(node)
    errorCount += errorCountJ
    warningCount += warningCountJ
    nodeInfos += infos
    nodeWarnings += warnings
    nodeErrors += errors

    if errorCount > 0 or warningCount > 0 or infoCount > 0:
        I3DAddMessage(node)
        if nodeInfos != '':
            I3DAddMessage(nodeInfos.rstrip('\n'))
        if nodeWarnings != '':
            I3DAddMessage(nodeWarnings.rstrip('\n'))
        if nodeErrors != '':
            I3DAddMessage(nodeErrors.rstrip('\n'))
        I3DAddMessage('')

    nodes = cmds.listRelatives(node)
    if not nodes is None:
        for cnode in nodes:
            cnode = node + '|' + cnode
            nodeType = cmds.objectType(cnode)
            if nodeType == 'transform':
                errorCountI, warningCountI = I3DCheckTransfromGroup(cnode)
                errorCountJ, warningCountJ, infos, warnings, errors = I3DCheckMaterials(cnode)
                errorCount += errorCountI + errorCountJ;
                warningCount += warningCountI + warningCountJ;
    return (errorCount, warningCount)


def I3DCheckMaterials(node):
    errorCount = 0
    warningCount = 0
    nodeWarnings = ''
    nodeInfos = ''
    nodeErrors = ''

    shapes = cmds.listRelatives(node)
    if not shapes is None:
        shape = node + '|' + shapes[0]

        materials = cmds.listConnections(shape, type='shadingEngine')
        if not materials is None:
            materials = list(set(materials))

            if (len(materials) > 1):
                warningCount += 1
                nodeWarnings += '  (Warning) Node has ' + str(len(
                    materials)) + ' material assigned to it. This might cause performance issues. Consider splitting up the mesh (Help: Split meshes)\n'

            mergeGroup = I3DGetAttributeValue(node, 'i3D_mergeGroup', 0)
            if mergeGroup > 0:
                if not mergeGroup in g_exportSkinnedMergeMaterials:
                    g_exportSkinnedMergeMaterials[mergeGroup] = {'material': materials[0], 'node': '|' + node}

                if g_exportSkinnedMergeMaterials[mergeGroup]['material'] != materials[0]:
                    nodeWarnings += '  (Warning) Node has different material (Mergegroup_' + str(
                        mergeGroup) + ' - Basematerialnode: ' + g_exportSkinnedMergeMaterials[mergeGroup][
                                        'node'] + ') assigned to it. This might cause performance issues. Consider using another mergegroup!\n'
                    warningCount += 1

                isRootNode = I3DGetAttributeValue(node, 'i3D_mergeGroupRoot', False)
                if isRootNode:
                    if not mergeGroup in g_exportSkinnedMergeRootNodes:
                        g_exportSkinnedMergeRootNodes[mergeGroup] = '|' + node
                    else:
                        nodeWarnings += '  (Warning) RootNode for MergeGroup_' + str(mergeGroup) + ' already set!\n'
                        warningCount += 1

            for material in materials:
                surfaceShader = cmds.listConnections(material + '.surfaceShader')
                if surfaceShader is None:
                    warningCount += 1
                    nodeWarnings += '  (Warning) Node has no material assigned to it. Assign a material!\n'

    return (errorCount, warningCount, nodeInfos, nodeWarnings, nodeErrors)


def I3DGetNodeType(node):
    type = 0
    nodes = cmds.listRelatives(node, shapes=True)
    if (cmds.nodeType(node) != 'transform' or (not nodes is None and len(nodes) > 0)):
        type = NODETYPE_MESH
    else:
        type = NODETYPE_GROUP
    return type


def I3DExportCustomAttributes(filename):
    nodes = cmds.ls(assemblies=True)
    for node in nodes:
        nodeType = cmds.objectType(node)
        if (nodeType == 'transform' and node != 'top' and node != 'side' and node != 'front' and node != 'persp'):
            I3DExportCustomAttributesByNode(filename, node)
    return


def I3DExportCustomAttributesByNode(filename, node):
    shapes = cmds.listRelatives(node)
    if not shapes is None:
        for i in range(0, len(shapes)):
            shapes[i] = node + '|' + shapes[i]

        materials = cmds.listConnections(shapes, type='shadingEngine')
        if not materials is None:
            materials = list(set(materials))
            for material in materials:
                surfaceShader = cmds.listConnections(material + '.surfaceShader')
                if not surfaceShader is None:
                    for shader in surfaceShader:
                        if (I3DAttributeExists(shader, 'i3D_reflectionMap_resolution')):
                            resolution = I3DGetAttributeValue(shader, 'i3D_reflectionMap_resolution', '0')
                            I3DAddCustomAttributeToMaterial(filename, shader, 'Reflectionmap', 'resolution', resolution)
                        if (I3DAttributeExists(shader, 'i3D_reflectionMap_wrap')):
                            state = I3DGetAttributeValue(shader, 'i3D_reflectionMap_wrap', 'false')
                            I3DAddCustomAttributeToMaterial(filename, shader, 'Reflectionmap', 'wrap', state)
                        if (I3DAttributeExists(shader, 'i3D_texture_wrap')):
                            state = I3DGetAttributeValue(shader, 'i3D_texture_wrap', 'false')
                            I3DAddCustomAttributeToMaterial(filename, shader, 'Texture', 'wrap', state)
                        if (I3DAttributeExists(shader, 'i3D_customMap_wrap')):
                            wrapText = I3DGetAttributeValue(shader, 'i3D_customMap_wrap', 'false')
                            tokens = wrapText.split(' ')
                            if (len(tokens) == 2):
                                textureName = 'Custommap name="' + tokens[0] + '"'
                                I3DAddCustomAttributeToMaterial(filename, shader, textureName, 'wrap', tokens[1])
                            else:
                                I3DAddError('Invalid customMap_Wrap value. Syntax: <customMapName> <true/false>')

    nodes = cmds.listRelatives(node)
    if not nodes is None:
        for cnode in nodes:
            cnode = node + '|' + cnode
            nodeType = cmds.objectType(cnode)
            if (nodeType == 'transform'):
                I3DExportCustomAttributesByNode(filename, cnode)

    return


def I3DAddCustomAttributeToMaterial(filename, materialName, textureType, attributeName, attributeValue):
    file = open(filename, 'r')
    content = file.readlines()
    file.close()

    material = '.*<Material.*name="' + materialName + '".*'
    texture = '<' + textureType + ' '
    pattern = attributeName + '="[a-zA-Z0-9]*"'
    textureReplacement = attributeName + '="' + attributeValue + '"'

    found = False

    for i in range(0, len(content)):
        line = content[i]
        materialMatch = re.match(material, line)

        if not materialMatch is None:
            found = True

        if found:
            textureMatch = re.match('.*' + texture + '.*', line)
            if not textureMatch is None:
                result = re.match('.*(' + pattern + ').*', line)
                if not result is None:
                    print('Attribute exist (' + str(i) + '): ' + line)
                    line = line.replace(result.group(1), textureReplacement)
                    print('Replaced attribute ' + str(i) + ': ' + line)
                else:
                    newTexture = texture + textureReplacement + ' '
                    line = line.replace(texture, newTexture)
                    print('Added attribute (' + str(i) + '): ' + line)
                found = False
        content[i] = line

    file = open(filename, 'w')
    for line in content:
        file.write(line)
    file.close()

    return


def I3DClearErrors():
    global g_exportSkinnedMergeMaterials, g_exportNumSkinnedMergeJoints, g_exportSkinnedMergeVolumes, g_exportSkinnedMergeRootNodes
    cmds.scrollField(UI_CONTROL_STRING_VALIDATION, edit=True, text='')
    g_exportSkinnedMergeMaterials = {}
    g_exportNumSkinnedMergeJoints = {}
    g_exportSkinnedMergeVolumes = {}
    g_exportSkinnedMergeRootNodes = {}
    return


def I3DSetIdentifier(unused):
    nodes = cmds.ls(sl=True, o=True, sn=True, long=True)
    if not nodes is None:
        for node in nodes:
            splittedNames = node.split('|')
            nodeName = splittedNames[len(splittedNames) - 1]
            cmds.textField(UI_CONTROL_STRING_IDENTIFIER, edit=True, text=nodeName)
            I3DSaveAttributeString(node, 'i3D_xmlIdentifier', nodeName)


def I3DRemoveIdentifier(unused):
    nodes = cmds.ls(sl=True, o=True, sn=True, long=True)
    if not nodes is None:
        for node in nodes:
            I3DRemoveAttribute(node, 'i3D_xmlIdentifier')
            cmds.textField(UI_CONTROL_STRING_IDENTIFIER, edit=True, text='')


def I3DAddInfo(msg):
    I3DAddDebugMessage('(Info)', msg)
    return


def I3DAddWarning(msg):
    I3DAddDebugMessage('(Warning)', msg)
    return


def I3DAddError(msg):
    I3DAddDebugMessage('(Error)', msg)
    return


def I3DAddDebugMessage(type, msg):
    I3DAddMessage(type + ' ' + msg)
    return


def I3DAddMessage(msg):
    text = cmds.scrollField(UI_CONTROL_STRING_VALIDATION, q=True, text=True)
    text = text + msg + '\n'
    cmds.scrollField(UI_CONTROL_STRING_VALIDATION, edit=True, text=text)
    cmds.refresh()
    return


def I3DMelMessageCallback(nativeMsg, messageType, data):
    global g_exportWarningCount
    global g_exportErrorCount
    if messageType == OpenMaya.MCommandMessage.kWarning:
        g_exportWarningCount = g_exportWarningCount + 1;
        I3DAddMessage('Warning: ' + nativeMsg)
    elif messageType == OpenMaya.MCommandMessage.kError:
        g_exportErrorCount = g_exportErrorCount + 1;
        I3DAddMessage('Error: ' + nativeMsg)


def I3DAddCheckBoxElement(parent, label, checkboxName, defaultValue=False, checkboxLabel='', annotation='',
                          editable=True, width=DEFAULT_FIELD_WIDTH):
    layout = cmds.rowLayout(parent=parent, adjustableColumn=2, numberOfColumns=2)
    cmds.text(parent=layout, label=label, width=TEXT_WIDTH, align='left', annotation=annotation)
    cmds.checkBox(checkboxName, parent=layout, label=checkboxLabel, align='left', value=defaultValue,
                  annotation=annotation, editable=editable)
    return


def I3DAddIntFieldElement(parent, label, intFieldName, defaultValue, annotation='', editable=True,
                          width=DEFAULT_FIELD_WIDTH):
    layout = cmds.rowLayout(parent=parent, adjustableColumn=2, numberOfColumns=2)
    cmds.text(parent=layout, label=label, width=TEXT_WIDTH, align='left', annotation=annotation)
    cmds.intField(intFieldName, parent=layout, value=defaultValue, annotation=annotation, editable=editable,
                  width=width)
    return


def I3DAddMergeGroup(parent):
    layout = cmds.rowLayout('mergeGroupLayout', parent=parent, adjustableColumn=4, numberOfColumns=4)
    cmds.text(parent=layout, label='Merge Group', width=TEXT_WIDTH, align='left', annotation='')
    cmds.intField(UI_CONTROL_INT_MERGE_GROUP, parent=layout, value=0, annotation='', editable=True,
                  width=DEFAULT_FIELD_WIDTH)
    cmds.text(parent=layout, label='Root', width=50, align='right')
    cmds.checkBox(UI_CONTROL_BOOL_MERGE_GROUP_ROOT, parent=layout, label='', align='left', value=False, annotation='',
                  editable=True)
    return


def I3DAddBoundVolume(parent):
    layout = cmds.rowLayout('boundingVolumeLayout', parent=parent, adjustableColumn=3, numberOfColumns=3)
    cmds.text(parent=layout, label='Bounds Of', width=TEXT_WIDTH, align='left')
    cmds.textField(UI_CONTROL_STRING_BOUNDINGVOLUME, parent=layout, text='',
                   annotation='Bounding volume for given shape name or merge group', editable=True, width=TEXT_WIDTH)
    menu = cmds.optionMenu(UI_OPTIONS_PREDEFINED_BOUNDINGVOLUME, parent=layout,
                           changeCommand=I3DBoundingVolumeOptionMenu, width=115)
    cmds.menuItem(parent=menu, label=' ')
    cmds.menuItem(parent=menu, label='MERGEGROUP_1')
    cmds.menuItem(parent=menu, label='MERGEGROUP_2')
    cmds.menuItem(parent=menu, label='MERGEGROUP_3')
    cmds.menuItem(parent=menu, label='MERGEGROUP_4')
    cmds.menuItem(parent=menu, label='MERGEGROUP_5')
    cmds.menuItem(parent=menu, label='MERGEGROUP_6')
    cmds.menuItem(parent=menu, label='MERGEGROUP_7')
    cmds.menuItem(parent=menu, label='MERGEGROUP_8')
    cmds.menuItem(parent=menu, label='MERGEGROUP_9')
    return


def I3DAddRestitution(parent):
    layout = cmds.rowLayout('restitutionLayout', parent=parent, adjustableColumn=4, numberOfColumns=4)
    cmds.text(parent=layout, label='Restitution', width=TEXT_WIDTH, align='left')
    cmds.floatField(UI_CONTROL_FLOAT_RESTITUTION, parent=layout, value=0, annotation='Bouncyness of the surface')
    menu = cmds.optionMenu(UI_OPTIONS_PREDEFINED_PHYSICS, parent=layout, changeCommand=I3DPhysicsOptionMenu, width=100)
    cmds.menuItem(parent=menu, label='Default')
    cmds.menuItem(parent=menu, label='Rubber')
    cmds.menuItem(parent=menu, label='Concrete')
    cmds.menuItem(parent=menu, label='Wood')
    cmds.menuItem(parent=menu, label='Metal')
    cmds.menuItem(parent=menu, label='Glass')
    return


def I3DAddMass(parent):
    layout = cmds.rowLayout('massLayout', parent=parent, adjustableColumn=2, numberOfColumns=2)
    cmds.text(parent=layout, label='Density', width=TEXT_WIDTH, align='left',
              annotation='Used with the shape of the object to calculate mass. The higher the number, the heavier the object')
    cmds.floatField(UI_CONTROL_FLOAT_DENSITY, parent=layout, value=0,
                    annotation='Used with the shape of the object to calculate mass. The higher the number, the heavier the object',
                    editable=True, width=DEFAULT_FIELD_WIDTH)
    layoutMass = cmds.rowLayout(parent=parent, adjustableColumn=3, numberOfColumns=3)
    cmds.text(UI_CONTROL_LABEL_MASS, parent=layoutMass, label='Mass', width=TEXT_WIDTH, align='left', visible=True)
    cmds.floatField(UI_CONTROL_FLOAT_MASS, parent=layoutMass, value=0, annotation='Total mass of the compound node',
                    editable=False, width=DEFAULT_FIELD_WIDTH, visible=True)
    cmds.textField(UI_CONTROL_STRING_MASS_NODE, parent=layoutMass, text='', annotation='Name of the compound node',
                   editable=False, width=150, visible=True)
    return


def I3DAddTextFieldElement(parent, label, textFieldName, defaultValue='', annotation='', editable=True,
                           width=DEFAULT_FIELD_WIDTH):
    layout = cmds.rowLayout(parent=parent, adjustableColumn=2, numberOfColumns=2)
    cmds.text(parent=layout, label=label, width=TEXT_WIDTH, align='left', annotation=annotation)
    cmds.textField(textFieldName, parent=layout, text=defaultValue, annotation=annotation, editable=editable,
                   width=width)
    return


def I3DAddFloatFieldElement(parent, label, floatFieldName, defaultValue, annotation='', editable=True,
                            width=DEFAULT_FIELD_WIDTH):
    layout = cmds.rowLayout(parent=parent, adjustableColumn=2, numberOfColumns=2)
    cmds.text(parent=layout, label=label, width=TEXT_WIDTH, align='left', annotation=annotation)
    cmds.floatField(floatFieldName, parent=layout, value=defaultValue, annotation=annotation, editable=editable,
                    width=width)
    return


def I3DAddFloatFieldElements(parent, label, floatFieldNames, defaultValues, annotations=[''], editable=True,
                             width=DEFAULT_FIELD_WIDTH):
    layout = cmds.rowLayout(parent=parent, adjustableColumn=len(floatFieldNames) + 1,
                            numberOfColumns=len(floatFieldNames) + 1)
    cmds.text(parent=layout, label=label, width=TEXT_WIDTH, align='left', annotation=annotations[0])
    for i in range(len(floatFieldNames)):
        annotation = ''
        if i + 1 < len(annotations):
            annotation = annotations[i + 1]
        cmds.floatField(floatFieldNames[i], parent=layout, value=defaultValues[i], annotation=annotation,
                        editable=editable, width=width)
    return


def I3DResetAttributesScreen(unused):
    for k, v in SETTINGS_ATTRIBUTES.iteritems():
        if v['type'] == TYPE_BOOL:
            cmds.checkBox(v['uiControl'], edit=True, v=v['defaultValue'])
        elif v['type'] == TYPE_INT:
            cmds.intField(v['uiControl'], edit=True, v=v['defaultValue'])
        elif v['type'] == TYPE_FLOAT:
            cmds.floatField(v['uiControl'], edit=True, v=v['defaultValue'])
        elif v['type'] == TYPE_STRING:
            cmds.textField(v['uiControl'], edit=True, text=v['defaultValue'])


def I3DManipulatorToPivot(unused):
    objs = cmds.filterExpand(ex=True, sm=12)
    isValidSelection = not objs is None and len(objs) > 0
    if (not isValidSelection):
        objs = cmds.filterExpand(ex=True, sm=31)
        isValidSelection = not objs is None and len(objs) > 0
        if (not isValidSelection):
            objs = cmds.filterExpand(ex=True, sm=32)
            isValidSelection = not objs is None and len(objs) > 0
            if (not isValidSelection):
                objs = cmds.filterExpand(ex=True, sm=34)
                isValidSelection = not objs is None and len(objs) > 0
    if (isValidSelection):
        cmds.setToolTo('moveSuperContext')
        result = cmds.manipMoveContext('Move', q=True, p=True)
        result = I3DUtils.linearInternalToUIVector(result)
        origObjShape = cmds.listRelatives(objs[0], p=True, pa=True)
        origObj = cmds.listRelatives(origObjShape, p=True, pa=True)
        targetMesh = origObj[0]
        cmds.xform(targetMesh, worldSpace=True, preserve=True, pivots=[result[0], result[1], result[2]])
        cmds.select(targetMesh, r=True)
    else:
        I3DShowWarning('Please select nodes, vertices, edges or faces')
    return


def I3DManipulatorToGroup(unused):
    objs = cmds.filterExpand(ex=True, sm=12)
    isValidSelection = not objs is None and len(objs) > 0
    if (not isValidSelection):
        objs = cmds.filterExpand(ex=True, sm=31)
        isValidSelection = not objs is None and len(objs) > 0
        if (not isValidSelection):
            objs = cmds.filterExpand(ex=True, sm=32)
            isValidSelection = not objs is None and len(objs) > 0
            if (not isValidSelection):
                objs = cmds.filterExpand(ex=True, sm=34)
                isValidSelection = not objs is None and len(objs) > 0
    if (isValidSelection):
        cmds.setToolTo('moveSuperContext')
        result = cmds.manipMoveContext('Move', q=True, p=True)
        result = I3DUtils.linearInternalToUIVector(result)

        origObjShape = cmds.listRelatives(objs[0], p=True, pa=True)
        origObj = cmds.listRelatives(origObjShape, p=True, pa=True)
        targetMesh = origObj[0]

        newGroup = cmds.group(em=True, name=targetMesh + 'PositionGroup')
        cmds.xform(newGroup, worldSpace=True, preserve=True, pivots=[result[0], result[1], result[2]])
        cmds.select(newGroup, r=True)

        I3DDoFreezeToPivot(newGroup)
    else:
        I3DShowWarning('Please select nodes, vertices, edges or faces')
    return


def I3DPhysicsOptionMenu(selectedItem):
    if selectedItem == 'Default':
        I3DSetPhysicsAttributes(0.0, 0.5, 0.5, 0.0, 0.01, 0.5)
    elif selectedItem == 'Rubber':
        I3DSetPhysicsAttributes(1.0, 0.7, 0.7, 0.0, 0.01, 1.0)
    elif selectedItem == 'Concrete':
        I3DSetPhysicsAttributes(1.0, 0.7, 0.7, 0.0, 0.01, 1.0)
    elif selectedItem == 'Wood':
        I3DSetPhysicsAttributes(0.3, 0.7, 0.7, 0.0, 0.01, 0.6)
    elif selectedItem == 'Metal':
        I3DSetPhysicsAttributes(0.1, 0.6, 0.7, 0.0, 0.01, 1.6)
    elif selectedItem == 'Glass':
        I3DSetPhysicsAttributes(0.1, 0.05, 0.05, 0.0, 0.01, 1.0)


def I3DSetPhysicsAttributes(restitution, staticFriction, dynamicFriction, linearDamping, angularDamping, density):
    cmds.floatField(UI_CONTROL_FLOAT_RESTITUTION, edit=True, value=restitution)
    cmds.floatField(UI_CONTROL_FLOAT_STATIC_FRICTION, edit=True, value=staticFriction)
    cmds.floatField(UI_CONTROL_FLOAT_DYNAMIC_FRICTION, edit=True, value=dynamicFriction)
    cmds.floatField(UI_CONTROL_FLOAT_LINEAR_DAMPING, edit=True, value=linearDamping)
    cmds.floatField(UI_CONTROL_FLOAT_ANGULAR_DAMPING, edit=True, value=angularDamping)
    cmds.floatField(UI_CONTROL_FLOAT_DENSITY, edit=True, value=density)


def I3DBoundingVolumeOptionMenu(selectedItem):
    if not selectedItem == ' ':
        cmds.textField(UI_CONTROL_STRING_BOUNDINGVOLUME, edit=True, text=selectedItem)


def I3DToggleViewCube(unused):
    cmds.viewManip(topRight=True, visible=(not cmds.viewManip(q=True, visible=True)))


def I3DGetShaderNode(node):
    shapes = cmds.listRelatives(node)
    for i in range(len(shapes)):
        shapes[i] = node + '|' + shapes[i]

    materials = list(set(cmds.listConnections(shapes, type='shadingEngine')))
    if (len(materials) > 1):
        I3DShowWarning(node + ' has more than 1 material assigned to it\n')

    surfaceShader = cmds.listConnections(materials[0] + '.surfaceShader')
    if (len(surfaceShader) == 0):
        I3DShowWarning(node + ' has no material assigned to it\n')

    return surfaceShader[0]


def I3DAddAttribute(node, name, value):
    if (not I3DAttributeExists(node, name)):
        cmds.addAttr(node, ln=name, nn=name, dt='string')
        cmds.setAttr(node + '.' + name, edit=True, keyable=True)
    cmds.setAttr(node + '.' + name, value, type='string')


def I3DSetAttributePreset(selectedItemName):
    I3DResetAttributesScreen(False)

    for attribute in SETTINGS_VEHICLE_ATTRIBUTES:
        if attribute['name'] == selectedItemName:
            I3DSetCollision(attribute['attributeValues'])
            return


def I3DSetCollision(attributeValues):
    cmds.checkBox(UI_CONTROL_BOOL_STATIC, edit=True, value=attributeValues['static'])
    cmds.checkBox(UI_CONTROL_BOOL_DYNAMIC, edit=True, value=attributeValues['dynamic'])
    cmds.checkBox(UI_CONTROL_BOOL_KINEMATIC, edit=True, value=attributeValues['kinematic'])
    cmds.checkBox(UI_CONTROL_BOOL_COMPOUND, edit=True, value=attributeValues['compound'])
    cmds.checkBox(UI_CONTROL_BOOL_COMPOUND_CHILD, edit=True, value=attributeValues['compoundChild'])
    cmds.checkBox(UI_CONTROL_BOOL_TRIGGER, edit=True, value=attributeValues['trigger'])
    cmds.checkBox(UI_CONTROL_BOOL_COLLISION, edit=True, value=attributeValues['collision'])
    cmds.floatField(UI_CONTROL_FLOAT_CLIP_DISTANCE, edit=True, value=attributeValues['clipDistance'])
    if 'density' in attributeValues:
        cmds.floatField(UI_CONTROL_FLOAT_DENSITY, edit=True, value=attributeValues['density'])
    cmds.checkBox(UI_CONTROL_BOOL_NON_RENDERABLE, edit=True, value=attributeValues['nonRenderable'])
    cmds.intField(UI_CONTROL_INT_COLLISION_MASK, edit=True, value=attributeValues['collisionMask'])
    if 'objectMask' in attributeValues:
        cmds.intField(UI_CONTROL_INT_OBJECT_MASK, edit=True, value=attributeValues['objectMask'])
    cmds.intField(UI_CONTROL_INT_DECAL_LAYER, edit=True, value=attributeValues['decalLayer'])
    if 'mergeGroup' in attributeValues:
        cmds.intField(UI_CONTROL_INT_MERGE_GROUP, edit=True, value=attributeValues['mergeGroup'])
    cmds.checkBox(UI_CONTROL_BOOL_CPUMESH, edit=True, value=attributeValues['cpuMesh'])


def I3DAdjustWorldPivot(unused):
    nodes = cmds.ls(sl=True, o=True)
    if (len(nodes) < 2):
        I3DShowWarning('You need to select a mesh and a target point!')
        return
    worldPivots = cmds.xform(nodes[1], q=True, ws=True, scalePivot=True)
    cmds.xform(nodes[0], worldSpace=True, preserve=True, pivots=worldPivots)


# detaches the selected faces to a separate object
def I3DDetachFaces(unused):
    origFaceSel = cmds.filterExpand(ex=1, sm=34)
    origObjShape = cmds.listRelatives(origFaceSel, p=True, pa=True)
    origObj = cmds.listRelatives(origObjShape, p=True, pa=True)

    nameSplitSkip = []
    faceNum = []
    newFaceSel = []

    skip = 0
    # get selected face numbers into faceNum
    for step in range(0, len(origFaceSel)):
        temp = origFaceSel[step].split('.')
        nameSplitSkip.append(temp[0])
        nameSplitSkip.append(temp[1])

    skip2 = 1
    for step2 in range(0, len(nameSplitSkip) / 2):
        faceNum.append(nameSplitSkip[skip2])
        skip2 = skip2 + 2

    # duplicate original object
    newObj = cmds.duplicate(origObj[0], un=True, rc=True)
    cmds.delete(newObj[0], ch=True)
    newAllFaces = cmds.ls(newObj[0] + '.f[*]')

    # make new array for face selection on newObj
    for step3 in range(0, len(faceNum)):
        newFaceSel.append(newObj[0] + '.' + faceNum[step3])

    # delete original face selection
    cmds.delete(origFaceSel)

    # delete inverse face selection on duplicate
    cmds.select(newAllFaces, r=True)
    cmds.select(newFaceSel, d=True)
    cmds.delete()

    cmds.select(newObj[0], r=True)
    children = cmds.listRelatives(c=True, f=True, type='transform')
    if not children is None:
        for child in children:
            cmds.delete(child)


# helper functions, like normal translation freeze, but not freeze to 0 0 0 but to the pivot point
def I3DFreezeToPivot(unused):
    nodes = I3DUtils.getSelectedObjects()

    if (len(nodes) == 0):
        I3DShowWarning('Nothing selected!')
        return

    for node in nodes:
        I3DDoFreezeToPivot(node)


# helper function for I3DFreezeToPivot
def I3DDoFreezeToPivot(node):
    localPivotPos = cmds.xform(node, q=True, sp=True, os=True)
    localPosition = cmds.xform(node, q=True, t=True, os=True)
    localRotation = cmds.xform(node, q=True, ro=True, eu=True)
    children = cmds.listRelatives(node, c=True, pa=True, ni=True, type='transform')

    matrix = []
    if not children is None:
        for child in children:
            localRotationChild = cmds.xform(child, q=True, ro=True, eu=True)
            matrix.append(localRotationChild)

    cmds.move(-localPivotPos[0], -localPivotPos[1], -localPivotPos[2], node, a=True, os=True, moveXYZ=True)
    cmds.makeIdentity(node, apply=True, t=True, r=False, s=False, n=False)
    cmds.xform(node, os=True, pivots=[0, 0, 0])
    cmds.move(localPosition[0] + localPivotPos[0], localPosition[1] + localPivotPos[1],
              localPosition[2] + localPivotPos[2], node, a=True, os=True, moveXYZ=True)

    if not children is None:
        i = 0
        for child in children:
            cmds.rotate(matrix[i][0], matrix[i][1], matrix[i][2], child, a=True, eu=True)
            i = i + 1

    cmds.rotate(localRotation[0], localRotation[1], localRotation[2], node, a=True, eu=True)

    if not children is None:
        for child in children:
            I3DDoFreezeToPivot(child)


def I3DRemoveObjectAttributes(unused):
    objectName = cmds.textField(UI_CONTROL_STRING_LOADED_NODE_NAME, q=True, text=True)
    if (len(objectName) > 0):
        I3DRemoveAttributes(objectName)
        I3DLoadObjectAttributes(objectName)


def I3DApplySelectedAttributes(unused):
    nodes = cmds.selectedNodes(dagObjects=True)
    if not nodes is None:
        for node in nodes:
            if (cmds.objectType(node, isType='transform')):
                I3DSaveAttributes(node)
        I3DUpdateMass(nodes[0])
    else:
        I3DShowWarning('Nothing selected')


def I3DLoadObjectAttributes(unused):
    nodes = cmds.selectedNodes(dagObjects=True)
    if not nodes is None:
        node = nodes[0]
        if cmds.objectType(node, isType='transform'):
            cmds.textField(UI_CONTROL_STRING_LOADED_NODE_NAME, edit=True, text=node)
            for k, v in SETTINGS_ATTRIBUTES.iteritems():
                if v['type'] == TYPE_BOOL:
                    cmds.checkBox(v['uiControl'], edit=True, v=I3DGetAttributeValue(node, k, v['defaultValue']))
                elif v['type'] == TYPE_INT:
                    cmds.intField(v['uiControl'], edit=True, v=I3DGetAttributeValue(node, k, v['defaultValue']))
                elif v['type'] == TYPE_FLOAT:
                    cmds.floatField(v['uiControl'], edit=True, v=I3DGetAttributeValue(node, k, v['defaultValue']))
                elif v['type'] == TYPE_STRING:
                    cmds.textField(v['uiControl'], edit=True, text=I3DGetAttributeValue(node, k, v['defaultValue']))
        I3DUpdateMass(node)
    else:
        I3DShowWarning('Nothing selected')


def I3DSaveAttributes(node):
    for k, v in SETTINGS_ATTRIBUTES.iteritems():
        if v['type'] == TYPE_BOOL:
            I3DSaveAttributeBool(node, k, cmds.checkBox(v['uiControl'], q=True, v=True))
        elif v['type'] == TYPE_INT:
            I3DSaveAttributeInt(node, k, cmds.intField(v['uiControl'], q=True, v=True))
        elif v['type'] == TYPE_FLOAT:
            I3DSaveAttributeFloat(node, k, cmds.floatField(v['uiControl'], q=True, v=True))
        elif v['type'] == TYPE_STRING:
            I3DSaveAttributeString(node, k, cmds.textField(v['uiControl'], q=True, text=True))

    I3DUpdateLayers(node)
    I3DUpdateMass(node)


def I3DRemoveAttributes(node):
    for k, v in SETTINGS_ATTRIBUTES.iteritems():
        I3DRemoveAttribute(node, k)
    I3DUpdateLayers(node)
    I3DUpdateMass(node)


def I3DSaveAttributeString(node, attribute, value):
    fullname = node + '.' + attribute
    if (not I3DAttributeExists(node, attribute)):
        cmds.addAttr(node, ln=attribute, dt='string')
    cmds.setAttr(fullname, value, type='string')


def I3DSaveAttributeInt(node, attribute, value):
    fullname = node + '.' + attribute
    if (not I3DAttributeExists(node, attribute)):
        cmds.addAttr(node, ln=attribute, at='long')
    cmds.setAttr(fullname, value)


def I3DSaveAttributeFloat(node, attribute, value):
    fullname = node + '.' + attribute
    if (not I3DAttributeExists(node, attribute)):
        cmds.addAttr(node, ln=attribute, at='float')
    cmds.setAttr(fullname, value)


def I3DSaveAttributeBool(node, attribute, value):
    fullname = node + '.' + attribute
    if (not I3DAttributeExists(node, attribute)):
        cmds.addAttr(node, ln=attribute, at='bool')
    cmds.setAttr(fullname, value)


def I3DGetAttributeValue(node, attribute, default):
    fullname = node + '.' + attribute
    if (I3DAttributeExists(node, attribute)):
        return cmds.getAttr(fullname)
    return default


def I3DRemoveAttribute(node, attribute):
    fullname = node + '.' + attribute
    if (I3DAttributeExists(node, attribute)):
        cmds.deleteAttr(fullname)


def I3DAttributeExists(node, attribute):
    node = str(node)
    attribute = str(attribute)
    if type(node) != type('') or type(attribute) != type(''): I3DShowWarning('not a valid name')
    if (attribute and node):
        if not cmds.objExists(node): return False
        if attribute in cmds.listAttr(node, shortNames=True): return True
        if attribute in cmds.listAttr(node): return True
    return False


def I3DRemoveNameSpace(nodeList):
    if not nodeList:
        nodes = cmds.ls(sl=True, o=True, long=True)
    else:
        nodes = nodeList

    if not nodes is None:
        for node in nodes:
            children = cmds.listRelatives(node, c=True, pa=True, type='transform')
            if not children is None:
                I3DRemoveNameSpace(children)

            selectedNode = cmds.ls(node)
            name = selectedNode[0]
            pos = name.rfind(':')
            if pos != -1:
                name = name[(pos + 1):]
                cmds.rename(node, name)


def I3DRemoveDuplicateMaterials(unused):
    deleteDuplicateMaterials.duplicateMaterials("full")


def I3DRemoveDuplicateTextures(unused):
    deleteDuplicateTextures.duplicateTextures()


def I3DMaterialRenamer(unused):
    MaterialRenamer.MaterialRenamer()


def I3DGetComponentShader(unused):
    getComponentShader.getComponentShader()


def I3DCleanupUVSet(unused):
    nodes = cmds.ls(sl=True, o=True, long=True)
    uvMap = cmds.textField(UI_CONTROL_STRING_UVSET_NAME, q=True, text=True)

    if uvMap != '':
        if not nodes is None:
            for node in nodes:
                cmds.select(node)
                nodeName = cmds.listRelatives(node)[0]
                cmds.polyUVSet(node + '|' + nodeName, currentUVSet=True, uvSet=uvMap)
                cmds.polyCopyUV(node, uvSetNameInput='', uvSetName='map1', ch=False)
                cmds.select(node)
                cmds.polyUVSet(node + '|' + nodeName, currentUVSet=True, uvSet=uvMap)
                cmds.polyUVSet(delete=True)


def I3DCombineMeshes(unused):
    nodes = cmds.ls(sl=True, o=True, l=True)
    if len(nodes) < 2:
        I3DShowWarning('You need to select at least 2 meshes!')
        return

    firstNode = nodes[0]

    parent = I3DUtils.getParent(firstNode)
    index = 0
    if not parent is None:
        index = I3DUtils.getCurrentNodeIndex(firstNode)
        firstNode = cmds.parent(firstNode, w=True)[0]
        nodes[0] = firstNode

    placeholder = cmds.group(em=True, name='placeholder', parent=firstNode)
    placeholder = cmds.parent(placeholder, w=True)

    newMesh = cmds.polyUnite(*nodes, name=firstNode, mergeUVSets=True, ch=False)
    newMesh = cmds.parent(newMesh, placeholder)
    worldPivots = cmds.xform(placeholder, q=True, ws=True, scalePivot=True)
    cmds.xform(newMesh, worldSpace=True, preserve=True, pivots=worldPivots)
    cmds.makeIdentity(newMesh, apply=True, t=True, r=True, s=True, n=False)
    newMesh = cmds.parent(newMesh, w=True)
    cmds.delete(placeholder)

    I3DRemoveNodeFromDisplayLayer(newMesh)


def I3DSelectIndex(unused):
    indexPath = cmds.textField(UI_CONTROL_STRING_NODE_INDEX, q=True, text=True)
    object = I3DUtils.getObjectByIndex(indexPath)
    if not object is None:
        cmds.select(object)


# rotate the object and the mesh, such that the local z-axis points towards to given point
def I3DAlignNegativeZAxis(unused):
    I3DAlignZAxis(-1)


def I3DAlignZAxis(direction):
    I3DFreezeToPivot(None)

    nodes = cmds.ls(sl=True, o=True)
    if len(nodes) != 2:
        I3DShowWarning('You need to select a mesh and a target point!')
        return

    I3DAlignZAxisToTargetPoint(nodes[0], nodes[1], direction)


def I3DAlignZAxisToManipulator(direction):
    I3DFreezeToPivot(None)

    nodes = I3DUtils.getSelectedObjects()

    objs = cmds.filterExpand(ex=True, sm=12)
    isValidSelection = not objs is None and len(objs) > 0
    if (not isValidSelection):
        objs = cmds.filterExpand(ex=True, sm=31)
        isValidSelection = not objs is None and len(objs) > 0
        if (not isValidSelection):
            objs = cmds.filterExpand(ex=True, sm=32)
            isValidSelection = not objs is None and len(objs) > 0
            if (not isValidSelection):
                objs = cmds.filterExpand(ex=True, sm=34)
                isValidSelection = not objs is None and len(objs) > 0
    if (isValidSelection):
        origObjShape = cmds.listRelatives(objs[0], p=True, pa=True)
        origObj = cmds.listRelatives(origObjShape, p=True, pa=True)
        rotationNode = origObj[0]

        cmds.setToolTo('moveSuperContext')
        result = cmds.manipMoveContext('Move', q=True, p=True)
        targetPosition = I3DUtils.linearInternalToUIVector(result)
        targetPoint = cmds.group(em=True, w=True)
        cmds.move(targetPosition[0], targetPosition[1], targetPosition[2], targetPoint, a=True, ws=True, moveXYZ=True)

        I3DAlignZAxisToTargetPoint(rotationNode, targetPoint, direction)


def I3DAlignZAxisToTargetPoint(rotationNode, targetPoint, direction):
    targetPosition = I3DUtils.linearUIToInternalVector(cmds.xform(targetPoint, q=True, t=True, ws=True))

    node = cmds.group(em=True, w=True)
    position = cmds.xform(rotationNode, q=True, t=True, ws=True)
    cmds.move(position[0], position[1], position[2], node, a=True, ws=True, moveXYZ=True)
    nodeMatrix = cmds.xform(node, q=True, m=True)
    invNodeMatrix = I3DUtils.invertTransformationMatrix(nodeMatrix)

    localTargetPosition = I3DUtils.transformPoint(targetPosition, invNodeMatrix)
    localTargetPosition[1] = 0

    zAxis = [0, 0, 1]
    if direction == -1:
        zAxis = [0, 0, -1]

    localTargetPositionLength = I3DUtils.vectorLength(localTargetPosition)

    if localTargetPositionLength > 0:
        yAngle = math.acos(I3DUtils.vectorDot(localTargetPosition, zAxis) / localTargetPositionLength)
        yAngle = I3DUtils.angleInternalToUI(yAngle)
        diffCrossZ = I3DUtils.vectorCross(localTargetPosition, zAxis)
        if diffCrossZ[1] > 0:
            yAngle = -yAngle
        cmds.rotate(0, yAngle, 0, node, r=True, os=True)

    nodeMatrix = cmds.xform(node, q=True, m=True)
    invNodeMatrix = I3DUtils.invertTransformationMatrix(nodeMatrix)

    localTargetPosition = I3DUtils.transformPoint(targetPosition, invNodeMatrix)
    localTargetPosition[0]
    localTargetPositionLength = I3DUtils.vectorLength(localTargetPosition)
    if localTargetPositionLength > 0:
        xAngle = math.acos(I3DUtils.vectorDot(localTargetPosition, zAxis) / localTargetPositionLength)
        xAngle = I3DUtils.angleInternalToUI(xAngle)
        diffCrossZ = I3DUtils.vectorCross(localTargetPosition, zAxis)
        if diffCrossZ[0] > 0:
            xAngle = -xAngle
        cmds.rotate(xAngle, 0, 0, node, r=True, os=True)

    currentParents = cmds.listRelatives(rotationNode, p=True, pa=True)
    currentParent = None
    nodeOrder = 0

    if not currentParents is None:
        currentParent = currentParents[0]
        currentParentChildren = cmds.listRelatives(currentParent, c=True, pa=True)
        if not currentParentChildren is None:
            for child in currentParentChildren:
                if child == rotationNode:
                    break
                nodeOrder = nodeOrder + 1

    newNames = cmds.parent(rotationNode, node)
    newName = newNames[0]
    cmds.makeIdentity(newName, apply=True, t=False, r=True, s=False, n=False)

    if not currentParent is None:
        names = cmds.parent(newName, currentParent)
        name = names[0]

        currentParentChildren = cmds.listRelatives(currentParent, c=True, pa=True)
        newNodeOrder = 0

        for child in currentParentChildren:
            if child == name:
                break
            newNodeOrder = newNodeOrder + 1

        if newNodeOrder != nodeOrder:
            cmds.reorder(name, relative=(nodeOrder - newNodeOrder))
    else:
        cmds.parent(newName, w=True)

    cmds.delete(node)


def I3DCreateSkeleton(unused):
    global SETTINGS_SKELETONS

    skeletonIndex = cmds.optionMenu(UI_OPTIONS_SKELETONS, query=True, sl=True)

    skeleton = SETTINGS_SKELETONS[skeletonIndex - 1]
    if not skeleton is None:
        skeleton['func'](None)
    return


def I3DCreateSkelNode(name, parent, displayHandle=False, translation=[0, 0, 0], rotation=['0', '0', '0']):
    node = cmds.group(em=True, name=name, parent=parent)
    if displayHandle:
        I3DSetDisplayHandle(node, 1)

    cmds.move(translation[0], translation[1], translation[2], node)
    cmds.rotate(rotation[0], rotation[1], rotation[2], node)

    return node


def I3DCreateBaseVehicle(unused):
    vehicle = I3DCreateBaseVec(False)
    cmds.select(vehicle)
    return


def I3DCreateBaseHarvester(unused):
    vehicle = I3DCreateBaseVec(True)
    cmds.select(vehicle)
    return


def I3DCreateAttacherJoints(unused):
    return I3DCreateVehicleAttacherJoints(False)


def I3DCreateBaseVec(isHarvester):
    vehicle = cmds.group(em=True, name='vehicleName_main_component1')
    vehicle_vis = cmds.group(em=True, name='vehicleName_vis', parent=vehicle)

    I3DCreateSkelNode("wheels", vehicle_vis)

    cameras = ""
    if isHarvester:
        cameras = I3DCreateCamerasHarvester(None)
    else:
        cameras = I3DCreateCamerasVehicle(None)
    cameras = cmds.parent(cameras, vehicle_vis)[0]

    cmds.parent(I3DCreateLights(None), vehicle_vis)[0]

    I3DCreateSkelNode("exitPoint", vehicle_vis, True)

    cabin = I3DCreateSkelNode("cabin_REPLACE_WITH_MESH", vehicle_vis)
    steeringBase = I3DCreateSkelNode("steeringBase", cabin)
    steeringWheel = I3DCreateSkelNode("steeringWheel_REPLACE_WITH_MESH", steeringBase)
    I3DCreateSkelNode("playerRightHandTarget", steeringWheel, True, [-0.188, 0.03, -0.022],
                      ['-10.518deg', '-4.708deg', '51.12deg'])
    I3DCreateSkelNode("playerLeftHandTarget", steeringWheel, True, [0.189, 0.03, -0.023],
                      ['-10.518deg', '-4.708deg', '-51.12deg'])

    seat = I3DCreateSkelNode("seat_REPLACE_WITH_MESH", cabin)
    I3DCreateSkelNode("playerSkin", seat, True)
    I3DCreateSkelNode("lights", cabin)
    I3DCreateSkelNode("wipers", cabin)
    I3DCreateSkelNode("dashboards", cabin)
    I3DCreateSkelNode("pedals", cabin)
    characterTargets = I3DCreateSkelNode("characterTargets", cabin, False)
    I3DCreateSkelNode("playerRightFootTarget", characterTargets, True)
    I3DCreateSkelNode("playerLeftFootTarget", characterTargets, True)
    I3DCreateSkelNode("mirrors", cabin)
    I3DCreateSkelNode("visuals", cabin)

    cmds.parent(I3DCreateVehicleAttacherJoints(isHarvester), vehicle_vis)

    ai = I3DCreateSkelNode("ai", vehicle_vis)
    I3DCreateSkelNode("aiCollisionTrigger_REPLACE_WITH_MESH", ai)
    exhaustParticles = None
    if isHarvester:
        exhaustParticles = I3DCreateSkelNode("particles", vehicle_vis)
    else:
        exhaustParticles = I3DCreateSkelNode("exhaustParticles", vehicle_vis)
    I3DCreateSkelNode("exhaustParticle1", exhaustParticles, True)
    I3DCreateSkelNode("exhaustParticle2", exhaustParticles, True)

    if isHarvester:
        I3DCreateSkelNode("movingParts", vehicle_vis)

    I3DCreateSkelNode("hydraulics", vehicle_vis)
    I3DCreateSkelNode("mirrors", vehicle_vis)
    I3DCreateSkelNode("configurations", vehicle_vis)

    if isHarvester:
        I3DCreateSkelNode("fillVolume", vehicle_vis)
        workAreas = I3DCreateSkelNode("workAreas", vehicle_vis)

        workAreaStraw = I3DCreateSkelNode("workAreaStraw", workAreas)
        I3DCreateSkelNode("workAreaStrawStart", workAreaStraw)
        I3DCreateSkelNode("workAreaStrawWidth", workAreaStraw)
        I3DCreateSkelNode("workAreaStrawHeight", workAreaStraw)

        workAreaChopper = I3DCreateSkelNode("workAreaChopper", workAreas)
        I3DCreateSkelNode("workAreaChopperStart", workAreaChopper)
        I3DCreateSkelNode("workAreaChopperWidth", workAreaChopper)
        I3DCreateSkelNode("workAreaChopperHeight", workAreaChopper)

    I3DCreateSkelNode("visuals", vehicle_vis)
    I3DCreateSkelNode("skinnedMeshes", vehicle)
    I3DCreateSkelNode("collisions", vehicle)

    return vehicle


def I3DCreateBaseTool(unused):
    tool = cmds.group(em=True, name='toolName_main_component1')

    vehicle_vis = I3DCreateSkelNode("toolName_vis", tool)

    attachable = I3DCreateSkelNode("attachable", vehicle_vis)
    I3DCreateSkelNode("attacherJoint", attachable)
    I3DCreateSkelNode("topReferenceNode", attachable)
    I3DCreateSkelNode("ptoInputNode", attachable)
    I3DCreateSkelNode("support", attachable)
    I3DCreateSkelNode("connectionHoses", attachable)
    I3DCreateSkelNode("wheelChocks", attachable)

    I3DCreateSkelNode("wheels", vehicle_vis)
    I3DCreateSkelNode("lights", vehicle_vis)
    I3DCreateSkelNode("movingParts", vehicle_vis)
    I3DCreateSkelNode("fillUnit", vehicle_vis)

    workArea = I3DCreateSkelNode("workArea", vehicle_vis)
    I3DCreateSkelNode("workAreaStart", workArea)
    I3DCreateSkelNode("workAreaWidth", workArea)
    I3DCreateSkelNode("workAreaHeight", workArea)

    I3DCreateSkelNode("effects", vehicle_vis)

    ai = I3DCreateSkelNode("ai", vehicle_vis)

    aiMarkers = I3DCreateSkelNode("aiMarkers", ai)
    I3DCreateSkelNode("aiMarkerLeft", aiMarkers)
    I3DCreateSkelNode("aiMarkerRight", aiMarkers)
    I3DCreateSkelNode("aiMarkerBack", aiMarkers)

    sizeMarkers = I3DCreateSkelNode("sizeMarkers", ai)
    I3DCreateSkelNode("sizeMarkerLeft", sizeMarkers)
    I3DCreateSkelNode("sizeMarkerRight", sizeMarkers)
    I3DCreateSkelNode("sizeMarkerBack", sizeMarkers)

    I3DCreateSkelNode("aiCollisionTrigger_TO_BE_REPLACED", ai)

    I3DCreateSkelNode("visuals", vehicle_vis)

    I3DCreateSkelNode("skinnedMeshes", tool)
    I3DCreateSkelNode("collisions", tool)

    return tool


def I3DCreatePlayer(steeringWheel):
    playerRoot = cmds.group(em=True, name='playerRoot')
    player_skin = cmds.group(em=True, name='playerSkin', parent=playerRoot)
    player_rightFoot = cmds.group(em=True, name='playerRightFootTarget', parent=playerRoot)
    player_leftFoot = cmds.group(em=True, name='playerLeftFootTarget', parent=playerRoot)

    cmds.move(-0.184, -0.514, 0.393, player_rightFoot)
    cmds.rotate('0', '-10deg', '0', player_rightFoot)
    cmds.move(0.184, -0.514, 0.393, player_leftFoot)
    cmds.rotate('0', '10deg', '0', player_leftFoot)
    I3DSetDisplayHandle(player_skin, 1)
    I3DSetDisplayHandle(player_rightFoot, 1)
    I3DSetDisplayHandle(player_leftFoot, 1)

    if not steeringWheel is None and not steeringWheel == False:
        rightHand = cmds.group(em=True, name='playerRightHandTarget', parent=steeringWheel)
        leftHand = cmds.group(em=True, name='playerLeftHandTarget', parent=steeringWheel)
        I3DSetDisplayHandle(rightHand, 1)
        I3DSetDisplayHandle(leftHand, 1)
        cmds.move(-0.188, 0.03, -0.022, rightHand)
        cmds.rotate('-10.518deg', '-4.708deg', '51.12deg', rightHand)
        cmds.move(0.189, 0.03, -0.023, leftHand)
        cmds.rotate('-10.518deg', '-4.708deg', '-51.12deg', leftHand)

    return playerRoot


def I3DSetDisplayHandle(node, value):
    cmds.setAttr(node + '.displayHandle', value)
    cmds.setAttr(node + '.displayLocalAxis', value)


def I3DCreateCamerasVehicle(unused):
    return I3DCreateCameras(60)


def I3DCreateCamerasHarvester(unused):
    return I3DCreateCameras(75)


def I3DCreateCameras(fov):
    cameraGroup = cmds.group(em=True, name='cameras')
    outdoorCameraGroup = cmds.group(em=True, name='outdoorCameraTarget', parent=cameraGroup)
    outdoorCamera = cmds.camera(nearClipPlane=0.3, farClipPlane=5000, name='outdoorCamera')
    outdoorCamTransfromGroup = cmds.parent(outdoorCamera[0], outdoorCameraGroup)[0]
    I3DSaveAttributeBool(outdoorCamTransfromGroup, 'i3D_collision', False)
    I3DSaveAttributeBool(outdoorCamTransfromGroup, 'i3D_static', False)
    cmds.move(0, 0, 11, outdoorCamera)
    indoorCamera = cmds.camera(nearClipPlane=0.1, farClipPlane=5000, hfv=fov, name='indoorCamera')
    camTransformGroup = cmds.parent(indoorCamera[0], cameraGroup)[0]
    I3DSaveAttributeBool(camTransformGroup, 'i3D_collision', False)
    I3DSaveAttributeBool(camTransformGroup, 'i3D_static', False)
    cmds.rotate('-18deg', '180deg', '0', camTransformGroup)

    cmds.group(em=True, name='cameraRaycastNode1', parent=cameraGroup)
    cmds.group(em=True, name='cameraRaycastNode2', parent=cameraGroup)
    cmds.group(em=True, name='cameraRaycastNode3', parent=cameraGroup)

    cmds.rotate('-24deg', '180deg', '0', outdoorCameraGroup)

    return cameraGroup


def I3DCreateLights(unused):
    lightsGroup = cmds.group(em=True, name='lights')

    cmds.group(em=True, name='sharedLights', parent=lightsGroup)
    cmds.group(em=True, name='staticLights', parent=lightsGroup)

    # default lights
    defaultLights = cmds.group(em=True, name='defaultLights', parent=lightsGroup)
    frontLightLow = I3DCreateLight('frontLightLow', defaultLights, 80, 20, 3, [0.85, 0.85, 1], 70)
    cmds.rotate('-15deg', '180deg', '0', frontLightLow)
    highBeamLow = I3DCreateLight('highBeamLow', defaultLights, 70, 30, 2, [0.85, 0.85, 1], 70)
    cmds.rotate('-10deg', '180deg', '0', highBeamLow)
    frontLightHigh = I3DCreateLight('frontLightHigh', defaultLights, 70, 25, 3, [0.85, 0.85, 1], 100)
    cmds.rotate('165deg', '8deg', '180deg', frontLightHigh)
    frontLightHigh1 = I3DCreateLight('frontLightHigh1', frontLightHigh, 70, 25, 3, [0.85, 0.85, 1], 100)
    cmds.rotate('0deg', '16deg', '0deg', frontLightHigh1)
    highBeamHigh = I3DCreateLight('highBeamHigh', defaultLights, 50, 35, 2.5, [0.85, 0.85, 1], 150)
    cmds.rotate('170deg', '5deg', '180deg', highBeamHigh)
    highBeamHigh1 = I3DCreateLight('highBeamHigh1', highBeamHigh, 50, 35, 2.5, [0.85, 0.85, 1], 150)
    cmds.rotate('0deg', '10deg', '0deg', highBeamHigh1)
    workLights = cmds.group(em=True, name='workLights', parent=lightsGroup)

    # work lights front
    workLightFrontLow = I3DCreateLight('workLightFrontLow', workLights, 130, 20, 2, [0.85, 0.85, 1], 50)
    cmds.rotate('-20deg', '180deg', '0deg', workLightFrontLow)
    workLightFrontHigh1 = I3DCreateLight('workLightFrontHigh1', workLights, 90, 25, 2, [0.85, 0.85, 1], 50)
    cmds.rotate('-15deg', '155deg', '0deg', workLightFrontHigh1)
    workLightFrontHigh2 = I3DCreateLight('workLightFrontHigh2', workLightFrontHigh1, 90, 25, 2, [0.85, 0.85, 1], 50)
    cmds.rotate('0deg', '50deg', '0deg', workLightFrontHigh2)

    # work lights back
    workLightBackLow = I3DCreateLight('workLightBackLow', workLights, 130, 20, 2, [0.85, 0.85, 1], 50)
    cmds.rotate('-20deg', '0deg', '0deg', workLightBackLow)
    workLightBackHigh1 = I3DCreateLight('workLightBackHigh1', workLights, 90, 25, 2, [0.85, 0.85, 1], 50)
    cmds.rotate('-20deg', '-20deg', '0deg', workLightBackHigh1)
    workLightBackHigh2 = I3DCreateLight('workLightBackHigh2', workLightBackHigh1, 90, 25, 2, [0.85, 0.85, 1], 50)
    cmds.rotate('0deg', '40deg', '0deg', workLightBackHigh2)

    # back lights
    backLights = cmds.group(em=True, name='backLights', parent=lightsGroup)
    backLightsHigh1 = I3DCreateLight('backLightsHigh1', backLights, 130, 2.5, 2, [0.5, 0, 0], 15)
    cmds.rotate('-15deg', '20deg', '0deg', backLightsHigh1)
    backLightsHigh2 = I3DCreateLight('backLightsHigh2', backLightsHigh1, 130, 2.5, 2, [0.5, 0, 0], 15)
    cmds.rotate('0deg', '-40deg', '0deg', backLightsHigh2)

    # turn lights
    turnLights = cmds.group(em=True, name='turnLights', parent=lightsGroup)
    turnLightLeftFront = I3DCreateLight('turnLightLeftFront', turnLights, 120, 4, 3, [0.31, 0.14, 0], 20)
    cmds.rotate('0deg', '185deg', '0deg', turnLightLeftFront)
    turnLightLeftBack = I3DCreateLight('turnLightLeftBack', turnLightLeftFront, 120, 4, 3, [0.31, 0.14, 0], 20)
    cmds.rotate('-8deg', '165deg', '0deg', turnLightLeftBack)
    turnLightRightFront = I3DCreateLight('turnLightRightFront', turnLights, 120, 4, 3, [0.31, 0.14, 0], 20)
    cmds.rotate('0deg', '175deg', '0deg', turnLightRightFront)
    turnLightRightBack = I3DCreateLight('turnLightRightBack', turnLightRightFront, 120, 4, 3, [0.31, 0.14, 0], 20)
    cmds.rotate('-8deg', '195deg', '0deg', turnLightRightBack)

    # beacon lights
    beaconLights = cmds.group(em=True, name='beaconLights', parent=lightsGroup)
    cmds.group(em=True, name='beaconLight1', parent=beaconLights)

    # reverse lights
    reverseLights = cmds.group(em=True, name='reverseLights', parent=lightsGroup)
    reverseLight = I3DCreateLight('reverseLight', reverseLights, 150, 5, 3, [0.9, 0.9, 1], 30)
    cmds.rotate('-15deg', '0deg', '0deg', reverseLight)

    cmds.select(lightsGroup)

    return lightsGroup


def I3DCreateLight(name, parent, coneAngle, intensity, dropOff, rgb, locatorScale=50, castShadowMap=False,
                   depthMapBias=0.001, depthMapResolution=256):
    light = cmds.spotLight(coneAngle=coneAngle, intensity=intensity, dropOff=dropOff, rgb=rgb)
    if castShadowMap and not depthMapBias is None and not depthMapResolution is None:
        cmds.setAttr(light + '.useDepthMapShadows', 1)
        cmds.setAttr(light + '.dmapResolution', depthMapResolution)
        cmds.setAttr(light + '.dmapBias', depthMapBias)

    cmds.setAttr(light + '.locatorScale', locatorScale)
    parents = cmds.listRelatives(light, fullPath=True, parent=True)
    I3DSaveAttributeBool(parents[0], 'i3D_collision', False)
    I3DSaveAttributeBool(parents[0], 'i3D_static', False)
    I3DSaveAttributeFloat(parents[0], 'i3D_clipDistance', 75.0)
    lightTransform = cmds.parent(parents[0], parent)[0]
    lightTransform = cmds.rename(lightTransform, name)
    cmds.setAttr(lightTransform + '.lodVisibility', 1)
    return lightTransform


def I3DCreateVehicleAttacherJoints(isHarvester):
    attacherJointGroup = cmds.group(em=True, name='attacherJoints')
    tools = cmds.group(em=True, name='tools', parent=attacherJointGroup)
    trailers = cmds.group(em=True, name='trailers', parent=attacherJointGroup)
    ptos = cmds.group(em=True, name='ptos', parent=attacherJointGroup)
    cmds.group(em=True, name='connectionHoses', parent=attacherJointGroup)

    if not isHarvester:
        # attacherjointbackrot
        attacherJointBackRot = cmds.group(em=True, name='attacherJointBackRot', parent=tools)
        attacherJointBackRot2 = cmds.group(em=True, name='attacherJointBackRot2', parent=attacherJointBackRot)
        attacherJointBack = cmds.group(em=True, name='attacherJointBack', parent=attacherJointBackRot2)
        I3DSetDisplayHandle(attacherJointBack, 1)
        cmds.xform(attacherJointBack, a=True, ro=['0', '90deg', '0'])
        cmds.xform(attacherJointBackRot2, r=True, ro=['13deg', '0', '0'])
        cmds.move(0, 0, -1, attacherJointBackRot2)
        cmds.xform(attacherJointBackRot, r=True, ro=['-13deg', '0', '0'])

        # attacherjointbackbottomarm
        attacherJointBackArmBottom = cmds.group(em=True, name='attacherJointBackArmBottom', parent=tools)
        lowerLink = cmds.group(em=True, name='lowerLink_REPLACE_WITH_MESH', parent=attacherJointBackArmBottom)
        referencePointBackBottom = cmds.group(em=True, name='referencePointBackBottom', parent=lowerLink)
        cmds.move(0, 0, -1, referencePointBackBottom)
        cmds.rotate('-13deg', '0', '0', attacherJointBackArmBottom)

        # attacherjointbacktoparm
        attacherJointBackArmTop = cmds.group(em=True, name='attacherJointBackArmTop', parent=tools)
        cmds.rotate('67deg', '0', '0', attacherJointBackArmTop)

    # attacherjointfrontrot
    attacherJointFrontRot = cmds.group(em=True, name='attacherJointFrontRot', parent=tools)
    attacherJointFrontRot2 = cmds.group(em=True, name='attacherJointFrontRot2', parent=attacherJointFrontRot)
    attacherJointFront = cmds.group(em=True, name='attacherJointFront', parent=attacherJointFrontRot2)
    I3DSetDisplayHandle(attacherJointFront, 1)
    cmds.xform(attacherJointFront, a=True, ro=['0', '-90deg', '0'])
    cmds.xform(attacherJointFrontRot2, r=True, ro=['13deg', '0', '0'])
    cmds.move(0, 0, 1, attacherJointFrontRot2)
    cmds.xform(attacherJointFrontRot, r=True, ro=['-13deg', '0', '0'])

    # attacherjointfrontbottomarm
    attacherJointFrontArmBottom = cmds.group(em=True, name='attacherJointFrontArmBottom', parent=tools)
    lowerLinkFront = cmds.group(em=True, name='lowerLinkFront_REPLACE_WITH_MESH', parent=attacherJointFrontArmBottom)
    referencePointFrontBottom = cmds.group(em=True, name='referencePointFrontBottom', parent=lowerLinkFront)
    cmds.move(0, 0, 1, referencePointFrontBottom)
    cmds.rotate('-26deg', '0', '0', attacherJointFrontArmBottom)

    # attacherjointfronttoparm
    attacherJointFrontArmTop = cmds.group(em=True, name='attacherJointFrontArmTop', parent=tools)
    cmds.rotate('-40deg', '0', '0', attacherJointFrontArmTop)
    I3DSetDisplayHandle(attacherJointFrontArmTop, 1)

    # trailer joints
    trailerAttacherJointBack = cmds.group(em=True, name='trailerAttacherJointBack', parent=trailers)
    cmds.rotate('0', '90deg', '0', trailerAttacherJointBack)
    I3DSetDisplayHandle(trailerAttacherJointBack, 1)

    if not isHarvester:
        trailerAttacherJointBackLow = cmds.group(em=True, name='trailerAttacherJointBackLow', parent=trailers)
        cmds.rotate('0', '90deg', '0', trailerAttacherJointBackLow)
        I3DSetDisplayHandle(trailerAttacherJointBackLow, 1)

    if not isHarvester:
        trailerAttacherJointFront = cmds.group(em=True, name='trailerAttacherJointFront', parent=trailers)
        cmds.rotate('0', '-90deg', '0', trailerAttacherJointFront)
        I3DSetDisplayHandle(trailerAttacherJointFront, 1)

    # ptos
    if not isHarvester:
        ptoBack = cmds.group(em=True, name='ptoBack', parent=ptos)
        cmds.rotate('0', '180deg', '0', ptoBack)
        I3DSetDisplayHandle(ptoBack, 1)

    ptoFront = cmds.group(em=True, name='ptoFront', parent=ptos)
    I3DSetDisplayHandle(ptoFront, 1)

    if not isHarvester:
        frontloader = cmds.group(em=True, name='frontloader', parent=attacherJointGroup)
        cmds.rotate('0', '0deg', '0', frontloader)
        I3DSetDisplayHandle(frontloader, 1)

    return attacherJointGroup


def I3DFreezeAll(unused):
    I3DFreeze(True, True, True)


def I3DFreezeTranslation(unused):
    nodes = cmds.ls(sl=True, o=True)
    if (len(nodes) == 0):
        I3DShowWarning('Nothing selected!')
        return

    for node in nodes:
        worldPivots = [0, 0, 0]

        parent = I3DUtils.getParent(node)
        if not parent is None:
            worldPivots = cmds.xform(parent, q=True, ws=True, scalePivot=True)

        cmds.xform(node, worldSpace=True, preserve=True, pivots=worldPivots)
        I3DFreezeToPivot(None)


def I3DFreezeRotation(unused):
    I3DFreeze(False, True, False)


def I3DFreezeScale(unused):
    I3DFreeze(False, False, True)


def I3DFreeze(t, r, s):
    nodes = cmds.ls(sl=True, o=True)
    if (len(nodes) == 0):
        I3DShowWarning('Nothing selected!')
        return

    if cmds.about(version=True) == '2016':
        cmds.makeIdentity(apply=True, t=t, r=r, s=s, n=False, pn=True);
    else:
        cmds.makeIdentity(apply=True, t=t, r=r, s=s, n=False);

    I3DFreezeToPivot(None)


def I3DClearOptionMenu(optionMenu):
    menuItems = cmds.optionMenu(optionMenu, q=True, itemListLong=True)
    if menuItems:
        cmds.deleteUI(menuItems)


def I3DUpdateShaderList(root):
    global SETTINGS_SHADERS
    I3DClearOptionMenu(UI_OPTIONS_PREDEFINED_SHADER_ATTRIBUTES)
    shaderFiles = I3DUtils.getFilesInDir(root, '*Shader*.xml')
    if not shaderFiles is None:
        SETTINGS_SHADERS = []
        cmds.setParent(UI_OPTIONS_PREDEFINED_SHADER_ATTRIBUTES, menu=True)
        firstShader = ''
        for shader in shaderFiles:
            shaderClean = shader.replace(root, '')
            if firstShader == '':
                firstShader = shaderClean
            I3DParseShader(SETTINGS_SHADERS, shaderClean, root, shader)
            cmds.menuItem(label=shaderClean)

        if firstShader != '':
            I3DUpdateShaderUI(firstShader)
    return


def I3DParseShader(data, name, rootPath, shaderPath):
    shaderInfo = I3DUtils.getShaderInfo(rootPath + '/' + shaderPath)
    data.append({'name': name, 'info': shaderInfo, })
    return


def I3DUpdateShaderUI(selectedItemName):
    shaderInfo = None

    for shader in SETTINGS_SHADERS:
        if shader['name'] == selectedItemName:
            shaderInfo = shader['info']
            break

    if shaderInfo is None:
        return

    if not SETTINGS_SHADER_PARAMETERS is None:
        for k in SETTINGS_SHADER_PARAMETERS.keys():
            if cmds.formLayout(SETTINGS_SHADER_PARAMETERS[k]['layout'], exists=True):
                cmds.deleteUI(SETTINGS_SHADER_PARAMETERS[k]['layout'])
            del SETTINGS_SHADER_PARAMETERS[k]
    if not SETTINGS_SHADER_TEXTURES is None:
        for k in SETTINGS_SHADER_TEXTURES.keys():
            if cmds.formLayout(SETTINGS_SHADER_TEXTURES[k]['layout'], exists=True):
                cmds.deleteUI(SETTINGS_SHADER_TEXTURES[k]['layout'])
            del SETTINGS_SHADER_TEXTURES[k]
    if not SETTINGS_SHADER_VARIATIONS is None:
        for k in SETTINGS_SHADER_VARIATIONS.keys():
            if cmds.menuItem(SETTINGS_SHADER_VARIATIONS[k], exists=True):
                cmds.deleteUI(SETTINGS_SHADER_VARIATIONS[k])
            del SETTINGS_SHADER_VARIATIONS[k]

    if 'parameters' in shaderInfo:
        for v in shaderInfo['parameters']:
            name = v['name']
            layout = cmds.formLayout('shaderSettingsParams' + name, parent=UI_CONTROL_PARAMETERS)
            checkbox = cmds.checkBox(label="", h=20, parent=layout)
            text = cmds.text(label=name, h=20, parent=layout)
            textField = cmds.textField(text=v['defaultValue'], h=20, w=230, parent=layout)
            cmds.formLayout(layout, edit=True, attachForm=(
                (checkbox, 'left', 0), (text, 'left', 20), (textField, 'left', 190), (textField, 'right', 0)))
            SETTINGS_SHADER_PARAMETERS[name] = {'layout': layout, 'checkbox': checkbox, 'textField': textField}

    if 'textures' in shaderInfo:
        for k, v in shaderInfo['textures'].iteritems():
            layout = cmds.formLayout('shaderSettingsTexture' + k, parent=UI_CONTROL_TEXTURES_SCROLL)
            checkbox = cmds.checkBox(label="", h=20, parent=layout)
            text = cmds.text(label=v['name'], h=20, parent=layout)
            textField = cmds.textField(text=v['defaultFilename'], h=20, w=230, parent=layout)
            cmds.formLayout(layout, edit=True, attachForm=(
                (checkbox, 'left', 0), (text, 'left', 20), (textField, 'left', 190), (textField, 'right', 0)))
            SETTINGS_SHADER_TEXTURES[k] = {'layout': layout, 'checkbox': checkbox, 'textField': textField}

    if 'variations' in shaderInfo:
        firstItem = cmds.menuItem(parent=UI_CONTROL_MENU_VARIATIONS, label='None')
        index = 1
        for k, v in shaderInfo['variations'].iteritems():
            menuItem = cmds.menuItem(parent=UI_CONTROL_MENU_VARIATIONS, label=k)
            SETTINGS_SHADER_VARIATIONS[index] = menuItem
            index = index + 1
        SETTINGS_SHADER_VARIATIONS[index + 1] = firstItem


def I3DGetNodeShaders():
    # get selected nodes:
    nodes = cmds.ls(selection=True, dag=True)
    shadingGroups = []
    shaders = []

    # get shading groups from shapes:
    if len(nodes) >= 1:
        shadingGroups = cmds.listConnections(nodes, t='shadingEngine')
    # get the shaders:
    if len(shadingGroups) >= 1:
        shaders = cmds.ls(cmds.listConnections(shadingGroups), materials=1)

    # this makes sure that if we've only selected a shader, the button will still work
    if len(shaders) == 0:
        nodes = cmds.ls(selection=True)
        for node in nodes:
            if cmds.nodeType(node, inherited=True)[0] == 'shadingDependNode':
                shaders.append(node)

    # graph shaders to the network in the hypershade:
    if shaders >= 1:
        cmds.hyperShade(shaders)

    return shaders


def I3DGetRelativePath(shaderName):
    mayaFilePath = os.path.dirname(cmds.file(q=True, sn=True))
    mayaFilePath = str(mayaFilePath.replace('\\', '/'))
    shaderName = str(shaderName.replace('\\', '/'))
    shaderPath = os.path.dirname(PROJECT_PATH + shaderName)
    shaderPath = shaderPath.replace('\\', '/')
    if mayaFilePath == '':
        mayaFilePath = shaderPath
    relPath = I3DUtils.getRelativePath(shaderPath, mayaFilePath)
    finalPath = shaderName
    if relPath != '.':
        finalPath = relPath + shaderName
    if finalPath.startswith('/'):
        finalPath = finalPath[1:]

    return finalPath


def I3DSetShader(unused):
    shaderName = cmds.optionMenu(UI_OPTIONS_PREDEFINED_SHADER_ATTRIBUTES, query=True, value=True)
    if shaderName == '' or shaderName is None:
        return

    root = cmds.textField(UI_CONTROL_STRING_SHADER_PATH, query=True, text=True)

    shaderPath = I3DUtils.getRelativeShaderPath(root + '/' + shaderName)

    shaders = I3DGetNodeShaders()

    for shader in shaders:
        cmds.select(shader)
        currentAttributes = cmds.listAttr(str(shader), userDefined=True)

        # delete all attributes
        if not currentAttributes is None:
            for attr in currentAttributes:
                cmds.deleteAttr(str(shader) + '.' + str(attr))

        cmds.addAttr(dt='string', shortName='customShader', niceName='customShader', longName='customShader')
        cmds.setAttr(str(shader) + '.customShader', shaderPath, type='string')

        for k, v in SETTINGS_SHADER_PARAMETERS.iteritems():
            if cmds.checkBox(v['checkbox'], query=True, value=True):
                name = 'customParameter_' + k
                value = cmds.textField(v['textField'], query=True, text=True)
                cmds.addAttr(dt='string', shortName=name, niceName=name, longName=name)
                cmds.setAttr(str(shader) + '.' + name, value, type='string')

        for k, v in SETTINGS_SHADER_TEXTURES.iteritems():
            if cmds.checkBox(v['checkbox'], query=True, value=True):
                name = 'customTexture_' + k
                value = cmds.textField(v['textField'], query=True, text=True)
                cmds.addAttr(dt='string', shortName=name, niceName=name, longName=name)
                cmds.setAttr(str(shader) + '.' + name, value, type='string')

        if not SETTINGS_SHADER_VARIATIONS is None:
            variation = cmds.optionMenu(UI_CONTROL_MENU_VARIATIONS, query=True, value=True)
            if not variation is None and variation != 'None':
                cmds.addAttr(dt='string', shortName='customShaderVariation', niceName='customShaderVariation',
                             longName='customShaderVariation')
                cmds.setAttr(str(shader) + '.customShaderVariation', variation, type='string')


def I3DShowWarning(text):
    if hasattr(cmds, 'warning'):
        cmds.warning(text)
    else:
        print(text)


def I3DSetupMirrorAxis(unused):
    nodes = cmds.ls(selection=True, l=True, tr=True)

    for node in nodes:
        I3DDoFreezeToPivot(node)

    if len(nodes) != 3:
        I3DShowWarning('You need to select 3 nodes (camera, mirror, target) !')
        return

    camera = nodes[0]
    mirror = nodes[1]
    target = nodes[2]

    mirrorParent = I3DUtils.getParent(mirror)
    mirrorIndex = I3DUtils.getCurrentNodeIndex(mirror)

    mirrorAxisTarget = cmds.group(em=True, w=True)
    targetMirror = cmds.group(em=True, w=True)

    cameraPos = cmds.xform(camera, q=True, ws=True, t=True)
    mirrorPos = cmds.xform(mirror, q=True, ws=True, t=True)
    targetPos = cmds.xform(target, q=True, ws=True, t=True)

    v1 = I3DUtils.vectorNorm([mirrorPos[0] - cameraPos[0], mirrorPos[1] - cameraPos[1], mirrorPos[2] - cameraPos[2]])
    v2 = I3DUtils.vectorNorm([mirrorPos[0] - targetPos[0], mirrorPos[1] - targetPos[1], mirrorPos[2] - targetPos[2]])

    v3 = [v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2]]

    cmds.move(mirrorPos[0], mirrorPos[1], mirrorPos[2], targetMirror, absolute=True, worldSpace=True)
    cmds.move(mirrorPos[0] - v3[0], mirrorPos[1] - v3[1], mirrorPos[2] - v3[2], mirrorAxisTarget, absolute=True,
              worldSpace=True)

    cmds.select(mirrorAxisTarget, targetMirror)
    constrain = cmds.aimConstraint(offset=[0, 0, 0], weight=1, aimVector=[0, 1, 0], upVector=[0, 0, 1],
                                   worldUpType='vector', worldUpVector=[0, 1, 0]);

    mirror = cmds.parent(mirror, targetMirror)[0]

    cmds.makeIdentity(mirror, apply=True, t=False, r=True, s=False, n=False)

    if not mirrorParent is None:
        mirror = cmds.parent(mirror, mirrorParent)[0]
    else:
        mirror = cmds.parent(mirror, w=True)[0]

    newMirrorIndex = I3DUtils.getCurrentNodeIndex(mirror)

    cmds.reorder(mirror, relative=(mirrorIndex - newMirrorIndex))

    cmds.delete(constrain)
    cmds.delete(targetMirror)
    cmds.delete(mirrorAxisTarget)


def I3DUpdateLayers(node):
    I3DRemoveNodeFromDisplayLayer(node)

    mergeGroup = I3DGetAttributeValue(node, 'i3D_mergeGroup', 0)
    layer = I3DCreateDisplayLayer('MERGEGROUP_' + str(mergeGroup), mergeGroup)
    I3DAddNodeToDisplayLayer(node, layer)


def I3DAddNodeToDisplayLayer(node, layer):
    cmds.editDisplayLayerMembers(layer, node, noRecurse=True)


def I3DRemoveNodeFromDisplayLayer(node):
    cmds.editDisplayLayerMembers("defaultLayer", node, noRecurse=True)


def I3DCreateDisplayLayer(name, mergeGroup):
    displayLayers = cmds.ls(name, type='displayLayer')
    if not len(displayLayers):
        colorIndex = 4
        if mergeGroup == 1:
            colorIndex = 2
        elif mergeGroup == 2:
            colorIndex = 3
        elif mergeGroup == 3:
            colorIndex = 7
        elif mergeGroup == 4:
            colorIndex = 24
        elif mergeGroup == 5:
            colorIndex = 25
        elif mergeGroup == 6:
            colorIndex = 28
        elif mergeGroup == 7:
            colorIndex = 29
        elif mergeGroup == 8:
            colorIndex = 30
        elif mergeGroup == 9:
            colorIndex = 31

        cmds.createDisplayLayer(name=name, number=1, empty=True)
        cmds.setAttr(name + '.displayType', 0)
        cmds.setAttr(name + '.color', colorIndex)
        # cmds.setAttr(name+'.overrideRGBColors', 0)
    return name


def I3DGetIsVisible(node):
    if not cmds.getAttr(node + '.visibility'):
        return False
    else:
        parent = I3DUtils.getParent(node)
        if not parent is None:
            return I3DGetIsVisible(parent)

    return True


def I3DFindCompound(node):
    if node is None:
        return None

    isCompound = I3DGetAttributeValue(node, 'i3D_compound', False)
    if isCompound:
        return node
    else:
        parentNode = I3DUtils.getParent(node)
        if not parentNode is None:
            return I3DFindCompound(parentNode)
        else:
            return None


def I3DGetCompoundMass(node, isCompoundNode):
    if node is None:
        return 0

    mass = 0

    isDynamic = I3DGetAttributeValue(node, 'i3D_dynamic', False)
    isCompound = I3DGetAttributeValue(node, 'i3D_compound', False)
    isCompoundChild = I3DGetAttributeValue(node, 'i3D_compoundChild', False)

    if isDynamic and (isCompoundNode and isCompound) or (not isCompoundNode and isCompoundChild):
        mass = I3DUtils.getMeshVolume(node) * I3DGetAttributeValue(node, 'i3D_density', 0)

    children = cmds.listRelatives(node, type='transform', fullPath=True)
    if not children is None:
        for child in children:
            mass = mass + I3DGetCompoundMass(child, False)

    return mass


def I3DUpdateMass(node):
    isDynamic = I3DGetAttributeValue(node, 'i3D_dynamic', False)
    cmds.text(UI_CONTROL_LABEL_MASS, edit=True, visible=isDynamic)
    cmds.floatField(UI_CONTROL_FLOAT_MASS, edit=True, visible=isDynamic)
    cmds.textField(UI_CONTROL_STRING_MASS_NODE, edit=True, visible=isDynamic)
    if isDynamic:
        compoundNode = node

        isCompound = I3DGetAttributeValue(node, 'i3D_compound', False)
        if not isCompound:
            compoundNode = I3DFindCompound(node)
        if not compoundNode is None:
            cmds.textField(UI_CONTROL_STRING_MASS_NODE, edit=True, text=compoundNode)
            mass = I3DGetCompoundMass(compoundNode, True)
            cmds.floatField(UI_CONTROL_FLOAT_MASS, edit=True, value=mass)
        else:
            cmds.textField(UI_CONTROL_STRING_MASS_NODE, edit=True, text='Compound-Node not found!')
            return


SETTINGS_SKELETONS = []
SETTINGS_SKELETONS.append({'name': 'Tractor', 'func': I3DCreateBaseVehicle})
SETTINGS_SKELETONS.append({'name': 'Combine', 'func': I3DCreateBaseHarvester})
SETTINGS_SKELETONS.append({'name': 'Tool', 'func': I3DCreateBaseTool})
SETTINGS_SKELETONS.append({'name': 'Attacher Joints', 'func': I3DCreateAttacherJoints})
SETTINGS_SKELETONS.append({'name': 'Player', 'func': I3DCreatePlayer})
SETTINGS_SKELETONS.append({'name': 'Lights', 'func': I3DCreateLights})
SETTINGS_SKELETONS.append({'name': 'Cameras (Tractor)', 'func': I3DCreateCamerasVehicle})
SETTINGS_SKELETONS.append({'name': 'Cameras (Combine)', 'func': I3DCreateCamerasHarvester})
