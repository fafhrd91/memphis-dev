"""

$Id: container.py 11771 2011-01-29 22:56:56Z fafhrd91 $
"""
from zope.event import notify
from zope import interface, component, schema
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectRemovedEvent

from memphis import config, storage
from exceptions import InvalidItemType
from interfaces import IContained, ISimpleContainer


class ISimpleContainerRelation(interface.Interface):
    """ sample container relation  """
    storage.relation('simple.container')

    name = schema.TextLine(
        title = u'Name',
        required = True)


class Contained(storage.BehaviorBase):
    interface.implements(IContained)

    storage.behavior('sample.contained', relation=ISimpleContainerRelation,
                     title = u'Contained item',
                     description = u'Contained item for sample container.')

    def __init__(self, item, relation):
        self.context = item
        self.relation = relation

        try:
            rel = self.relation.getRelations(destination=self.context).next()
            self.__name__ = rel.name
            self.__parent__ = rel.__source__
        except StopIteration:
            self.__name__ = None
            self.__parent__ = None


class Container(storage.BehaviorBase):
    interface.implements(ISimpleContainer)

    storage.behavior('sample.container', relation=ISimpleContainerRelation,
                     title = u'Container',
                     description = u'Sample container behavior.')

    def __init__(self, item, relation):
        self.context = item
        self.relation = relation

    def __iter__(self):
        relation = self.relation
        for rel in relation.getRelations(self.context):
            yield rel.name

    keys = __iter__

    def __getitem__(self, name):
        try:
            rel = self.relation.getRelations(self.context, name=name).next()
            return rel.__destination__
        except StopIteration:
            pass
        raise KeyError(name)

    def get(self, key, default=None):
        try:
            rel = self.relation.getRelations(self.context, name=key).next()
            return rel.__destination__
        except StopIteration:
            pass
        return default

    def values(self):
        relation = self.relation
        for rel in relation.getRelations(self.context):
            yield rel.__destination__

    def __len__(self):
        data = [r for r in self.relation.getRelations(self.context)]
        if data is not None:
            return len(data)
        return 0

    def items(self):
        for rel in self.relation.getRelations(self.context):
            yield rel.name, rel.__destination__

    def __contains__(self, key):
        try:
            self.relation.getRelations(self.context, name=key).next()
            return True
        except StopIteration:
            pass
        return False

    has_key = __contains__

    def __setitem__(self, name, object):
        if not IContained.providedBy(object):
            raise InvalidItemType("Item has to implement IContained interface")

        if not isinstance(name, unicode):
            name = unicode(name)

        if not name:
            raise ValueError("empty names are not allowed")

        container = self.context

        old = self.get(name)
        if old and (old.oid == object.oid):
            return
        if old is not None:
            raise KeyError(name)

        contained = IContained(object)
        oldname = contained.__name__
        oldparent = contained.__parent__
        oldname = None
        oldparent = None

        if oldparent is None or oldname is None:
            event = ObjectAddedEvent(object, container, name)
        else:
            event = ObjectMovedEvent(
                object, oldparent, oldname, container, name)

        self.relation.insert(container, object, name=name)

        notify(event)

    def __delitem__(self, name):
        try:
            rel = self.relation.getRelations(self.context, name=name).next()
        except StopIteration:
            raise KeyError(name)

        notify(ObjectRemovedEvent(rel.__destination__, self.context, name))

        self.relation.remove(rel.oid)
