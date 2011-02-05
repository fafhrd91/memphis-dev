"""

$Id: views.py 11810 2011-01-31 06:56:01Z fafhrd91 $
"""
from zope.component import getUtility, queryUtility
from zope.schema.interfaces import IVocabularyFactory

from pyramid import security
from pyramid.config import Configurator
from pyramid.exceptions import NotFound

from memphis import view, config, ttwschema, container
from memphis.form import form, field
from memphis.form.pagelets import IFormView
from memphis.preferences.root import Preferences
from memphis.preferences.interfaces import IPreferences, IPreference
from memphis.preferences.interfaces import ITTWProfileConfiglet


# layout
config.action(
    view.registerLayout,
    '', IPreferences, parent='page',
    template=view.template("memphis.preferences:templates/layout.pt"))


# /preferences/* route
def getPreferences(request):
    userid = security.authenticated_userid(request)
    if userid is None:
        raise NotFound

    return Preferences.get(userid)


def registerRoute():
    cfg = Configurator.with_context(config.getContext())
    cfg.add_route(
        'memphis.preferences', 'preferences/*traverse',
        factory=getPreferences, use_global_views = True)

config.action(registerRoute)


# preferences view
class PreferencesView(view.View):
    view.pyramidView(
        'index.html', IPreferences,
        template=view.template('memphis.preferences:templates/category.pt'))

    def update(self):
        super(PreferencesView, self).update()

        root = self.context
        request = self.request
        base_url = request.resource_url(root)

        data = []

        for category in root.categories.values():
            prefs = []
            for pref in category.values():
                pref = pref.__bind__(root.context)

                if not pref.isAvailable():
                    continue

                info = {'title': pref.__title__,
                        'description': pref.__description__,
                        'url': '%s%s/%s/'%(base_url, category.__name__,
                                           pref.__name__)
                        }

                prefs.append((pref.__title__, info))

            if prefs:
                prefs.sort()
                data.append(
                    (category.title,
                     {'title': category.title,
                      'description': category.description,
                      'prefs': [c for t, c in prefs]}))

        data.sort()
        self.data = [info for t, info in data]

config.action(
    view.registerDefaultView,
    'index.html', IPreferences)


# preference view

class Preference(view.View, form.EditForm):
    """ configlet view """
    view.pyramidView('index.html', IPreference)

    prefix = 'preference.'

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
    view.registerDefaultView, 'index.html', IPreference)


# profile configlet view
class TTWProfileConfigletView(view.View):
    view.pyramidView('index.html', ITTWProfileConfiglet)

    def render(self):
        context = self.context
        sch = ttwschema.ITTWSchema(context)
        sch.__name__ = context.__name__
        sch.__parent__ = context.__parent__
        return view.renderPagelet(
            ttwschema.ISchemaView, sch, self.request)


class AddProfileFieldView(view.View):
    view.pyramidView('+', ITTWProfileConfiglet)
    
    def __call__(self):
        context = self.context
        sch = ttwschema.ITTWSchema(context)
        sch.__name__ = context.__name__
        sch.__parent__ = context.__parent__
        return view.renderView('+', sch, self.request)


class ConfigletActions(view.Pagelet):
    view.pagelet(container.pagelets.IActions, ITTWProfileConfiglet)
    
    def __call__(self):
        context = self.context
        sch = ttwschema.ITTWSchema(context)
        sch.__name__ = context.__name__
        sch.__parent__ = context.__parent__
        return view.renderPagelet(
            container.pagelets.IActions, sch, self.request)


class ConfigletSchemaPreview(view.View):
    view.pyramidView('preview.html', ITTWProfileConfiglet)

    def __call__(self):
        context = self.context
        sch = ttwschema.ITTWSchema(context)
        sch.__name__ = context.__name__
        sch.__parent__ = context.__parent__
        sch.title = context.__title__
        sch.description = context.__description__
        return view.renderView('preview.html', sch, self.request)
