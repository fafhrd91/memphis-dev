""" control panel api """
from zope import interface
from zope.component.hooks import getSite

from BTrees.OOBTree import OOBTree

from memphis import config
from memphis.controlpanel.interfaces import IConfiglet


class Configlet(object):
    interface.implements(IConfiglet)

    @property
    def id(self):
        return self.__id__

    def getId(self):
        return self.__id__

    def Title(self):
        return self.__title__
    
    @property
    def __name__(self):
        return self.__id__

    @property
    def __data__(self):
        site = getSite()
        data = getattr(site.aq_base, '__cp_data__', None)
        if data is None:
            data = OOBTree()
            site.__cp_data__ = data
        
        cdata = data.get(self.__id__)
        if cdata is None:
            cdata = OOBTree()
            data[self.__id__] = cdata

        return cdata
