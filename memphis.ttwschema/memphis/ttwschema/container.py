"""

$Id: container.py 4711 2011-02-02 22:55:35Z nikolay $
"""
from zope import interface
from memphis import storage

from interfaces import ITTWSchemaContainer


class ITTWSchemaRelation(interface.Interface):
    storage.relation('memphis.ttwschema.container')


class TTWSchemaContainer(storage.BehaviorBase):
    storage.behavior('schema.container', ITTWSchemaContainer,
                     relation=ITTWSchemaRelation)
