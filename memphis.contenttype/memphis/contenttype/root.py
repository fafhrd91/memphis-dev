""" Smiple implementation for Application Root concept.

    >>> from memphis import storage

Root item is automaticly created on the first access

    >>> item = getRoot()

    >>> IRoot.providedBy(item)
    True

    >>> isinstance(IRoot(item), Root)
    True

    >>> getRoot() == item
    True

It's not pssible to create more than one root item

    >>> item = storage.insertItem('app.root')
    Traceback (most recent call last):
    ...
    BehaviorException: Can't create more than one root object.

Also root behavior can't be dropped

    >>> storage.getBehavior(IRoot).remove(item)
    Traceback (most recent call last):
    ...
    BehaviorException: Can't remove app.root behavior.

Contained

    >>> IContained(item)
    <memphis.contenttype.root.ContainedRoot ...>

"""
from zope import interface, event
from zope.lifecycleevent import ObjectCreatedEvent

from memphis import storage, config, view

from interfaces import IRoot, IContent, IContained
from location import LocationProxy
from container import ContentContainer, IContentContainerRelation


rootOID = None

def getRoot():
    global rootOID

    behavior = storage.getBehavior(IRoot)
    try:
        if rootOID is None:
            rootOID = behavior.getBehaviorOIDs().next()
        return LocationProxy(storage.getItem(rootOID), None, '')
    except StopIteration:
        item = storage.insertItem(IRoot)
        rootOID = item.oid
        dc = IContent(item)
        dc.title = u'Site'
        dc.description = u'Default memphis site.'

        event.notify(ObjectCreatedEvent(item))
        return LocationProxy(item, None, '')


class Root(ContentContainer):
    interface.implements(IRoot, IContained)
    storage.behavior(
        'app.root',
        schema = IContent,
        relation = IContentContainerRelation,
        title = u'Application root',
        description = u'Smiple implementation for Application Root concept')

    __name__ = ''
    __parent__ = None

    @classmethod
    def applyBehavior(cls, item, behavior):
        try:
            behavior.getBehaviorOIDs().next()
            raise storage.BehaviorException(
                "Can't create more than one root object.")
        except StopIteration:
            pass

    @classmethod
    def removeBehavior(cls, item, behavior):
        raise storage.BehaviorException("Can't remove app.root behavior.")
