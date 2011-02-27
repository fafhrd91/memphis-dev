""" Control panel """
from zope import interface
from memphis import storage, config, view
from memphis.controlpanel import interfaces
from memphis.controlpanel.api import registerCategory, registerConfiglet

_ = interfaces._


class ControlPanel(dict):
    interface.implements(interfaces.IControlPanel)

    __name__ = 'settings'
    __parent__ = view.Root

    def __init__(self):
        self.configlets = {}

    def addConfiglet(self, configlet):
        category = self[configlet.__category__]
        category.addConfiglet(configlet)

    def addCategory(self, category):
        if category.__name__ in self:
            raise KeyError(category.__name__)

        category.__parent__ = self

        self[category.__name__] = category

    def __repr__(self):
        return "ControlPanel"


def registerControlPanel():
    config.registerUtility(ControlPanel(), interfaces.IControlPanel, '')

config.action(registerControlPanel)


registerCategory(
    "default", interfaces.IDefaultCategory,
    _(u"Basic configuration"))

registerCategory(
    "system", interfaces.ISystemCategory,
    _(u"System configuration"),
    _(u"This area allows you to configure system."))

registerCategory(
    "ui", interfaces.IUICategory,
    _(u"User interface configuration"),
    _(u"This area allows you to configure portal look&amp;feel."))

registerCategory(
    "principals", interfaces.IPrincipalsCategory,
    _("Principals management"),
    _("Portal principals management panel."))
