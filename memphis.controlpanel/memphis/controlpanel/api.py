"""

$Id: api.py 11787 2011-01-31 00:38:52Z fafhrd91 $
"""
from zope import interface
from zope.component import getUtility

from memphis import storage, config
from memphis.controlpanel import configlet, configlettype
from memphis.controlpanel.interfaces import IControlPanel, IConfigletData


def getControlPanel(*args):
    return getUtility(IControlPanel)


def registerCategory(
    name, marker=None, title='', description='', configContext=None):

    def _register(category):
        getUtility(IControlPanel).addCategory(category)

    category = configlet.ConfigletCategory(name, title, description)

    if marker is not None:
        interface.directlyProvides(category, marker)

    config.addAction(
        configContext,
        discriminator= ('controlpanel:category', name),
        callable = _register, args = (category,))

    return category


def registerConfiglet(name=None, schema=None, klass=None,
                      title='', description='', configContext=None):
    if '.' in name:
        category, name = name.split('.', 1)
    else:
        raise ValueError("Category name is required.")

    ConfigletClass = configlettype.ConfigletType(
        str(name), schema, klass, title, description)
    interface.classImplements(ConfigletClass, schema)

    # register behavior for configlet
    bname = 'memphis.controlpanel-%s'%name

    # behavior
    bfactory = configlet.BehaviorFactory(name, bname)
    storage.registerBehavior(
        bname, schema, bfactory, schema = IConfigletData,
        title=title, description=description, configContext=configContext)

    # set additional attributes
    ConfigletClass.__category__ = category

    # configlet instance
    inst = ConfigletClass()

    # register configlet as utility
    config.registerUtility(inst, schema, '')

    # register configlet in control panel
    def _register(configlet):
        getUtility(IControlPanel).addConfiglet(configlet)
        inst.__behavior__ = storage.getBehavior(schema)

    config.addAction(
        configContext,
        discriminator = ('controlpanel:configlet', name),
        callable = _register, args = (inst,))

    return inst
