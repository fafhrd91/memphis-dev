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

from memphis.storage.registry import getSchema, querySchema
from memphis.storage.registry import getBehavior, queryBehavior

from memphis.storage.interfaces import ISchemaWrapper, IBehaviorWrapper

_marker = object()

from zope.interface.adapter import AdapterRegistry


class ItemSpecification(ObjectSpecificationDescriptor):
    """ __providedBy__ decorator """

    def __get__(self, inst, cls=None):
        if inst is None:
            return getObjectSpecification(cls)

        cached = getattr(inst, '_v__providedBy', _marker)
        if cached is not _marker:
            return cached

        provided = []
        bhreg = AdapterRegistry()
        for behavior in inst.behaviors:
            behavior = queryBehavior(behavior)
            if behavior is not None:
                bhreg.register((), behavior.spec, '', behavior)
                provided.append(behavior.spec)

        schreg = AdapterRegistry()
        for schId in inst.schemas:
            sch = querySchema(schId)
            if sch is not None and sch.spec not in provided:
                schreg.register((), sch.spec, '', sch)
                provided.append(sch.spec)

        if provided:
            spec = Implements(*provided)
        else:
            spec = None

        inst._v__providedBy = spec
        inst._v__bhCache = bhreg
        inst._v__schCache = schreg

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
        provided = self.__providedBy__

        # lookup for behavior
        bh = self._v__bhCache.lookup((), spec)
        if bh is not None:
            wrapper = self._v__bhCache.lookup((), IBehaviorWrapper)
            if wrapper is not None:
                return wrapper(self).wrapBehavior(bh, self)
            return bh(self)

        # lookup for schema
        sch = self._v__schCache.lookup((), spec)
        if sch is not None:
            wrapper = self._v__bhCache.lookup((), ISchemaWrapper)
            if wrapper is not None:
                return wrapper(self).wrapSchema(sch, self)
            return sch(self)

    @classmethod
    def getItem(cls, oid):
        item = getSession().query(Item).filter(Item.oid == oid).first()
        if item is None:
            raise KeyError(oid)
        return item

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

    def remove(self):
        # fixme: it too explicite, it do a lot of db queries
        # this method has to be simplier 

        self.type = ''

        # first remove behavior, because behavior can remove some of schemas
        behaviors = self.behaviors
        while behaviors:
            self.removeBehavior(behaviors[0])
            behaviors = self.behaviors

        for schId in self.schemas:
            self.removeSchema(schId)

        session = getSession()
        session.delete(self)
        session.flush()

    def getReferences(self, type=None):
        return Relation.getItemReferences(self.oid, type)

    def getBackReferences(self, type=None):
        return Relation.getItemBackReferences(self.oid, type)

    def applyBehavior(self, *args):
        for behavior in args:
            if hasattr(self, '_v__providedBy'):
                del self._v__providedBy

            behavior = getBehavior(behavior)
            behavior.apply(self)
            notify(BehaviorAppliedEvent(self, behavior.name, behavior.spec))

        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy

    def removeBehavior(self, *args):
        for behavior in args:
            if hasattr(self, '_v__providedBy'):
                del self._v__providedBy

            behavior = getBehavior(behavior)

            if behavior.name == self.type:
                raise BehaviorException("Can't remove primary behavior.")

            behavior.remove(self)
            notify(BehaviorRemovedEvent(self, behavior.name, behavior.spec))

        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy

    def applySchema(self, type):
        getSchema(type).apply(self.oid)
        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy

    def removeSchema(self, type):
        getSchema(type).remove(self.oid)
        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy

    def getDatasheet(self, name, apply=False):
        sch = getSchema(name)
        if apply or (sch.name in Schema.getItemSchemas(self.oid)):
            wrapper = ISchemaWrapper(self, None)
            if wrapper is not None:
                return wrapper.wrapSchema(sch, self)
            return sch(self)
        else:
            raise KeyError(name)


hooks.getItem = Item.getItem
