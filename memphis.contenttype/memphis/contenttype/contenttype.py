from zope import interface, event
from zope.component import \
    getAdapters, getUtility, queryUtility, getUtilitiesFor

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
                     description = 'Base behavior for content items.')


class ContentType(storage.BehaviorBase):
    interface.implements(IContentType)
    storage.behavior('memphis.contenttype', schema=IContentTypeSchema)

    __name__ = ''
    __parent__ = None

    @property
    def name(self):
        return self.context.oid

    def __call__(self, **data):
        # create content with behaviors
        content = storage.insertItem(IContent)
        if self.behaviors:
            content.applyBehavior(*self.behaviors)
        content.getDatasheet(IContent).type = self.name

        for schema in self.schemas:
            sch = getUtility(storage.ISchema, schema)
            content.applySchema(sch.specification, True)

        # update datasheets
        for name, ds in data.items():
            datasheet = content.getDatasheet(name)
            if datasheet is not None:
                datasheet.__load__(ds)

        event.notify(ObjectCreatedEvent(content))
        return content

    def isAddable(self):
        if not IBoundContentType.providedBy(self):
            return False

        for name, checker in getAdapters(
            (self, self.context), IContentTypeChecker):
            if not checker.check():
                return False
        else:
            return True

    def isAvailable(self):
        if not IBoundContentType.providedBy(self):
            return False

        for name, checker in getAdapters(
            (self, self.context), IContentTypeChecker):
            if not checker.check():
                return False
        else:
            return True


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
