from zope import interface, event
from zope.component import \
    getAdapters, getUtility, queryUtility, getUtilitiesFor

from zope.lifecycleevent import ObjectCreatedEvent

from memphis import storage, config, container

from interfaces import _, IContent, IContentContainer
from interfaces import IContentType, IContentTypeSchema, IBoundContentType


class ContentType(storage.BehaviorBase):
    interface.implements(IContentType)
    storage.behavior('memphis.contenttype', schema=IContentTypeSchema)

    __name__ = ''
    __parent__ = None

    @property
    def name(self):
        return self.context.oid

    def add(self, content, name=''):
        context = IContentContainer(self.context)

        #print list(content.behaviors)
        #print list(interface.providedBy(content))
        #from memphis.storage.interfaces import IContained
        #print IContained.providedBy(content)

        idx = 0
        name = 'item%s'%idx
        while name in context:
            idx += 1
            name = 'item%s'%idx

        context[name] = content
        return content

    def __call__(self, **data):
        # create content with behaviors
        content = storage.insertItem(IContent)
        if self.behaviors:
            content.applyBehavior(*self.behaviors)
        content.getDatasheet(IContent).type = self.name

        for schema in self.schemas:
            sch = getUtility(storage.ISchema, schema)
            content.applySchema(sch.specification)

        # update datasheets
        #for ds in datasheets:
        #    datasheet = content.queryDatasheet(ds.__id__)
        #    if datasheet is not None:
        #        datasheet.__load__(ds)

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
