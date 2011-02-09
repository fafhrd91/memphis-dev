import uuid
from zope import interface
from zope.event import notify
from zope.interface.declarations import Implements
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor

from memphis.storage import hooks
from memphis.storage.hooks import getSession
from memphis.storage.schema import Schema
from memphis.storage.behavior import Behavior
from memphis.storage.relation import Relation

from memphis.storage.interfaces import IItem
from memphis.storage.interfaces import BehaviorAppliedEvent
from memphis.storage.interfaces import BehaviorRemovedEvent
from memphis.storage.exceptions import BehaviorException

from memphis.storage.registry import getSchema, getBehavior, queryBehavior

_marker = object()


class ItemSpecification(ObjectSpecificationDescriptor):
    """ __providedBy__ decorator """

    def __get__(self, inst, cls=None):
        if inst is None:
            return getObjectSpecification(cls)

        cached = getattr(inst, '_v__providedBy', _marker)
        if cached is not _marker:
            return cached

        provided = []
        cache = {}
        for behavior in inst.behaviors:
            behavior = getBehavior(behavior)
            cache[behavior.spec] = behavior
            provided.append(behavior.spec)

        if provided:
            spec = Implements(*provided)
        else:
            spec = None

        inst._v__providedBy = spec
        inst._v__providedByCache = cache

        return spec


class Item(object):
    interface.implements(IItem)

    __providedBy__ = ItemSpecification()

    def __init__(self, oid, type=''):
        self.oid = oid
        self.type = type

    def __eq__(self, item):
        return self.oid == item.oid

    def __conform__(self, spec):
        # first try find directly applied behavior
        if not hasattr(self, '_v__providedBy'):
            provided = self.__providedBy__

        behavior = self._v__providedByCache.get(spec)
        if behavior is not None:
            return behavior(self)

        # probably item implements more specific behavior than `spec`
        behavior = queryBehavior((self.__providedBy__,), spec)
        if behavior is not None:
            return behavior(self)

    @classmethod
    def getItem(cls, oid):
        return getSession().query(Item).filter(Item.oid == oid).first()

    @classmethod
    def listItems(cls, type):
        return getSession().query(Item).filter(
            Item.type == getBehavior(type).name)

    @classmethod
    def insertItem(cls, type=''):
        if type:
            type = getBehavior(type).name

        oid = uuid.uuid1().hex
        item = Item(oid, type)

        session = getSession()
        session.add(item)
        if type:
            item.applyBehavior(type)
        session.flush()

        return Item.getItem(oid)

    @property
    def behaviors(self):
        return Behavior.getItemBehaviors(self.oid)

    @property
    def schemas(self):
        return Schema.getItemSchemas(self.oid)

    def getReferences(self, type=None):
        return Relation.getItemReferences(self.oid, type)

    def getBackReferences(self, type=None):
        return Relation.getItemBackReferences(self.oid, type)

    def applyBehavior(self, *args):
        for behavior in args:
            if hasattr(self, '_v__providedBy'):
                del self._v__providedBy
                del self._v__providedByCache

            behavior = getBehavior(behavior)
            behavior.apply(self)
            notify(BehaviorAppliedEvent(self, behavior.name, behavior.spec))

        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy
            del self._v__providedByCache

    def removeBehavior(self, *args):
        for behavior in args:
            if hasattr(self, '_v__providedBy'):
                del self._v__providedBy
                del self._v__providedByCache

            behavior = getBehavior(behavior)

            if behavior.name == self.type:
                raise BehaviorException("Can't remove primary behavior.")

            behavior.remove(self)
            notify(BehaviorRemovedEvent(self, behavior.name, behavior.spec))

        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy
            del self._v__providedByCache

    def applySchema(self, type):
        getSchema(type).apply(self.oid)

    def removeSchema(self, type):
        getSchema(type).remove(self.oid)

    def getDatasheet(self, name, apply=False):
        sch = getSchema(name)
        if apply or (sch.name in Schema.getItemSchemas(self.oid)):
            return sch.getDatasheet(self.oid)
        else:
            raise KeyError(name)


hooks.getItem = Item.getItem
