""" 

$Id: views.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from pyramid import url
from zope import interface
from zope.component import getAdapters
from zope.schema.vocabulary import SimpleVocabulary
from memphis import view, config, form
from memphis.container import pagelets, interfaces
from memphis.container.location import LocationWrapper


class AddingMenu(view.Pagelet):
    view.pagelet(
        pagelets.IAddingMenuView,
        template = view.template('memphis.container:templates/addingmenu.pt'))

    def update(self):
        self.url = url.resource_url(self.context, self.request)
        self.factories = interfaces.IFactoryVocabulary(self.context, None)
        if self.factories is None:
            self.factories = SimpleVocabulary(())


class AddingForm(view.View):
    view.pyramidView('+', interfaces.IContainer)

    def __call__(self):
        request = self.request

        if request.subpath:
            fvoc = interfaces.IFactoryVocabulary(self.context)
            factory = fvoc.getTermByToken(request.subpath[0]).value
            factory = LocationWrapper(
                factory, self.context, factory.name)
            return view.renderView('', factory, request)

        raise NotFound


class Actions(view.Pagelet):
    view.pagelet(
        pagelets.IActions,
        template = view.template('memphis.container:templates/actions.pt'))

    def update(self):
        self.actions = [action for name, action in 
                        getAdapters((self.context,), interfaces.IAction)]

    def render(self):
        if self.actions:
            return super(Actions, self).render()
        return u''


config.action(
    view.registerPagelet,
    form.IFormActionsView, interfaces.IAddContentForm,
    template = view.template('memphis.container:templates/addformactions.pt'))
