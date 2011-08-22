""" memphis controlpanel interfaces """
from zope import interface


class IConfiglet(interface.Interface):
    """ configlet interface """

    __id__ = interface.Attribute('id')

    __title__ = interface.Attribute('title')

    __description__ = interface.Attribute('Description')

    __schema__ = interface.Attribute('Configlet schema')

    __data__ = interface.Attribute('Data dictionary')


class IPloneConfiglet(interface.Interface):
    """ marker interface for plone configlet """
