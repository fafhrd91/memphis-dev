""" content instance """
from BTrees.OOBTree import OOBTree

from zope import interface
from zope.interface.adapter import AdapterRegistry
from zope.interface.declarations import Implements, implementedBy
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor

from cmfmixin import CMFMixin
from interfaces import IInstance
from registry import queryBehavior, getSchema, querySchema

_marker = object()


class InstanceSpecification(ObjectSpecificationDescriptor):
    """ Instance __providedBy__ decorator """

    def __get__(self, inst, cls=None):
        if inst is None:
            return getObjectSpecification(cls)

        tp = inst.__type__
        cached = getattr(tp, '_v__providedBy', _marker)
        if cached is not _marker:
            return cached

        provided = [implementedBy(inst.__class__)]
        bhreg = AdapterRegistry()
        for behavior in tp.behaviors:
            behavior = queryBehavior(behavior)
            if behavior is not None:
                bhreg.register((), behavior.spec, '', behavior)
                provided.append(behavior.spec)

        schreg = AdapterRegistry()
        for schId in tp.schemas:
            sch = querySchema(schId)
            if sch is not None and sch.spec not in provided:
                schreg.register((), sch.spec, '', sch)
                provided.append(sch.spec)

        spec = Implements(*provided)

        tp._v__providedBy = spec
        tp._v__bhCache = bhreg
        tp._v__schCache = schreg

        return spec


class Instance(CMFMixin):
    interface.implements(IInstance)

    __type__ = None
    __providedBy__ = InstanceSpecification()

    def __init__(self, ti):
        self.__type__ = ti
        self.__datasheets__ = OOBTree()

    def __conform__(self, spec):
        ti = self.__type__
        if ti is None:
            return

        # first try find directly applied behavior
        provided = self.__providedBy__

        # lookup for behavior
        bh = ti._v__bhCache.lookup((), spec)
        if bh is not None:
            return bh(self)

        # lookup for schema
        sch = ti._v__schCache.lookup((), spec)
        if sch is not None:
            return sch(self)

    def getDatasheet(self, name):
        sch = getSchema(name)
        if sch.name in self.__type__.schemas:
            return sch(self)
        else:
            raise KeyError(name)
