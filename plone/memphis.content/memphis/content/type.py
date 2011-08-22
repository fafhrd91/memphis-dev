""" type implementation """
import sys
from memphis import config
from memphis.config.directives import getInfo

from zope import interface, event
from zope.interface.interface import InterfaceClass
from zope.component import queryUtility, getUtilitiesFor
from zope.lifecycleevent import ObjectCreatedEvent

import Products
from Acquisition import aq_base
from Products.CMFCore.interfaces import ITypeInformation

from instance import Instance
from datasheet import Datasheet
from cmftinfo import TypeInformation
from directives import behavior
from registry import getSchema, getBehavior, BehaviorBase
from exceptions import BehaviorException, SchemaNotFound
from interfaces import _, IContent, IContentSchema, IContentType
from interfaces import BehaviorAppliedEvent, BehaviorRemovedEvent


def getType(name):
    ti = registered.get(name)
    if ti is not None:
        return ti

    # fixme: should return special type "broken" or "unavailable"
    return ti


class Content(BehaviorBase):
    interface.implements(IContent)
    behavior('content.instance',
             schema = IContentSchema,
             title = 'Content instance',
             description = 'Base behavior for content instance.')


class ContentType(TypeInformation):
    """ memphis content type """
    interface.implements(IContentType)

    def __init__(self, bh, name, factory, 
                 behaviors=(), schemas=(), **kw):
        self.type = bh
        self.factory = factory
        self.schemas = []
        self.behaviors = []

        self._completed = False
        self._completion = [(1, (bh,))]

        if behaviors:
            self._completion.append((1, behaviors))
        if schemas:
            self._completion.append((2, schemas))

        super(ContentType, self).__init__(name, **kw)

    def __reduce__(self):
        return getType, (self.id,)

    def _complete(self):
        self._completed = True

        # complete registrations
        for c, args in self._completion:
            if c == 1:
                self.applyBehavior(*args)
        for c, args in self._completion:
            if c == 2:
                self.applySchema(*args)

        self._completion = []

    def create(self, **data):
        instance = Instance(aq_base(self))

        # load datasheets
        for schId in self.schemas:
            if schId in data:
                if isinstance(data[schId], Datasheet):
                    ds = instance.getDatasheet(schId)
                    ds.__load__(data[schId])

        event.notify(ObjectCreatedEvent(instance))
        return instance

    def applyBehavior(self, *args):
        if not self._completed:
            self._completion.append((1, args))
            return

        for behavior in args:
            bh = getBehavior(behavior)
            if bh.name in self.behaviors:
                raise BehaviorException(behavior)

            self.behaviors.append(bh.name)
            if bh.schema:
                self.applySchema(bh.schema)

            event.notify(BehaviorAppliedEvent(self, bh.name, bh.spec))

        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy

    def removeBehavior(self, *args):
        for behavior in args:
            bh = getBehavior(behavior)
            if (bh.name == self.type) or (bh.spec == self.type):
                raise BehaviorException("Can't remove primary behavior")

            if bh.name not in self.behaviors:
                raise BehaviorException("Behavior is not applied: %s"%bh.name)

            self.behaviors.remove(bh.name)
            if bh.schema:
                self.removeSchema(bh.schema)
            event.notify(BehaviorRemovedEvent(self, bh.name, bh.spec))

        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy

    def applySchema(self, sch):
        if not self._completed:
            self._completion.append((2, (sch,)))
            return

        name = None
        if isinstance(sch, InterfaceClass):
            name = sch.queryTaggedValue('__sch_name__')
            if not name:
                raise SchemaNotFound(sch)
        else:
            name = getSchema(sch).name

        if name not in self.schemas:
            self.schemas.append(name)

            if hasattr(self, '_v__providedBy'):
                del self._v__providedBy

    def removeSchema(self, sch):
        sch = getSchema(sch)
        if sch.name not in self.schemas:
            raise KeyError(sch.spec)

        self.schemas.remove(sch.name)
        if hasattr(self, '_v__providedBy'):
            del self._v__providedBy


def registerType(
    name,
    behavior = 'content.instance',
    factory = Instance,
    schemas = (),
    behaviors = (),
    title = '',
    description = '', 
    global_allow = True, 
    permission = 'View', 
    actions = None,
    **kw):

    if name in registered:
        raise ValueError('Content type "%s" already registered.'%name)

    if not title:
        title = name

    if 'add_view_expr' not in kw:
        kw['add_view_expr'] = 'string:${object_url}/++content++%s'%name

    if 'icon_expr' not in kw:
        kw['icon_expr'] = 'string:${portal_url}/document_icon.png'

    if actions is None:
        actions = (
            {'id': 'view',
             'title': 'View',
             'action': 'string:${object_url}',
             'visible': True,
             'permissions': ('View',)},
            {'id': 'edit',
             'title': 'Edit',
             'action': 'string:${object_url}/edit.html',
             'visible': True,
             'permissions': ('Modify portal content',)},
            )

    ti = ContentType(
        behavior, name, factory, 
        behaviors = behaviors,
        schemas = schemas,
        title = title,
        description = description,
        content_meta_type = name,
        global_allow = global_allow,
        permission = permission,
        actions = actions,
        **kw)

    registered[name] = ti

    def completeRegistration():
        config.registerUtility(ti, ITypeInformation, name)

        # register zope2 meta_type
        info = {'name': name,
                'action': '',
                'product': 'memphis.content',
                'permission': permission,
                'visibility': 'Global',
                'interfaces': interface.Interface,
                'instance': None,
                'container_filter': None}

        meta_types = getattr(Products, 'meta_types', ())
        meta_types += (info,)
        Products.meta_types = meta_types

        ti._complete()

    frame = sys._getframe(1)

    config.action(
        completeRegistration,
        __frame = frame,
        __info = config.getInfo(2),
        __discriminator = ('memphis.content:type', name),
        __order = (config.moduleNum(frame.f_locals['__name__']), 990))

    return ti


registered = {}

@config.cleanup
def cleanUp():
    registered.clear()
