from zope import interface
from pyramid import url
from memphis import config, view
from memphis.contenttype import pagelets
from memphis.contenttype.interfaces import \
    _, IContained, IContainer, \
    IContentType, IContentContainer, IDCTimes, IDCDescriptive


config.action(
    view.registerDefaultView,
    'listing.html', IContentContainer)

config.action(
    view.registerActions,
    ('listing.html', IContentContainer, 
     _('Listing'), _('Container listing.'), 11))


class Listing(view.Pagelet):
    view.pagelet(
        pagelets.IListing, IContentContainer,
        template = view.template('memphis.contenttype:templates/listing.pt'))

    def update(self):
        self.url = url.resource_url(IContained(self.context), self.request)
        self.container = IContainer(self.context)
        try:
            self.hasitems = self.container.keys().next()
        except StopIteration:
            self.hasitems = False

    def values(self):
        for item in self.container.values():
            c = IContained(item, item)
            try:
                dc = IDCDescriptive(item)
                dctimes = IDCTimes(item)
                yield {'name': c.__name__,
                       'title': dc.title,
                       'description': dc.description,
                       'modified': dctimes.modified,
                       'created': dctimes.created,
                       'type': IContentType(item).title}
            except KeyError:
                yield {'name': c.__name__,
                       'title': u'No title',
                       'description': u'',
                       'modified': u'--',
                       'created': u'--',
                       'type': IContentType(item).title}


class ListingView(view.View):
    view.pyramidView(
        'listing.html', IContentContainer,
        template = view.template(
            'memphis.contenttype:templates/listingview.pt'))

    def update(self):
        super(ListingView, self).update()

        try:
            dc = IDCDescriptive(self.context)
            self.title = dc.title
            self.description = dc.description
        except:
            self.title = 'No title'
            self.description = ''
