""" 

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope import interface, event
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from memphis import config, controlpanel, container, storage

from interfaces import ISchema, ISchemaManagement


class SchemaManagement(object):
    interface.implements(ISchemaManagement)

    def create(self, data):
        item = storage.insertItem(ISchema)
        ds = ISchema(item)
        for key, val in data.items():
            setattr(ds, key, val)

        ttwschema = ISchema(item)
        return container.LocationProxy(ds, self, item.oid)

    @property
    def schema(self):
        return storage.getSchema(ISchema)

    def keys(self):
        return [item.oid for item in self.schema.query()]

    def values(self):
        schemas = [item for item in self.schema.query()]
        for item in schemas:
            ISchema(storage.Item(item.oid)).installSchema()
        return [container.LocationProxy(item, self, item.oid) for item in schemas]

    def items(self):
        return [(item.oid, container.LocationProxy(item, self, item.oid))
                for item in self.schema.query()]

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def __iter__(self):
        return iter(self.keys())

    def __contains__(self, name):
        item = self.schema.query(self.schema.Type.oid==name).first()
        return item is not None

    def __getitem__(self, name):
        item = self.schema.query(self.schema.Type.oid==name).first()
        if item is None:
            raise KeyError(name)

        item = ISchema(storage.Item(item.oid))
        item.__parent__ = self
        
        return item


config.action(
    controlpanel.registerConfiglet,
    'system.schemas', ISchemaManagement, SchemaManagement,
    title = u'Schemas',
    description = u'TTW Schemas management configlet.')


class SchemaFactory(object):
    config.adapts(ISchemaManagement, 'schema')
    interface.implements(container.IFactory)

    name = 'schema'
    schema = ISchema
    title = 'TTW Schema'
    description = 'Schema object editable through the web.'
    hiddenFields = ('model',)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kw):
        pass
