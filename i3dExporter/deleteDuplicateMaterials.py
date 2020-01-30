#-----------------------------------------------------------------------------------
#
#   SCRIPT      deleteDuplicateMaterials.py
#   AUTHOR      Zaitsev Evgeniy
#               ev.zaitsev@gmail.com
#
#       import deleteDuplicateMaterials; deleteDuplicateMaterials.duplicateMaterials("simple")
#       or 
#       import deleteDuplicateMaterials; deleteDuplicateMaterials.duplicateMaterials("full")
#       
#-----------------------------------------------------------------------------------
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import os
DEBUG1 = False
DEBUG2 = False
DEBUG3 = False

class duplicateMaterials( object ):
    def __init__(self, m_state = "full" ):
        self.m_state = m_state
        self.m_sourceList = []
        self.m_destinationList = []
        self.m_needToDeleteList = []
        self.m_assignedShadingGroups = set()
        self._getAssignedShadingGroups()
        self._getSourceAndDestinationLists()
        self._deleteDuplicate()
        
    def _deleteDuplicate( self ):
        '''
        if DEBUG2: print( " ------------------------ ")
        for m_value in self.m_needToDeleteList :
            m_nodeConnected     = m_value[0]
            m_hash              = m_value[1]
            m_nodeSG            = m_value[2]
            m_nodeFnConnected   = OpenMaya.MFnDependencyNode( m_nodeConnected ) 
            m_nodeSGFn          = OpenMaya.MFnDependencyNode( m_nodeSG ) 
            m_index = self._getIndexFromDestinationList( m_hash ) 
            m_destinationValue  = self.m_destinationList[m_index]
            m_destinationNode   = m_destinationValue[0]
            m_destinationHash   = m_destinationValue[1]
            m_destinationSG     = m_destinationValue[2]
            m_destinationNodeFn = OpenMaya.MFnDependencyNode( m_destinationNode ) 
            m_destinationSGFn   = OpenMaya.MFnDependencyNode( m_destinationSG )
            if DEBUG2: print ( "{0:30} must be REPLACED by    {1}".format( m_nodeSGFn.name(), m_destinationSGFn.name() ) )
        '''
        if DEBUG3: print( " ------------------------ ")
        m_resultString =  "select -clear;\n"
        m_iterator = OpenMaya.MItDag( OpenMaya.MItDag.kDepthFirst )
        while not m_iterator.isDone():
            m_path = OpenMaya.MDagPath()
            m_iterator.getPath( m_path ) 
            if ( OpenMaya.MFn.kMesh == m_path.node().apiType() ):
                m_path.extendToShape()
                m_meshFn    = OpenMaya.MFnMesh( m_path )
                m_sets      = OpenMaya.MObjectArray()
                m_comps     = OpenMaya.MObjectArray()
                m_instanceNumber = m_path.instanceNumber()
                m_meshFn.getConnectedSetsAndMembers( m_instanceNumber, m_sets, m_comps, 1 )
                # ------------------------------------------ 
                m_SGNames = []                              # Stores Shading Group name
                m_sameSGFaceCount = OpenMaya.MIntArray()    # storoes the number of faces included in each shading group
                m_memberFaceNames = []                      # stores names of faces included in each shading group
                m_sameSGFaceCount.clear()
                # ------------------------------------------------
                # 1    Initialization of variables
                # ------------------------------------------------ 
                for i in range( m_sets.length() ):
                    m_setFn = OpenMaya.MFnSet( m_sets[i] )
                    if ( self._isShadingGroupInNeedToDeleteList( m_setFn.name() ) ):
                        m_index             = self._getIndexFromNeedToDeleteList( m_setFn.name() )
                        m_sourceValue       = self.m_needToDeleteList[m_index]
                        m_sourceHash        = m_sourceValue[1]
                        m_sourceSG          = m_sourceValue[2]
                        m_nodeSGFn          = OpenMaya.MFnDependencyNode( m_sourceSG ) 
                        m_index             = self._getIndexFromDestinationList( m_sourceHash ) 
                        m_destinationValue  = self.m_destinationList[m_index]
                        m_destinationSG     = m_destinationValue[2]
                        m_destinationSGFn   = OpenMaya.MFnDependencyNode( m_destinationSG )
                        if DEBUG3: print ( "MESH: {0}".format( m_path.fullPathName() ) )
                        if DEBUG3: print ( "{0:30} must be REPLACED by    {1}".format( m_nodeSGFn.name(), m_destinationSGFn.name() ) )
                        m_faceIt = OpenMaya.MItMeshPolygon( m_path, m_comps[i] )
                        # ------------------------------------------ 
                        m_SGNames.append( m_destinationSGFn.name() )
                        m_sameSGFaceCount.append( m_faceIt.count() )
                        m_aMemberFaceName   = ''
                        m_lastIndices       = [ -1, -1 ]
                        m_haveFace          = False
                        # ------------------------------------------ 
                        while not m_faceIt.isDone():                           
                            if ( -1 == m_lastIndices[0] ):
                                m_lastIndices[0] = m_faceIt.index()
                                m_lastIndices[1] = m_faceIt.index()
                            else:
                                m_currentIndex = m_faceIt.index()
                                # Hit non-contiguous face #. split out a new string
                                if ( m_currentIndex > m_lastIndices[1] + 1 ):
                                    m_aMemberFaceName += '{0}.f[{1}:{2}] '.format( m_path.fullPathName(), m_lastIndices[0], m_lastIndices[1] )
                                    m_lastIndices[0] = m_currentIndex
                                    m_lastIndices[1] = m_currentIndex 
                                else:
                                    m_lastIndices[1] = m_currentIndex
                            m_haveFace = True
                            m_faceIt.next()
                        # Only one member. Add it.
                        if ( m_haveFace ):
                            m_aMemberFaceName += '{0}.f[{1}:{2}] '.format( m_path.fullPathName(), m_lastIndices[0], m_lastIndices[1] )
                        m_memberFaceNames.append( m_aMemberFaceName )
                # ------------------------------------------------
                # 2    Output
                # ------------------------------------------------
                for i in range( m_sameSGFaceCount.length() ):
                    if ( 0 != m_sameSGFaceCount[i] ):
                        m_resultString += "select -r {0};\n".format( m_memberFaceNames[i] )
                        m_resultString += "sets -e -forceElement {0};\n".format( m_SGNames[i] )
                m_resultString +=  "select -clear;\n"
            m_iterator.next()
        if DEBUG3: print(m_resultString)
        OpenMaya.MGlobal.executeCommand( m_resultString )
        OpenMaya.MGlobal.executeCommand( 'hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");' )

    def _getAssignedShadingGroups( self ):
        if DEBUG1: print( " -------------------------------------------- " )  
        m_iterator  = OpenMaya.MItDag( OpenMaya.MItDag.kDepthFirst, OpenMaya.MFn.kMesh )
        m_dapPath   = OpenMaya.MDagPath()
        m_nodeFn    = OpenMaya.MFnDependencyNode()

        while not m_iterator.isDone():
            m_object = m_iterator.currentItem()
            m_nodeFn.setObject( m_object )
            m_iterator.getPath(m_dapPath)
            if m_nodeFn.isFromReferencedFile():
                OpenMaya.MGlobal.displayWarning( "Skipped {0} - from a reference".format( m_nodeFn.name() ) )
            else:
                if DEBUG1: print( "{0}".format( m_dapPath.fullPathName() ) )    
                m_meshFn = OpenMaya.MFnMesh( m_dapPath )
                m_sets  = OpenMaya.MObjectArray()
                m_comps = OpenMaya.MObjectArray()
                m_instanceNumber = m_dapPath.instanceNumber()
                m_meshFn.getConnectedSetsAndMembers( m_instanceNumber, m_sets, m_comps, 1 )
                for i in range( m_sets.length() ):
                    m_setFn = OpenMaya.MFnSet( m_sets[i] )
                    self.m_assignedShadingGroups.add(m_setFn.name())
                    if DEBUG1: print( "  --  {0}".format( m_setFn.name() ) )
            m_iterator.next()

    def _isShadingGroupAssigned( self, m_shadingGroupName ):
        return ( m_shadingGroupName in self.m_assignedShadingGroups )

    def _getSourceAndDestinationLists( self ):
        if DEBUG1: print( " -------------------------------------------- " )  
        m_iterator  = OpenMaya.MItDependencyNodes( OpenMaya.MFn.kShadingEngine )
        m_nodeFn    = OpenMaya.MFnDependencyNode()
        while not m_iterator.isDone():
            m_object = m_iterator.thisNode()
            m_nodeFn.setObject( m_object )
            if m_nodeFn.isFromReferencedFile():
                OpenMaya.MGlobal.displayWarning( "Skipped {0} - from a reference".format( m_nodeFn.name() ) )
            else:
                if ( self._isShadingGroupAssigned( m_nodeFn.name() ) ):
                    m_plug = m_nodeFn.findPlug( "surfaceShader" )
                    if DEBUG1: print( "{0}".format( m_nodeFn.name()) )
                    m_plugArrayConnected = OpenMaya.MPlugArray()
                    m_plug.connectedTo( m_plugArrayConnected, True, False )
                    for i in range( m_plugArrayConnected.length() ): 
                        m_plugConnected   = m_plugArrayConnected[i]
                        m_nodeConnected   = m_plugConnected.node()
                        m_nodeFnConnected = OpenMaya.MFnDependencyNode( m_nodeConnected ) 
                        m_hash            = self._getHash( m_nodeConnected )
                        m_value           = ( m_nodeConnected, m_hash, m_object )
                        if DEBUG1: print( "  --  {0:30} {1:20} {2}".format( m_nodeFnConnected.name(), m_nodeConnected.apiTypeStr(), m_hash ) )
                        if ( not self._isMaterialInTheList( m_hash ) ): 
                            self.m_destinationList.append( m_value )
                        else:
                            self.m_needToDeleteList.append( m_value )
                        self.m_sourceList.append( m_value )
            m_iterator.next()
        if DEBUG2: self.printLists( )

    def printLists( self ):
        print( " --- SOURCE --- {0} nodes".format( len( self.m_sourceList )) )
        for m_value in self.m_sourceList :            
            m_nodeConnected     = m_value[0]
            m_hash              = m_value[1]
            m_nodeSG            = m_value[2]
            m_nodeFnConnected   = OpenMaya.MFnDependencyNode( m_nodeConnected ) 
            print( "{0:30} {1}".format( m_nodeFnConnected.name(), m_hash ) )
        print( " --- DESTINATION --- {0} nodes".format( len( self.m_destinationList )) )
        for m_value in self.m_destinationList :
            m_nodeConnected     = m_value[0]
            m_hash              = m_value[1]
            m_nodeSG            = m_value[2]
            m_nodeFnConnected   = OpenMaya.MFnDependencyNode( m_nodeConnected ) 
            print( "{0:30} {1}".format( m_nodeFnConnected.name(), m_hash ) )
        print( " --- NEED TO DELETE --- {0} nodes".format( len( self.m_needToDeleteList )) )
        for m_value in self.m_needToDeleteList :
            m_nodeConnected     = m_value[0]
            m_hash              = m_value[1]
            m_nodeSG            = m_value[2]
            m_nodeFnConnected   = OpenMaya.MFnDependencyNode( m_nodeConnected ) 
            print( "{0:30} {1}".format( m_nodeFnConnected.name(), m_hash ) )

    def _isMaterialInTheList( self, m_hash ):
        for m_value in self.m_destinationList :
            if ( m_hash  ==  m_value[1] ): return True
        return False

    def _getIndexFromDestinationList( self, m_hash ):
        for m_value in self.m_destinationList :
            if ( m_hash ==  m_value[1] ): return self.m_destinationList.index( m_value )
        return False

    def _getIndexFromNeedToDeleteList( self, m_sgName ):
        for m_value in self.m_needToDeleteList :
            m_nodeSG    = m_value[2]
            m_nodeSGFn  = OpenMaya.MFnDependencyNode( m_nodeSG ) 
            if ( m_sgName ==  m_nodeSGFn.name() ): return self.m_needToDeleteList.index( m_value )
        return False

    def _isShadingGroupInNeedToDeleteList( self, m_sgName ):
        for m_value in self.m_needToDeleteList :
            m_nodeSG    = m_value[2]
            m_nodeSGFn  = OpenMaya.MFnDependencyNode( m_nodeSG ) 
            if ( m_sgName ==  m_nodeSGFn.name() ): return True
        return False
    
    def _getHash( self, m_node ):
        m_nodeFnConnected    = OpenMaya.MFnDependencyNode( m_node )
        m_list = []
        m_tmpList = []
        m_list.append( str( m_node.apiTypeStr() ) ) 
        m_tmpList.append( str( m_node.apiTypeStr() ) ) 
        if  ( "full"  == self.m_state ):                 
            for i in range( m_nodeFnConnected.attributeCount()):
                m_atrr      = m_nodeFnConnected.attribute(i) 
                m_fnAttr    = OpenMaya.MFnAttribute( m_atrr )      
                m_attrPlug  = OpenMaya.MPlug( m_node, m_atrr )                  
                if ( not m_fnAttr.isHidden() ):
                    m_value = getValue( m_attrPlug )       
                    m_list.append(  hash( str(m_value[1]) ) )
                    m_tmpList.append( str(m_value[1]) )
        elif ( "simple" == self.m_state ):
            m_attrList = [  "color", 
                            "transparency", 
                            "ambientColor", 
                            "normalCamera", 
                            "translucence", 
                            "cosinePower",
                            "specularColor",
                            "reflectedColor",
                            "glowIntensity",
                            "refractions",
                            "refractiveIndex",
                            "lightAbsorbance" ]
            for i in range( m_nodeFnConnected.attributeCount()):
                m_atrr      = m_nodeFnConnected.attribute(i)    
                m_fnAttr    = OpenMaya.MFnAttribute( m_atrr )       
                m_attrPlug  = OpenMaya.MPlug( m_node, m_atrr )
                if ( m_fnAttr.name() in m_attrList ):
                    m_value     = getValue( m_attrPlug )    
                    m_list.append(  hash( str(m_value[1]) ) )
                    m_tmpList.append( m_value )
        if DEBUG1: print( "values list: {}".format( m_tmpList ) )
        if DEBUG1: print( "hash list: {}".format( m_list ) )
        return hash(str(m_list))  

