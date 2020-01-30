#-----------------------------------------------------------------------------------
#
#   SCRIPT      deleteDuplicateTextures.py
#   AUTHOR      Zaitsev Evgeniy
#               ev.zaitsev@gmail.com
#
#       import deleteDuplicateTextures; deleteDuplicateTextures.duplicateTextures()
#       
#-----------------------------------------------------------------------------------
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import os
DEBUG = False

class duplicateTextures( object ):
    def __init__(self):
        self.m_sourceList = []
        self.m_destinationList = []
        self.m_needToDeleteList = []
        self.getSourceAndDestinationLists()

    def getSourceAndDestinationLists( self ):

        m_iterator  = OpenMaya.MItDependencyNodes( OpenMaya.MFn.kFileTexture )
        m_nodeFn    = OpenMaya.MFnDependencyNode()

        while not m_iterator.isDone():
            m_object = m_iterator.thisNode()
            m_nodeFn.setObject( m_object )
            if m_nodeFn.isFromReferencedFile():
                OpenMaya.MGlobal.displayWarning( "Skipped {0} - from a reference".format( m_nodeFn.name() ) )
            else:
                m_textureNamePlug   = m_nodeFn.findPlug( "fileTextureName" ) 
                m_textureNameDict   = {}               
                m_plugArray         = OpenMaya.MPlugArray()
                m_isNeedProcessing  = False
                m_nodeFn.getConnections( m_plugArray )
                for i in range( m_plugArray.length() ):
                    m_plug = m_plugArray[i]
                    if ( m_plug.isSource() and self._isPlugFromOut( m_plug ) ):
                        m_textureNameDict[ m_plug.info() ] = []
                        m_plugArrayConnected = OpenMaya.MPlugArray()
                        m_plug.connectedTo( m_plugArrayConnected, False, True )
                        for j in range( m_plugArrayConnected.length() ):                        
                            m_plugConnected = m_plugArrayConnected[j]
                            m_textureNameDict[ m_plug.info() ].append( m_plugConnected.info() )
                        if len( m_textureNameDict[ m_plug.info() ] ): m_isNeedProcessing = True
                if ( m_isNeedProcessing ): 
                    m_value  = ( m_textureNamePlug, m_textureNameDict )
                    if ( not self._isFileIntheList( m_textureNamePlug ) ): 
                        self.m_destinationList.append( m_value )
                    else:
                        self.m_needToDeleteList.append( m_value )
                    self.m_sourceList.append( m_value )
            m_iterator.next()
        
        if DEBUG: self.printLists( "simple" )
        self._connectAttributes()
        OpenMaya.MGlobal.executeCommand( 'hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");' )

    def _connectAttributes( self ):
        if DEBUG: print( " ------------------------ ")
        for m_value in self.m_needToDeleteList :            
            m_textureNamePlug   = m_value[0]
            m_textureNameDict   = m_value[1]
            m_index = self._getIndexFromList( m_textureNamePlug ) 
            m_destinationValue  = self.m_destinationList[m_index]
            m_destinationPlug   = m_destinationValue[0]
            m_destinationDict   = m_destinationValue[1]
            for m_key, m_values in m_textureNameDict.iteritems():
                m_startPart = m_destinationPlug.info().split(".")[0]
                m_endPart   = m_key.split(".")[1]
                m_newConnection = "{0}.{1}".format( m_startPart, m_endPart )
                if DEBUG: print ( "{0} must be connectedTo:".format( m_newConnection ) )
                if DEBUG: print ( "{0} is connectedTo:".format( m_key ) )
                for m_val in m_values:
                    if DEBUG: print( "         {0}".format( m_val ) )
                    try:
                        cmds.connectAttr( m_newConnection, m_val, force = True )
                        print("{0} ConnectedTo {1}".format(m_newConnection,m_val) )
                    except:
                        print("Can't connect {0} TO {1}".format(m_newConnection, m_val))

    def _getIndexFromList( self, m_filePlug ):
        for m_value in self.m_destinationList :
            if ( m_filePlug.asString()  ==  m_value[0].asString() ): return self.m_destinationList.index( m_value )
        return False

    def _isFileIntheList( self, m_filePlug ):
        for m_value in self.m_destinationList :
            if ( m_filePlug.asString()  ==  m_value[0].asString() ): return True
        return False

    def _isPlugFromOut( self, m_plug ):
        m_out = [ "outColor", "outTransparency", "outAlpha", "outSize" ]
        m_attr = OpenMaya.MFnAttribute( m_plug.attribute() )
        if ( m_out.count( m_attr.name() ) ): return True
        return False

    def printLists( self, m_state = "simple" ):
        print( " --- SOURCE --- {0} nodes".format( len( self.m_sourceList )) )
        for m_value in self.m_sourceList :
            m_textureNamePlug  = m_value[0]
            m_textureNameDict  = m_value[1]
            print( "{0} {1}".format( m_textureNamePlug.info(), m_textureNamePlug.asString() ) )
            if ( "simple" != m_state ):
                for m_key, m_values in m_textureNameDict.iteritems():
                    print ( "{0} connectedTo:".format( m_key ) )
                    for m_val in m_values:
                        print( "         {0}".format( m_val ) )
        print( " --- DESTINATION --- {0} nodes".format( len( self.m_destinationList )) )
        for m_value in self.m_destinationList :
            m_textureNamePlug  = m_value[0]
            m_textureNameDict  = m_value[1]
            print( "{0} {1}".format( m_textureNamePlug.info(), m_textureNamePlug.asString() ) )
            if ( "simple" != m_state ):
                for m_key, m_values in m_textureNameDict.iteritems():
                    print ( "{0} connectedTo:".format( m_key ) )
                    for m_val in m_values:
                        print( "         {0}".format( m_val ) )
        print( " --- NEED TO DELETE --- {0} nodes".format( len( self.m_needToDeleteList )) )
        for m_value in self.m_needToDeleteList :
            m_textureNamePlug  = m_value[0]
            m_textureNameDict  = m_value[1]
            print( "{0} {1}".format( m_textureNamePlug.info(), m_textureNamePlug.asString() ) )
            if ( "simple" != m_state ):
                for m_key, m_values in m_textureNameDict.iteritems():
                    print ( "{0} connectedTo:".format( m_key ) )
                    for m_val in m_values:
                        print( "         {0}".format( m_val ) )