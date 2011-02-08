"""

$Id: views.py 11810 2011-01-31 06:56:01Z fafhrd91 $
"""
from pyramid import url
from pyramid.config import Configurator
from zope.component import getAdapters

from memphis import view, config, form, container
from memphis.controlpanel.api import getControlPanel
from memphis.controlpanel.interfaces import IConfiglet, IControlPanel


# layout
class LayoutView(object):

    data = None

    def update(self):
        super(LayoutView, self).update()

        self.actions = [action for name, action in 
                        getAdapters((self.maincontext,), container.IAction)]

        context = self.maincontext
        cp = getControlPanel()
        if context is cp:
            return

        data = []
        while not IConfiglet.providedBy(context):
            context = getattr(context, '__parent__', None)
            if context is None:
                break

        id = getattr(context, '__id__', '')
        base_url = url.resource_url(cp, self.request)

        for category in cp.values():
            configlets = []
            for configlet in category.values():
                info = {'title': configlet.__title__,
                        'description': configlet.__description__,
                        'url': '%s%s/%s/'%(base_url, category.__name__,
                                           configlet.__name__),
                        'selected': configlet.__id__ == id
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
    view.registerLayout,
    '', IControlPanel, parent='page', skipParent=True,
    klass = LayoutView,
    template=view.template("memphis.controlpanel:templates/layout.pt"))


# /settings/* route
def registerRoute():
    cfg = Configurator.with_context(config.getContext())
    cfg.add_route(
        'memphis.controlpanel', 'settings/*traverse',
        factory=getControlPanel, use_global_views = True)

config.action(registerRoute)


class ControlPanelView(view.View):
    view.pyramidView(
        'index.html', IControlPanel,
        template=view.template('memphis.controlpanel:templates/category.pt'))

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
    view.registerDefaultView,
    'index.html', IControlPanel)


# configlet view

class Configlet(form.EditForm, view.View):
    """ configlet view """
    view.pyramidView('index.html', IConfiglet)

    prefix = 'configlet.'

    @property
    def label(self):
        return self.context.__title__

    @property
    def description(self):
        return self.context.__description__

    @property
    def fields(self):
        return form.Fields(self.context.__schema__)


config.action(
    view.registerDefaultView, 'index.html', IConfiglet)
