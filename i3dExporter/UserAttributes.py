#
# UserAttributes
#
# Authors: Stijn Wopereis (Wopster)
# Description: Adds to the option to add and modify I3D user attributes.
#
# Copyright (c) Stijn Wopereis, 2018

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import random
import string

from functools import partial

from I3DExporter import TEXT_WIDTH, DEFAULT_FIELD_WIDTH, I3DUpdateLayers, I3DSaveAttributeBool, I3DSaveAttributeString, I3DSaveAttributeFloat, I3DSaveAttributeInt, \
    I3DAttributeExists

# UserAttributes
UI_OPTIONS_PREDEFINED_USERATTRIBUTETYPES = 'wopster_optionsUserAttributeTypes'
UI_OPTIONS_PREDEFINED_USERATTRIBUTE_NAME = 'wopster_optionsUserAttributeName'
UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE = 'wopster_optionsUserAttributeValue'

UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME = 'wopster_attributeObjectName'
UI_CONTROL_USERATTRIBUTES_STRING_NODE_INDEX = 'wopster_attributeObjectIndex'

UI_CONTROL_LAYOUT_USERATTRIBUTES = 'wopster_layoutUserAtrributes'
UI_CONTROL_LAYOUT_USERATTRIBUTES_ROWS = 'wopster_attributesRows'
UI_CONTROL_LAYOUT_USERATTRIBUTES_ADD_ATTRIBUTE = 'wopster_layoutUserAtrributesAddNew'
UI_CONTROL_BUTTON_USERATTRIBUTES_ADD_ATTRIBUTE = 'wopster_buttonUserAtrributesAddNew'

TYPE_BOOL = 1
TYPE_INT = 2
TYPE_FLOAT = 3
TYPE_STRING = 4
TYPE_SCRIPTCALLBACK = 5

UI_MENU_USERATTRIBUTES = {
    'bool': TYPE_BOOL,
    'integer': TYPE_INT,
    'long': TYPE_INT,
    'string': TYPE_STRING,
    'float': TYPE_FLOAT,
    'double': TYPE_FLOAT,
    'scriptCallback': TYPE_SCRIPTCALLBACK,
}


