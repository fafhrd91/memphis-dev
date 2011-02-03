""" memphis.controlpanel interfaces

$Id: interfaces.py 11787 2011-01-31 00:38:52Z fafhrd91 $
"""
from zope import schema, interface
from pyramid.i18n import TranslationStringFactory

from memphis import storage, view

_ = TranslationStringFactory('memphis.controlpanel')


class IConfiglet(interface.Interface):
    """A group of settings."""

    __id__ = schema.TextLine(
        title = u"Id",
        description = u"The id of the configlet.",
        required = True)

    __title__ = schema.TextLine(
        title = u"Title",
        description = u"The title of the configlet used in the UI.",
        required = True)

    __description__ = schema.TextLine(
        title = u"Description",
        description = u"The description of the configlet used in the UI.",
        required = False)

    __schema__ = interface.Attribute('Configlet schema (readonly)')

    __category__ = interface.Attribute('Configlet category')

    def isAvailable():
        """ is configlet available in current site """


class IControlPanel(view.IRoot):
    """ root settings configlet """

    def addCategory(category):
        """ add category """

    def addConfiglet(configlet):
        """ add configlet """


class IConfigletCategory(interface.Interface):
    """A group of configlets."""

    name = schema.TextLine(
        title = u"Name",
        description = u"The name of the configlet.",
        required = True)

    title = schema.TextLine(
        title = u"Title",
        description = u"The title of the category.",
        required = True)

    description = schema.TextLine(
        title = u"Description",
        description = u"The description of the category.",
        required = False)

    def addConfiglet(configlet):
        """ add configlet """


class IConfigletData(interface.Interface):
    storage.schema('memphis.controlpanel',
                   title='Configlet data container')

    data = schema.Dict(
        title = u'Configlet data',
        default = {},
        required = True)
