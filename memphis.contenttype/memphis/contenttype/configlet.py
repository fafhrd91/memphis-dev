from zope import interface, event
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from memphis import config, controlpanel, container, storage
from memphis.contenttype.interfaces import \
    IContentType, IContentTypeSchema, IContentTypesConfiglet


class ContentTypeFactory(object):
    interface.implements(container.IFactory)

    name = 'ct'
    schema = IContentTypeSchema
    title = 'Content Type'
    description = ''
    hiddenFields = ('name', 'schemas', 'behaviors')

    def __call__(self, **kw):
        pass


class ContentTypesConfiglet(object):
    interface.implements(IContentTypesConfiglet)

    __factories__ = {'ct': ContentTypeFactory()}

    def create(self, data):
        item = storage.insertItem(IContentType)
        ds = item.getDatasheet(IContentTypeSchema)
        for key, val in data.items():
            setattr(ds, key, val)
        return container.LocationProxy(ds, self, item.oid)

    @property
    def schema(self):
        return storage.getSchema(IContentTypeSchema)

    def keys(self):
        return [item.oid for item in self.schema.query()]

    def values(self):
        return [container.LocationProxy(item, self, item.oid)
                for item in self.schema.query()]

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

        return container.LocationProxy(item, self, item.oid)

    def __delitem__(self, name):
        pass


config.action(
    controlpanel.registerConfiglet,
    'system.contenttypes', IContentTypesConfiglet, 
    klass = ContentTypesConfiglet,
    title = 'Content types',
    description = 'Content types configuration.')
