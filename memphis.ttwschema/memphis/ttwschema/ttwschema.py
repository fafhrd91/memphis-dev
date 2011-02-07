"""

$Id: ttwschema.py 4730 2011-02-03 05:27:33Z nikolay $
"""
from zope import interface, schema
from zope.schema import getFieldNamesInOrder
from zope.lifecycleevent import IObjectModifiedEvent

from plone import supermodel

from memphis import config, storage, container
from memphis.ttwschema.interfaces import IField, ISchema, ISchemaType


class DefaultSchema(interface.Interface):
    """ default empty schema """


class Schema(storage.BehaviorBase):
    interface.implements(ISchema, container.IContainer)
    storage.behavior('memphis.schema', ISchema, schema=ISchema)

    def __init__(self, *args, **kw):
        super(Schema, self).__init__(*args, **kw)

        if self.model:
            self.schema = supermodel.loadString(self.model).schema
        else:
            self.schema = DefaultSchema

        for id in schema.getFields(self.schema):
            field = self.schema[id]
            field.__name__ = str(field.__name__)

    @property
    def __name__(self):
        return self.context.oid

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
        field.__name__ = str(name)
        field.__parent__ = self
        interface.directlyProvides(field, IField)
        return field

    def __setitem__(self, name, field):
        field.__name__ = name

        if self.schema._InterfaceClass__attrs.has_key(name):
            raise KeyError('Field already exists %s'%name)

        self.schema._InterfaceClass__attrs[name] = field
        self.model = unicode(supermodel.serializeSchema(self.schema))

    def __delitem__(self, name):
        pass

    def updateSchema(self):
        self.model = supermodel.serializeSchema(self.schema)

    def installSchema(self):
        print '---install---', self.title
        # warning
        storage.registerSchema(
            self.context.oid, self.schema, 
            type=ISchemaType, title=self.title, description=self.description)
    

@config.handler(IField, IObjectModifiedEvent)
def fieldModifiedEvent(field, ev):
    field.ttwschema.updateSchema()


@config.handler(storage.IStorageInitializedEvent)
def storageInitializedEvent(ev):
    sch = storage.getSchema(ISchema)
    
    for item in sch.query(sch.Type.published == True):
        ttwschema = ISchema(storage.getItem(item.oid))
        ttwschema.installSchema()
