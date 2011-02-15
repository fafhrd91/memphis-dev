""" content container implementation """
from zope.event import notify
from zope import interface, component, schema
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectRemovedEvent

from memphis import config, storage
from exceptions import InvalidItemType
from interfaces import IBehaviorType, IContentContained, IContentContainer


class IContentContainerRelation(interface.Interface):
    """ content container relation  """
    storage.relation('content.container')

    name = schema.TextLine(
        title = u'Name',
        required = True)


class Contained(storage.BehaviorBase):
    interface.implements(IContentContained)

    storage.behavior('content.contained', relation=IContentContainerRelation,
                     title = u'Contained item',
                     description = u'Contained item for content container.')

    def __init__(self, item, relation):
        self.__context__ = item
        self.__relation__ = relation

        try:
            rel = self.__relation__.getReferences(
                destination=self.__context__.oid).next()
            self.__name__ = rel.name
            self.__parent__ = rel.__source__
        except StopIteration:
            self.__name__ = None
            self.__parent__ = None


class ContentContainer(storage.BehaviorBase):
    interface.implements(IContentContainer)

    storage.behavior('simple.container', relation=IContentContainerRelation,
                     type = IBehaviorType,
                     title = 'Container',
                     description = 'Allow contain other content types.')

    def __iter__(self):
        relation = self.__relation__
        for rel in relation.getReferences(self.__context__.oid):
            yield rel.name

    keys = __iter__

    def __getitem__(self, name):
        try:
            rel = self.__relation__.getReferences(
                self.__context__.oid, name=name).next()
            return rel.__destination__
        except StopIteration:
            pass
        raise KeyError(name)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            pass
        return default

    def values(self):
        relation = self.__relation__
        for rel in relation.getReferences(self.__context__.oid):
            yield rel.__destination__

    def __len__(self):
        return len(list(self.__relation__.getReferences(self.__context__.oid)))

    def items(self):
        for rel in self.__relation__.getReferences(self.__context__.oid):
            yield rel.name, rel.__destination__

    def __contains__(self, key):
        try:
            self.__relation__.getReferences(
                self.__context__.oid, name=key).next()
            return True
        except StopIteration:
            pass
        return False

    has_key = __contains__

    def __setitem__(self, name, object):
        if not IContentContained.providedBy(object):
            object.applyBehavior(IContentContained)

        if not isinstance(name, unicode):
            name = unicode(name)

        if not name:
            raise ValueError("empty names are not allowed")

        container = self.__context__

        old = self.get(name)
        if old and (old.oid == object.oid):
            return
        if old is not None:
            raise KeyError(name)

        contained = IContentContained(object)
        oldname = contained.__name__
        oldparent = contained.__parent__
        oldname = None
        oldparent = None

        if oldparent is None or oldname is None:
            event = ObjectAddedEvent(object, container, name)
        # fixme: fix moving item from one container to another
        #else:
        #    event = ObjectMovedEvent(
        #        object, oldparent, oldname, container, name)

        self.__relation__.insert(container.oid, object.oid, name=name)

        notify(event)

    def __delitem__(self, name):
        try:
            rel = self.__relation__.getReferences(
                self.__context__.oid, name=name).next()
        except StopIteration:
            raise KeyError(name)

        notify(ObjectRemovedEvent(rel.__destination__, self.__context__, name))

        self.__relation__.remove(rel.oid)
