""" Control panel

$Id: cp.py 11791 2011-01-31 02:57:54Z fafhrd91 $
"""
from zope import interface
from memphis import storage, config, view
from memphis.controlpanel.api import registerCategory, registerConfiglet
from memphis.controlpanel.interfaces import _, IControlPanel


class ControlPanel(dict):
    interface.implements(IControlPanel)

    __name__ = 'settings'
    __parent__ = view.Root

    configlets = {}

    def addConfiglet(self, configlet):
        category = self[configlet.__category__]
        category.addConfiglet(configlet)

    def addCategory(self, category):
        if category.__name__ in self:
            raise KeyError(category.__name__)

        category.__parent__ = self

        self[category.__name__] = category


config.action(
    config.registerUtility,
    ControlPanel(), IControlPanel, '')


config.action(
    registerCategory,
    "default", _(u"Basic configuration"))

config.action(
    registerCategory,
    "system", _(u"System configuration"),
    _(u"This area allows you to configure system."))

config.action(
    registerCategory,
    "ui", _(u"User interface configuration"),
    _(u"This area allows you to configure portal look&amp;feel."))

config.action(
    registerCategory,
    "content", _(u"Content types"),
    _(u"This area allows you to configure portal content types."))

config.action(
    registerCategory,
    "principals", _("Principals management"),
     _("Portal principals management panel."))


#api.registerRelation(
#    u"memphis.controlpanel", title=u'Control panel configlet')
#
#api.registerBehavior(
#    u'memphis.controlpanel', IControlPanel, ControlPanel,
#    title = u'Control Panel')
