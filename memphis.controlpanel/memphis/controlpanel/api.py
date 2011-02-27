""" control panel registation api """
import sys
from zope import interface
from zope.component import getUtility

from memphis import storage, config
from memphis.controlpanel import configlet, configlettype
from memphis.controlpanel.interfaces import IControlPanel, IConfigletData


def getControlPanel(*args):
    return getUtility(IControlPanel)


def registerCategory(name, marker=None, title='', description='',):
    def _register(name, marker, title, description):
        category = configlet.ConfigletCategory(name, title, description)

        if marker is not None:
            interface.directlyProvides(category, marker)

        getUtility(IControlPanel).addCategory(category)

    # add config action
    frame = sys._getframe(1)

    config.action.store.set(
        frame.f_locals, config.action,
        (_register, (name, marker, title, description),
         {'discriminator': ('controlpanel:category', name)},
         config.getInfo()))

    del frame


def registerConfiglet(name=None, schema=None, klass=None,
                      title='', description=''):
    if '.' in name:
        category, name = name.split('.', 1)
    else:
        raise ValueError("Category name is required.")

    def _register(name, category, schema, klass, title, description):
        ConfigletClass = configlettype.ConfigletType(
            str(name), schema, klass, title, description)
        interface.classImplements(ConfigletClass, schema)

        # register behavior for configlet
        bname = 'memphis.controlpanel-%s'%name

        # behavior
        bfactory = configlet.BehaviorFactory(name, bname)
        storage.registerBehavior(
            bname, schema, bfactory, schema = IConfigletData,
            title=title, description=description, configContext=None)

        # set additional attributes
        ConfigletClass.__category__ = category

        # configlet instance
        inst = ConfigletClass()

        # register configlet as utility
        config.registerUtility(inst, schema, '')

        # register configlet in control panel
        getUtility(IControlPanel).addConfiglet(inst)
        inst.__behavior__ = storage.getBehavior(schema)

    # add config action
    frame = sys._getframe(1)

    config.action.store.set(
        frame.f_locals, config.action,
        (_register, (name, category, schema, klass, title, description),
         {'discriminator': ('controlpanel:configlet', category, name)},
         config.getInfo()))

    del frame
