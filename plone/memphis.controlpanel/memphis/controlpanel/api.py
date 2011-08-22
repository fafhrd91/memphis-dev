""" control panel api """
import sys
from zope import interface
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.PloneControlPanel import PloneConfiglet

from memphis import config
from memphis.controlpanel.cptype import ConfigletType
from memphis.controlpanel.configlet import Configlet
from memphis.controlpanel.interfaces import IConfiglet, IPloneConfiglet


def registerConfiglet(name, schema=None, klass=None, 
                      title='', description='', 
                      category = 'Products', permission = 'Manage portal'):

    if not title:
        title = name

    ConfigletClass = ConfigletType(
        str(name), schema, klass, title, description)
    interface.classImplements(ConfigletClass, schema)

    ConfigletClass.permission = permission

    def completeRegistration():
        # configlet instance
        inst = ConfigletClass()

        # register configlet as utility
        config.registerUtility(inst, schema, '')
        config.registerUtility(inst, IConfiglet, name)

        # register plone configlet
        ai = PloneConfiglet(
            name,
            id = name,
            title = title, 
            description = description, 
            permissions = (permission,),
            action = Expression(
                text=u"python:'%%s/++cp++%s/'%%%s"%(name, 'portal_url')),
            category = category,
            )

        config.registerUtility(ai, IPloneConfiglet, name)

    frame = sys._getframe(1)

    config.action(
        completeRegistration,
        __frame = frame,
        __discriminator = ('memphis.content:configlet', name),
        __order = (config.moduleNum(frame.f_locals['__name__']), 992))
