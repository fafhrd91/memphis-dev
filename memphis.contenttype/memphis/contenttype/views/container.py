from zope import interface
from pyramid import url
from memphis import config, view, container
from memphis.contenttype.interfaces import IContentType, IContentContainer
from memphis.contenttype import schemas

config.action(
    view.registerDefaultView,
    'listing.html', IContentContainer)


class Listing(view.Pagelet):
    view.pagelet(
        container.pagelets.IListing, IContentContainer,
        template = view.template('memphis.contenttype:templates/listing.pt'))

    def update(self):
        self.url = url.resource_url(self.context, self.request)
        self.container = container.IContainer(self.context)
        try:
            self.hasitems = self.container.keys().next()
        except StopIteration:
            self.hasitems = False

    def values(self):
        for item in self.container.values():
            c = container.IContained(item, item)
            try:
                dc = schemas.IDublinCore(item)
                yield {'name': c.__name__,
                       'title': dc.title,
                       'modified': dc.modified,
                       'created': dc.created,
                       'type': IContentType(item).title}
            except KeyError:
                yield {'name': c.__name__,
                       'title': 'No title',
                       'modified': '--',
                       'created': '--',
                       'type': IContentType(item).title}


class ListingView(view.View):
    view.pyramidView(
        'listing.html', IContentContainer,
        template = view.template(
            'memphis.contenttype:templates/listingview.pt'))

    def update(self):
        super(ListingView, self).update()

        
