""" Configlet implementation

$Id: configlet.py 11791 2011-01-31 02:57:54Z fafhrd91 $
"""
from zope import interface
from memphis import storage
from memphis.controlpanel.interfaces import IConfiglet, IConfigletData


class BehaviorFactory(object):

    def __init__(self, id, bid):
        self.id = id
        self.bid = bid

    def __call__(self, item):
        raise RuntimeError("Configlet behavior can't be called directly.")

    def applyBehavior(self, item, behavior):
        try:
            behavior.getBehaviorOIDs().next()
            raise storage.BehaviorException(
                "Can't create more than one configlet: %s"%self.id)
        except StopIteration:
            pass


class Configlet(object):
    interface.implements(IConfiglet)

    @property
    def __name__(self):
        return self.__id__

    @property
    def __item__(self):
        try:
            oid = self.__behavior__.getBehaviorOIDs().next()
            item = storage.getItem(oid)
        except StopIteration:
            item = storage.insertItem(self.__behavior__.name)

        return item

    @property
    def datasheet(self):
        return IConfigletData(self.__item__)

    def isAvailable(self):
        return True


class ConfigletCategory(dict):

    def __init__(self, name, title, description):
        self.__name__ = name
        self.title = title
        self.description = description

    def addConfiglet(self, configlet):
        if configlet.__id__ in self:
            raise KeyError(configlet.__id__)

        configlet.__parent__ = self

        self[configlet.__id__] = configlet

    def __repr__(self):
        return "Category <%s>"%self.__name__
