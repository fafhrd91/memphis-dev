""" content type desc implementation """
from zope import interface, event
from zope.component import getAdapters, queryUtility, getUtility
from zope.lifecycleevent import ObjectCreatedEvent

from memphis import storage, config

from interfaces import _
from interfaces import IContent, IContentContainer, IFactoryProvider
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

        for schId in self.schemas:
            schema = queryUtility(storage.ISchema, schId)
            if schema is None:
                continue
            content.applySchema(schema.spec)
            #schema.apply(content.oid)

        ds = content.getDatasheet(IContent)
        if 'content.item' in data:
            ds.__load__(data['content.item'])
        ds.type = self.name

        for schId in self.schemas:
            if schId in data:
                ds = content.getDatasheet(schId)
                ds.__load__(data[schId])

        event.notify(ObjectCreatedEvent(content))
        return content


class FactoryProvider(object):
    interface.implements(IFactoryProvider)
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