def getMObjectFromSelection():
    m_selectionList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( m_selectionList )
    m_node = OpenMaya.MObject() 
    try:                          
        m_selectionList.getDependNode( 0, m_node )
        if ( m_node.isNull() ): return None
    except:
        return None
    return m_node

def printAllAttr():
    m_node = getMObjectFromSelection()
    m_nodeFnConnected    = OpenMaya.MFnDependencyNode(m_node)
    for i in range( m_nodeFnConnected.attributeCount()):
        m_atrr      = m_nodeFnConnected.attribute(i) 
        m_fnAttr    = OpenMaya.MFnAttribute( m_atrr )      
        m_attrPlug  = OpenMaya.MPlug( m_node, m_atrr )
        m_value = getValue( m_attrPlug )   
        m_str = "{0:30}  == {1}".format( m_fnAttr.name(), m_value )
        print(m_str)

def getBumpTextureStr( m_node ):
    m_plugFn = OpenMaya.MFnDependencyNode(m_node)
    m_attrPlug = m_plugFn.findPlug("bumpValue")
    m_plugArrayConnected  = OpenMaya.MPlugArray()
    m_attrPlug.connectedTo( m_plugArrayConnected, True, True )
    for j in range( m_plugArrayConnected.length() ):
        m_plugConnected     = m_plugArrayConnected[j]
        m_plugConnectedNode = m_plugConnected.node()
        m_plugConnectedNodeFn = OpenMaya.MFnDependencyNode(m_plugConnectedNode)
        m_textureNamePlug = m_plugConnectedNodeFn.findPlug("fileTextureName")
        return m_textureNamePlug.asString()
    return None
        
