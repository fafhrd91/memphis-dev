"""

$Id: preference.py 102668 2009-08-11 10:27:43Z fafhrd $
"""
import sqlalchemy
from zope import interface
from memphis import storage

from interfaces import UnboundPreferenceGroup
from interfaces import IPreference, IPreferenceCategory, IBound

_marker = object()


class Preference(object):
    interface.implements(IPreference)

    __data__ = None
    __principal__ = None

    def __init__(self, tests=()):
        self.__tests__ = tests

    @property
    def __name__(self):
        return self.__id__

    @property
    def __data__(self):
        if not IBound.providedBy(self):
            raise UnboundPreferenceGroup(self.__id__)

        # set principal data
        data = self.principal.getDatasheet(self.__schema__, apply=True)

        self.__dict__['__data__'] = data
        return data

    def __bind__(self, principal):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.principal = principal

        interface.alsoProvides(clone, IBound)
        return clone

    def isAvailable(self):
        for test in self.__tests__:
            if not test(self):
                return False

        return True


class PreferenceCategory(dict):
    interface.implements(IPreferenceCategory)

    context = None

    def __init__(self, name, title, description):
        self.__name__ = name
        self.title = title
        self.description = description

    def addPreference(self, prefs):
        if prefs.__id__ in self:
            raise KeyError(prefs.__id__)

        prefs.__parent__ = self
        self[prefs.__id__] = prefs

    def __getitem__(self, name):
        pref = super(PreferenceCategory, self).__getitem__(name)

        if self.context is not None:
            pref = pref.__bind__(self.context)
            pref.__parent__ = self

        return pref
