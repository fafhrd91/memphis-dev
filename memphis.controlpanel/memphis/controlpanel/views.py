"""

$Id: views.py 11810 2011-01-31 06:56:01Z fafhrd91 $
"""
from pyramid import url
from pyramid.config import Configurator
from memphis import view, config
from memphis.form import form, field
from memphis.controlpanel.api import getControlPanel
from memphis.controlpanel.interfaces import IConfiglet, IControlPanel


# layout
config.action(
    view.registerLayout,
    '', IControlPanel, parent='page', skipParent=True,
    template=view.template("memphis.controlpanel:templates/layout.pt"))


# /settings/* route
def registerRoute():
    cfg = Configurator.with_context(config.getContext())
    cfg.add_route(
        'memphis.controlpanel', 'settings/*traverse',
        factory=getControlPanel, use_global_views = True)

config.action(registerRoute)


# control panel view
class ControlPanelView(object):

    def update(self):
        super(ControlPanelView, self).update()

        request = self.request
        cp = getControlPanel(request)
        base_url = url.resource_url(cp, request)

        data = []

        for category in cp.values():
            configlets = []
            for configlet in category.values():
                info = {'title': configlet.__title__,
                        'description': configlet.__description__,
                        'url': '%s%s/%s/'%(base_url, category.__name__,
                                           configlet.__name__)
                        }

                configlets.append((configlet.__title__, info))

            if configlets:
                configlets.sort()
                data.append(
                    (category.title,
                     {'title': category.title,
                      'description': category.description,
                      'configlets': [c for t, c in configlets]}))

        data.sort()
        self.data = [info for t, info in data]


config.action(
    view.registerView,
    'index.html', IControlPanel, ControlPanelView,
    template=view.template('memphis.controlpanel:templates/category.pt'))

config.action(
    view.registerDefaultView,
    'index.html', IControlPanel)


# configlet view

class Configlet(form.EditForm):
    """ configlet view """

    prefix = 'configlet.'

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    @property
    def fields(self):
        return field.Fields(self.context.__schema__)


config.action(
    view.registerView,
    'index.html', IConfiglet, Configlet)

config.action(
    view.registerDefaultView, 'index.html', IConfiglet)