def getValue( m_attrPlug ):
    m_str = "kUnknown"  
    try:
        m_atrr = m_attrPlug.attribute()     
        if ( m_attrPlug.isDestination() ):          
            m_list  = []
            m_plugArrayConnected = OpenMaya.MPlugArray()
            m_attrPlug.connectedTo( m_plugArrayConnected, True, True )
            for j in range( m_plugArrayConnected.length() ):
                m_plugConnected = m_plugArrayConnected[j]
                m_addStr        = m_plugConnected.info()
                m_plugConnectedNode = m_plugConnected.node()
                m_plugConnectedNodeFn = OpenMaya.MFnDependencyNode(m_plugConnectedNode)
                if ('kBump' == m_plugConnectedNode.apiTypeStr() ):
                    m_addStr = getBumpTextureStr( m_plugConnectedNode )
                m_list.append( m_addStr )
            m_str = "isDestination"     
            return ( m_str, m_list )
        elif ( m_attrPlug.isCompound() ):
            m_str = "isCompound"    
            return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
        elif ( m_attrPlug.isArray() ):
            m_str = "isArray"   
            return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
        elif ( OpenMaya.MFn.kCompoundAttribute      == m_atrr.apiType() ):
            m_str = "kCompoundAttribute"
            return ( m_str, cmds.getAttr( m_attrPlug.info() ) )     
        elif ( OpenMaya.MFn.kTimeAttribute          == m_atrr.apiType() ):
            m_str = "kTimeAttribute" 
            return ( m_str, cmds.getAttr( m_attrPlug.info() )  )    
        elif ( OpenMaya.MFn.kEnumAttribute          == m_atrr.apiType() ): 
            m_fnEnum    = OpenMaya.MFnEnumAttribute( m_atrr )
            m_util      = OpenMaya.MScriptUtil()
            m_ptr       = m_util.asShortPtr()
            m_fnEnum.getMin( m_ptr )
            m_min       = m_util.getShort( m_ptr )
            m_fnEnum.getMax( m_ptr )
            m_max       = m_util.getShort( m_ptr )
            m_list  = []
            for i in range( m_min, ( m_max + 1) ):
                m_list.append( m_fnEnum.fieldName(i) )
            m_str = "kEnumAttribute" 
            return ( m_str, cmds.getAttr( m_attrPlug.info() ), m_list )
        elif ( OpenMaya.MFn.kUnitAttribute          == m_atrr.apiType() ):
            m_str = "kUnitAttribute"
            return ( m_str, cmds.getAttr( m_attrPlug.info() )  )
        elif ( OpenMaya.MFn.kGenericAttribute       == m_atrr.apiType() ):
            m_str = "kGenericAttribute"
            return ( m_str, cmds.getAttr( m_attrPlug.info() )  )
        elif ( OpenMaya.MFn.kLightDataAttribute     == m_atrr.apiType() ):
            m_str = "kLightDataAttribute"
            return ( m_str, cmds.getAttr( m_attrPlug.info() )  )
        elif ( OpenMaya.MFn.kMatrixAttribute        == m_atrr.apiType() ):
            m_str = "kMatrixAttribute"
            return ( m_str, cmds.getAttr( m_attrPlug.info() )  )
        elif ( OpenMaya.MFn.kFloatMatrixAttribute   == m_atrr.apiType() ):
            m_str = "kFloatMatrixAttribute" 
            return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
        elif ( OpenMaya.MFn.kMessageAttribute       == m_atrr.apiType() ):
            m_str = "kMessageAttribute"
            return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
        elif ( OpenMaya.MFn.kToonLineAttributes     == m_atrr.apiType() ):
            m_str = "kToonLineAttributes" 
            return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
        elif ( OpenMaya.MFn.kTransferAttributes     == m_atrr.apiType() ):
            m_str = "kTransferAttributes"
            return ( m_str, cmds.getAttr( m_attrPlug.info() )  )
        elif ( OpenMaya.MFn.kAttribute3Double   == m_atrr.apiType() ): 
            m_str = "kAttribute3Double"
            return ( m_str, [ m_attrPlug.child(0).asDouble(), m_attrPlug.child(1).asDouble(), m_attrPlug.child(2).asDouble()] )
        elif ( OpenMaya.MFn.kAttribute3Float    == m_atrr.apiType() ): 
            m_str = "kAttribute3Float"
            return ( m_str, [ m_attrPlug.child(0).asFloat(),  m_attrPlug.child(1).asFloat(),  m_attrPlug.child(2).asFloat()] )
        elif ( OpenMaya.MFn.kAttribute3Int      == m_atrr.apiType() ): 
            m_str = "kAttribute3Int"
            return ( m_str, [ m_attrPlug.child(0).asInt(),   m_attrPlug.child(1).asInt(),   m_attrPlug.child(2).asInt()] )
        elif ( OpenMaya.MFn.kAttribute3Short    == m_atrr.apiType() ): 
            m_str = "kAttribute3Short"
            return ( m_str, [ m_attrPlug.child(0).asInt(),   m_attrPlug.child(1).asInt(),   m_attrPlug.child(2).asInt()] )
        elif ( OpenMaya.MFn.kAttribute3Long     == m_atrr.apiType() ): 
            m_str = "kAttribute3Long"
            return ( m_str, [ m_attrPlug.child(0).asInt(), m_attrPlug.child(1).asInt(), m_attrPlug.child(2).asInt()] )      
        elif ( OpenMaya.MFn.kAttribute2Double   == m_atrr.apiType() ): 
            m_str = "kAttribute2Double"
            return ( m_str, [ m_attrPlug.child(0).asDouble(), m_attrPlug.child(1).asDouble()] )
        elif ( OpenMaya.MFn.kAttribute2Float    == m_atrr.apiType() ): 
            m_str = "kAttribute2Float"
            return ( m_str, [ m_attrPlug.child(0).asFloat(), m_attrPlug.child(1).asFloat()] )
        elif ( OpenMaya.MFn.kAttribute2Int      == m_atrr.apiType() ): 
            m_str = "kAttribute2Int"
            return ( m_str, [ m_attrPlug.child(0).asInt(),   m_attrPlug.child(1).asInt() ] )
        elif ( OpenMaya.MFn.kAttribute2Short    == m_atrr.apiType() ): 
            m_str = "kAttribute2Short"
            return ( m_str, [ m_attrPlug.child(0).asInt(),   m_attrPlug.child(1).asInt() ] )
        elif ( OpenMaya.MFn.kAttribute2Long     == m_atrr.apiType() ): 
            m_str = "kAttribute2Long"
            return ( m_str, [ m_attrPlug.child(0).asInt(), m_attrPlug.child(1).asInt()] )       
        elif ( OpenMaya.MFn.kAttribute4Double   == m_atrr.apiType() ): 
            m_str = "kAttribute4Double"
            return ( m_str, [ m_attrPlug.child(0).asDouble(), m_attrPlug.child(1).asDouble(), m_attrPlug.child(2).asDouble(), m_attrPlug.child(3).asDouble() ] )                
        elif ( OpenMaya.MFn.kDoubleLinearAttribute  == m_atrr.apiType() ): 
            m_str = "kDoubleLinearAttribute"
            return ( m_str, m_attrPlug.asMDistance().asCentimeters() )
        elif ( OpenMaya.MFn.kFloatLinearAttribute   == m_atrr.apiType() ): 
            m_str = "kFloatLinearAttribute"
            return ( m_str, m_attrPlug.asMDistance().asCentimeters() )      
        elif ( OpenMaya.MFn.kDoubleAngleAttribute   == m_atrr.apiType() ): 
            m_str = "kDoubleAngleAttribute"
            return ( m_str, m_attrPlug.asMAngle().asDegrees() )
        elif ( OpenMaya.MFn.kFloatAngleAttribute    == m_atrr.apiType() ): 
            m_str = "kFloatAngleAttribute"
            return ( m_str, m_attrPlug.asMAngle().asDegrees() )             
        elif ( OpenMaya.MFn.kTypedAttribute         == m_atrr.apiType() ): 
            m_fnType = OpenMaya.MFnTypedAttribute( m_atrr )         
            if   ( OpenMaya.MFnData.kAny                == m_fnType.attrType() ):
                m_str = "kAny" 
                return ( m_str, cmds.getAttr( m_attrPlug.info() )  )
            elif ( OpenMaya.MFnData.kComponentList  == m_fnType.attrType() ):
                m_str = "kComponentList"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kDoubleArray        == m_fnType.attrType() ):
                m_str = "kDoubleArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kDynArrayAttrs  == m_fnType.attrType() ):
                m_str = "kDynArrayAttrs"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kDynSweptGeometry == m_fnType.attrType() ): 
                m_str = "kDynSweptGeometry"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kFloatArray         == m_fnType.attrType() ):
                m_str = "kFloatArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kIntArray       == m_fnType.attrType() ):
                m_str = "kIntArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kInvalid            == m_fnType.attrType() ):
                m_str = "kInvalid"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kLast           == m_fnType.attrType() ):
                m_str = "kLast"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kLattice            == m_fnType.attrType() ):
                m_str = "kLattice"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kMatrix             == m_fnType.attrType() ): 
                m_matrix = OpenMaya.MFnMatrixData( m_attrPlug.asMObject() ).matrix()
                m_str = "kMatrix"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kMatrixArray        == m_fnType.attrType() ): 
                m_str = "kMatrixArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kMesh           == m_fnType.attrType() ):
                m_str = "kMesh"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kNId                == m_fnType.attrType() ):
                m_str = "kNId"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kNObject            == m_fnType.attrType() ): 
                m_str = "kNObject"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kNumeric            == m_fnType.attrType() ): 
                m_str = "kNumeric"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kNurbsCurve         == m_fnType.attrType() ):
                m_str = "kNurbsCurve"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kNurbsSurface   == m_fnType.attrType() ): 
                m_str = "kNurbsSurface"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kPluginGeometry     == m_fnType.attrType() ):
                m_str = "kPluginGeometry"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kPointArray         == m_fnType.attrType() ):
                m_str = "kPointArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kSphere             == m_fnType.attrType() ): 
                m_str = "kSphere"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kString             == m_fnType.attrType() ):
                m_str = "kString"
                return ( m_str, m_attrPlug.asString()  )
            elif ( OpenMaya.MFnData.kStringArray        == m_fnType.attrType() ):
                m_str = "kStringArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kSubdSurface        == m_fnType.attrType() ):
                m_str = "kSubdSurface"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnData.kVectorArray        == m_fnType.attrType() ):
                m_str = "kVectorArray"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )                             
        elif ( OpenMaya.MFn.kNumericAttribute == m_atrr.apiType() ):
            m_fnNum = OpenMaya.MFnNumericAttribute( m_atrr )            
            if   ( OpenMaya.MFnNumericData.kInvalid     == m_fnNum.unitType() ): 
                m_str = "kInvalid"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
            elif ( OpenMaya.MFnNumericData.kBoolean     == m_fnNum.unitType() ):  
                m_str = "kBoolean"
                return ( m_str, m_attrPlug.asBool() )
            elif ( OpenMaya.MFnNumericData.kByte        == m_fnNum.unitType() ):  
                m_str = "kByte"
                return ( m_str, m_attrPlug.asInt() )        
            elif ( OpenMaya.MFnNumericData.kChar        == m_fnNum.unitType() ):  
                m_str = "kChar"
                return ( m_str, m_attrPlug.asChar() )
            elif ( OpenMaya.MFnNumericData.kShort       == m_fnNum.unitType() ):  
                m_str = "kShort"
                return ( m_str, m_attrPlug.asInt() )
            elif ( OpenMaya.MFnNumericData.k2Short      == m_fnNum.unitType() ):  
                m_str = "k2Short"
                return ( m_str, [ m_attrPlug.child(0).asInt(), m_attrPlug.child(1).asInt() ] )
            elif ( OpenMaya.MFnNumericData.k3Short      == m_fnNum.unitType() ):  
                m_str = "k3Short"
                return ( m_str, [ m_attrPlug.child(0).asInt(), m_attrPlug.child(1).asInt(), m_attrPlug.child(2).asInt()] )
            elif ( OpenMaya.MFnNumericData.kLong        == m_fnNum.unitType() ):  
                m_str = "kLong"
                return ( m_str, m_attrPlug.asInt() )
            elif ( OpenMaya.MFnNumericData.kInt         == m_fnNum.unitType() ):  
                m_str = "kInt"
                return ( m_str, m_attrPlug.asInt() )
            elif ( OpenMaya.MFnNumericData.k2Long       == m_fnNum.unitType() ):  
                m_str = "k2Long"
                return ( m_str, [ m_attrPlug.child(0).asInt(), m_attrPlug.child(1).asInt() ] )
            elif ( OpenMaya.MFnNumericData.k2Int        == m_fnNum.unitType() ):  
                m_str = "k2Int"
                return ( m_str, [ m_attrPlug.child(0).asInt(),   m_attrPlug.child(1).asInt() ] )
            elif ( OpenMaya.MFnNumericData.k3Long       == m_fnNum.unitType() ):  
                m_str = "k3Long"
                return ( m_str, [ m_attrPlug.child(0).asInt(), m_attrPlug.child(1).asInt(), m_attrPlug.child(2).asInt() ] )
            elif ( OpenMaya.MFnNumericData.k3Int        == m_fnNum.unitType() ):  
                m_str = "k3Int"
                return ( m_str, [ m_attrPlug.child(0).asInt(),   m_attrPlug.child(1).asInt(),   m_attrPlug.child(2).asInt() ] )
            elif ( OpenMaya.MFnNumericData.kFloat       == m_fnNum.unitType() ):  
                m_str = "kFloat"
                return ( m_str, m_attrPlug.asFloat() )
            elif ( OpenMaya.MFnNumericData.k2Float      == m_fnNum.unitType() ):  
                m_str = "k2Float"
                return ( m_str, [ m_attrPlug.child(0).asFloat(), m_attrPlug.child(1).asFloat() ] )
            elif ( OpenMaya.MFnNumericData.k3Float      == m_fnNum.unitType() ):  
                m_str = "k3Float"
                return ( m_str, [ m_attrPlug.child(0).asFloat(), m_attrPlug.child(1).asFloat(), m_attrPlug.child(2).asFloat() ] )
            elif ( OpenMaya.MFnNumericData.kDouble      == m_fnNum.unitType() ):  
                m_str = "kDouble"
                return ( m_str, m_attrPlug.asDouble() )
            elif ( OpenMaya.MFnNumericData.k2Double     == m_fnNum.unitType() ):  
                m_str = "k2Double"
                return ( m_str,[ m_attrPlug.child(0).asDouble(), m_attrPlug.child(1).asDouble() ] )
            elif ( OpenMaya.MFnNumericData.k3Double     == m_fnNum.unitType() ):  
                m_str = "k3Double"
                return ( m_str,[ m_attrPlug.child(0).asDouble(), m_attrPlug.child(1).asDouble(), m_attrPlug.child(2).asDouble() ] )
            elif ( OpenMaya.MFnNumericData.k4Double     == m_fnNum.unitType() ):  
                m_str = "k4Double"
                return ( m_str,[ m_attrPlug.child(0).asDouble(), m_attrPlug.child(1).asDouble(), m_attrPlug.child(2).asDouble(), m_attrPlug.child(3).asDouble()] )
            elif ( OpenMaya.MFnNumericData.kAddr        == m_fnNum.unitType() ):  
                m_str = "kAddr"
                return ( m_str, m_attrPlug.asDouble())
            elif ( OpenMaya.MFnNumericData.kLast        == m_fnNum.unitType() ):  
                m_str = "kLast"
                return ( m_str, cmds.getAttr( m_attrPlug.info() ) )
        else:
            return ( m_str,  m_attrPlug.asMObject() )
    except:
        return ( "kError_{0}".format(m_str), None )
    return ( m_str, None )