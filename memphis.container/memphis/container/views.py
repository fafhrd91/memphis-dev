""" 

$Id: views.py 4729 2011-02-03 05:26:47Z nikolay $
"""
from pyramid import url
from zope import interface, component
from zope.component import getAdapters
from zope.schema.vocabulary import SimpleVocabulary
from memphis import view, config, form
from memphis.container import pagelets, interfaces
from memphis.container.form import AddContentForm
from memphis.container.location import LocationProxy


config.action(
    view.registerDefaultView,
    'listing.html', interfaces.IContainer)


class Listing(view.Pagelet):
    view.pagelet(
        pagelets.IListing,
        template = view.template('memphis.container:templates/listing.pt'))

    def update(self):
        self.url = url.resource_url(
            interfaces.IContained(self.context), self.request)

    def values(self):
        for item in self.context.values():
            yield interfaces.IContained(item, item)


class ListingView(view.View):
    view.pyramidView(
        'listing.html', interfaces.IContainer,
        template = view.template('memphis.container:templates/listingview.pt'))

    def update(self):
        context = self.context
        self.title = getattr(context, 'title', context.__name__)
        self.description = getattr(context, 'description', '')


class AddingMenu(view.Pagelet):
    view.pagelet(
        pagelets.IAddingMenuView,
        template = view.template('memphis.container:templates/addingmenu.pt'))

    def update(self):
        context = self.context

        self.url = url.resource_url(
            interfaces.IContained(context), self.request)

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
    template = view.template('memphis.container:templates/addformactions.pt'))
