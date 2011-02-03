""" 

$Id: views.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from zope import interface
from memphis import view, config, form
from memphis.container import pagelets, interfaces
from memphis.container.location import LocationWrapper


class AddingMenu(object):

    def update(self):
        self.url = self.request.resource_url(self.context)
        self.factories = interfaces.IFactoryVocabulary(self.context)


class AddingForm(object):

    def __call__(self):
        request = self.request

        if request.subpath:
            fvoc = interfaces.IFactoryVocabulary(self.context)
            factory = fvoc.getTermByToken(request.subpath[0]).value
            factory = LocationWrapper(
                factory, self.context, factory.name)
            return view.renderView('', factory, request)

        raise NotFound


config.action(
    view.registerPagelet,
    pagelets.IAddingMenuView,
    klass = AddingMenu,
    template = view.template('memphis.container:templates/addingmenu.pt'))


config.action(
    view.registerView,
    '+', interfaces.IManageableContainer,
    klass = AddingForm)


config.action(
    view.registerPagelet,
    form.IFormActionsView, interfaces.IAddContentForm,
    template = view.template('memphis.container:templates/addformactions.pt'))

