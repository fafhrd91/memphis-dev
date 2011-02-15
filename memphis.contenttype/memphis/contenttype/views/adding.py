""" adding views """
from pyramid import url
from zope import interface, component
from zope.component import getAdapters
from memphis import view, config, form
from memphis.contenttype import pagelets, interfaces
from memphis.contenttype.form import AddContentForm
from memphis.contenttype.location import LocationProxy


class AddingMenu(view.Pagelet):
    view.pagelet(
        pagelets.IAddingMenuView,
        template = view.template('memphis.contenttype:templates/addingmenu.pt'))

    def update(self):
        context = self.context

        self.url = url.resource_url(
            interfaces.IContained(context, context), self.request)

        factories = {}
        factories.update(getattr(context, '__factories__', {}))
        factories.update(
            [(name, factory) for name, factory in 
             getAdapters((context,), interfaces.IFactory) if name])

        for name, provider in \
                getAdapters((context,), interfaces.IFactoryProvider):
            for factory in provider:
                factories[factory.name] = factory

        factories = [(f.title, f) for f in factories.values()]
        factories.sort()
        self.factories = [f for t, f in factories]


class AddingForm(view.View):
    view.pyramidView('+', interfaces.IContainer)

    def __call__(self):
        request = self.request

        if request.subpath:
            context = self.context
            name = request.subpath[0]

            factory = getattr(context, '__factories__', {}).get(name)
            if factory is None:
                factory = component.queryAdapter(
                    context, interfaces.IFactory, name=name)

            if factory is None:
                for pname, provider in \
                        getAdapters((context,), interfaces.IFactoryProvider):
                    factory = provider.get(name)
                    if factory is not None:
                        break

            if factory is not None:
                return view.renderView(
                    '', LocationProxy(factory, context, name), request)

        raise NotFound


class AddContentForm(AddContentForm, view.View):
    view.pyramidView('', interfaces.IFactory)


config.action(
    view.registerPagelet,
    form.IFormActionsView, interfaces.IAddContentForm,
    template = view.template('memphis.contenttype:templates/addformactions.pt'))