class UserAttributes:

    def __init__(self):
        self.userAttributes_type_settings = []

    def delete(self):
        self.userAttributes_type_settings = []
        # pass

    def showWarning(self, text):
        OpenMaya.MGlobal.displayWarning(text)

    def initUI(self, parent):
        tab = cmds.formLayout('TabUserAttributes', parent=parent)
        cmds.columnLayout(adjustableColumn=True)

        # Frame for the current selection
        selection_frame = cmds.frameLayout('ua_selectionFrame', label='Current Selection', parent=tab, w=390, cll=False, mh=2, mw=2)
        current_node_layout = cmds.columnLayout(adjustableColumn=True, parent=selection_frame)

        self.addTextFieldElement(current_node_layout, 'Node Name', UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME, '', '', editable=False, width=245)
        self.addTextFieldElement(current_node_layout, 'Node Index', UI_CONTROL_USERATTRIBUTES_STRING_NODE_INDEX, '', '', editable=False, width=245)

        attributes_main_frame = cmds.frameLayout(parent=tab, label='Attributes', w=390, cll=False, mh=2, mw=2)
        attributes_scroll_layout = cmds.scrollLayout('scrollAttributes', parent=attributes_main_frame, cr=True, verticalScrollBarAlwaysVisible=False)

        # Add user attribute
        new_attributes_layout = cmds.frameLayout(UI_CONTROL_LAYOUT_USERATTRIBUTES_ADD_ATTRIBUTE, parent=attributes_scroll_layout, label='Add new attribute', w=390, cll=False, mh=2, mw=2)

        # Type of new attribute
        attributes_type_row_layout = cmds.rowLayout(adjustableColumn=2, numberOfColumns=2, parent=new_attributes_layout)
        cmds.text(parent=attributes_type_row_layout, label='Type', width=TEXT_WIDTH, align='left', annotation='')

        type_option_menu = cmds.optionMenu(UI_OPTIONS_PREDEFINED_USERATTRIBUTETYPES, parent=attributes_type_row_layout, annotation='Type',
                                           changeCommand=self.onChangeUserAttributeType)

        for k, _ in UI_MENU_USERATTRIBUTES.iteritems():
            cmds.menuItem(parent=type_option_menu, label=k)

        self.onChangeUserAttributeType(UI_MENU_USERATTRIBUTES['bool'])

        attributes_frame = cmds.frameLayout(UI_CONTROL_LAYOUT_USERATTRIBUTES, label='Current attributes', parent=attributes_scroll_layout, w=390, cll=True, mh=2, mw=2)
        attributes_layout = cmds.columnLayout(adjustableColumn=True, parent=attributes_frame)

        attributes_row_layout = cmds.rowLayout(UI_CONTROL_LAYOUT_USERATTRIBUTES_ROWS, parent=attributes_layout, columnWidth4=(TEXT_WIDTH, TEXT_WIDTH * 2, TEXT_WIDTH, 10),
                                               adjustableColumn=4, numberOfColumns=4, )
        cmds.text(parent=attributes_row_layout, label='Name', width=TEXT_WIDTH, align='left', annotation='')
        cmds.text(parent=attributes_row_layout, label='Value', width=TEXT_WIDTH * 2, align='left', annotation='')
        cmds.text(parent=attributes_row_layout, label='Type', width=TEXT_WIDTH, align='right', annotation='')

        attribute_button_items = cmds.formLayout('AttributeButtons', parent=tab)

        button_load = cmds.button(parent=attribute_button_items, label='Load', height=30, width=150, align='right', command=self.loadObjectUserAttribute)
        button_save = cmds.button(parent=attribute_button_items, label='Save', height=30, width=150, align='left', command=self.updateObjectUserAttribute)
        cmds.formLayout(attribute_button_items, edit=True, attachPosition=((button_load, 'left', 0, 0), (button_load, 'right', 5, 50),
                                                                           (button_save, 'left', 0, 50), (button_save, 'right', 5, 100)))
        cmds.formLayout(tab, edit=True, attachForm=(
            (selection_frame, 'top', 2), (selection_frame, 'left', 2), (selection_frame, 'right', 2),
            (attributes_main_frame, 'top', 74), (attributes_main_frame, 'left', 2), (attributes_main_frame, 'right', 2), (attributes_main_frame, 'bottom', 32),
            (attribute_button_items, 'bottom', 2), (attribute_button_items, 'left', 2), (attribute_button_items, 'right', 2)
        ))

        return tab

    def updateCurrentSelectionNode(self, index, node):
        cmds.textField(UI_CONTROL_USERATTRIBUTES_STRING_NODE_INDEX, edit=True, text=index)
        cmds.textField(UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME, edit=True, text=node)

    def loadObjectUserAttribute(self, unused):
        object_name = str(cmds.textField(UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME, q=True, text=True))

        if not len(object_name) > 0:
            self.showWarning('Nothing selected')
            return

        if not self.userAttributes_type_settings is None:
            for v in self.userAttributes_type_settings:
                cmds.deleteUI('userAttribute' + v['key'])

        self.userAttributes_type_settings = []

        if not object_name is None:
            attributes = cmds.listAttr(object_name, userDefined=True)

            if attributes is None:
                self.showWarning('No user attributes found!')
                return

            for name in attributes:
                key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
                object_key = object_name + "." + name
                type_name = cmds.getAttr(object_key, type=True)
                attribute_type = UI_MENU_USERATTRIBUTES[type_name]

                self.userAttributes_type_settings.append({'type': attribute_type, 'typeName': type_name, 'name': name, 'value': cmds.getAttr(object_key), 'key': key})

            self.updateUserAttributeUI()
        else:
            self.showWarning('Nothing selected')

    def updateObjectUserAttribute(self, unused):
        for v in self.userAttributes_type_settings:
            if v['type'] == TYPE_BOOL:
                updated_value = cmds.checkBox('userAttributeValue' + v['key'], q=True, v=True)
            elif v['type'] == TYPE_INT:
                updated_value = cmds.intField('userAttributeValue' + v['key'], q=True, v=True)
            elif v['type'] == TYPE_FLOAT:
                updated_value = cmds.floatField('userAttributeValue' + v['key'], q=True, v=True)
            else:
                updated_value = cmds.textField('userAttributeValue' + v['key'], q=True, text=True)

            v['value'] = updated_value

        self.saveObjectUserAttribute()

    def updateUserAttributeUI(self):
        attributes_layout = cmds.frameLayout(UI_CONTROL_LAYOUT_USERATTRIBUTES, edit=True)
        for v in self.userAttributes_type_settings:
            layout = cmds.rowLayout('userAttribute' + v['key'], columnWidth4=(TEXT_WIDTH, TEXT_WIDTH * 2, TEXT_WIDTH, 10), adjustableColumn=4, numberOfColumns=4,
                                    parent=attributes_layout)

            cmds.text(label=v['name'], width=TEXT_WIDTH, align='left', annotation='', parent=layout)

            # Switch display type
            if v['type'] == TYPE_BOOL:
                cmds.checkBox('userAttributeValue' + v['key'], label=v['name'], v=v['value'], width=TEXT_WIDTH * 2, parent=layout, annotation='', editable=True)
            elif v['type'] == TYPE_INT:
                cmds.intField('userAttributeValue' + v['key'], v=v['value'], editable=True, width=TEXT_WIDTH * 2, parent=layout)
            elif v['type'] == TYPE_FLOAT:
                cmds.floatField('userAttributeValue' + v['key'], v=v['value'], editable=True, width=TEXT_WIDTH * 2, parent=layout)
            else:
                cmds.textField('userAttributeValue' + v['key'], text=v['value'], width=TEXT_WIDTH * 2, editable=True, parent=layout)

            cmds.text(label=v['typeName'], width=200, annotation='', parent=layout)
            cmds.button('userAttributeDeleteButton', parent=layout, label='X', width=10, align='right', command=partial(self.deleteObjectUserAttribute, v['name']))

    def saveObjectUserAttributes(self, unused):
        object_name = cmds.textField(UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME, q=True, text=True)

        if not len(object_name) > 0:
            self.showWarning('Nothing selected')
            return

        name = cmds.textField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_NAME, q=True, text=True)
        type_name = cmds.optionMenu(UI_OPTIONS_PREDEFINED_USERATTRIBUTETYPES, q=True, value=True)

        if type_name == "bool":
            value = cmds.checkBox(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, q=True, v=True)
        elif type_name == "integer" or type_name == "long":
            value = cmds.intField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, q=True, v=True)
        elif type_name == "float":
            value = cmds.floatField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, q=True, v=True)
        else:
            value = cmds.textField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, q=True, text=True)

        if not type_name is None and len(name) > 0:
            if not self.userAttributes_type_settings is None:
                for v in self.userAttributes_type_settings:
                    cmds.deleteUI('userAttribute' + v['key'])

            attribute_type = UI_MENU_USERATTRIBUTES[type_name]
            key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

            self.userAttributes_type_settings.append(
                {'type': attribute_type, 'typeName': type_name, 'name': name, 'value': value, 'key': key})

            self.saveObjectUserAttribute()
            self.updateUserAttributeUI()
            I3DUpdateLayers(str(object_name))
        else:
            self.showWarning('Not all fields are valid!')

    def saveObjectUserAttribute(self):
        object_name = str(cmds.textField(UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME, q=True, text=True))

        if not len(object_name) > 0:
            self.showWarning('Nothing selected')
            return

        for v in self.userAttributes_type_settings:
            if v['type'] == TYPE_BOOL:
                I3DSaveAttributeBool(object_name, v['name'], v['value'])
            elif v['type'] == TYPE_INT:
                I3DSaveAttributeInt(object_name, v['name'], v['value'])
            elif v['type'] == TYPE_FLOAT:
                I3DSaveAttributeFloat(object_name, v['name'], v['value'])
            elif v['type'] == TYPE_STRING or v['type'] == TYPE_SCRIPTCALLBACK:
                I3DSaveAttributeString(object_name, v['name'], v['value'])

    def onChangeUserAttributeType(self, selected):
        if not selected is None:
            # Delete current UI and redraw
            if cmds.rowLayout(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_NAME + "layout", exists=True):
                cmds.deleteUI(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_NAME + "layout")

            if cmds.rowLayout(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE + "layout", exists=True):
                cmds.deleteUI(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE + "layout")

            if cmds.button(UI_CONTROL_BUTTON_USERATTRIBUTES_ADD_ATTRIBUTE, exists=True):
                cmds.deleteUI(UI_CONTROL_BUTTON_USERATTRIBUTES_ADD_ATTRIBUTE)

            attribute_layout = cmds.frameLayout(UI_CONTROL_LAYOUT_USERATTRIBUTES_ADD_ATTRIBUTE, label='Add new attribute', w=390, edit=True, cll=True, mh=2, mw=2)

            self.addTextFieldElement(attribute_layout, 'Name', UI_OPTIONS_PREDEFINED_USERATTRIBUTE_NAME, '', '', editable=True, width=245)

            layout_value = cmds.rowLayout(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE + "layout", adjustableColumn=2, numberOfColumns=2, parent=attribute_layout)
            cmds.text(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE + "label", label='Value', width=TEXT_WIDTH, align='left', annotation='', parent=layout_value)

            if selected == "bool":
                cmds.checkBox(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, label="", width=245, parent=layout_value, annotation='', editable=True)
            elif selected == "integer" or selected == "long":
                cmds.intField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, editable=True, value=0, width=245, parent=layout_value)
            elif selected == "float":
                cmds.floatField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, editable=True, value=0, width=245, parent=layout_value)
            else:
                cmds.textField(UI_OPTIONS_PREDEFINED_USERATTRIBUTE_VALUE, width=245, editable=True, parent=layout_value)

            cmds.button(UI_CONTROL_BUTTON_USERATTRIBUTES_ADD_ATTRIBUTE, parent=attribute_layout, label='Add', width=126, align='right', command=self.saveObjectUserAttributes)

    def deleteObjectUserAttribute(self, name, unused):
        object_name = str(cmds.textField(UI_CONTROL_USERATTRIBUTES_STRING_NODE_NAME, q=True, text=True))
        object_key = object_name + "." + name

        if I3DAttributeExists(object_name, name):
            cmds.deleteAttr(object_key)

        self.loadObjectUserAttribute(None)

    def addTextFieldElement(self, parent, label, textFieldName, defaultValue='', annotation='', editable=True,
                            width=DEFAULT_FIELD_WIDTH):
        layout = cmds.rowLayout(textFieldName + 'layout', parent=parent, adjustableColumn=2, numberOfColumns=2)
        cmds.text(parent=layout, label=label, width=TEXT_WIDTH, align='left', annotation=annotation)
        cmds.textField(textFieldName, parent=layout, text=defaultValue, annotation=annotation, editable=editable,
                       width=width)


try:
    if not main is None:
        main.delete()
except NameError as e:
    pass

main = UserAttributes()
