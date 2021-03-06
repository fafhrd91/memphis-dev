""" Configlet implementation """
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

    # __oid__ is item for configlet, this is optimization
    # memphis.storage can cache Item.getItem call, 
    # but Behavior.getBehaivorOIDs is not cacheable.
    # __oid__ for configlet is never changing
    __oid__ = None

    @property
    def __name__(self):
        return self.__id__

    @property
    def __item__(self):
        try:
            if self.__oid__ is None:
                self.__oid__ = self.__behavior__.getBehaviorOIDs().next()
            item = storage.getItem(self.__oid__)
        except StopIteration:
            item = storage.insertItem(self.__behavior__.name)
            self.__oid__ = item.oid

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
