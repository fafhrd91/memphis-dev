"""

$Id: pagelets.py 4711 2011-02-02 22:55:35Z nikolay $
"""
from zope import interface
from memphis import view
from memphis.ttwschema.interfaces import ISchema


class ISchemaView(interface.Interface):
    view.pageletType("memphis.ttwschema:view", ISchema)


class IAddFieldView(interface.Interface):
    view.pageletType("memphis.ttwschema:addfield", ISchema)
