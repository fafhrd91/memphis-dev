""" ttw content types management """
from zope import interface, event
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from memphis import controlpanel, storage
from memphis.contenttype.location import LocationProxy
from memphis.contenttype.interfaces import \
    IFactory, IContentType, IContentTypeSchema, IContentTypesConfiglet


class ContentTypeFactory(object):
    interface.implements(IFactory)

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
        ds = IContentTypeSchema(item)
        for key, val in data.items():
            setattr(ds, key, val)
        return LocationProxy(ds, self, item.oid)

    @property
    def schema(self):
        return storage.getSchema(IContentTypeSchema)

    def keys(self):
        return [item.oid for item in self.schema.query()]

    def values(self):
        return [LocationProxy(item, self, item.oid)
                for item in self.schema.query()]

    def items(self):
        return [(item.oid, LocationProxy(item, self, item.oid))
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

        return LocationProxy(item, self, item.oid)

    def __delitem__(self, name):
        pass


controlpanel.registerConfiglet(
    'system.contenttypes', IContentTypesConfiglet, 
    klass = ContentTypesConfiglet,
    title = 'Content types',
    description = 'Content types configuration.')
