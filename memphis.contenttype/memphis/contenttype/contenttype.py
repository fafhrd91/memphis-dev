""" IContentType implementation

$Id: contenttype.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope import interface, event
from zope.component import \
    getAdapters, getUtility, queryUtility, getUtilitiesFor

from zope.lifecycleevent import ObjectCreatedEvent
#from zope.container.interfaces import INameChooser, IContainerNamesContainer

from memphis import storage

from interfaces import _
from interfaces import IContent, IContainer
from interfaces import IBoundContentType, IContentType, IContentTypeChecker
from interfaces import IContentTypeSchema


class Content(object):
    """ default content behavior """
    interface.implements(IContent)

    def __init__(self, item, relation=None):
        self.item = item
        self.relation = relation


class ContentType(object):
    interface.implements(IContentType)

    __name__ = ''
    __parent__ = None

    context = None

    def __init__(self, name, spec, behaviors, schemas, title, description):
        self.name = name
        self.specification = spec
        self.schemas = schemas
        self.behaviors = behaviors
        self.title = title
        self.description = description

    def __bind__(self, context):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.context = context
        if context is not None:
            interface.alsoProvides(clone, IBoundContentType)
        return clone

    def __str__(self):
        if IBoundContentType.providedBy(self):
            return "<BoundContentType:%s.%s %s '%s'>"%(
                self.__class__.__module__, self.__class__.__name__,
                self.name, self.title)
        else:
            return "<ContentType:%s.%s %s '%s'>"%(
                self.__class__.__module__, self.__class__.__name__,
                self.name, self.title)

    @property
    def container(self):
        return self.context

    def checkObject(self, container, name, content):
        return checkObject(container, name, content)

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

    def create(self, *datasheets):
        # create content with behaviors
        content = storage.insertItem('content.type', 'content.item')
        if self.behaviors:
            content.applyBehavior(*self.behaviors)
        content.getDatasheet('content.type').type = self.name

        for schema in self.schemas:
            content.applySchema(schema)

        # update datasheets
        for ds in datasheets:
            datasheet = content.queryDatasheet(ds.__id__)
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

    def listContainedTypes(self, checkAvailability=True):
        if IBoundContentType.providedBy(self):
            context = self.context
            if not IContentContainer.providedBy(context):
                return

            precondition = IItemTypePrecondition(self, None)
            if precondition is not None:
                contenttypes = []
                for tp in precondition.types:
                    ct = queryUtility(IContentType, tp)
                    if ct is not None and ct not in contenttypes:
                        contenttypes.append(ct)

                for tp in precondition.ifaces:
                    for name, ct in getUtilitiesFor(tp):
                        if ct not in contenttypes:
                            contenttypes.append(ct)

                for contenttype in contenttypes:
                    contenttype = contenttype.__bind__(context)

                    explicit = True
                    if IExplicitlyAddable.providedBy(contenttype):
                        explicit = False
                        for tp in precondition.ifaces:
                            if tp not in (IActiveType, IExplicitlyAddable)\
                                    and tp.providedBy(contenttype):
                                explicit = True
                                break

                        for tp in precondition.types:
                            if contenttype.name == tp:
                                explicit = True
                                break

                    if explicit:
                        # check the container constraint
                        validate = queryUtility(
                            IContainerTypesConstraint, contenttype.name)
                        if validate is not None:
                            try:
                                validate(self)

                                if not checkAvailability:
                                    yield contenttype

                                elif contenttype.isAvailable():
                                    yield contenttype
                            except InvalidContainerType:
                                pass
                        else:
                            if not checkAvailability:
                                yield contenttype

                            elif contenttype.isAvailable():
                                yield contenttype



class ContentTypeBehaviorFactory(storage.BehaviorFactoryBase):
    storage.behavior('content.type', IContentType,
                     title = 'Content type',
                     description = 'Content type behavior',
                     schema = IContentTypeSchema)

    def removeBehavior(self, item):
        raise storage.BehaviorException("Can't remove content.type behavior.")

    def __call__(self, item):
        ct = getUtility(IContentType, item.getDatasheet('content.type').type)
        return ct.__bind__(item)
