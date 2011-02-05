"""

$Id: ttwschema.py 4730 2011-02-03 05:27:33Z nikolay $
"""
from zope import interface, schema
from zope.schema import getFieldNamesInOrder
from zope.lifecycleevent import IObjectModifiedEvent

from plone import supermodel

from memphis import config, storage, container
from memphis.ttwschema.interfaces import IField, ITTWSchema
from memphis.ttwschema.vocabulary import getFieldFactories


class DefaultSchema(interface.Interface):
    """ default empty schema """


class TTWSchema(storage.BehaviorBase):
    interface.implements(ITTWSchema, container.IContainer)
    storage.behavior('memphis.ttwschema', ITTWSchema, schema=ITTWSchema)

    def __init__(self, *args, **kw):
        super(TTWSchema, self).__init__(*args, **kw)

        self.datasheet = self.context.getDatasheet(ITTWSchema)
        if self.datasheet.model:
            self.schema = supermodel.loadString(self.datasheet.model).schema
        else:
            self.schema = DefaultSchema

    def keys(self):
        return getFieldNamesInOrder(self.schema)

    def values(self):
        schema = self.schema
        return [schema[name] for name in getFieldNamesInOrder(schema)]

    def items(self):
        return [(name, schema[name]) for name in getFieldNamesInOrder(schema)]

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, name):
        field = self.schema[name]
        field.ttwschema = self
        interface.directlyProvides(field, IField)
        return field

    def __setitem__(self, name, field):
        field.__name__ = name

        if self.schema._InterfaceClass__attrs.has_key(name):
            raise KeyError('Field already exists %s'%name)

        self.schema._InterfaceClass__attrs[name] = field
        self.datasheet.model = supermodel.serializeSchema(self.schema)        

    def __delitem__(self, name):
        pass

    def updateSchema(self):
        self.datasheet.model = supermodel.serializeSchema(self.schema)        
    

@config.handler(IField, IObjectModifiedEvent)
def fieldModifiedEvent(field, ev):
    field.ttwschema.updateSchema()
