from zope import interface, event
from zope.component import getAdapters, queryUtility, getUtility
from zope.lifecycleevent import ObjectCreatedEvent

from memphis import storage, config, container

from interfaces import _, IContent, IContentContainer
from interfaces import IContentType, IContentTypeSchema, ISchemaType


config.action(
    storage.registerSchema,
    'content.item', IContent, title = 'Content item')


class Content(storage.BehaviorBase):
    interface.implements(IContent)
    storage.behavior('content.item',
                     schema = IContent,
                     title = 'Content item',
                     description = 'Base behavior for content item.')


class ContentType(storage.BehaviorBase):
    interface.implements(IContentType)
    storage.behavior('memphis.contenttype', schema=IContentTypeSchema)

    __name__ = ''
    __parent__ = None

    @property
    def name(self):
        return self.__context__.oid

    def __call__(self, **data):
        # create content with behaviors
        content = storage.insertItem(IContent)
        if self.behaviors:
            content.applyBehavior(*self.behaviors)

        ds = IContent(content)
        ds.type = self.name
        if 'content.item' in data:
            ds.title = data['content.item'].title
            ds.description = data['content.item'].description

        for schId in self.schemas:
            schema = queryUtility(storage.ISchema, schId)
            if schema is None:
                continue
            #content.applySchema(schema.spec)
            schema.apply(content.oid)
            if schId in data:
                ds = schema.getDatasheet(content.oid)
                ds.__load__(data[schId])

        event.notify(ObjectCreatedEvent(content))
        return content


class FactoryProvider(object):
    interface.implements(container.IFactoryProvider)
    config.adapts(IContentContainer, name='memphis.contenttype')

    def __init__(self, container):
        self.container = container

    def __iter__(self):
        for item in storage.listItems(IContentType):
            yield IContentType(item)

    def get(self, name, default=None):
        schema = storage.getSchema(IContentTypeSchema)

        item = schema.query(schema.Type.oid == name).first()
        if item is None:
            return default

        return IContentType(storage.getItem(item.oid))


@config.adapter(IContent)
@interface.implementer(IContentType)
def getContentType(item):
    content = IContent(item)
    
    schema = storage.getSchema(IContentTypeSchema)
    item = schema.query(schema.Type.oid == content.type).first()
    if item is not None:
        return IContentType(storage.getItem(item.oid))
