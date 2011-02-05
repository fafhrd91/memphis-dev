""" Smiple implementation for Application Root concept.

    >>> from memphis import storage

Register behavior

    >>> bh = api.registerBehavior("app.root", IRoot, Root)

Root item is automaticly created on the first access

    >>> item = getRoot()

    >>> IRoot.providedBy(item)
    True

    >>> isinstance(IRoot(item), Root)
    True

    >>> getRoot() == item
    True

It's not pssible to create more than one root item

    >>> item = api.insertItem('app.root')
    Traceback (most recent call last):
    ...
    BehaviorException: Can't create more than one root object.

Also root behavior can't be dropped

    >>> bh.remove(item)
    Traceback (most recent call last):
    ...
    BehaviorException: Can't remove app.root behavior.

$Id: root.py 11777 2011-01-30 07:41:52Z fafhrd91 $
"""
from zope import interface
from memphis import storage

from interfaces import IRoot

BEHAVIOR_NAME = 'app.root'


def getRoot():
    behavior = storage.getBehavior(IRoot)
    try:
        oid = behavior.getBehaviorOIDs().next()
        return storage.getItem(oid)
    except StopIteration:
        return storage.insertItem(IRoot)


class Root(storage.BehaviorBase):
    interface.implements(IRoot)
    storage.behavior(
        'app.root',
        title = u'Application root',
        description = u'Smiple implementation for Application Root concept')

    def __init__(self, item):
        self.item = item

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
