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
    <memphis.container.root.ContainedRoot ...>

$Id: root.py 11777 2011-01-30 07:41:52Z fafhrd91 $
"""
from zope import interface
from memphis import storage, config, view, container
from memphis.container.simple import ISimpleContainerRelation

from interfaces import IRoot
from container import ContentContainer


def getRoot():
    behavior = storage.getBehavior(IRoot)
    try:
        oid = behavior.getBehaviorOIDs().next()
        return IRoot(storage.getItem(oid))
    except StopIteration:
        return IRoot(storage.insertItem(IRoot))


class Root(ContentContainer):
    interface.implements(IRoot, view.IRoot, container.IContained)
    storage.behavior(
        'app.root',
        relation = ISimpleContainerRelation,
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
